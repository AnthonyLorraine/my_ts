from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from datetime import datetime, timedelta
import autoslug
from django.db.models import Sum


class Settings(models.Model):
    name = models.TextField(unique=True)
    value = models.TextField()

    # Celery/Redis Task?
    @staticmethod
    def update_pay_period():
        today = datetime.today()
        current_period = Settings.objects.get(name='pay_period')
        current_pay_period = current_period.value
        next_pay_period = datetime.strptime(current_pay_period, '%d%m%Y') + timedelta(days=14)
        if next_pay_period > today:
            pass
        else:
            current_period.value = next_pay_period.strftime('%d%m%Y')
            current_period.save()

    @staticmethod
    def get_pay_period():
        return datetime.strptime(Settings.objects.get(name='pay_period').value, '%d%m%Y')


class PenaltyType(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name

    @property
    def is_used(self):
        return Penalty.objects.filter(penalty_type=self).count() > 0

    def available_employee_time(self, employee: 'Employee'):
        employee_timesheets = Timesheet.objects.filter(penalty__penalty_type=self, employee=employee)
        employee_claims = PenaltyClaim.objects.filter(employee=employee, penalty=self)
        available_time = sum([ts.payout_duration_str.total_seconds()/3600 for ts in employee_timesheets if not ts.expired ])
        claimed_time = sum([claim.claimed_seconds/3600 for claim in employee_claims])
        return available_time - claimed_time


class Penalty(models.Model):
    name = models.TextField()
    penalty_type = models.ForeignKey(PenaltyType, on_delete=models.RESTRICT)
    valid_for_day_count = models.IntegerField(default=14)

    def __str__(self):
        return self.name


class Employee(AbstractUser):
    team = models.ForeignKey('Team', on_delete=models.RESTRICT, null=True, blank=True)
    slug = autoslug.AutoSlugField(populate_from='get_full_name', unique=True, null=True)
    tutorial_done = models.BooleanField(default=False)

    def add_timesheet(self, start_date_time: datetime, duration: int, penalty: Penalty):
        ts = Timesheet.objects.create(employee=self,
                                      start_date_time=start_date_time,
                                      duration=duration,
                                      penalty=penalty)
        ts.save()

    def claim_penalty(self, penalty: Penalty, claimed_seconds: int):
        if self.can_claim(penalty, claimed_seconds):
            claimed = PenaltyClaim.objects.create(employee=self,
                                                  penalty=penalty,
                                                  claimed_seconds=claimed_seconds)
            claimed.save()
        else:
            print('Employee doesn\'t have enough time available to make this claim.')

    def can_claim(self, penalty: Penalty, amount_to_claim: int) -> bool:
        employee_time_sheets = Timesheet.objects.filter(employee=self, penalty=penalty)
        available_time = sum([ts.payout_duration_str for ts in employee_time_sheets if not ts.expired])
        if available_time >= amount_to_claim:
            return True
        else:
            return False

    @property
    def last_5_time_sheets(self):
        pay_period = Settings.get_pay_period()
        time_sheets = Timesheet.objects.filter(employee=self).filter(start_date_time__lte=pay_period).order_by(
            'start_date_time').reverse()[:5]
        return time_sheets

    @property
    def pay_period_time_sheets(self):
        pay_period = Settings.get_pay_period()
        time_sheets = Timesheet.objects.filter(employee=self
                                               ).filter(start_date_time__gte=pay_period,
                                                        start_date_time__lte=pay_period + timedelta(days=14)
                                                        ).order_by('start_date_time').reverse()[:5]
        return time_sheets

    def __str__(self):
        return f'[{self.username}] {self.first_name} {self.last_name}'

    @property
    def total_time_sheets_submitted(self) -> int:
        time_sheets = Timesheet.objects.filter(employee=self)
        return time_sheets.count()

    @property
    def duration_per_penalty(self):
        penalties = PenaltyType.objects.all()
        durations = []
        for penalty in penalties:
            durations.append({'penalty': penalty,
                              'available': penalty.available_employee_time(self)})
        return durations

    @property
    def duration_outstanding_per_penalty_type(self):
        time_sheet = Timesheet.objects.filter(employee=self)
        penalty_types = PenaltyType.objects.all()
        duration = []
        for pt in penalty_types:
            time = {}
            timer = 0
            for tsr in time_sheet:
                if tsr.penalty.penalty_type.name == pt.name and not tsr.expired:
                    timer += tsr.payout_duration_str.total_seconds() / 3600
            time[pt.name] = round(timer)
            duration.append(time)
        return duration

    @property
    def is_manager(self):
        if self.groups:
            try:
                self.groups.get(name='Manager')
                return True
            except KeyError:
                return False
        else:
            return False


class Team(models.Model):
    name = models.TextField()
    manager = models.ForeignKey(Employee, on_delete=models.RESTRICT, related_name='team_manager', blank=True, null=True)
    slug = autoslug.AutoSlugField(populate_from='name', unique=True, null=True)

    def __str__(self):
        return self.name

    @property
    def staff_count(self):
        return Employee.objects.filter(team=self).count()

    @property
    def staff_penalty_hours(self):
        time_sheets = Timesheet.objects.filter(employee__team=self)
        penalty_types = PenaltyType.objects.all()
        duration = []
        for pt in penalty_types:
            time = {}
            timer = 0
            for tsr in time_sheets:
                if tsr.penalty.penalty_type.name == pt.name and not tsr.expired:
                    timer += tsr.payout_duration_str.total_seconds() / 3600
            time[pt.name] = round(timer)
            duration.append(time)
        return duration

    def add_staff(self, staff: Employee):
        if staff.team is None:
            staff.team = self
            staff.save()
        else:
            print('# Error, staff already in a team. staff.team')

    def add_manager(self, staff: Employee):
        if staff.team is None and self.manager is None:
            staff.team = self
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.add(staff)
            manager_group.save()
            self.manager = staff
            self.save()
            staff.save()
        else:
            print('Staff in a team or Team has a manager')

    def remove_staff(self, staff: Employee):
        if staff.team is not None:
            staff.team = None
            staff.save()
        else:
            print('# Error, staff not in a team. ')

    def remove_manager(self, staff: Employee):
        if staff.team is not None and self.manager is not None:
            staff.team = None
            staff.save()
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.remove(staff)
            manager_group.save()
            self.manager = None
            self.save()
        else:
            print('# Error, staff team is None or team manager is none already. ')

    @property
    def time_sheets(self):
        return Timesheet.objects.filter(employee__team=self)


class Timesheet(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT)
    start_date_time = models.DateTimeField()
    duration = models.IntegerField()
    penalty = models.ForeignKey(Penalty, on_delete=models.RESTRICT)

    @property
    def expired(self):

        today = datetime.today()
        if self.start_date_time + timedelta(self.penalty.valid_for_day_count) <= today:
            return False
        else:
            return True

    @property
    def rows(self):
        rows = TimesheetRow.objects.filter(timesheet=self)
        return rows

    @property
    def duration_str(self):
        return f'{timedelta(seconds=self.duration)}'

    @property
    def payout_duration_str(self):
        rows = TimesheetRow.objects.filter(timesheet=self)
        payout_seconds = 0
        for ts in rows:
            payout_seconds += ts.payout_seconds
        return timedelta(seconds=payout_seconds)

    def save(self, *args, **kwargs):
        super(Timesheet, self).save(*args, **kwargs)
        self.create_time_sheet_row()

    @property
    def end_date_time(self):
        return self.start_date_time + timedelta(seconds=self.duration)

    def create_time_sheet_row(self):
        diff = self.end_date_time - self.start_date_time

        def get_hours_left(ts):
            return 24 - (ts.hour + ts.minute / 60)

        # Worked Time is all within one day.
        if self.start_date_time.date() == self.end_date_time.date():
            tsr = TimesheetRow.objects.create(date_worked=self.start_date_time.date(),
                                              worked_seconds=self.duration,
                                              payout_seconds=self.get_payout_amount_in_seconds(
                                                  day=self.start_date_time.date(),
                                                  hours=self.duration / 3600),
                                              timesheet_id=self.pk)
            tsr.save()
        else:
            # Worked Time is on multiple days.
            start = self.start_date_time
            for day in range(diff.days + bool(diff.seconds) + 1):
                if start.date() != self.end_date_time.date():
                    hours_remaining = get_hours_left(start)
                else:
                    hours_remaining = self.end_date_time.hour + self.end_date_time.minute / 60
                tsr = TimesheetRow.objects.create(date_worked=start.date(),
                                                  worked_seconds=round(hours_remaining) * 3600,
                                                  payout_seconds=self.get_payout_amount_in_seconds(
                                                      day=start.date(),
                                                      hours=round(hours_remaining)),
                                                  timesheet=self)
                tsr.save()
                start = start + timedelta(hours=hours_remaining)

    def public_holiday(self, day):
        return False

    def get_payout_amount_in_seconds(self, day, hours) -> int:
        is_public_holiday = self.public_holiday(day)
        duration = 0
        if is_public_holiday:  # public holiday 2.5x Multiplier
            duration += hours * 3600 * 2.5
        elif day.weekday() == 6 and not is_public_holiday:  # Sunday 2x Multiplier
            duration += hours * 3600 * 2
        elif not is_public_holiday and not day.weekday() == 6:  # Base 1.5x Multiplier
            duration += hours * 3600 * 1.5
        return round(duration)


class TimesheetRow(models.Model):
    date_worked = models.DateField()
    worked_seconds = models.IntegerField()
    payout_seconds = models.IntegerField()
    timesheet = models.ForeignKey(Timesheet, on_delete=models.RESTRICT)

    @property
    def payout_duration_str(self):
        return f'{timedelta(seconds=self.payout_seconds)}'

    @property
    def worked_duration_str(self):
        return f'{timedelta(seconds=self.worked_seconds)}'


class PenaltyClaim(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT)
    claimed_seconds = models.IntegerField(verbose_name='Duration')
    penalty = models.ForeignKey(PenaltyType, on_delete=models.RESTRICT)
    claim_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.penalty.available_employee_time(self.employee) <= 0:
            print('Not enough available time')
        else:
            super(PenaltyClaim, self).save(*args, **kwargs)

