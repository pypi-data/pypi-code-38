import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from bdacore.preprocessing.fillna import fillna


class TestFillna(unittest.TestCase):
    def test_fillna_should_remove_nans_from_a_dataframe_and_replace_them_with_zeroes(self):
        # Given
        dataframe = pd.DataFrame([[0.0, np.nan], [np.nan, 1.0]])

        # When
        na_filled_dataframe = fillna(dataframe)

        # Then
        nans_replaced_with_zeroes_dataframe = pd.DataFrame([[0.0, 0.0], [0.0, 1.0]])
        self.assertFalse(na_filled_dataframe.isnull().values.any())
        assert_frame_equal(nans_replaced_with_zeroes_dataframe, na_filled_dataframe)
