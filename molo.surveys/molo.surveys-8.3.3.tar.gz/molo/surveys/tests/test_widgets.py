from datetime import datetime

from django.test import TestCase

from mock import patch

from molo.surveys.widgets import NaturalDateInput


class TestNaturalDateInputWidget(TestCase):
    def setUp(self):
        self.widget = NaturalDateInput()

    def test_widget_returns_value_if_falsey(self):
        data = {'name': ''}

        self.assertEqual(
            self.widget.value_from_datadict(data, None, 'name'),
            '',
        )

    def test_uses_dateparser_to_parse_dates(self):
        data = {'name': '1 January 2018'}

        self.assertEqual(
            self.widget.value_from_datadict(data, None, 'name'),
            datetime(2018, 1, 1),
        )

    def test_uses_dateparser_to_parse_datetimes(self):
        data = {'name': '1 January 2018 5pm'}

        self.assertEqual(
            self.widget.value_from_datadict(data, None, 'name'),
            datetime(2018, 1, 1, 17, 0),
        )

    @patch('molo.surveys.widgets.NaturalDateInput._parse_date')
    def test_caches_expensive_result_of_dateparser(self, parse_date_mock):
        parse_date_mock.return_value = datetime(2018, 1, 1)
        data = {'name': '1 January 2018'}

        self.widget.value_from_datadict(data, None, 'name')
        self.widget.value_from_datadict(data, None, 'name')

        self.assertEqual(parse_date_mock.call_count, 1)

    @patch('molo.surveys.widgets.NaturalDateInput._parse_date')
    def test_return_original_if_dateparser_returns_none(self, parse_date_mock):
        parse_date_mock.return_value = None
        data = {'name': "rubbish value which can't be parsed as a date"}

        self.widget.value_from_datadict(data, None, 'name')

        self.assertEqual(
            self.widget.value_from_datadict(data, None, 'name'),
            "rubbish value which can't be parsed as a date",
        )
