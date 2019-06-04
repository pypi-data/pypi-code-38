from ...utils import working_days
import unittest
import os
from pathlib import Path

base_path = Path(__file__).parent
holidays_file = (base_path / '../../includes/holidays.csv').resolve()


class Test(unittest.TestCase):
    def test_add_5_working_days(self):
        future = working_days.check_working_days_in_future(5)
        self.assertEqual('2019-06-06', str(future))

    def test_add_10_working_days(self):
        future = working_days.check_working_days_in_future(10)
        self.assertEqual('2019-06-13', str(future))

    def test_add_working_days_overlapping_bank_holiday(self):
        # Next holiday is 2019-08-26.
        future = working_days.check_working_days_in_future(62)
        self.assertEqual('2019-08-27', future)

    def test_add_working_days_starting_on_weekend_starts_from_next_w_day(self):
        future = working_days.check_working_days_in_future(1)
        self.assertEqual('2019-06-03', future)


    def test_read_bank_holidays_file(self):
        x = working_days.read_bank_holiday_file_and_check_if_update_needed()
        self.assertIn('2019-04-19', x)

    def test_create_bank_holidays_file_if_not_exist(self):
        os.remove(holidays_file)
        x = working_days.read_bank_holiday_file_and_check_if_update_needed()
        self.assertIn('2019-04-19', x)