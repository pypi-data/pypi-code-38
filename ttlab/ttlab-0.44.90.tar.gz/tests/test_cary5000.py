import unittest
import numpy as np
from ttlab.optical_spectroscopy.cary5000 import Cary5000
from ttlab.optical_spectroscopy.cary5000.cary5000_file_reader import Data


baseline = Data()
baseline.transmission = np.array([50.73487854, 50.7313118, 50.73355865, 50.73348999])
baseline.wavelength = np.array([800, 799, 798, 797])

sample_1 = Data()
sample_1.transmission = np.array([97.96983337, 97.95070648, 97.91414642, 97.9327774])
sample_1.wavelength = np.array([800, 799, 798, 797])

sample_2 = Data()
sample_2.transmission = np.array([97.32642365, 97.34346008, 97.32424164, 97.31974792])
sample_2.wavelength = np.array([800, 799, 798, 796])

class Cary5000TestCases(unittest.TestCase):

    class Cary5000DataExample:
        filename = 'tests/mock_data/cary_5000_example.csv'
        data = {
            'Baseline 100%T': baseline,
            '60_Co_1': sample_1,
            '60_Co_2': sample_2
        }

    class Cary5000DataExampleJohan:
        filename = 'tests/mock_data/cary_5000_example.csv'
        sample_names = ['Baseline 100%T','60_Co_1','60_Co_2']
        acquired_data = {
            'Baseline 100%T': {
                'Wavelength (nm)': np.array([800, 799, 798, 797]),
                '%T': np.array([50.73487854, 50.7313118, 50.73355865, 50.73348999])
            },
            '60_Co_1': {
                'Wavelength (nm)': np.array([800, 799, 798, 797]),
                '%T': np.array([97.96983337, 97.95070648, 97.91414642, 97.9327774])
            },
            '60_Co_2': {
                'Wavelength (nm)': np.array([800, 799, 798, 796]),
                '%T': np.array([97.32642365, 97.34346008, 97.32424164, 97.31974792])
            }
        }

    def test_import_cary5000(self):
        result = Cary5000(self.Cary5000DataExample.filename)
        self.assertEqual(self.Cary5000DataExample.filename, result.filename)
        np.testing.assert_array_equal(self.Cary5000DataExample.data['Baseline 100%T'].wavelength, result.data['Baseline 100%T'].wavelength)
        np.testing.assert_array_equal(self.Cary5000DataExample.data['Baseline 100%T'].transmission, result.data['Baseline 100%T'].transmission)
        np.testing.assert_array_equal(self.Cary5000DataExample.data['60_Co_1'].transmission, result.data['60_Co_1'].transmission)
        #self.assertEqual(self.Cary5000DataExample.data['60_Co_1'], result.data['60_Co_1'])
        #self.assertEqual(self.Cary5000DataExample.data['60_Co_2'], result.data['60_Co_2'])

    def test_import_cary5000_johan(self):
        result = Cary5000(self.Cary5000DataExampleJohan.filename,johan_version=True)
        self.assertEqual(self.Cary5000DataExampleJohan.filename, result.filename)
        np.testing.assert_array_equal(
            self.Cary5000DataExampleJohan.acquired_data['Baseline 100%T']['Wavelength (nm)'],
            result.data['acquired data']['Baseline 100%T']['Wavelength (nm)'])
        np.testing.assert_array_equal(
            self.Cary5000DataExampleJohan.acquired_data['Baseline 100%T']['%T'],
            result.data['acquired data']['Baseline 100%T']['%T'])
        np.testing.assert_array_equal(
            self.Cary5000DataExampleJohan.acquired_data['60_Co_1']['Wavelength (nm)'],
            result.data['acquired data']['60_Co_1']['Wavelength (nm)'])
        np.testing.assert_array_equal(
            self.Cary5000DataExampleJohan.acquired_data['60_Co_1']['%T'],
            result.data['acquired data']['60_Co_1']['%T'])
        np.testing.assert_array_equal(
            self.Cary5000DataExampleJohan.acquired_data['60_Co_2']['Wavelength (nm)'],
            result.data['acquired data']['60_Co_2']['Wavelength (nm)'])
        np.testing.assert_array_equal(
            self.Cary5000DataExampleJohan.acquired_data['60_Co_2']['%T'],
            result.data['acquired data']['60_Co_2']['%T'])