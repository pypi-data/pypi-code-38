import numpy as np
import scipy.stats
import scipy.optimize
import pandas as pd
import re
import copy
from datetime import (datetime, timedelta)


class PSenseCalibration(object):
    "Compute the sensitivity, background signal of a sensor, and its correlation with reference values"

    def __init__(self, expid, data, sample_offset_time=-5, sample_window_time=5, debugmode=False):
        assert isinstance(data, pd.DataFrame), "data must be a pandas DataFrame"
        self.debug = debugmode
        self.msgid = '[PSenseCalibration]'
        self.expid = expid

        self.raw = data
        r = re.compile("signal*")
        self.channels = list(filter(r.match, data.columns.values.tolist()))

        self.calibration = pd.DataFrame()
        self.sample_offset = timedelta(minutes=sample_offset_time)
        self.sample_window = timedelta(minutes=sample_window_time)

        self.result = dict(coeff=[], r=[])

    def logm(self, level, message):
        if level == 'debug' and not self.debug:
            return False

        print('{}  [{}]\t{} {}'.format(
            datetime.now().strftime('%Y%m%dT%H:%M:%S'),
            level.upper().strip(),
            self.msgid,
            message)
        )
        return True

    def get_sensordata_slice(self, t_start, t_finish):
        self.logm('debug', '[get_sensordata_slice] data from {} to {}'.format(
            t_start, t_finish))
        mask = (self.raw.index >= t_start) & (self.raw.index < t_finish)
        return self.raw.loc[mask]

    def add_reference(self, ts, reference):
        self.logm('info', '[add_reference] ts={}'.format(ts.isoformat()))
        # replace existing calibration point if the timestamp is the same
        mask = (self.calibration.index == ts)
        if len(self.calibration.loc[mask]) > 0:
            self.calibration = self.calibration.loc[~mask]

        sensor = self.get_sensordata_slice(
            ts + self.sample_offset,
            ts + self.sample_offset + self.sample_window)

        record = [ts.replace(tzinfo=None), reference]
        keys = ['ts', 'ref']
        for channel in self.channels:
            record.append(np.round(np.mean(sensor[channel]), 2))
            keys.append(channel)

        self.logm('debug', '[add_reference] record={}'.format(
            record[1:]))

        record = pd.DataFrame([record], columns=keys)
        if self.calibration.count == 0:
            record.set_index('ts')
            self.calibration = record
        else:
            self.calibration = self.calibration.append(record)

        return True

    def dump(self):
        return copy.deepcopy(self.calibration)

    def model_fit(self, model_type='linear'):
        assert len(self.calibration) > 1, 'model_fit requires more than 1 calibration point'

        # per each sensor
        reference = self.calibration['ref']
        for channel in self.channels:
            sensor = self.calibration[channel]

            if model_type == 'linear':
                slope, intercept, r, p, stderr = scipy.stats.linregress(
                    reference, sensor)
                self.result['coeff'].append([round(slope, 4), round(intercept, 2)])
                self.result['r'].append(round(r, 4))
                self.logm(
                    'debug', '[model_fit] {} fit: y={}x+{}'.format(model_type, slope, intercept))

            elif model_type == 'logarithmic':
                def exp_func(x, a, b, c):
                    return a * np.exp(-b * x) + c

                popt, pcov = scipy.optimize.curve_fit(exp_func, reference, sensor)
                self.result['coeff'].append(popt)

                ss_res = np.sum((sensor - exp_func(reference, *popt)) ** 2)  # sum of residuals
                ss_tot = np.sum((sensor - np.mean(sensor)) ** 2)  # total sum of squares
                r2 = 1 - (ss_res / ss_tot)  # r-squared
                self.result['r'].append(round(np.sqrt(r2), 4))  # pearson
                self.logm(
                    'debug', '[model_fit] {} fit: y= {}*exp(-{}*x) + {}'.format(model_type, popt[0], popt[1], popt[2]))

        return copy.deepcopy(self.result)
