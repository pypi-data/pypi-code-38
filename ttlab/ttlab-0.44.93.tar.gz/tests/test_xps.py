import unittest
from ttlab import XPS
import numpy as np


class XPSTestCases(unittest.TestCase):
    class XPSDataExample:
        filename_survey = 'tests/mock_data/AuAlPd21.asc'
        filename_multi = 'tests/mock_data/xps_multi_example.asc'

    class SurveyDataExample:
        counts = np.array([18979.9980, 18894.2852, 18854.2852, 18705.7129, 21028.5703])
        energy = np.array([1200, 1199.2, 1198.4, 1197.6, 1196.8])

    class MultiDataExample:
        counts = \
            {
                'C1s': np.array([3640.8594, 3556.5583, 3561.2896]),
                'O1s': np.array([7133.7617, 7016.3423, 7063.6543, 6956.1274]),
                'Si2p': np.array([2408.1714, 2421.0747])
            }
        energy = \
            {
                'C1s': np.array([310, 309.875, 309.75]),
                'O1s': np.array([545, 544.875, 544.75, 544.625]),
                'Si2p': np.array([115, 114.875])
            }

    def test_import_XPS(self):
        result = XPS(filename_survey=self.XPSDataExample.filename_survey,filename_multi=self.XPSDataExample.filename_multi)
        self.assertEqual(self.XPSDataExample.filename_survey, result.filename_survey)
        self.assertEqual(self.XPSDataExample.filename_multi, result.filename_multi)
        np.testing.assert_array_equal(self.SurveyDataExample.counts, result.survey_data.counts)
        np.testing.assert_array_equal(self.SurveyDataExample.energy,result.survey_data.energy)
        np.testing.assert_array_equal(self.MultiDataExample.counts['C1s'],result.multi_data.counts['C1s'])
        np.testing.assert_array_equal(self.MultiDataExample.counts['O1s'],result.multi_data.counts['O1s'])
        np.testing.assert_array_equal(self.MultiDataExample.counts['Si2p'],result.multi_data.counts['Si2p'])
        np.testing.assert_array_equal(self.MultiDataExample.energy['C1s'],result.multi_data.energy['C1s'])
        np.testing.assert_array_equal(self.MultiDataExample.energy['O1s'],result.multi_data.energy['O1s'])
        np.testing.assert_array_equal(self.MultiDataExample.energy['Si2p'],result.multi_data.energy['Si2p'])
