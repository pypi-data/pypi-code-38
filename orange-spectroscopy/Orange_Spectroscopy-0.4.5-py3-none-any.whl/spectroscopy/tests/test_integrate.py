import unittest

import Orange
import numpy as np

from orangecontrib.spectroscopy.preprocess import Integrate


class TestIntegrate(unittest.TestCase):

    def test_simple(self):
        data = Orange.data.Table([[1, 2, 3, 1, 1, 1], [1, 2, 3, 1, np.nan, 1],
                                  [1, 2, 3, 1, 1, np.nan]])
        i = Integrate(methods=Integrate.Simple, limits=[[0, 5]])(data)
        self.assertEqual(i[0][0], 8)
        self.assertEqual(i[1][0], 8)
        self.assertEqual(i[2][0], 8)
        np.testing.assert_equal(i.domain[0].compute_value.baseline(data)[1], 0)

    def test_baseline(self):
        data = Orange.data.Table([[1, 2, 3, 1, 1, 1], [1, 2, 3, 1, np.nan, 1],
                                  [1, 2, 3, 1, 1, np.nan]])
        i = Integrate(methods=Integrate.Baseline, limits=[[0, 5]])(data)
        self.assertEqual(i[0][0], 3)
        self.assertEqual(i[1][0], 3)
        self.assertEqual(i[2][0], 3)
        np.testing.assert_equal(i.domain[0].compute_value.baseline(data)[1], 1)

    def test_peakmax(self):
        d1 = Orange.data.Table([[1, 2, 3, 1, 1, 1]])
        d2 = Orange.data.Table([[1, 2, 3, np.nan, 1, 1]])
        for data in d1, d2:
            i = Integrate(methods=Integrate.PeakMax, limits=[[0, 5]])(data)
            self.assertEqual(i[0][0], 3)
            np.testing.assert_equal(i.domain[0].compute_value.baseline(data)[1], 0)

    def test_peakbaseline(self):
        data = Orange.data.Table([[1, 2, 3, 1, 1, 1]])
        i = Integrate(methods=Integrate.PeakBaseline, limits=[[0, 5]])(data)
        self.assertEqual(i[0][0], 2)
        np.testing.assert_equal(i.domain[0].compute_value.baseline(data)[1],
                                [[1, 1, 1, 1, 1, 1]])

    def test_peakat(self):
        data = Orange.data.Table([[1, 2, 3, 1, 1, 1]])
        i = Integrate(methods=Integrate.PeakAt, limits=[[0, 5]])(data)
        self.assertEqual(i[0][0], 1)
        np.testing.assert_equal(i.domain[0].compute_value.baseline(data)[1],
                                0)
        i = Integrate(methods=Integrate.PeakAt, limits=[[1.4, None]])(data)
        self.assertEqual(i[0][0], 2)
        i = Integrate(methods=Integrate.PeakAt, limits=[[1.6, None]])(data)
        self.assertEqual(i[0][0], 3)

    def test_peakx(self):
        d1 = Orange.data.Table([[1, 2, 3, 1, 1, 1]])
        d2 = Orange.data.Table([[1, 2, 3, np.nan, 1, 1]])
        for data in d1, d2:
            i = Integrate(methods=Integrate.PeakX, limits=[[0, 5]])(data)
            self.assertEqual(i[0][0], 2)
            np.testing.assert_equal(i.domain[0].compute_value.baseline(data)[1], 0)

    def test_peakxbaseline(self):
        data = Orange.data.Table([[1, 2, 3, 1, 1, 1]])
        i = Integrate(methods=Integrate.PeakXBaseline, limits=[[0, 5]])(data)
        self.assertEqual(i[0][0], 2)
        np.testing.assert_equal(i.domain[0].compute_value.baseline(data)[1],
                                [[1, 1, 1, 1, 1, 1]])

    def test_empty_interval(self):
        data = Orange.data.Table([[1, 2, 3, 1, 1, 1]])
        i = Integrate(methods=Integrate.Simple, limits=[[10, 16]])(data)
        self.assertEqual(i[0][0], 0)
        i = Integrate(methods=Integrate.Baseline, limits=[[10, 16]])(data)
        self.assertEqual(i[0][0], 0)
        i = Integrate(methods=Integrate.PeakMax, limits=[[10, 16]])(data)
        self.assertEqual(i[0][0], np.nan)
        i = Integrate(methods=Integrate.PeakBaseline, limits=[[10, 16]])(data)
        self.assertEqual(i[0][0], np.nan)
        i = Integrate(methods=Integrate.PeakAt, limits=[[10, 16]])(data)
        self.assertEqual(i[0][0], 1)  # get the rightmost one

    def test_different_integrals(self):
        data = Orange.data.Table([[1, 2, 3, 1, 1, 1]])
        i = Integrate(methods=[Integrate.Simple, Integrate.Baseline],
                      limits=[[0, 5], [0, 5]])(data)
        self.assertEqual(i[0][0], 8)
        np.testing.assert_equal(i.domain[0].compute_value.baseline(data)[1], 0)
        np.testing.assert_equal(i.domain[1].compute_value.baseline(data)[1], 1)

    def test_names(self):
        data = Orange.data.Table([[1, 2, 3, 1, 1, 1]])
        i = Integrate(methods=[Integrate.Simple, Integrate.Baseline],
                      limits=[[0, 5], [0, 6]])(data)
        self.assertEqual(i.domain[0].name, "0 - 5")
        self.assertEqual(i.domain[1].name, "0 - 6")
        i = Integrate(methods=[Integrate.Simple, Integrate.Baseline],
                      limits=[[0, 5], [0, 6]], names=["simple", "baseline"])(data)
        self.assertEqual(i.domain[0].name, "simple")
        self.assertEqual(i.domain[1].name, "baseline")

    def test_repeated(self):
        data = Orange.data.Table([[1, 2, 3, 1, 1, 1]])
        i = Integrate(methods=[Integrate.Simple, Integrate.Baseline],
                      limits=[[0, 5], [0, 6]], names=["int", "int"])(data)
        self.assertEqual(i.domain[0].name, "int")
        self.assertEqual(i.domain[1].name, "int (1)")

    def test_metas_output(self):
        data = Orange.data.Table([[1, 2, 3, 1, 1, 1]])
        i = Integrate(methods=[Integrate.Simple, Integrate.Baseline],
                      limits=[[0, 5], [0, 6]], metas=True)(data)
        metavars = [a.name for a in i.domain.metas]
        self.assertTrue("0 - 5" in metavars and "0 - 6" in metavars)
        self.assertEqual(i[0]["0 - 5"], 8)
        self.assertEqual(i[0]["0 - 6"], 3)
