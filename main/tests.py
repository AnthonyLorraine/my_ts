from datetime import datetime, timedelta

from django.test import TestCase

from main.models import Settings


class SettingsTestCase(TestCase):
    def setUp(self):
        self.last_period = datetime.today() - timedelta(days=20)
        Settings.objects.create(name="pay_period", value=self.last_period.strftime('%d%m%Y'))

    def test_settings_creation(self):
        Settings.objects.create(name='test_setting', value='test_value')
        test_object = Settings.objects.get(name='test_setting')
        self.assertEqual(test_object.value, 'test_value')

    def test_update_pay_period(self):
        current_pay_period = Settings().get_pay_period().date()
        Settings().update_pay_period()
        updated_pay_period = Settings().get_pay_period().date()
        self.assertNotEqual(current_pay_period, updated_pay_period)

    def test_get_pay_period(self):
        pay_period = datetime.strptime(Settings.objects.get(name='pay_period').value, '%d%m%Y')
        db_pay_period = Settings().get_pay_period()
        self.assertEqual(db_pay_period, pay_period)


class PenaltyTestCase(TestCase):
    def setUp(self):
        pass

    def test_penalty_creation(self):
        pass

    def test_is_used(self):
        pass

    def test_calculate_available_employee_time(self):
        pass
