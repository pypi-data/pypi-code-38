import logging
import sys
import unittest

from lbmessaging import EMERGENCY, NORMAL, LOW, priority, _map


class TestPriorityLevels(unittest.TestCase):

    def test_emergency(self):
        self.assertEqual(_map[EMERGENCY], priority(EMERGENCY, 1))
        self.assertEqual(_map[EMERGENCY], priority(EMERGENCY, 0))

    def test_low(self):
        self.assertEqual(_map[LOW], priority(LOW, 0))
        self.assertEqual(_map[NORMAL] -1, priority(LOW, 1))


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger().setLevel(logging.WARNING)
    unittest.main()
