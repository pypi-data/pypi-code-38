import numpy as np
import re


class kfilter(object):
    "PercuSense filter generates kalman and savitzky-golay outputs that are used for data smoothing/estimation"

    def __init__(self, filter_length=10, filter_init=40, process_variance=0.01, initial_guess=5, measurements=[], error_guess=0.01, rep_count=0):
        self.debugmode = False
        self.filter_length = filter_length

        # disable filter for first 40 points (~20min)
        self.filter_init = filter_init
        # 5% change allowed between consecutive measurements
        self.clip_pct_high = 1.05
        self.clip_pct_low = 0.95

        # kalman filter coefficients
        self.process_variance = process_variance
        self.posteri_estimate = initial_guess
        self.posteri_error_estimate = error_guess

        # filter initialization + state
        self.measurements = measurements
        self.consecutive_replacements = rep_count
        self.posteri_noise = 0
        self.posteri_deriv = 0

        # savitzky-golay filter first derivative coeff -- use this for rate term
        self.coeff_sg_velocity = [-3, -2, -1, 0, 3, 1, 2]
        self.denom_sg_velocty = 28
        # savitzky-golay filter second derivative coeff -- accel + noise calcs
        self.coeff_sg_accel = [5, 0, -3, -4, -3, 0, 5]
        self.denom_sg_accel = 42

    def in_init(self):
        return (self.filter_init > 0)

    def calculate_derivative(self, measurements=None):
        if measurements is None:
            measurements = self.measurements
            '''if self.in_init():
                return 0'''

        # savitzky-golay first derivative filter
        coeff = self.coeff_sg_velocity
        normalization = self.denom_sg_velocty

        if len(measurements) < 7:
            return 0
        else:
            dp = np.dot(coeff, measurements[-7:])
            return dp / normalization

    def calculate_accel(self, measurements=None):
        if measurements is None:
            measurements = self.measurements
            '''if self.in_init():
                return 0'''

        # savitzky-golay second derivative filter
        coeff = self.coeff_sg_accel
        normalization = self.denom_sg_accel

        if len(measurements) < 7:
            return 0
        else:
            dp = np.dot(coeff, measurements[-7:])
            return dp / normalization

    def update_measurement_state(self, measurement_value):
        "update kalman states"
        if (
            # filter fully populated
            (len(self.measurements) >= (self.filter_length)) and
            # filter doesn't need to be reset
            (self.consecutive_replacements < (self.filter_length)) and
            (not self.in_init())  # no during init
        ):
            latest_measurement = self.measurements[-1]

            # simple validation -- don't alow raw signal to change to 3/4 or 4/3 latestbetween samples
            if (np.mean(self.measurements) >= 0):
                # positive signals
                if (measurement_value > self.clip_pct_high * latest_measurement):
                    measurement_value = self.clip_pct_high * latest_measurement
                    self.consecutive_replacements += 1
                elif (measurement_value < self.clip_pct_low * latest_measurement):
                    measurement_value = self.clip_pct_low * latest_measurement
                    self.consecutive_replacements += 1
                else:
                    self.consecutive_replacements = 0
            else:
                # negative signals
                if (measurement_value < self.clip_pct_high * latest_measurement):
                    measurement_value = self.clip_pct_high * latest_measurement
                    self.consecutive_replacements += 1
                elif (measurement_value > self.clip_pct_low * latest_measurement):
                    measurement_value = self.clip_pct_low * latest_measurement
                    self.consecutive_replacements += 1
                else:
                    self.consecutive_replacements = 0

            self.measurements.append(round(measurement_value, 2))

            # if the filter has been fully populated
            if len(self.measurements) > self.filter_length:
                self.measurements.pop(0)

            # noise = measurement sigma over the last n-samples
            self.posteri_noise = round(np.std(self.measurements), 3)

            # update the rate
            self.posteri_deriv = round(
                self.measurements[-1] - self.posteri_estimate, 3)

            '''
            print('{},{:.3},{:.3}'.format(self.posteri_estimate, self.posteri_deriv, round(
                np.mean([t - s for s, t in zip(self.measurements, self.measurements[1:])][-3:]), 3)))

            # self.posteri_deriv = round(
            #    np.mean([t - s for s, t in zip(self.measurements, self.measurements[1:])][-3:]), 3)
            if self.filter_length < 7:
                # this is a simple calculation. Difference between previous estimate and new measurement.
                self.posteri_deriv = round(
                    self.measurements[-1] - self.posteri_estimate, 3)
            else:
                self.posteri_deriv = self.calculate_derivative(
                    self.measurements)
            '''
        else:
            if self.consecutive_replacements > 0:
                self.consecutive_replacements = 0
                for i in range(min(round(self.filter_length / 2), len(self.measurements))):
                    self.measurements.pop(0)

            self.measurements.append(round(measurement_value, 2))
            self.posteri_estimate = measurement_value

            # if the filter has been fully populated
            if len(self.measurements) > self.filter_length:
                self.measurements.pop(0)

            # if we are in init, decrement the # of samples remaining for init mode
            if self.in_init():
                self.filter_init -= 1

            # don't update noise, don't update rate of change
            pass

    def input_latest_measurement(self, measurement_value):
        "update the filter with new raw data"
        if isinstance(measurement_value, str):
            measurement_value = float(measurement_value)

        assert(isinstance(measurement_value, (int, float)))

        # update posteri_noise and posteri_deriv values
        self.update_measurement_state(measurement_value)
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance

        blending_factor = priori_error_estimate / \
            (priori_error_estimate + self.posteri_noise)

        self.posteri_estimate = round(
            priori_estimate + blending_factor * self.posteri_deriv, 3)
        self.posteri_error_estimate = round(
            (1 - blending_factor) * priori_error_estimate, 4)

    def get_latest_estimated_measurement(self):
        "return kalman estimate along with the clipped input stored in the measurement buffer"
        return self.posteri_estimate, self.measurements[-1]

    def run(self, data):
        "generator for retrieving full filter outputs"

        for val in data:
            self.input_latest_measurement(val)
            filt, clip = self.get_latest_estimated_measurement()
            velocity = self.calculate_derivative()
            acceleration = self.calculate_accel()
            init = self.in_init()
            yield init, clip, filt, velocity, acceleration


def blend(signal1, signal2, noise, blending_factor=0.05):
    "blends two signals based on a normalizing noise factor"
    return ((signal1 * blending_factor) + (signal2 * noise)) / (noise + blending_factor)


def run_psensefilter(data, blending_factor):
    "apply kfilter and blending to pandas dataframe (raw data in col signal#)"
    keys = data.columns.values.tolist()
    r = re.compile("signal*")

    for channel in list(filter(r.match, keys)):
        signal = data[channel]
        kf = kfilter(initial_guess=signal[0])
        clip = []
        fsig = []
        dsig = []
        ddsig = []
        smooth = []
        noise = []
        for init, a, b, c, d in kf.run(signal):
            clip.append(a)
            fsig.append(b)
            dsig.append(c)
            ddsig.append(d)

            if init:
                smooth.append(np.mean(clip))
                noise.append(0)
            else:
                smooth.append(np.mean(clip[-39:]))
                noise.append(np.std(ddsig[-6:]))

        del kf  # not sure why but kf isn't re-initializing for new channels

        data['c_{}'.format(channel)] = clip
        data['fsg_{}'.format(channel)] = fsig
        data['f20_{}'.format(channel)] = smooth = np.array(smooth)
        data['d_{}'.format(channel)] = dsig
        data['dd_{}'.format(channel)] = ddsig
        data['noise_{}'.format(channel)] = noise = np.array(noise)
        data['blend_{}'.format(channel)] = blend(
            np.add(fsig, dsig), smooth, noise, blending_factor)

    data = data.round(2)
    return data
