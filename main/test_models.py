from unittest import TestCase


class TestPenaltyType(TestCase):
    def test_is_used(self):
        self.fail()

    def test_calculate_available_employee_time(self):
        self.fail()


class TestPenalty(TestCase):
    pass


class TestEmployee(TestCase):
    def test_add_timesheet(self):
        self.fail()

    def test_add_claim(self):
        self.fail()

    def test_last_5_time_sheets(self):
        self.fail()

    def test_last_5_claims(self):
        self.fail()

    def test_total_time_sheets_submitted(self):
        self.fail()

    def test_total_claims_submitted(self):
        self.fail()

    def test_duration_per_penalty(self):
        self.fail()

    def test_is_manager(self):
        self.fail()


class TestTeam(TestCase):
    def test_add_employee(self):
        self.fail()

    def test_add_manager(self):
        self.fail()

    def test_remove_employee(self):
        self.fail()

    def test_remove_manager(self):
        self.fail()

    def test_staff_count(self):
        self.fail()

    def test_duration_per_penalty(self):
        self.fail()


class TestTimesheet(TestCase):
    def test_save(self):
        self.fail()

    def test_create_time_sheet_row(self):
        self.fail()

    def test_public_holiday(self):
        self.fail()

    def test__calculate_payout_amount_in_seconds(self):
        self.fail()

    def test_expired(self):
        self.fail()

    def test_rows(self):
        self.fail()

    def test_duration(self):
        self.fail()

    def test_claimable_duration(self):
        self.fail()

    def test_accrued_duration(self):
        self.fail()

    def test_end_date_time(self):
        self.fail()


class TestTimesheetRow(TestCase):
    def test_duration(self):
        self.fail()

    def test_accrued_duration(self):
        self.fail()


class TestClaim(TestCase):
    def test_save(self):
        self.fail()

    def test_employee_can_claim_penalty_type(self):
        self.fail()

    def test_duration(self):
        self.fail()
