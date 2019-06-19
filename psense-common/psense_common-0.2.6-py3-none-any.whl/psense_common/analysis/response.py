import numpy as np
import pandas as pd
import re
from datetime import datetime, timedelta
import json
import copy


class StepResponse(object):
    def __init__(self, data, channels=[], c_thresh_ignore=0.25, debugmode=False):
        assert isinstance(data, pd.DataFrame), "data must be a pandas DataFrame"

        self.debug = debugmode
        self.msgid = '[StepResponse]'
        self.data = data
        self.to_per_minute = 60 / \
            pd.Timedelta(np.median(np.diff(data.index))).total_seconds()
        self.coeff_thresh_ignore_peak = c_thresh_ignore

        self.output = pd.DataFrame()
        self.result = dict()

        self.compute_sensor_response()

    def __str__(self):
        return json.dumps(
            self.result,
            indent=2
        )

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

    def is_valid(self):
        return len(self.output.index) > 0

    def compute_sensor_response(self, channels=[]):
        "collect response time related stats, return as dataframe (each row is a separate channel's results)"
        keys = self.data.columns.values.tolist()
        if len(channels) == 0:
            r = re.compile("signal*")
            channels = list(filter(r.match, keys))

        output = []
        for channel in channels:
            clip = self.data['c_{}'.format(channel)]
            deriv = self.data['d_{}'.format(channel)]

            if np.max(deriv) * self.to_per_minute < self.coeff_thresh_ignore_peak:
                self.logm(
                    'debug', '[compute_sensor_response] insufficient rate ({} na/sample). ignored'.format(np.max(deriv)))
                continue

            clip_range = np.percentile(clip, [0, 100])
            cum_deriv = clip - clip[0]  # np.cumsum(deriv)
            goal_start = 0.1 * cum_deriv[-1]
            goal_end = 0.9 * cum_deriv[-1]

            t_rt10 = cum_deriv.where(cum_deriv < goal_start).last_valid_index()
            t_rt90 = cum_deriv.ge(goal_end).idxmax()
            t_rt = round((t_rt90 - t_rt10).total_seconds() / 6) / 10

            if t_rt < 0:
                self.logm(
                    'debug', '[compute_sensor_response] not a real step. ignoring.')
                continue

            start = self.data.index[0]
            finish = self.data.index[-1]

            self.result[channel] = dict(
                max_achieved_rate=np.max(deriv) * self.to_per_minute,
                response_time=t_rt,
                t10_ts=t_rt10.tz_localize(None).to_pydatetime().isoformat(),
                t10_val=clip[t_rt10].tolist(),
                t90_ts=t_rt90.tz_localize(None).to_pydatetime().isoformat(),
                t90_val=clip[t_rt90].tolist(),
            )

            output.append([
                start.tz_localize(None),
                round((finish - start).total_seconds() / 6) / 10,
                clip_range[0],
                clip_range[1],
                cum_deriv[-1],
                t_rt,
                t_rt10.tz_localize(None),
                clip[t_rt10],
                t_rt90.tz_localize(None),
                clip[t_rt90],
                np.max(deriv) * self.to_per_minute
            ])

            self.logm('debug', '[compute_sensor_response] [channel={}] step analyzed, rt={:04.1f}m, dI={:05.2f}'.format(
                channel, t_rt, np.max(deriv) * self.to_per_minute))

        # print(clip)
        self.output = pd.DataFrame.from_records(output, columns=[
            'T_Start', 'Width_P', 'I_P0', 'I_P1', 'Range_I_RT', 'T_RT', 'T_RT10', 'I_RT10', 'T_RT90', 'I_RT90', 'Max_dI'])


class PSenseResponse(object):
    "PercuSense class handles calculations associated with sensor response."

    def __init__(self, df, debugmode=False):
        self.debug = debugmode
        self.msgid = '[PSenseResponse]'
        self.data = df
        self.coeff_thresh_low = 0.012
        self.coeff_thresh_high = 2
        self.coeff_thresh_ignore_peak = 0.25
        self.result = dict()

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

    def find_steps_in_signal(self, signal, dsignal=None, numsteps=5, samplewindow=8):
        assert isinstance(signal, pd.Series), "signal should be a pandas Series"

        signal_min = signal.quantile(0.01) if (
            len(signal) < 7000) else (signal.quantile(0.001))
        signal_max = signal.quantile(0.95)
        thresh_too_high = (signal_max - signal_min) / (numsteps)
        thresh_high = thresh_too_high / self.coeff_thresh_high
        thresh_low = self.coeff_thresh_low * samplewindow

        self.logm('info', '[find_steps_in_signal] data content (channel {}): range({}, {})'.format(
            signal.name, signal_max, signal_min))
        self.logm(
            'debug', '[find_steps_in_signal] estimates based on {} steps'.format(numsteps))
        self.logm('debug', '[find_steps_in_signal] thresholds: {:05.2f}, {:05.2f}, {:05.2f} nA'.format(
            thresh_low, thresh_high, thresh_too_high))

        # dsig = data['d_signal{}'.format(channel)]
        if dsignal is None:
            dsignal = signal.diff()

        rollsum = dsignal.rolling(samplewindow).sum()

        is_high = rollsum > thresh_high
        is_too_high = rollsum > thresh_too_high
        is_first_hit = is_high != (is_high.shift())  # or is_high != is_high.shift(2)

        steps = signal[is_high & ~is_too_high & is_first_hit]

        start_tm = []
        end_tm = []

        is_stable = signal[(rollsum > -thresh_low) & (rollsum < thresh_low)]
        for index, step in steps.iteritems():

            if len(end_tm) > 0 and is_stable[:index].index[-1] < end_tm[-1]:
                "don't allow overlapping steps"
                continue

            if (index >= is_stable.index[-1] or
                    index < is_stable.index[0] or
                    (is_stable[index:].index[0] - is_stable[:index].index[-1]) < timedelta(seconds=15)):
                "steps that are too rapid are likely noise"
                continue

            start_tm.append(is_stable[:index].index[-1])
            end_tm.append(is_stable[index:].index[0])

        self.logm(
            'debug', '[find_steps_in_signal] found {} possible steps'.format(len(start_tm)))

        return start_tm, end_tm

    def define_steps_in_signal(self, tm_start, time_window_mins=20):
        "manual definition of steps (alternative to find_steps_in_signal(..))"

        if isinstance(tm_start, list):
            tm_start = pd.Series(tm_start)

        assert isinstance(
            tm_start, pd.Series), 'tm_start must be of type list or pd.Series'

        # we want pandas Timestamps in our lists
        if not isinstance(tm_start[0], pd.Timestamp):
            tm_start = pd.to_datetime(tm_start)

        are_steps_independent = (np.nanmin(tm_start.diff()).astype(float)
                                 * (1e-9) / 60) > time_window_mins
        assert are_steps_independent, 'Overlapping steps detected. Timestamps must be at least time_window_mins ({} min) apart.'.format(
            time_window_mins)

        # generate end-windows
        tm_finish = []
        for t0 in tm_start:
            tm_finish.append(t0 + timedelta(minutes=time_window_mins))

        return tm_start, tm_finish

    def run(self, channels=[], tm_start=[], tm_finish=[], numsteps=5, samplewindow=8):
        "guess the steps and iterate through them to generate sensor response analyses for each"
        if len(channels) == 0:
            keys = self.data.columns.tolist()
            r = re.compile("signal*")
            channels = list(filter(r.match, keys))

        for channel in channels:
            self.logm('info', '[run] analysis starting for channel {}'.format(channel))
            if len(tm_start) > 0:
                assert tm_start[0].tzinfo is not None, 'timestamps should be timezone-aware'
            else:
                try:
                    tm_start, tm_finish = self.find_steps_in_signal(
                        signal=self.data['c_{}'.format(channel)],
                        numsteps=numsteps,
                        samplewindow=samplewindow)
                except:
                    self.logm(
                        'info',
                        '[run] find_steps_in_signal() failed. skipping sensor.')
                    continue

            self.result[channel] = pd.DataFrame()
            self.logm('info', '[run] checking steps for sensor response')
            for start, finish in zip(tm_start, tm_finish):
                window = self.data[(self.data.index >= start) &
                                   (self.data.index < finish)]
                sr = StepResponse(
                    data=window,
                    c_thresh_ignore=self.coeff_thresh_ignore_peak,
                    channels=[channel],
                    debugmode=self.debug)

                if sr.is_valid():
                    self.logm('debug', '[run] adding step to result')
                    self.result[channel] = self.result[channel].append(
                        sr.output,
                        ignore_index=True)

    def getResult(self):
        return copy.deepcopy(self.result)
