# Copyright (c) 2017 Microsoft Corporation.  All rights reserved.
import unittest
import numpy as np
from ddt import ddt, file_data

from azureml.automl.core import preprocess as pp


@ddt
class BinningTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(BinningTests, self).__init__(*args, **kwargs)

    @file_data('binning_test_data.json')
    def test_binning_transform(self, actual_array, expected_array, bin_value):
        tr = pp.BinTransformer(bin_value)
        x = np.array(actual_array)
        expected_out = np.array(expected_array)
        self.assertTrue(np.all(tr.fit_transform(x) == expected_out))
