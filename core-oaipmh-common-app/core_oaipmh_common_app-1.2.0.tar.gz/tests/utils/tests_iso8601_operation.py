"""
    Iso8601 operation test class
"""

from unittest import TestCase
from core_oaipmh_common_app.utils import UTCdatetime
import datetime


class TestDatetimeToUTCDatetimeIso8601(TestCase):
    def test_valid_conversion(self):
        # Arrange
        date_to_convert = datetime.datetime(2016, 11, 18, 8, 30)

        # Act
        result = UTCdatetime.datetime_to_utc_datetime_iso8601(date_to_convert)

        # Assert
        self.assertEquals(result, "2016-11-18T08:30:00Z")


class TestUTCDatetimeIso8601ToDatetime(TestCase):
    def test_valid_conversion(self):
        # Arrange
        date_to_convert = "2016-11-18T08:30:00Z"

        # Act
        result = UTCdatetime.utc_datetime_iso8601_to_datetime(date_to_convert)

        # Assert
        self.assertEquals(result, datetime.datetime(2016, 11, 18, 8, 30))

    def test_invalid_conversion(self):
        # Arrange
        date_to_convert = "20166-11-18T08:30:00Z"

        # Act # Assert
        with self.assertRaises(Exception):
            UTCdatetime.utc_datetime_iso8601_to_datetime(date_to_convert)

