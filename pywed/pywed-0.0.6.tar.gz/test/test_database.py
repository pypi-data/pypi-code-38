import unittest
import math
import datetime
import shutil
import logging
logging.basicConfig(level=logging.INFO)

import wed

import functools

@functools.lru_cache(maxsize=10)
def test(i: int):
    print("in test")
    return 0

class HighLevelTest(unittest.TestCase):
    def test_basic(self):
        coord = wed.Coordinate(0, 0)

        wed.Settings().latitude_precision = 0.5
        wed.Settings().longitude_precision = 0.5
        wed.Settings().time_precision = datetime.timedelta(hours=6)
        for i in range(1000):
            # vary the time and coordinate according to i so that we can check the caching behavior
            t = datetime.datetime(2017, 5, 12, math.floor(i/60), i % 60)
            coord = wed.Coordinate(i/100, i/100)
            wed.read(wed.DataType.WIND, t, coord)

    def test_wind_speed(self):
        t = datetime.datetime(2017, 6, 21)
        coord = wed.Coordinate(48, 8)
        wind = wed.read(wed.DataType.WIND, t, coord)
        print(wind)
        print(math.sqrt(wind['u10'] ** 2 + wind['v10'] ** 2) * 1.94384)

class DatabaseTest(unittest.TestCase):
    def test_basic(self):
        db = wed.Database(
            [wed.DataType.WIND],
            datetime.datetime(2017, 5, 12, 20, 4)
            # cache_duration=datetime.timedelta(days=5)
        )
        coord = wed.Coordinate(48, 8)
        print(db.read(wed.DataType.WIND, datetime.datetime(2017, 5, 12, 20, 4), coord))
        print(db.read(wed.DataType.WIND, datetime.datetime(2017, 5, 15, 20, 4), coord))
    # def test_basic(self):
    #     t = datetime.datetime(2017, 5, 12, 20, 4)
    #     print(wed.read(wed.DataType.WIND, t, wed.Coordinate(0, 0)))
    #     print(wed.read(wed.DataType.WIND, t, wed.Coordinate(12, 150)))
    #
    # def test_negative(self):
    #     c1 = wed.round_coordinate(wed.Coordinate(0, -90), wed.DataType.WIND)
    #     c2 = wed.round_coordinate(wed.Coordinate(0, 270), wed.DataType.WIND)
    #     self.assertEqual(c1.latitude, c2.latitude)
    #     self.assertEqual(c1.longitude, c2.longitude)
    #
    # def test_range(self):
    #     t = datetime.datetime(2019, 5, 12, 20, 4)
    #     range = wed.get_time_range(wed.DataType.WIND)
    #     def is_in_range(time: datetime.datetime) -> bool:
    #         return range['min'] <= time <= range['max']
    #     self.assertFalse(is_in_range(datetime.datetime(2019, 5, 12, 20, 4)))
    #     self.assertTrue(is_in_range(datetime.datetime(2017, 5, 12, 20, 4)))
    #
    # def test_basic_wave(self):
    #     t = datetime.datetime(2017, 5, 12, 20, 4)
    #     print(wed.read(wed.DataType.WAVE, t, wed.Coordinate(0, 0)))
    #     print(wed.read(wed.DataType.WAVE, t, wed.Coordinate(12, 150)))
