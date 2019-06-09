import unittest
import pandas as pd
import numpy as np
import json
from psense_common.analysis import StepResponse, PSenseResponse
from datetime import datetime


class TestStepResponse(unittest.TestCase):
    def setUp(self):
        self.test_sensor = pd.read_csv('tests/testdata_stepresponse', sep=',', index_col='timestamp', parse_dates=['timestamp'])
        self.stepresponse = StepResponse(data=self.test_sensor)
        self.expected_result = {'signal1': {'max_achieved_rate': 0.62, 'response_time': 61.6, 't10_ts': '2019-04-02T09:05:11', 't10_val': 3.22, 't90_ts': '2019-04-02T10:06:49', 't90_val': 8.55}}
        self.presponse = PSenseResponse(df=self.test_sensor)

    def test_sr_init(self):
        self.assertRaises(AssertionError, StepResponse, [0, 1, 2])

        sr = StepResponse(data=self.test_sensor)
        self.assertEqual(sr.to_per_minute, 2)
        self.assertEqual(len(sr.data), len(self.test_sensor))

    def test_psenseresponse_init(self):
        self.assertEqual(self.presponse.coeff_thresh_low, 0.012)
        self.assertEqual(self.presponse.coeff_thresh_high, 2)
        self.assertEqual(self.presponse.coeff_thresh_ignore_peak, 0.25)
        self.assertEqual(len(self.presponse.data), len(self.test_sensor))

    def test_sr_tostr(self):
        stringified = json.dumps(self.expected_result, indent=2)
        self.assertEqual(str(self.stepresponse), stringified)

    def test_logm(self):
        self.stepresponse.debug = True
        self.assertTrue(self.stepresponse.logm('info', 'info-message-always-show'))
        self.assertTrue(self.stepresponse.logm('debug', 'debug-message-show-by-level'))
        self.stepresponse.debug = False
        self.assertFalse(self.stepresponse.logm('debug', 'debug-message-hide'))
        self.presponse.debug = True
        self.assertTrue(self.presponse.logm('info', 'info-message-always-show'))
        self.assertTrue(self.presponse.logm('debug', 'debug-message-show-by-level'))
        self.presponse.debug = False
        self.assertFalse(self.presponse.logm('debug', 'debug-message-hide'))

    def test_sr_compute(self):
        stepresponse = StepResponse(data=self.test_sensor[:pd.Timestamp('2019-04-02 09:35:02')])
        self.assertTrue(stepresponse.is_valid())
        output = stepresponse.output
        self.assertEqual(len(output), 1)
        output = output.iloc[0]
        self.assertEqual(output.T_Start, pd.Timestamp('2019-04-02 08:00:03'))
        self.assertEqual(output.Width_P, 95)
        self.assertEqual(output.I_P0, 2.65)
        self.assertEqual(output.I_P1, 4.83)
        self.assertEqual(output.Range_I_RT, 2.07)
        self.assertEqual(output.T_RT, 5.6)
        self.assertEqual(output.T_RT10, pd.Timestamp('2019-04-02 09:04:11'))
        self.assertEqual(output.I_RT10, 2.92)
        self.assertEqual(output.T_RT90, pd.Timestamp('2019-04-02 09:09:47'))
        self.assertEqual(output.I_RT90, 4.61)
        self.assertEqual(output.Max_dI, 0.34)

        stepresponse = StepResponse(data=self.test_sensor[:pd.Timestamp('2019-04-02 08:00:33')])
        self.assertFalse(stepresponse.is_valid())

    def test_find_steps(self):

        tm_start, tm_finish = self.presponse.find_steps_in_signal(
            signal=self.test_sensor['c_signal1'],
            numsteps=3,
            samplewindow=8)
        self.assertEqual(len(tm_start), 3)
        self.assertEqual(tm_start, [pd.Timestamp('2019-04-02 09:03:41'), pd.Timestamp('2019-04-02 09:36:32'), pd.Timestamp('2019-04-02 10:04:19')])
        self.assertEqual(tm_finish, [pd.Timestamp('2019-04-02 09:14:18'), pd.Timestamp('2019-04-02 09:47:10'), pd.Timestamp('2019-04-02 10:14:56')])

        tm_start, tm_finish = self.presponse.find_steps_in_signal(
            signal=self.test_sensor['c_signal1'],
            numsteps=5,
            samplewindow=5)
        self.assertEqual(len(tm_start), 3)
        self.assertEqual(tm_start[0], pd.Timestamp('2019-04-02 09:03:41'))
        self.assertEqual(tm_finish[0], pd.Timestamp('2019-04-02 09:12:47'))

    def test_define_steps(self):
        self.assertRaises(AssertionError, self.presponse.define_steps_in_signal, 'not-a-list-or-series')
        injections = ['2019-04-02 09:03', '2019-04-02 09:36', '2019-04-02 10:03']

        # check that overlapping steps aren't allowed
        self.assertRaises(AssertionError, self.presponse.define_steps_in_signal, injections, 30)

        tm_start, tm_finish = self.presponse.define_steps_in_signal(injections, time_window_mins=15)
        self.assertTrue(isinstance(tm_start, pd.Series))
        self.assertTrue(len(tm_start), 3)
        self.assertTrue(len(tm_finish), 3)
        self.assertEqual(tm_start[0], pd.Timestamp(injections[0]))
        self.assertEqual(tm_finish[0], pd.Timestamp('2019-04-02 09:18:00'))
        self.assertEqual(tm_start[2], pd.Timestamp(injections[2]))
        self.assertEqual(tm_finish, [pd.Timestamp('2019-04-02 09:18:00'), pd.Timestamp('2019-04-02 09:51:00'), pd.Timestamp('2019-04-02 10:18:00')])

    def test_sr_from_computed_steps(self):
        tm_start, tm_finish = self.presponse.find_steps_in_signal(
            signal=self.test_sensor['c_signal1'],
            numsteps=3,
            samplewindow=8)

        window = self.test_sensor[(self.test_sensor.index >= tm_start[0]) &
                                  (self.test_sensor.index < tm_finish[0])]
        sr = StepResponse(
            data=window,
            c_thresh_ignore=self.presponse.coeff_thresh_ignore_peak,
            channels=['signal1'])
        expected_output = dict(signal1={
            "max_achieved_rate": 0.34,
            "response_time": 4.6,
            "t10_ts": "2019-04-02T09:04:11",
            "t10_val": 2.92,
            "t90_ts": "2019-04-02T09:08:47",
            "t90_val": 4.55})
        self.assertEqual(str(sr), json.dumps(expected_output, indent=2))

    def test_psenseresponse_run(self):
        self.presponse.run()

        # test deepcopy
        result = self.presponse.getResult()
        result['signal1'] = result['signal1'][:1]
        self.assertEqual(len(result['signal1']), 1)

        # test run results
        result = self.presponse.result['signal1']
        self.assertEqual(len(result), 3)
        self.assertTrue(result.Width_P.equals(pd.Series([10.1, 10.0, 10.1])))
        self.assertTrue(result.I_P0.equals(pd.Series([2.78, 4.80, 6.73])))
        self.assertTrue(result.I_P1.equals(pd.Series([4.74, 6.62, 8.99])))
        self.assertTrue(result.T_RT.equals(pd.Series([4.6, 5.5, 3.5])))
        self.assertTrue(result.Max_dI.equals(pd.Series([0.34, 0.46, 0.62])))


if __name__ == '__main__':
    unittest.main()
