import unittest
from ttlab.optical_spectroscopy.insplorion import Insplorion
import numpy as np


class InsplorionTestCases(unittest.TestCase):

    class InsplorionDataExample:
        filename = 'tests/mock_data/light_spectrometer_example.ins'
        wavelength = np.array([350.76616465291863, 351.82069361649877, 352.87511994500551])
        dark_ref = np.array([48.8, 124.56, 58.57])
        bright_ref = np.array([422.49, 499.73, 446.08])
        time = np.array([3.0346465, 8.0355699, 13.0370031])
        intensity = [
            np.array([368.56, 460.23, 403.37])-bright_ref,
            np.array([367.69, 455.12, 419.51])-bright_ref,
            np.array([361.73, 450.99, 418.43])-bright_ref
                     ]

    def test_import_insplorion(self):
        result = Insplorion(self.InsplorionDataExample.filename)
        self.assertEqual(self.InsplorionDataExample.filename, result.filename)
        np.testing.assert_array_equal(self.InsplorionDataExample.wavelength, result.data['wavelength'])
        np.testing.assert_array_equal(self.InsplorionDataExample.dark_ref, result.data['dark ref'])
        np.testing.assert_array_equal(self.InsplorionDataExample.bright_ref, result.data['bright ref'])
        np.testing.assert_array_equal(self.InsplorionDataExample.time, result.data['time'])
        np.testing.assert_array_equal(self.InsplorionDataExample.intensity, result.data['intensity'])