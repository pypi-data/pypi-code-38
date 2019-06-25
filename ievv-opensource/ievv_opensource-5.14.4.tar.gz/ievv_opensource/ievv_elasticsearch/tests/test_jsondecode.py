from django.test import TestCase
from django_cradmin.datetimeutils import default_timezone_datetime

from ievv_opensource.ievv_elasticsearch import jsondecode


class JsonDecode(TestCase):
    def test_datetime(self):
        self.assertEquals(
            jsondecode.datetime(default_timezone_datetime(2015, 1, 1).isoformat()),
            default_timezone_datetime(2015, 1, 1))
