# standard libraries
import logging
import math
import unittest

# third party libraries
# None

# local libraries
from nion.utils import Geometry


class TestGeometryClass(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_fit_to_size(self):
        eps = 0.0001
        rects = []
        sizes = []
        rects.append( ((0, 0), (300, 700)) )
        sizes.append( (600, 1200) )
        rects.append( ((0, 0), (300, 700)) )
        sizes.append( (1200, 600) )
        rects.append( ((0, 0), (600, 800)) )
        sizes.append( (700, 1300) )
        rects.append( ((0, 0), (600, 800)) )
        sizes.append( (1300, 700) )
        for rect, size in zip(rects, sizes):
            fit = Geometry.fit_to_size(rect, size)
            self.assertTrue(abs(float(fit[1][1])/float(fit[1][0]) - float(size[1])/float(size[0])) < eps)

    def test_int_point_ne(self):
        p1 = Geometry.IntPoint(x=0, y=1)
        p2 = Geometry.IntPoint(x=0, y=2)
        self.assertNotEqual(p1, p2)

    def test_rect_intersects(self):
        r1 = Geometry.IntRect.from_tlbr(10,10,20,30)
        r2 = Geometry.IntRect.from_tlbr(0, 15, 30, 25)
        self.assertTrue(r1.intersects_rect(r2))

    def test_ticker_produces_unique_labels(self):
        pairs = ((1, 4), (.1, .4), (1E12, 1.000062E12), (1E-18, 1.000062E-18), (-4, -1), (-10000.001, -10000.02),
                 (1E8 - 0.002, 1E8 + 0.002), (0, 1E8 + 0.002))
        for l, h in pairs:
            ticker = Geometry.Ticker(l, h)
            self.assertEqual(len(set(ticker.labels)), len(ticker.labels))
            # print(ticker.labels)

    def test_ticker_handles_edge_cases(self):
        self.assertEqual(Geometry.Ticker(0, 0).labels, ['0'])
        self.assertEqual(Geometry.Ticker(1, 1).labels, ['1'])
        self.assertEqual(Geometry.Ticker(-1, -1).labels, ['-1'])
        self.assertEqual(Geometry.Ticker(-math.inf, math.inf).labels, ['0'])
        self.assertEqual(Geometry.Ticker(-math.nan, math.nan).labels, ['0'])
        self.assertEqual(Geometry.Ticker(math.nan, 1).labels, ['0'])
        self.assertEqual(Geometry.Ticker(-math.inf, 1).labels, ['0'])
        self.assertEqual(Geometry.Ticker(0, math.inf).labels, ['0'])

    def test_ticker_value_label(self):
        mn, mx = 18000000, 21000000
        ticker = Geometry.Ticker(mn, mx)
        self.assertIsNotNone(ticker.value_label(900000))

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
