import unittest
import datetime
import shutil
import logging
logging.basicConfig(level=logging.INFO)

import wed


class DatabaseTest(unittest.TestCase):
    def test_basic(self):
        db = wed.Database()
        # db.local_cache_path = "test_cache"

        dataset = db.open_dataset(wed.DataType.WIND)
        t = datetime.datetime(2017, 5, 12, 20, 4)
        print(dataset.read(t, wed.Coordinate(0, 0)))
        print(dataset.read(t, wed.Coordinate(12, 150)))

        # shutil.rmtree(db.local_cache_path)

    def test_negative(self):
        db = wed.Database()
        dataset = db.open_dataset(wed.DataType.WIND)
        t = datetime.datetime(2017, 5, 12, 20, 4)

        # make sure that values at -90 is the same as 270
        v1 = dataset.read(t, wed.Coordinate(0, -90))
        v2 = dataset.read(t, wed.Coordinate(0, 270))
        self.assertEqual(v1, v2)

    def test_range(self):
        db = wed.Database()
        dataset = db.open_dataset(wed.DataType.WIND)
        t = datetime.datetime(2019, 5, 12, 20, 4)
        with self.assertRaises(Exception):
            dataset.read(t, wed.Coordinate(0, -90))

    def test_basic_wave(self):
        db = wed.Database()
        # db.local_cache_path = "test_cache"

        dataset = db.open_dataset(wed.DataType.WAVE)
        t = datetime.datetime(2017, 5, 12, 20, 4)
        print(dataset.read(t, wed.Coordinate(0, 0)))
        print(dataset.read(t, wed.Coordinate(12, 150)))
