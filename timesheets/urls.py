from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from main.views import EmployeeDetailView, TimesheetCreateView, TimesheetDetailView, LogOffView, LogInView, \
    RegisterEmployeeView, TeamCreateView, TeamListView, TeamJoinStaffView, TeamJoinManagerView, TeamViewMembersListView, \
    TeamLeaveStaffView, TeamLeaveManagerView, ManagerTeamViewMembersListView, SettingsListView, TeamDeleteView, \
    PenaltyCreateView, PenaltyTypeCreateView, PenaltyDeleteView, PenaltyTypeDeleteView, PayPeriodView

urlpatterns = [
    path('', EmployeeDetailView.as_view(), name='home'),
    path('employee/<slug:slug>', EmployeeDetailView.as_view(), name='employee-detail'),
    path('logout', LogOffView.as_view(), name='logout'),
    path('login', LogInView.as_view(), name='login'),
    path('register', RegisterEmployeeView.as_view(), name='register-employee'),
    path('create', TimesheetCreateView.as_view(), name='timesheet-create'),
    path('timesheet-detail/<int:pk>', TimesheetDetailView.as_view(), name='timesheet-detail'),
    path('penalty-create', PenaltyCreateView.as_view(), name='penalty-create'),
    path('penalty-delete/<int:pk>', PenaltyDeleteView.as_view(), name='penalty-delete'),
    path('penalty-type-create', PenaltyTypeCreateView.as_view(), name='penalty-type-create'),
    path('penalty-type-delete/<int:pk>', PenaltyTypeDeleteView.as_view(), name='penalty-type-delete'),
    path('team-create', TeamCreateView.as_view(), name='team-create'),
    path('team-delete/<slug:slug>', TeamDeleteView.as_view(), name='team-delete'),
    path('team-list', TeamListView.as_view(), name='team-list'),
    path('team-join-staff/<int:team_id>', TeamJoinStaffView.as_view(), name='team-join-staff'),
    path('team-leave-staff/<int:team_id>', TeamLeaveStaffView.as_view(), name='team-leave-staff'),
    path('team-join-manager/<int:team_id>', TeamJoinManagerView.as_view(), name='team-join-manager'),
    path('team-leave-manager/<int:team_id>', TeamLeaveManagerView.as_view(), name='team-leave-manager'),
    path('team-detail/<int:team_id>', TeamViewMembersListView.as_view(), name='team-view-members-list'),
    path('manager-team-member-list', ManagerTeamViewMembersListView.as_view(), name='manager-team-member-list'),
    path('settings-list', SettingsListView.as_view(), name='settings-list'),
    path('update-pay-period', PayPeriodView.as_view(), name='update-pay-period'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
