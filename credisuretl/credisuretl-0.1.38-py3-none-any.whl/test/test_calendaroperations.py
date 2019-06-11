import unittest

from unittest.mock import patch

from datetime import datetime
from dateintelligence import CalendarOperations

class CalendarOperationsTestCase(unittest.TestCase):
    def setUp(self):
        self.out = CalendarOperations()
        self.base_date = datetime(2018, 5, 5)

    def test_default_widget_size(self):
        pass

    def test_valid_add_months(self):
        actual_result = self.out.add_months(self.base_date, 3)
        expected_result = datetime(2018, 8, 5)
        self.assertEqual(actual_result,expected_result)

    def test_valid_add_months_to_next_year(self):
        actual_result = self.out.add_months(self.base_date, 8)
        expected_result = datetime(2019, 1, 5)
        self.assertEqual(actual_result,expected_result)

    def test_valid_add_months_zero_months(self):
        actual_result = self.out.add_months(self.base_date, 0)
        expected_result = datetime(2018, 5, 5)
        self.assertEqual(actual_result,expected_result)

    def test_valid_add_months_negative_months(self):
        actual_result = self.out.add_months(self.base_date, -1)
        expected_result = datetime(2018, 4, 5)
        self.assertEqual(actual_result,expected_result)

    def test_add_months_not_a_date(self):
        self.assertRaises(ValueError, self.out.add_months, "not a date", 1)

    def test_add_months_not_an_int(self):
        self.assertRaises(ValueError, self.out.add_months, self.base_date, "not an int")

    '''
    @patch('dateintelligence.calendaroperations.datetime')
    def test_last_day_of_month(self, mock_dt):
        mock_dt.now.return_value = self.base_date

        actual_result = self.out.last_day_of_month()
        expected_result = datetime(2018,5,31)
        self.assertEqual(actual_result,expected_result)
    '''