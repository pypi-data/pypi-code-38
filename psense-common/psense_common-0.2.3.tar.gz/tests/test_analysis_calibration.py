import unittest
import pandas as pd
import numpy as np
from psense_common.analysis import PSenseCalibration
from datetime import datetime


class TestPCal(unittest.TestCase):
    def setUp(self):
        self.test_expid = '19D01B101G03-0229-229-HT-G11CPBX'
        self.test_sensor = pd.read_csv('tests/testdata_calibration_sensor', sep=',', index_col='timestamp', parse_dates=['timestamp'])

    def test_init(self):
        cal = PSenseCalibration(expid=self.test_expid, data=self.test_sensor)

        self.assertEqual(cal.expid, self.test_expid)
        self.assertEqual(list(cal.result.keys()), ['coeff', 'r'])
        self.assertEqual(cal.channels, ['signal1'])
        self.assertEqual(len(cal.raw), 319)

    def test_logm(self):
        cal = PSenseCalibration(expid=self.test_expid, data=self.test_sensor)
        cal.debug = True
        self.assertTrue(cal.logm('info', 'info-message-always-show'))
        self.assertTrue(cal.logm('debug', 'debug-message-show-by-level'))
        cal.debug = False
        self.assertFalse(cal.logm('debug', 'debug-message-hide'))

    def test_get_dataslice(self):
        cal = PSenseCalibration(expid=self.test_expid, data=self.test_sensor)

        t_start = pd.Timestamp('2019-04-02 06:30:00')
        t_end = pd.Timestamp('2019-04-02 06:40:00')
        res = cal.get_sensordata_slice(t_start, t_end)
        self.assertEqual(len(res), 20)
        self.assertEqual(res.iloc[0]['signal1'], 2.72)
        self.assertEqual(res.iloc[-1]['signal1'], 2.73)
        self.assertEqual(res.index[0], pd.Timestamp('2019-04-02 06:30:10'))

        t_end = t_start
        t_start = pd.Timestamp('2019-04-01 06:30:00')
        res = cal.get_sensordata_slice(t_start, t_end)
        self.assertEqual(len(res), 0)

        t_start = pd.Timestamp('2019-04-02 10:55:00')
        t_end = pd.Timestamp('2019-04-03 01:00:00')
        res = cal.get_sensordata_slice(t_start, t_end)
        self.assertEqual(len(res), 10)
        self.assertEqual(res.index[-1], pd.Timestamp('2019-04-02 10:59:49'))

    def test_add_reference(self):
        cal = PSenseCalibration(expid=self.test_expid, data=self.test_sensor, debugmode=False)

        # confirm a point can be added
        ts = pd.Timestamp('2019-04-02 08:55:00')
        cal.add_reference(ts, 100)
        self.assertEqual(cal.calibration.iloc[0]['signal1'], 2.73)
        self.assertEqual(cal.calibration.iloc[0]['ref'], 100)
        self.assertEqual(cal.calibration.iloc[0]['ts'], pd.Timestamp('2019-04-02 08:55:00'))

        # confirm offset and window will change based on initialization
        cal = PSenseCalibration(expid=self.test_expid, data=self.test_sensor, sample_offset_time=0, sample_window_time=10)
        ts = pd.Timestamp('2019-04-02 08:55:00')
        cal.add_reference(ts, 200)
        self.assertEqual(cal.calibration.iloc[0]['signal1'], 2.82)
        self.assertEqual(cal.calibration.iloc[0]['ref'], 200)

        # should add null value when sensor data doesn't exist
        ts = pd.Timestamp('2019-04-03 08:55:00')
        cal.add_reference(ts, 100)
        self.assertTrue(pd.isnull(cal.calibration.iloc[-1]['signal1']))
        self.assertEqual(len(cal.calibration), 2)

    def test_linear_reg(self):
        cal = PSenseCalibration(expid=self.test_expid, data=self.test_sensor, debugmode=False)
        self.assertRaises(AssertionError, cal.model_fit)

        cal.add_reference(pd.Timestamp('2019-04-02 09:00:00'), 100)
        cal.add_reference(pd.Timestamp('2019-04-02 09:30:00'), 200)
        cal.add_reference(pd.Timestamp('2019-04-02 10:00:00'), 300)
        cal.add_reference(pd.Timestamp('2019-04-02 10:30:00'), 400)

        cal.model_fit()
        self.assertTrue(len(cal.result['coeff']) == 1)
        self.assertEqual(cal.result['coeff'][0], [0.0208, 0.62])
        self.assertEqual(cal.result['r'][0], [0.9986])

        cal = PSenseCalibration(expid=self.test_expid, data=self.test_sensor, debugmode=False)
        cal.add_reference(pd.Timestamp('2019-04-02 09:00:00'), 400)
        cal.add_reference(pd.Timestamp('2019-04-02 09:30:00'), 300)
        cal.add_reference(pd.Timestamp('2019-04-02 10:00:00'), 200)
        cal.add_reference(pd.Timestamp('2019-04-02 10:30:00'), 100)
        cal.model_fit()
        self.assertEqual(cal.result['coeff'][0], [-0.0208, 11.0])
        self.assertEqual(cal.result['r'][0], [-0.9986])

    def test_logarithmic_reg(self):
        self.test_sensor = pd.read_csv('tests/testdata_calibration_logfit', sep=',', index_col='timestamp', parse_dates=['timestamp'])
        cal = PSenseCalibration(expid=self.test_expid, data=self.test_sensor, debugmode=False)
        cal.add_reference(pd.Timestamp('2019-04-02 09:00:00'), 0)
        cal.add_reference(pd.Timestamp('2019-04-02 09:30:00'), 1)
        cal.add_reference(pd.Timestamp('2019-04-02 10:00:00'), 2)
        cal.add_reference(pd.Timestamp('2019-04-02 10:30:00'), 3)

        cal.model_fit()
        self.assertEqual(cal.result['r'][0], 0.9418)
        cal.result = dict(coeff=[], r=[])

        cal.model_fit(model_type='logarithmic')
        self.assertTrue(np.array_equal(cal.result['coeff'][0], np.array([-0.668813166669576, 0.8773716434543674, 1.0801832613942033])))
        self.assertEqual(cal.result['r'][0], 0.9993)

    def test_multichan(self):
        self.test_sensor = pd.read_csv('tests/testdata_calibration_multichan', sep=',', index_col='ts', parse_dates=['ts'])
        cal = PSenseCalibration(expid=self.test_expid, data=self.test_sensor, debugmode=False)
        self.assertEqual(cal.channels, ['signal1', 'signal2'])

        cal.add_reference(pd.Timestamp('2019-04-02 8:30'), 100)
        cal.add_reference(pd.Timestamp('2019-04-02 9:00'), 200)
        cal.add_reference(pd.Timestamp('2019-04-02 9:45'), 300)
        cal.model_fit()
        self.assertEqual(cal.result['coeff'][0], [0.0106, 0.57])
        self.assertEqual(cal.result['coeff'][1], [0.0107, 0.7])
        self.assertEqual(cal.result['r'], [0.9909, 0.9940])

    def test_dump_creates_deepcopy(self):
        cal = PSenseCalibration(expid=self.test_expid, data=self.test_sensor, debugmode=False)
        cal.add_reference(pd.Timestamp('2019-04-02 09:00:00'), 100)
        mycopy = cal.dump()
        cal.add_reference(pd.Timestamp('2019-04-02 09:30:00'), 200)

        self.assertEqual(len(mycopy), 1)
        self.assertEqual(len(cal.calibration), 2)


if __name__ == '__main__':
    unittest.main()
