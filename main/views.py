from datetime import datetime, timedelta

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse

from django.views.generic import DetailView, CreateView, ListView, RedirectView, DeleteView, UpdateView

from main.forms import TimeSheetModelForm
from main.models import Employee, Timesheet, Team, PenaltyType, Settings


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee

    def get_object(self, *args, **kwargs):
        try:
            user_obj = super().get_object()
            return user_obj
        except AttributeError:
            return self.request.user

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['pay_period_start'] = Settings.get_pay_period()
        context['pay_period_end'] = context['pay_period_start'] + timedelta(days=14)
        return context


class TimesheetCreateView(LoginRequiredMixin, CreateView):
    model = Timesheet
    form_class = TimeSheetModelForm

    def get_initial(self):
        return {'employee': self.request.user}

    def get_success_url(self):
        return reverse('home')

    def get_form_kwargs(self):
        form_kwargs = super(TimesheetCreateView, self).get_form_kwargs()
        try:
            data = form_kwargs['data'].copy()
            data['duration'] = str(int(form_kwargs['data']['duration']) * 60)
            data['employee'] = str(self.request.user.pk)
            form_kwargs['data'] = data
        except KeyError:
            pass
        return form_kwargs


class TimesheetDetailView(LoginRequiredMixin, DetailView):
    model = Timesheet


class LogOffView(LoginRequiredMixin, LogoutView):
    pass


class LogInView(LoginView):
    template_name = 'main/login_form.html'


class RegisterEmployeeView(LoginRequiredMixin, CreateView):
    model = Employee
    template_name = 'main/register_form.html'
    fields = '__all__'

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
    fields = ['name']

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
        team.add_staff(self.request.user)
        team.save()
        return redirect('team-list')


class TeamLeaveStaffView(LoginRequiredMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        team = Team.objects.get(id=kwargs['team_id'])
        team.remove_staff(self.request.user)
        team.save()
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

