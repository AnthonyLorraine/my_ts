from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from django.views.generic import DetailView, CreateView, ListView, RedirectView, DeleteView, UpdateView

from main.forms import TimeSheetModelForm, PenaltyCreateModelForm, PenaltyTypeCreateModelForm, \
    EmployeeUpdateModelForm, ClaimForm, LogInModelForm, RegisterModelForm, TeamCreateModelForm
from main.models import Employee, Timesheet, Team, PenaltyType, Settings, Penalty, Claim


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee

    def get_object(self, *args, **kwargs):
        try:
            user_obj = super().get_object()
            return user_obj
        except AttributeError:
            return self.request.user

    def get_context_data(self, *, object_list=None, **kwargs):
        messages.info(self.request, 'TEST')
        context = super().get_context_data()
        context['pay_period_start'] = Settings.get_pay_period()
        context['pay_period_end'] = context['pay_period_start'] + timedelta(days=14)
        return context


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeUpdateModelForm
    template_name = 'main/employee_form.html'

    def get_success_url(self):
        return reverse('employee-detail', kwargs={'slug': self.object.slug})


class TimesheetCreateView(LoginRequiredMixin, CreateView):
    model = Timesheet
    form_class = TimeSheetModelForm

    def get_initial(self):
        return {'employee': self.request.user}

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        self.object: Timesheet = form.save(commit=False)
        self.object.employee = self.request.user

        seconds = self.object.duration.total_seconds()
        self.object._duration = round(seconds * 60)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class TimesheetDetailView(LoginRequiredMixin, DetailView):
    model = Timesheet


class ClaimCreateView(LoginRequiredMixin, CreateView):
    model = Claim
    form_class = ClaimForm
    template_name = 'main/claim_form.html'

    def get_initial(self):
        initial = super().get_initial()
        initial['employee'] = self.request.user
        return initial

    def get_success_url(self):
        return reverse('home')

    def form_valid(self, form):
        self.object: Claim = form.save(commit=False)
        self.object.employee = self.request.user

        minutes = self.object.claimed_seconds
        self.object.claimed_seconds = round(minutes * 60)
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class PenaltyCreateView(LoginRequiredMixin, CreateView):
    model = Penalty
    form_class = PenaltyCreateModelForm

    def get_success_url(self):
        return reverse('penalty-create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['penalties'] = Penalty.objects.all()
        return context


class PenaltyDeleteView(LoginRequiredMixin, DeleteView):
    model = Penalty

    def get_success_url(self):
        return reverse('penalty-create')


class PenaltyTypeCreateView(LoginRequiredMixin, CreateView):
    model = PenaltyType
    form_class = PenaltyTypeCreateModelForm

    def get_success_url(self):
        return reverse('penalty-type-create')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['penalty_types'] = PenaltyType.objects.all()
        return context


class PenaltyTypeDeleteView(LoginRequiredMixin, DeleteView):
    model = PenaltyType

    def get_success_url(self):
        return reverse('penalty-type-create')


class LogOffView(LoginRequiredMixin, LogoutView):
    pass


class LogInView(LoginView):
    template_name = 'main/login_form.html'
    authentication_form = LogInModelForm


class RegisterEmployeeView(CreateView):
    model = Employee
    template_name = 'main/register_form.html'
    form_class = RegisterModelForm

    def get_success_url(self):
        return reverse('home')

    def get_form_kwargs(self):
        form_kwargs = super(RegisterEmployeeView, self).get_form_kwargs()
        try:
            data = form_kwargs['data'].copy()
            data['date_joined'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            form_kwargs['data'] = data
        except KeyError:
            pass
        return form_kwargs

    def form_valid(self, form):
        form_valid = super().form_valid(form)
        self.object.is_active = True
        self.object.set_password(form.instance.password)
        self.object.save()
        login(self.request, self.object)
        return form_valid


class TeamCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Team
    form_class = TeamCreateModelForm

    def test_func(self):
        return self.request.user.groups.filter(name='Manager').exists() or self.request.user.is_superuser

    def get_success_url(self):
        return reverse('team-list')


class TeamDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Team

    def test_func(self):
        return self.request.user.groups.filter(name='Manager').exists()

    def get_success_url(self):
        return reverse('team-list')

    def get_object(self, queryset=None):
        team_obj = super().get_object()
        if not team_obj.staff_count == 0:
            raise Http404()
        return team_obj


class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    paginate_by = 5
    ordering = ['name']


class TeamJoinStaffView(LoginRequiredMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        team = Team.objects.get(id=kwargs['team_id'])
        try:
            team.add_employee(self.request.user)
        except ValidationError:
            messages.error(self.request, f'You\'re already in a team, please leave your team first.')
        team.save()
        return redirect('team-list')


class TeamLeaveStaffView(LoginRequiredMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        team = Team.objects.get(id=kwargs['team_id'])
        team.remove_employee(self.request.user)
        return redirect(self.request.META['HTTP_REFERER'])


class TeamJoinManagerView(LoginRequiredMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        team = Team.objects.get(id=kwargs['team_id'])
        team.add_manager(self.request.user)
        team.save()
        return redirect('team-list')


class TeamLeaveManagerView(LoginRequiredMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        team = Team.objects.get(id=kwargs['team_id'])
        team.remove_manager(self.request.user)
        team.save()
        return redirect('team-list')


class TeamViewMembersListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'main/team_members_list.html'

    def get_queryset(self):
        return Employee.objects.filter(team__id=self.kwargs.get('team_id'))

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['team'] = Team.objects.get(pk=self.kwargs.get('team_id'))
        context['penalty_types'] = PenaltyType.objects.all()
        return context


class ManagerTeamViewMembersListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'main/manager_team_members_list.html'

    def get_queryset(self):
        return Employee.objects.filter(team=self.request.user.team)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['team'] = self.request.user.team
        return context


class SettingsListView(LoginRequiredMixin, ListView):
    model = Settings


class PayPeriodView(LoginRequiredMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        Settings.update_pay_period()
        return redirect('settings-list')
