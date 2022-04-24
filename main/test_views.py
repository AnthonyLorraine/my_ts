from datetime import datetime

from django.test import TestCase
from django.urls import reverse

from main.models import PenaltyType, Employee, Penalty, Team, Timesheet


class PenaltyTypeCreateViewTestCase(TestCase):
    fixtures = ['auth_group.json']

    def setUp(self) -> None:
        self.test_employee = Employee.objects.create_user(username='ant')
        self.client.force_login(user=self.test_employee)

    def test_get_require_authentication(self):
        self.client.logout()
        response = self.client.get(reverse('penalty-type-create'))
        self.assertRedirects(response, reverse('login') + '?next=/penalty-type-create')

    def test_user_authenticated(self):
        response = self.client.get(reverse('penalty-type-create'))
        self.assertEqual(response.status_code, 200)

    def test_penalty_types_context(self):
        new_penalty_type = PenaltyType.objects.create(name='Test Penalty Type')
        response = self.client.get(reverse('penalty-type-create'))
        self.assertQuerysetEqual(response.context['penalty_types'], [new_penalty_type])

    def test_success_url_redirect(self):
        response = self.client.post(reverse('penalty-type-create'), data={
            'name': 'Test Penalty Type'
        })
        self.assertRedirects(response, reverse('penalty-type-create'))

    def test_penalty_type_creation(self):
        response = self.client.post(reverse('penalty-type-create'), data={
            'name': 'Test Penalty Type'
        }, follow=True)
        context = {'penalty_types': PenaltyType.objects.all()}
        self.assertQuerysetEqual(response.context['penalty_types'], context['penalty_types'])

    def test_template_used(self):
        response = self.client.get(reverse('penalty-type-create'))
        self.assertTemplateUsed(response, 'main/penaltytype_form.html')


class PenaltyTypeDeleteViewTestCase(TestCase):
    fixtures = ['auth_group.json']

    def setUp(self) -> None:
        self.test_employee = Employee.objects.create_user(username='ant')
        self.new_penalty_type = PenaltyType.objects.create(name='Test Penalty Type')
        self.client.force_login(user=self.test_employee)

    def test_get_require_authentication(self):
        self.client.logout()
        response = self.client.get(reverse('penalty-type-delete', kwargs={'pk': self.new_penalty_type.pk}))
        self.assertRedirects(response, reverse('login') + '?next=/penalty-type-delete/1')

    def test_post_require_authentication(self):
        self.client.logout()
        response = self.client.post(reverse('penalty-type-delete', kwargs={'pk': self.new_penalty_type.pk}))
        self.assertRedirects(response, reverse('login') + '?next=/penalty-type-delete/1')

    def test_get_user_authenticated(self):
        response = self.client.get(reverse('penalty-type-delete', kwargs={'pk': self.new_penalty_type.pk}))
        self.assertEqual(response.status_code, 200)

    def test_post_user_authenticated_and_penalty_type_deletion(self):
        response = self.client.post(reverse('penalty-type-delete', kwargs={'pk': self.new_penalty_type.pk}))
        self.assertRedirects(response, reverse('penalty-type-create'))

    def test_template_used(self):
        response = self.client.get(reverse('penalty-type-delete', kwargs={'pk': self.new_penalty_type.pk}))
        self.assertTemplateUsed(response, 'main/penaltytype_confirm_delete.html')


class PenaltyCreateViewTestCase(TestCase):
    fixtures = ['auth_group.json']

    def setUp(self) -> None:
        self.test_employee = Employee.objects.create_user(username='ant')
        self.test_penalty_type = PenaltyType.objects.create(name='Test Penalty Type')
        self.client.force_login(user=self.test_employee)

    def test_get_require_authentication(self):
        self.client.logout()
        response = self.client.get(reverse('penalty-create'))
        self.assertRedirects(response, reverse('login') + '?next=/penalty-create')

    def test_get_user_authenticated(self):
        response = self.client.get(reverse('penalty-create'))
        self.assertEqual(response.status_code, 200)

    def test_penalties_context(self):
        new_penalty = Penalty.objects.create(name='Test Penalty', penalty_type=self.test_penalty_type)
        response = self.client.get(reverse('penalty-create'))
        self.assertQuerysetEqual(response.context['penalties'], [new_penalty])

    def test_success_url_redirect(self):
        response = self.client.post(reverse('penalty-create'), data={
            'name': 'Test Penalty',
            'penalty_type': 1,
            'valid_for_day_count': 14
        })
        self.assertRedirects(response, reverse('penalty-create'))

    def test_penalty_type_creation(self):
        response = self.client.post(reverse('penalty-create'), data={
            'name': 'Test Penalty',
            'penalty_type': 1,
            'valid_for_day_count': 14
        }, follow=True)
        context = {'penalties': Penalty.objects.all()}
        self.assertQuerysetEqual(response.context['penalties'], context['penalties'])

    def test_template_used(self):
        response = self.client.get(reverse('penalty-create'))
        self.assertTemplateUsed(response, 'main/penalty_form.html')


class PenaltyDeleteViewTestCase(TestCase):
    fixtures = ['auth_group.json']

    def setUp(self) -> None:
        self.test_employee = Employee.objects.create_user(username='ant')
        self.new_penalty_type = PenaltyType.objects.create(name='Test Penalty Type')
        self.new_penalty = Penalty.objects.create(name='Test Penalty', penalty_type=self.new_penalty_type)
        self.client.force_login(user=self.test_employee)

    def test_get_require_authentication(self):
        self.client.logout()
        response = self.client.get(reverse('penalty-delete', kwargs={'pk': self.new_penalty.pk}))
        self.assertRedirects(response, reverse('login') + '?next=/penalty-delete/1')

    def test_post_require_authentication(self):
        self.client.logout()
        response = self.client.get(reverse('penalty-delete', kwargs={'pk': self.new_penalty.pk}))
        self.assertRedirects(response, reverse('login') + '?next=/penalty-delete/1')

    def test_get_user_authenticated(self):
        response = self.client.get(reverse('penalty-delete', kwargs={'pk': self.new_penalty.pk}))
        self.assertEqual(response.status_code, 200)

    def test_post_user_authenticated_and_penalty_type_deletion(self):
        response = self.client.post(reverse('penalty-delete', kwargs={'pk': self.new_penalty.pk}))
        self.assertRedirects(response, reverse('penalty-create'))

    def test_template_used(self):
        response = self.client.get(reverse('penalty-delete', kwargs={'pk': self.new_penalty.pk}))
        self.assertTemplateUsed(response, 'main/penalty_confirm_delete.html')


class TestRegisterEmployeeView(TestCase):
    fixtures = ['auth_group.json']

    def setUp(self) -> None:
        self.test_employee = Employee.objects.create_user(username='ant')
        self.client.force_login(user=self.test_employee)

    def test_get_require_no_authentication(self):
        self.client.logout()
        response = self.client.get(reverse('register-employee'))
        self.assertEqual(response.status_code, 200)

    def test_post_require_no_authentication(self):
        self.client.logout()
        response = self.client.post(reverse('register-employee'), data={
            'username': 'test_user',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'test_password'
        })
        self.assertRedirects(response, reverse('home'))

    def test_get_user_authenticated(self):
        response = self.client.get(reverse('register-employee'))
        self.assertRedirects(response, reverse('home'))

    def test_get_success_url(self):
        response = self.client.post(reverse('register-employee'), data={
            'username': 'test_user',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'test_password'
        })
        self.assertRedirects(response, reverse('home'))

    def test_template_used(self):
        self.client.logout()
        response = self.client.get(reverse('register-employee'))
        self.assertTemplateUsed(response, 'main/register_form.html')


class TestEmployeeDetailView(TestCase):
    fixtures = ['auth_group.json']

    def setUp(self) -> None:
        self.test_employee = Employee.objects.create_user(username='ant',
                                                          first_name='Anthony',
                                                          last_name='Lorraine')
        self.client.force_login(user=self.test_employee)

    def test_get_require_authentication(self):
        self.client.logout()
        response = self.client.get(reverse('employee-detail', kwargs={'slug': self.test_employee.slug}))
        self.assertRedirects(response, reverse('login') + '?next=/employee/anthony-lorraine')

    def test_get_user_authenticated(self):
        response = self.client.get(reverse('employee-detail', kwargs={'slug': self.test_employee.slug}))
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        response = self.client.get(reverse('employee-detail', kwargs={'slug': self.test_employee.slug}))
        self.assertTemplateUsed(response, 'main/employee_detail.html')

    def test_get_object(self):
        response = self.client.get(reverse('employee-detail', kwargs={'slug': self.test_employee.slug}))
        self.assertEqual(response.context['object'], self.test_employee)


class TestHomeView(TestCase):
    fixtures = ['auth_group.json']

    def setUp(self) -> None:
        self.test_employee = Employee.objects.create_user(username='ant',
                                                          first_name='Anthony',
                                                          last_name='Lorraine')
        self.client.force_login(user=self.test_employee)

    def test_get_require_authentication(self):
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('login') + '?next=/')

    def test_get_user_authenticated(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'main/employee_detail.html')

    def test_get_object(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['object'], self.test_employee)


class TestEmployeeUpdateView(TestCase):
    fixtures = ['auth_group.json']

    def setUp(self) -> None:
        self.test_employee = Employee.objects.create_user(username='ant',
                                                          first_name='Anthony',
                                                          last_name='Lorraine')
        self.test_manager = Employee.objects.create_user(username='manager',
                                                         first_name='manager',
                                                         last_name='user')
        self.test_team = Team.objects.create(name='test team')
        self.test_team.add_employee(self.test_employee)
        self.test_team.add_manager(self.test_manager)
        self.test_not_manager = Employee.objects.create_user(username='not_a_manager',
                                                             first_name='not manager',
                                                             last_name='user')
        self.client.force_login(user=self.test_employee)

    def test_get_require_authentication(self):
        self.client.logout()
        response = self.client.get(reverse('employee-update', kwargs={'slug': self.test_employee.slug}))
        self.assertRedirects(response, reverse('login') + '?next=/employee-update/anthony-lorraine')

    def test_get_user_authenticated(self):
        response = self.client.get(reverse('employee-update', kwargs={'slug': self.test_employee.slug}))
        self.assertEqual(response.status_code, 200)

    def test_get_user_is_manager(self):
        self.client.logout()
        self.client.force_login(user=self.test_manager)
        response = self.client.get(reverse('employee-update', kwargs={'slug': self.test_employee.slug}))
        self.assertEqual(response.status_code, 200)

    def test_get_user_is_not_manager(self):
        self.client.logout()
        self.client.force_login(user=self.test_not_manager)
        response = self.client.get(reverse('employee-update', kwargs={'slug': self.test_employee.slug}))
        self.assertEqual(response.status_code, 403)

    def test_template_used(self):
        response = self.client.get(reverse('employee-update', kwargs={'slug': self.test_employee.slug}))
        self.assertTemplateUsed(response, 'main/employee_form.html')

    def test_get_object(self):
        response = self.client.get(reverse('employee-update', kwargs={'slug': self.test_employee.slug}))
        self.assertEqual(response.context['object'], self.test_employee)

    def test_get_success_url(self):
        response = self.client.post(reverse('employee-update', kwargs={'slug': self.test_employee.slug}),
                                    data={
                                        'username': 'test_user',
                                        'first_name': 'Test',
                                        'last_name': 'User',
                                        'password': 'test_password'
                                    })
        updated_user = Employee.objects.get(pk=self.test_employee.pk)
        self.assertRedirects(response, reverse('employee-detail', kwargs={'slug': updated_user.slug}))


class TestTimesheetCreateView(TestCase):
    fixtures = ['auth_group.json']

    def setUp(self) -> None:
        self.new_penalty_type = PenaltyType.objects.create(name='Test Penalty Type')
        self.new_penalty = Penalty.objects.create(name='Test Penalty', penalty_type=self.new_penalty_type)
        self.test_employee: Employee = Employee.objects.create_user(username='ant',
                                                                    first_name='Anthony',
                                                                    last_name='Lorraine')
        start_date_time = datetime.today()
        self.test_manager = Employee.objects.create_user(username='manager',
                                                         first_name='manager',
                                                         last_name='user')
        self.test_employee.add_timesheet(start_date_time=start_date_time,
                                         duration=60,
                                         penalty=self.new_penalty)
        self.test_not_manager = Employee.objects.create_user(username='not_a_manager',
                                                             first_name='not manager',
                                                             last_name='user')
        self.client.force_login(user=self.test_employee)

        self.test_team = Team.objects.create(name='test team')
        self.test_team.add_employee(self.test_employee)
        self.test_team.add_manager(self.test_manager)

    def test_get_success_url(self):
        start_date_time = datetime.today()
        response = self.client.post(reverse('timesheet-create'),
                                    data={
                                        'start_date_time': start_date_time,
                                        '_duration': 60,
                                        'penalty': self.new_penalty.pk

                                    })
        self.assertRedirects(response, reverse('home'))

    def test_get_require_authentication(self):
        self.client.logout()
        response = self.client.get(reverse('timesheet-create'))
        self.assertRedirects(response, reverse('login') + '?next=' + reverse('timesheet-create'))

    def test_get_user_authenticated(self):
        response = self.client.get(reverse('timesheet-create'))
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        response = self.client.get(reverse('timesheet-create'))
        self.assertTemplateUsed(response, 'main/timesheet_form.html')


class TestTimesheetDetailView(TestCase):
    fixtures = ['auth_group.json']

    def setUp(self) -> None:
        self.new_penalty_type = PenaltyType.objects.create(name='Test Penalty Type')
        self.new_penalty = Penalty.objects.create(name='Test Penalty', penalty_type=self.new_penalty_type)
        self.test_employee: Employee = Employee.objects.create_user(username='ant',
                                                                    first_name='Anthony',
                                                                    last_name='Lorraine')
        start_date_time = datetime.today()
        self.test_manager = Employee.objects.create_user(username='manager',
                                                         first_name='manager',
                                                         last_name='user')
        self.test_employee.add_timesheet(start_date_time=start_date_time,
                                         duration=60,
                                         penalty=self.new_penalty)
        self.test_not_manager = Employee.objects.create_user(username='not_a_manager',
                                                             first_name='not manager',
                                                             last_name='user')
        self.client.force_login(user=self.test_employee)

        self.test_team = Team.objects.create(name='test team')
        self.test_team.add_employee(self.test_employee)
        self.test_team.add_manager(self.test_manager)

    def test_get_require_authentication(self):
        self.client.logout()
        response = self.client.get(reverse('timesheet-detail', kwargs={'pk': 1}))
        self.assertRedirects(response, reverse('login') + '?next=/timesheet-detail/1')

    def test_get_user_authenticated(self):
        response = self.client.get(reverse('timesheet-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_template_used(self):
        response = self.client.get(reverse('timesheet-detail', kwargs={'pk': 1}))
        self.assertTemplateUsed(response, 'main/timesheet_detail.html')

    def test_get_object(self):
        response = self.client.get(reverse('timesheet-detail', kwargs={'pk': 1}))
        timesheet = Timesheet.objects.get(pk=1)
        self.assertEqual(response.context['object'], timesheet)

    def test_get_user_is_manager(self):
        self.client.logout()
        self.client.force_login(user=self.test_manager)
        response = self.client.get(reverse('timesheet-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)

    def test_get_user_is_not_manager(self):
        self.client.logout()
        self.client.force_login(user=self.test_not_manager)
        response = self.client.get(reverse('timesheet-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)
