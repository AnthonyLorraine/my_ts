from unittest import TestCase

from django.test import TestCase
from django.urls import reverse

from main.models import PenaltyType, Employee, Penalty


class PenaltyTypeCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.test_employee = Employee.objects.create_user(username='ant')

    def test_require_authentication(self):
        response = self.client.get(reverse('penalty-type-create'))
        self.assertEqual(response.status_code, 302)

    def test_penalty_creation(self):
        new_penalty_type = PenaltyType.objects.create(name='Test Penalty Type')
        self.client.force_login(user=self.test_employee)
        response = self.client.get(reverse('penalty-type-create'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['penalty_types'], [new_penalty_type])


class PenaltyTypeDeleteViewTestCase(TestCase):
    def setUp(self) -> None:
        self.test_employee = Employee.objects.create_user(username='ant')

    def test_get_require_authentication(self):
        new_penalty_type = PenaltyType.objects.create(name='Test Penalty Type')
        response = self.client.get(reverse('penalty-type-delete', kwargs={'pk': new_penalty_type.pk}))
        self.assertEqual(response.status_code, 302)

    def test_post_require_authentication(self):
        new_penalty_type = PenaltyType.objects.create(name='Test Penalty Type')
        response = self.client.post(reverse('penalty-type-delete', kwargs={'pk': new_penalty_type.pk}))
        self.assertEqual(response.status_code, 302)

    def test_get_request(self):
        new_penalty_type = PenaltyType.objects.create(name='Test Penalty Type')
        self.client.force_login(user=self.test_employee)
        response = self.client.get(reverse('penalty-type-delete', kwargs={'pk': new_penalty_type.pk}), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_post_request(self):
        new_penalty_type = PenaltyType.objects.create(name='Test Penalty Type')
        self.client.force_login(user=self.test_employee)
        post_response = self.client.post(reverse('penalty-type-delete', kwargs={'pk': new_penalty_type.pk}),
                                         follow=True)
        self.assertRedirects(post_response, reverse('penalty-type-create'), status_code=302)


class PenaltyCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.test_employee = Employee.objects.create_user(username='ant')
        self.test_penalty_type = PenaltyType.objects.create(name='Test Penalty Type')

    def test_require_authentication(self):
        response = self.client.get(reverse('penalty-create'))
        self.assertEqual(response.status_code, 302)

    def test_penalty_creation(self):
        new_penalty = Penalty.objects.create(name='Test Penalty', penalty_type=self.test_penalty_type)
        self.client.force_login(user=self.test_employee)
        response = self.client.get(reverse('penalty-create'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['penalties'], [new_penalty])


class PenaltyDeleteViewTestCase(TestCase):
    def setUp(self) -> None:
        self.test_employee = Employee.objects.create_user(username='ant')
        self.test_penalty_type = PenaltyType.objects.create(name='Test Penalty Type')

    def test_get_require_authentication(self):
        new_penalty = Penalty.objects.create(name='Test Penalty', penalty_type=self.test_penalty_type)
        response = self.client.get(reverse('penalty-delete', kwargs={'pk': new_penalty.pk}))
        self.assertEqual(response.status_code, 302)

    def test_post_require_authentication(self):
        new_penalty = Penalty.objects.create(name='Test Penalty', penalty_type=self.test_penalty_type)
        response = self.client.post(reverse('penalty-delete', kwargs={'pk': new_penalty.pk}))
        self.assertEqual(response.status_code, 302)

    def test_get_request(self):
        new_penalty = Penalty.objects.create(name='Test Penalty', penalty_type=self.test_penalty_type)
        self.client.force_login(user=self.test_employee)
        response = self.client.get(reverse('penalty-delete', kwargs={'pk': new_penalty.pk}), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_post_request(self):
        new_penalty = Penalty.objects.create(name='Test Penalty', penalty_type=self.test_penalty_type)
        self.client.force_login(user=self.test_employee)
        post_response = self.client.post(reverse('penalty-delete', kwargs={'pk': new_penalty.pk}), follow=True)
        self.assertRedirects(post_response, reverse('penalty-create'), status_code=302)


class TestRegisterEmployeeView(TestCase):
    def test_get_success_url(self):
        self.fail()

    def test_get_form_kwargs(self):
        self.fail()

    def test_form_valid(self):
        self.fail()


class TestEmployeeDetailView(TestCase):
    def test_get_object(self):
        self.fail()


class TestEmployeeUpdateView(TestCase):
    def test_get_success_url(self):
        self.fail()


class TestTimesheetCreateView(TestCase):
    def test_get_initial(self):
        self.fail()

    def test_get_success_url(self):
        self.fail()

    def test_form_valid(self):
        self.fail()


class TestTimesheetDetailView(TestCase):
    pass


class TestClaimCreateView(TestCase):
    def test_get_initial(self):
        self.fail()

    def test_get_success_url(self):
        self.fail()

    def test_form_valid(self):
        self.fail()


class TestLogOffView(TestCase):
    pass


class TestLogInView(TestCase):
    pass


class TestTeamCreateView(TestCase):
    def test_test_func(self):
        self.fail()

    def test_get_success_url(self):
        self.fail()


class TestTeamDeleteView(TestCase):
    def test_test_func(self):
        self.fail()

    def test_get_success_url(self):
        self.fail()

    def test_get_object(self):
        self.fail()


class TestTeamListView(TestCase):
    pass


class TestTeamJoinStaffView(TestCase):
    def test_get(self):
        self.fail()


class TestTeamLeaveStaffView(TestCase):
    def test_get(self):
        self.fail()


class TestTeamJoinManagerView(TestCase):
    def test_get(self):
        self.fail()


class TestTeamLeaveManagerView(TestCase):
    def test_get(self):
        self.fail()


class TestTeamViewMembersListView(TestCase):
    def test_get_queryset(self):
        self.fail()

    def test_get_context_data(self):
        self.fail()


class TestManagerTeamViewMembersListView(TestCase):
    def test_get_queryset(self):
        self.fail()

    def test_get_context_data(self):
        self.fail()
