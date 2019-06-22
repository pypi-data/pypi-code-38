# coding=utf-8

import unittest
import stime

class TestSimulatedTime(unittest.TestCase):

    def test_reset_defaults_to_zero(self):
        stime.reset()
        self.assertEqual(stime.time(), 0.0, "expected time to be 0.0 after being reset")

    def test_reset_to_arbitrary_value(self):
        stime.reset(4.7)
        self.assertEqual(stime.time(), 4.7, "expected time to be 4.7 after being reset to that value")

    def test_tick_defaults_to_one_second(self):
        stime.reset()
        stime.tick()
        self.assertEqual(stime.time(), 1.0, "expected time to be 1.0 after one tick")

    def test_tick_with_arbitrary_increment(self):
        stime.reset()
        stime.tick(6.3)
        self.assertEqual(stime.time(), 6.3, "expected time to be 6.3 after ticking with 6.3 increment")

    def test_tick_with_arbitrary_increment(self):
        stime.reset()
        stime.tick(5.9)
        stime.tick(6.1)
        self.assertEqual(stime.time(), 12.0, "expected time to be sum of increments after multiple ticks")

    def test_monotonic_is_alias_of_time(self):
        stime.reset(0.1)
        stime.tick()
        stime.tick(4)
        self.assertEqual(stime.monotonic(), stime.time(), "expected monotonic() to be an alias of time()")

    def test_current_time_is_not_globally_exported(self):
        def attempt_access_to_current_time(self):
            _current_time
        self.assertRaises(NameError, attempt_access_to_current_time, "expected _current_time not to pollute the namespace")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSimulatedTime)
    unittest.TextTestRunner(verbosity=2).run(suite)
