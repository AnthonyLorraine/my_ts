from django.db.models.query import QuerySet
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ValidationError
from django.db import models
from datetime import datetime, timedelta
import autoslug
from django.urls import reverse


class PenaltyType(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name

    @property
    def is_used(self):
        return Penalty.objects.filter(penalty_type=self).count() > 0

    def calculate_available_employee_time(self, employee: 'Employee'):
        employee_timesheets = Timesheet.objects.filter(penalty__penalty_type=self, employee=employee)
        employee_claims = Claim.objects.filter(employee=employee, penalty_type=self)
        available_time = sum([ts.claimable_duration.total_seconds() for ts in employee_timesheets])
        claimed_time = sum([claim.claimed_seconds for claim in employee_claims])
        return (available_time - claimed_time) / 3600


class Penalty(models.Model):
    penalty_types = [
        ('PD', 'Paid'),
        ('TL', 'Toil')
    ]
    name = models.TextField()
    penalty_type = models.CharField(max_length=2, choices=penalty_types, default='PD')
    # penalty_type = models.ForeignKey(PenaltyType, on_delete=models.RESTRICT)
    valid_for_day_count = models.IntegerField(default=14)
    base_threshold = models.IntegerField(default=7200)

    def __str__(self):
        return self.name


class Employee(AbstractUser):
    team = models.ForeignKey('Team', on_delete=models.RESTRICT, null=True, blank=True)
    slug = autoslug.AutoSlugField(populate_from='get_full_name', unique=True, null=True)
    tutorial_done = models.BooleanField(default=False)

    def __str__(self):
        return f'[{self.username}] {self.first_name} {self.last_name}'

    def add_timesheet(self, start_date_time: datetime, duration: int, penalty: Penalty):
        ts = Timesheet.objects.create(employee=self,
                                      start_date_time=start_date_time,
                                      _duration=duration,
                                      penalty=penalty)
        ts.save()

    def add_claim(self, penalty_type: PenaltyType, claimed_seconds: int):
        claimed = Claim.objects.create(employee=self,
                                       penalty=penalty_type,
                                       claimed_seconds=claimed_seconds)
        claimed.save()

    @property
    def last_5_time_sheets(self):
        time_sheets = Timesheet.objects.filter(employee=self).order_by(
            'start_date_time').reverse()[:5]
        return time_sheets

    @property
    def last_5_claims(self):
        return Claim.objects.filter(employee=self).order_by('claim_date').reverse()[:5]

    @property
    def total_time_sheets_submitted(self) -> int:
        time_sheets = Timesheet.objects.filter(employee=self)
        return time_sheets.count()

    @property
    def total_claims_submitted(self):
        claim = Claim.objects.filter(employee=self)
        return claim.count()

    @property
    def duration_per_penalty(self):
        """
        Gets available claimable time in hours for each penalty type.

        :return: List[Dictionary{penalty:PenaltyType, available: Int}
        """
        penalties = PenaltyType.objects.all()
        durations = []
        for penalty in penalties:
            durations.append({'penalty_type': penalty,
                              'available': penalty.calculate_available_employee_time(self)})
        return durations

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

    def add_employee(self, employee: Employee):
        """
        Add an employee to the team.

        :param employee: Employee object
        """
        if employee.team:
            raise ValidationError(f'Error, staff already in team "{employee.team.name}".')
        employee.team = self
        employee.save()

    def add_manager(self, employee: Employee):
        """
        Adds the employee to the team using self.add_employee then adds the employee to the Manager group.

        :param employee: Employee object
        """
        if self.manager:
            raise ValidationError(f'Team already has a manager, "{self.manager.name}".')

        self.add_employee(employee)  # Add Employee to the team

        manager_group = Group.objects.get(name='Manager')  # Add Employee to the Manager group
        manager_group.user_set.add(employee)
        manager_group.save()
        self.manager = employee  # Set the teams manager to the Employee
        self.save()

    def remove_employee(self, employee: Employee):
        """
        Removes an employee from a team.

        :param employee: Employee object
        """
        if employee.team != self:
            raise ValidationError('Employee isn\'t a member of this team.')
        if employee.team is None:
            raise ValidationError('Employee isn\'t a member of a team.')
        employee.team = None
        employee.save()

    def remove_manager(self, employee: Employee):
        """
        Removes the employee from the team using self.remove_employee then removes the employee from the Manager group.
        Finally sets the team manager to None.

        :param employee: Employee object
        """
        if self.manager != employee:
            raise ValidationError('Employee isn\'t the manager of this team.')

        self.remove_employee(employee)  # Remove Employee from the team

        manager_group = Group.objects.get(name='Manager')  # Remove Employee from the Manager group
        manager_group.user_set.remove(employee)
        manager_group.save()

        self.manager = None  # Remove the team manager.
        self.save()

    @property
    def staff_count(self):
        return Employee.objects.filter(team=self).count()

    @property
    def duration_per_penalty(self) -> list:
        # todo Needs to match the Employee duration_per_penalty, to make rendering the same on the templates.
        """
        Gets available claimable time in hours for each penalty type for the team.

        :return: List[Dictionary{penalty:PenaltyType, available: Int}]
        """
        durations = {}
        for employee in Employee.objects.filter(team=self):
            for penalty in employee.duration_per_penalty:
                try:
                    durations[penalty['penalty_type'].name] += penalty['available']
                except KeyError:
                    durations[penalty['penalty_type'].name] = penalty['available']
        return list(zip(list(durations), list(durations.values())))


def get_hours_left(ts):
    return 24 - (ts.hour + ts.minute / 60)


class Timesheet(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT)
    start_date_time = models.DateTimeField()
    _duration = models.IntegerField()
    penalty = models.ForeignKey(Penalty, on_delete=models.RESTRICT)
    claim = models.ForeignKey('TimesheetClaim', blank=True, null=True, on_delete=models.RESTRICT)

    def save(self, *args, **kwargs):
        super(Timesheet, self).save(*args, **kwargs)
        self.create_time_sheet_row()
        self.create_time_sheet_cost_row()

    def create_time_sheet_row(self):
        diff = self.end_date_time - self.start_date_time

        # Worked Time is all within one day.
        if self.start_date_time.date() == self.end_date_time.date():
            TimesheetRow.objects.create(date_worked=self.start_date_time.date(),
                                        worked_seconds=self.duration.total_seconds(),
                                        payout_seconds=self._calculate_payout_amount_in_seconds(
                                            day=self.start_date_time.date(),
                                            seconds=self.duration.total_seconds()),
                                        timesheet_id=self.pk)
        else:
            # Worked Time is on multiple days.
            start = self.start_date_time
            for day in range(diff.days + bool(diff.seconds) + 1):
                if start.date() != self.end_date_time.date():
                    hours_remaining = get_hours_left(start)
                else:
                    hours_remaining = self.end_date_time.hour + self.end_date_time.minute / 60
                TimesheetRow.objects.create(date_worked=start.date(),
                                            worked_seconds=round(hours_remaining * 3600),
                                            payout_seconds=self._calculate_payout_amount_in_seconds(
                                                day=start.date(),
                                                seconds=round(hours_remaining * 3600)),
                                            timesheet=self)

                start = start + timedelta(hours=hours_remaining)

    def create_time_sheet_cost_row(self):
        if self.start_date_time.date() == self.end_date_time.date():
            # Worked Time is all within one day.
            self._calculate_and_create_cost_codes(self.start_date_time.date(), self._duration, 0)
        else:
            # Worked Time is on multiple days.
            start = self.start_date_time
            diff = self.end_date_time - self.start_date_time
            prior_day_time = 0
            for day in range(diff.days + bool(diff.seconds) + 1):
                if start.date() != self.end_date_time.date():
                    hours_remaining = get_hours_left(start)
                else:
                    hours_remaining = self.end_date_time.hour + self.end_date_time.minute / 60

                self._calculate_and_create_cost_codes(start.date(),
                                                      round(hours_remaining * 3600),
                                                      prior_day_time)
                prior_day_time = round(hours_remaining * 3600)

                start = start + timedelta(hours=hours_remaining)

    def public_holiday(self, day):
        return False

    def _calculate_payout_amount_in_seconds(self, day, seconds) -> int:
        is_public_holiday = self.public_holiday(day)
        duration = 0
        if is_public_holiday:  # public holiday 2.5x Multiplier
            duration += seconds * 2.5
        elif day.weekday() == 6 and not is_public_holiday:  # Sunday 2x Multiplier
            duration += seconds * 2
        elif not is_public_holiday and not day.weekday() == 6:  # Base 1.5x Multiplier
            duration += seconds * 1.5
        return round(duration)

    def _calculate_and_create_cost_codes(self, day, seconds, prior) -> None:
        is_public_holiday = self.public_holiday(day)
        over_base_threshold = prior >= self.penalty.base_threshold
        seconds_below_threshold = seconds < self.penalty.base_threshold
        first_record = prior == 0
        if is_public_holiday:  # Always public holiday 2.5x Multiplier
            cost_code = CostCode.objects.get(pk=3)  # Not ideal
            TimesheetClaimRow.objects.create(time_sheet=self,
                                             cost_code=cost_code,
                                             seconds=seconds)
            return
        elif day.weekday() == 6 and not is_public_holiday:  # Always Sunday 2x Multiplier
            cost_code = CostCode.objects.get(pk=2)  # Not ideal
            TimesheetClaimRow.objects.create(time_sheet=self,
                                             cost_code=cost_code,
                                             seconds=seconds)
            return
        elif not is_public_holiday and not day.weekday() == 6:  # Weekday, no modifiers, can have carry over

            if first_record and seconds_below_threshold:  # First cost code entered, not over threshold
                cost_code = CostCode.objects.get(pk=1)  # Not ideal
                # All seconds are added to base code, no further actions
                TimesheetClaimRow.objects.create(
                    time_sheet=self,
                    cost_code=cost_code,
                    seconds=seconds
                )
                return

            if first_record and not seconds_below_threshold:  # First cost code entered, over threshold
                cost_code = CostCode.objects.get(pk=1)  # Not ideal
                # Assign the base threshold seconds to the base code
                TimesheetClaimRow.objects.create(
                    time_sheet=self,
                    cost_code=cost_code,
                    seconds=self.penalty.base_threshold
                )
                cost_code = CostCode.objects.get(pk=2)  # Not ideal
                # Assign remaining seconds to the overtime code
                TimesheetClaimRow.objects.create(
                    time_sheet=self,
                    cost_code=cost_code,
                    seconds=abs(self.penalty.base_threshold - seconds)
                )
                return

            if not first_record and over_base_threshold:
                # previous record already over threshold, apply next modifier to remaining time.
                # check if there is a previous record with the same code
                cost_code = CostCode.objects.get(pk=2)
                tcr = TimesheetClaimRow.objects.filter(time_sheet=self, cost_code=cost_code).first()
                if tcr:
                    # add seconds to existing claim
                    tcr.seconds += seconds
                    tcr.save()
                    return
                else:
                    # create new claim with over time code
                    TimesheetClaimRow.objects.create(
                        time_sheet=self,
                        cost_code=cost_code,
                        seconds=seconds
                    )
                    return

            if not first_record and not over_base_threshold:
                # previous record wasn't over the threshold
                cost_code = CostCode.objects.get(pk=1)
                # take the prior amount and subtract it from the base threshold
                # then use that value to create a claim with the base code
                tcr = TimesheetClaimRow.objects.filter(time_sheet=self, cost_code=cost_code).first()
                if tcr:
                    tcr.seconds += abs(prior - self.penalty.base_threshold)
                    tcr.save()
                else:
                    TimesheetClaimRow.objects.create(
                        time_sheet=self,
                        cost_code=cost_code,
                        seconds=abs(prior - self.penalty.base_threshold)
                    )

                cost_code = CostCode.objects.get(pk=2)
                # remaining seconds are to be used on the over time code
                TimesheetClaimRow.objects.create(
                    time_sheet=self,
                    cost_code=cost_code,
                    seconds=abs(seconds - abs(prior - self.penalty.base_threshold))
                )
                return

    @property
    def expired(self):
        today = datetime.today()
        expiry_date = self.start_date_time + timedelta(self.penalty.valid_for_day_count)
        if expiry_date >= today:
            return False
        else:
            return True

    @property
    def rows(self) -> QuerySet:
        """
        List of the timesheet rows.

        :return: QuerySet[TimesheetRow]
        """
        rows = TimesheetRow.objects.filter(timesheet=self)
        return rows

    @property
    def costs(self):
        return TimesheetClaimRow.objects.filter(time_sheet=self)

    @property
    def duration(self):
        return timedelta(seconds=self._duration)

    @property
    def claimable_duration(self):
        return self.accrued_duration if not self.expired else timedelta(seconds=0)

    @property
    def accrued_duration(self):
        return timedelta(seconds=sum([row.accrued_duration.total_seconds() for row in self.rows]))

    @property
    def end_date_time(self):
        return self.start_date_time + timedelta(seconds=self.duration.total_seconds())


class TimesheetRow(models.Model):
    date_worked = models.DateField()
    worked_seconds = models.IntegerField()
    payout_seconds = models.IntegerField()
    timesheet = models.ForeignKey(Timesheet, on_delete=models.RESTRICT)

    @property
    def duration(self):
        return timedelta(seconds=self.worked_seconds)

    @property
    def accrued_duration(self):
        return timedelta(seconds=self.payout_seconds)

    @property
    def day_name(self):
        return self.date_worked.strftime("%A")


class Claim(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.RESTRICT)
    claimed_seconds = models.IntegerField(verbose_name='Duration')
    penalty_type = models.ForeignKey(PenaltyType, on_delete=models.RESTRICT)
    claim_date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.employee_can_claim_penalty_type():
            super(Claim, self).save(*args, **kwargs)
        else:
            raise ValidationError('Employee doesn\'t have enough time available to make this claim.', code='invalid')

    def employee_can_claim_penalty_type(self) -> bool:
        employee_time_sheets = Timesheet.objects.filter(employee=self.employee, penalty__penalty_type=self.penalty_type)
        available_time = sum([ts.penalty.penalty_type.calculate_available_employee_time(self.employee) * 3600
                              for ts in employee_time_sheets])
        if available_time >= self.claimed_seconds:
            return True
        else:
            return False

    @property
    def duration(self):
        return timedelta(seconds=self.claimed_seconds)


class CostCode(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=50)


class TimesheetClaimRow(models.Model):
    time_sheet = models.ForeignKey(Timesheet, on_delete=models.RESTRICT)
    cost_code = models.ForeignKey(CostCode, on_delete=models.RESTRICT)
    seconds = models.IntegerField(default=0)

    @property
    def units(self):
        return self.seconds / 3600


class TimesheetClaim(models.Model):
    pay_date = models.DateField(blank=True, null=True)

    @property
    def period_end(self):
        return self.pay_date - timedelta(days=self.pay_date.weekday() + 1)

    @property
    def period_start(self):
        return self.period_end - timedelta(days=14)

    def add_time_sheets(self):
        time_sheets = Timesheet.objects.filter(start_date_time__gte=self.period_start,
                                               start_date_time__lte=self.period_end)
        for time_sheet in time_sheets:
            if time_sheet.end_date_time.date() > self.period_end:
                pass
            else:
                self.timesheet_set.add(time_sheet)
                # todo will currently override existing time sheets with newest claim #
                # todo allow for checking existing records

# output duration per cost code (multiplier)
# 1.5 is drawn from cost code A
# 2 is drawn from cost code B
# setting public holidays out of scope
# focus is to accurately record duration spent on a task and in the accrued duration,
# calculate timesheet rows accordingly
#
# 3 hr timesheet will have, timesheet rows:
# 2 hours @ code A
#       11pm - 12am 1 hr x 1.5
#       12am - 1am 1 hr x 1.5
# 1 hour @ code B
#       1am - 2am 1 hr x 2.0

# proposal
# hard code Penalty Types so only PAID and TOIL are supported
# Add cost code table with Code, Name
# A claim will take everything within a pay period and group by date for the time sheet submission
# There will be a breakdown of duration by cost codes, this will be a base duration worked
