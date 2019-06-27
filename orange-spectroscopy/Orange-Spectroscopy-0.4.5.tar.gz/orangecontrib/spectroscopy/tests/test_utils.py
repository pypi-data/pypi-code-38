import unittest
import array

import numpy as np

import Orange.data

from orangecontrib.spectroscopy.data import _spectra_from_image, build_spec_table, getx
from orangecontrib.spectroscopy.utils import get_hypercube, index_values, \
    InvalidAxisException


class TestHyperspec(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mosaic = Orange.data.Table("agilent/5_mosaic_agg1024.dmt")

    def test_hypercube_roundtrip(self):
        d = self.mosaic
        xat = [v for v in d.domain.metas if v.name == "map_x"][0]
        yat = [v for v in d.domain.metas if v.name == "map_y"][0]
        hypercube, lsx, lsy = get_hypercube(d, xat, yat)

        features = getx(d)
        ndom = Orange.data.Domain([xat, yat])
        datam = Orange.data.Table(ndom, d)
        coorx = datam.X[:, 0]
        coory = datam.X[:, 1]
        coords = np.ones((lsx[2], lsy[2], 2))
        coords[index_values(coorx, lsx), index_values(coory, lsy)] = datam.X
        x_locs = coords[:, 0, 0]
        y_locs = coords[0, :, 1]

        features, spectra, data = _spectra_from_image(hypercube, features,
            x_locs, y_locs)
        nd = build_spec_table(features, spectra, data)

        np.testing.assert_equal(d.X, nd.X)
        np.testing.assert_equal(d.Y, nd.Y)
        np.testing.assert_equal(d.metas, nd.metas)
        self.assertEqual(d.domain, nd.domain)

    def test_none_attr(self):
        with self.assertRaises(InvalidAxisException):
            get_hypercube(self.mosaic, None, None)
