import logging
import sys
import unittest

from geoalchemy2.shape import from_shape
from shapely.geometry.point import Point

from peek.core.orm.Display import DispLevel
from peek.core.queue_processesors.GridKeyUtil import makeGridKeys

logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s:%(message)s'
                    , datefmt='%d-%b-%Y %H:%M:%S'
                    , level=logging.DEBUG
                    , stream=sys.stdout)

logger = logging.getLogger(__name__)


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.geom = from_shape(Point((0, 0)))

    def test_keys(self):
        def make(min, max):
            gridKeys = makeGridKeys(self.geom,
                                    DispLevel(minZoom=min, maxZoom=max))
            return sorted(gridKeys)

        # Test Level 0 only
        self.assertEqual(make(min=0.0, max=0.0), [])

        # Test Level 0 only
        self.assertEqual(make(min=0.0, max=0.04), ['0.0x0'])

        # Test Level 0 only
        self.assertEqual(make(min=0.0, max=0.1), ['0.0x0', '1.0x0'])

        # TEST Z 0, 1
        self.assertEqual(make(min=0.0, max=0.3), ['0.0x0', '1.0x0', '2.0x0'])

        # TEST Z 0, 1
        self.assertEqual(make(min=0.1, max=0.4), ['1.0x0', '2.0x0'])

        # TEST Z 0, 1
        self.assertEqual(make(min=0.1, max=0.5), ['1.0x0', '2.0x0'])

        # TEST Z 1 only
        self.assertEqual(make(min=0.1001, max=0.5), ['2.0x0'])

        # TEST Z 1 only
        self.assertEqual(make(min=0.23, max=0.499), ['2.0x0'])

        # TEST Z 0, 1, 2
        self.assertEqual(make(min=0.1, max=0.5001), ['1.0x0', '2.0x0', '3.0x0'])

        # TEST Z 0, 1, 2
        self.assertEqual(make(min=0.0, max=9999), ['0.0x0', '1.0x0', '2.0x0', '3.0x0'])

        # TEST Z 0, 1, 2
        self.assertEqual(make(min=0.0, max=0.7), ['0.0x0', '1.0x0', '2.0x0', '3.0x0'])

        # TEST Z 1, 2
        self.assertEqual(make(min=0.25, max=0.7), ['2.0x0', '3.0x0'])

        # TEST Z 1, 2
        self.assertEqual(make(min=0.25, max=0.7), ['2.0x0', '3.0x0'])

        # TEST Z 2
        self.assertEqual(make(min=0.5, max=0.7), ['2.0x0', '3.0x0'])

        # TEST Z 2
        self.assertEqual(make(min=0.5001, max=0.7), ['3.0x0'])

        # TEST Z 2
        self.assertEqual(make(min=0.5001, max=0.7), ['3.0x0'])
