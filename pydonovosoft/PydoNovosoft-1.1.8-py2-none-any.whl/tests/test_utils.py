from unittest import TestCase
import PydoNovosoft


class TestUtils(TestCase):

    def test_dateutc(self):
        utc = 1546570779
        ret = PydoNovosoft.Utils.utc_to_datetime(utc)
        self.assertTrue(ret.day == 4)

    def test_timezone(self):
        utc = PydoNovosoft.Utils.utc_to_datetime(1546570779)
        ret = PydoNovosoft.Utils.datetime_zone(utc, "America/Mexico_City")
        self.assertTrue(ret.hour == 20 and ret.minute == 59)

    def test_format(self):
        utc = PydoNovosoft.Utils.utc_to_datetime(1546570779)
        ret = PydoNovosoft.Utils.datetime_zone(utc, "America/Mexico_City")
        form = PydoNovosoft.Utils.format_date(ret, "%Y-%m-%d %H:%M:%S")
        self.assertEquals(form, "2019-01-03 20:59:39")

    def test_strpdate(self):
        date = PydoNovosoft.Utils.string_to_date("2019-01-04 03:25:12", "%Y-%m-%d %H:%M:%S")
        tz = PydoNovosoft.Utils.datetime_zone(date, "America/Mexico_City")
        self.assertTrue(tz.day == 3 and tz.hour == 21 and tz.minute == 25)

