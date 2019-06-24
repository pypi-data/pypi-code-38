import unittest
from datetime import datetime
from ttlab import MassSpectrometer


class MassSpecTestCases(unittest.TestCase):
    class MassSpecDataExample:
        filename = 'tests/mock_data/mass_spec_example.asc'
        start_time = 1511868445.737
        end_time = 1511888093.706
        gases = ['Ar', 'O2', 'N2']
        acquired_data = \
            {
                'Ar':
                    {
                        'Time':
                            [
                                1511868445.736,
                                1511868461.296,
                                1511868476.791,
                                1511868492.287,
                                1511868507.786
                            ],
                        'Time Relative [s]':
                            [
                                0.000,
                                15.559,
                                31.054,
                                46.550,
                                62.050
                            ],
                        'Ion Current [A]':
                            [
                                2.114839e-007,
                                1.977911e-007,
                                1.929350e-007,
                                1.901243e-007,
                                1.883651e-007
                            ]
                    },
                'O2':
                    {
                        'Time':
                            [
                                1511868450.93,
                                1511868466.464,
                                1511868481.951,
                                1511868497.455,
                                1511868512.95
                            ],
                        'Time Relative [s]':
                            [
                                5.194,
                                20.728,
                                36.214,
                                51.718,
                                67.213
                            ],
                        'Ion Current [A]':
                            [
                                2.351942e-010,
                                2.033837e-010,
                                1.871818e-010,
                                1.767437e-010,
                                1.691230e-010
                            ]
                    },
                'N2':
                    {
                        'Time':
                            [
                                1511868456.124,
                                1511868471.624,
                                1511868487.12,
                                1511868502.624,
                                1511868518.112
                            ],
                        'Time Relative [s]':
                            [
                                10.387,
                                25.887,
                                41.383,
                                56.887,
                                72.375
                            ],
                        'Ion Current [A]':
                            [
                                1.266428e-010,
                                1.101265e-010,
                                1.001284e-010,
                                9.322573e-011,
                                8.806678e-011
                            ]
                    }
            }

    class MassSpecDataExampleTimeShifted:
        start_time = 1511868435.737
        end_time = 1511888083.706
        acquired_data = \
            {
                'Ar':
                    {
                        'Time':
                            [
                                1511868445.736,
                                1511868461.296,
                                1511868476.791,
                                1511868492.287,
                                1511868507.786
                            ],
                        'Time Relative [s]':
                            [
                                0.000 + 10,
                                15.559 + 10,
                                31.054 + 10,
                                46.550 + 10,
                                62.050 + 10
                            ],
                        'Ion Current [A]':
                            [
                                2.114839e-007,
                                1.977911e-007,
                                1.929350e-007,
                                1.901243e-007,
                                1.883651e-007
                            ]
                    },
                'O2':
                    {
                        'Time':
                            [
                                1511868450.93,
                                1511868466.464,
                                1511868481.951,
                                1511868497.455,
                                1511868512.95
                            ],
                        'Time Relative [s]':
                            [
                                5.194 + 10,
                                20.728 + 10,
                                36.214 + 10,
                                51.718 + 10,
                                67.213 + 10
                            ],
                        'Ion Current [A]':
                            [
                                2.351942e-010,
                                2.033837e-010,
                                1.871818e-010,
                                1.767437e-010,
                                1.691230e-010
                            ]
                    },
                'N2':
                    {
                        'Time':
                            [
                                1511868456.124,
                                1511868471.624,
                                1511868487.12,
                                1511868502.624,
                                1511868518.112
                            ],
                        'Time Relative [s]':
                            [
                                10.387 + 10,
                                25.887 + 10,
                                41.383 + 10,
                                56.887 + 10,
                                72.375 + 10
                            ],
                        'Ion Current [A]':
                            [
                                1.266428e-010,
                                1.101265e-010,
                                1.001284e-010,
                                9.322573e-011,
                                8.806678e-011
                            ]
                    }
            }

    def test_import_mass_spec(self):
        result = MassSpectrometer(self.MassSpecDataExample.filename)
        self.assertEqual(self.MassSpecDataExample.filename, result.filename)
        self.assertEqual(self.MassSpecDataExample.start_time, result.start_time, )
        self.assertEqual(self.MassSpecDataExample.end_time, result.end_time)
        self.assertEqual(self.MassSpecDataExample.gases, result.gases)
        self.assertEqual(self.MassSpecDataExample.acquired_data, result.acquired_data)

    def test_shift_start_time(self):
        mass_spec = MassSpectrometer(self.MassSpecDataExample.filename)
        mass_spec.shift_start_time_back(10)
        self.assertEqual(self.MassSpecDataExampleTimeShifted.start_time, mass_spec.start_time)
        self.assertEqual(self.MassSpecDataExampleTimeShifted.end_time, mass_spec.end_time)
        self.assertEqual(self.MassSpecDataExampleTimeShifted.acquired_data, mass_spec.acquired_data)
