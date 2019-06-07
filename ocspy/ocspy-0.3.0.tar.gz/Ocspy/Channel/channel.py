from numpy.fft import fftfreq
from scipy.fftpack import fft, ifft

try:
    import cupy as cp
    from cupy.fft import fft as cfft
    from cupy.fft import ifft as icfft
except Exception as e:
    print('cupy can not be used')

from ..Base import SignalInterface
import numpy as np
from scipy.constants import c
import math
# import progressbar
from .ssfm import  symmetric_ssfm

# import arrayfire as af


class Awgn(object):

    def __init__(self, signal_power, request_snr, sps):
        self.signal_power = signal_power
        self.request_snr = request_snr
        self.sps = sps

    def __call__(self, shape):
        noise_power = self.signal_power / self.request_snr_lin

        noise_power = noise_power * self.sps
        noise_x = np.sqrt(noise_power / 2 / 2) * (
                np.random.randn(shape) + 1j * np.random.randn(shape))

        noise_y = np.sqrt(noise_power / 2 / 2) * (
                np.random.randn(shape) + 1j * np.random.randn(shape))

        return noise_x, noise_y

    @property
    def request_snr_lin(self):
        return 10 ** (self.request_snr / 10)


class LinearFiber(object):
    '''
        property:
            self.alpha  [db/km]
            self.D [ps/nm/km]
            self.length [km]
            self.wave_length:[nm]
            self.beta2: caculate beta2 from D,s^2/km
            self.slope: derivative of self.D ps/nm^2/km
            self.beta3_reference: s^3/km
        method:
            __call__: the signal will
    '''

    def __init__(self, alpha, D, length, slope=0, reference_wave_length=1550):
        self.alpha = alpha
        self.D = D
        self.length = length
        self.reference_wave_length = reference_wave_length
        self.slope = slope

    @property
    def beta3_reference(self):
        res = (self.reference_wave_length * 1e-12 / 2 / np.pi / c / 1e-3) ** 2 * (
                2 * self.reference_wave_length * 1e-12 * self.D + (
                self.reference_wave_length * 1e-12) ** 2 * self.slope * 1e12)

        return res

    @property
    def alpha_lin(self):
        # [1/km]
        return 0.1 * self.alpha * np.log(10)

    def leff(self, length):
        '''

        :param length: the length of a fiber [km]
        :return: the effective length [km]
        '''
        effective_length = 1 - np.exp(-self.alpha_lin * length)
        effective_length = effective_length / self.alpha_lin
        return effective_length

    @property
    def beta2_reference(self):
        return -self.D * (self.reference_wave_length * 1e-12) ** 2 / 2 / np.pi / c / 1e-3

    def beta2(self, wave_length):
        '''

        :param wave_length: [m]
        :return: beta2 at wave_length [s^2/km]
        '''
        dw = 2 * np.pi * c * (1 / wave_length - 1 / (self.reference_wave_length * 1e-9))
        return self.beta2_reference + self.beta3_reference * dw

    def _prop(self, signal: SignalInterface.Signal):
        '''

        :param signal: signal object to propagation across this fiber
        :return: ndarray
        '''
        center_lambda = signal.center_wave_length

        after_prop = np.zeros_like(signal[:])
        for pol in range(0, signal.pol_number):
            sample = signal[pol, :]
            sample_fft = fft(sample)
            freq = fftfreq(signal.sample_number_in_fiber, 1 / signal.fs_in_fiber)
            omeg = 2 * np.pi * freq

            after_prop[pol, :] = sample_fft * np.exp(-self.alpha_lin * self.length / 2)
            after_prop[pol, :] = ifft(after_prop[pol, :])

            disp = np.exp(-1j / 2 * self.beta2(center_lambda) * omeg ** 2 * self.length)
            after_prop[pol, :] = ifft(fft(after_prop[pol, :]) * disp)

        return np.atleast_2d(after_prop)

    def inplace_prop(self, signal: SignalInterface.Signal):
        after_prop = self._prop(signal)

        for i in range(signal.pol_number):
            signal[i, :] = after_prop[i, :]
        return signal

    def __call__(self, signal):
        self.inplace_prop(signal)
        return signal

    def __str__(self):
        string = f"alpha is {self.alpha} [db/km]\n" \
            f"beta2 is {self.beta2_reference} [s^2/km]\n" \
            f"beta3 is {self.beta3_reference} []\n" \
            f"D is {self.D} ps/nm/km\n" \
            f"length is {self.length} km\n" \
            f"reference wave length is {self.reference_wave_length * 1e9} [nm]"

        return string

    def __repr__(self):
        return self.__str__()


class NonlinearFiber(LinearFiber):

    def __init__(self, alpha, D, length, gamma, slope=0, step_length=5 / 1000, reference_wave_length=1550):
        super().__init__(alpha, D, length, slope=slope, reference_wave_length=reference_wave_length)
        self.gamma = gamma
        self.step_length = step_length

    @property
    def step_length_eff(self):
        return (1 - np.exp(-self.alpha_lin * self.step_length)) / self.alpha_lin

    def cupy_prop(self, signal):
#         print("cupy is used")

        if signal.pol_number != 2:
            raise Exception("only dp signal supported at this time")
        step_number = self.length / self.step_length
        step_number = int(np.floor(step_number))
        temp = np.zeros_like(signal[:])
        freq = fftfreq(signal.sample_number_in_fiber, 1 / signal.fs_in_fiber)
        freq_gpu = cp.asarray(freq)
        omeg = 2 * np.pi * freq_gpu
        D = -1j / 2 * self.beta2(signal.center_wave_length) * omeg ** 2
        N = 8 / 9 * 1j * self.gamma
        atten = -self.alpha_lin / 2

        time_x = cp.asarray(signal[0, :])
        time_y = cp.asarray(signal[1, :])

#         print('*' * 20 + "begin simulation" + '*' * 20)
#         bar = progressbar.ProgressBar(max_value=step_number)
        for i in range(step_number):
#             bar.update(i + 1)
            fftx = cfft(time_x)
            ffty = cfft(time_y)

            time_x, time_y = self.linear_prop_cupy(D, fftx, ffty, self.step_length / 2)
            time_x, time_y = self.nonlinear_prop_cupy(N, time_x, time_y)
            time_x = time_x * math.exp(atten * self.step_length)
            time_y = time_y * math.exp(atten * self.step_length)

            fftx = cfft(time_x)
            ffty = cfft(time_y)

            time_x, time_y = self.linear_prop_cupy(D, fftx, ffty, self.step_length / 2)

#         bar.finish()

#         print('*' * 20 + "end simulation" + '*' * 20)

        last_step = self.length - self.step_length * step_number
        last_step_eff = (1 - np.exp(-self.alpha_lin * last_step)) / self.alpha_lin
        if last_step == 0:
            time_x = cp.asnumpy(time_x)
            time_y = cp.asnumpy(time_y)
            temp[0, :] = time_x
            temp[1, :] = time_y
            return temp

        fftx = cfft(time_x)
        ffty = cfft(time_y)

        time_x, time_y = self.linear_prop_cupy(D, fftx, ffty, last_step / 2)
        time_x, time_y = self.nonlinear_prop_cupy(N, time_x, time_y, last_step_eff)
        time_x = time_x * math.exp(atten * last_step)
        time_y = time_y * math.exp(atten * last_step)

        fftx = cfft(time_x)
        ffty = cfft(time_y)
        time_x, time_y = self.linear_prop_cupy(D, fftx, ffty, last_step / 2)

        temp[0, :] = cp.asnumpy(time_x)
        temp[1, :] = cp.asnumpy(time_y)
        return temp

    def nonlinear_prop_cupy(self, N, time_x, time_y, step_length=None):

        if step_length is None:
            time_x = time_x * cp.exp(
                N * self.step_length_eff * (cp.abs(time_x) ** 2 + cp.abs(
                    time_y) ** 2))
            time_y = time_y * cp.exp(
                N * self.step_length_eff * (cp.abs(time_x) ** 2 + cp.abs(time_y) ** 2))
        else:
            time_x = time_x * cp.exp(
                N * step_length * (cp.abs(time_x) ** 2 + cp.abs(
                    time_y) ** 2))
            time_y = time_y * cp.exp(
                N * step_length * (cp.abs(time_x) ** 2 + cp.abs(time_y) ** 2))

        return time_x, time_y

    def linear_prop_cupy(self, D, fftx, ffty, length):
        time_x = icfft(fftx * cp.exp(D * length))
        time_y = icfft(ffty * cp.exp(D * length))

        return time_x, time_y

    def inplace_prop(self, signal,backend):
        if backend =='cupy':
            after_prop = self.cupy_prop(signal)
        else:
            setting = dict(beta2 = self.beta2(signal.center_wave_length),
                           gamma = self.gamma,step_length = self.step_length,fiber_length = self.length,
                           alpha_lin = self.alpha_lin)
            after_prop = symmetric_ssfm(signal,setting)
        signal.data_sample_in_fiber = np.array(after_prop)
        return signal

    def __call__(self, signal,backend='arrayfire'):
        self.inplace_prop(signal,backend)
        return signal

    def __str__(self):
        string = super(NonlinearFiber, self).__str__()
        string = f"{string}" \
            f"the step length is {self.step_length} [km]\n"
        return string

    def __repr__(self):
        return self.__str__()


class NonlinearFiberWithPMD(LinearFiber):

    def __init__(self, alpha, D, length, gamma, reference_length=1550, step_length=5 / 1000, is_dgd=True, **kwargs):
        '''

        :param alpha: [db/km]
        :param D: [ps/nm/km]
        :param length: [km]
        :param gamma: []
        :param reference_length:
        :param is_vector:
        :param kwargs:
                if pmd, dgd_coef should be specified,ps/sqrt(km)
                step_length [km]  the step length of split step fourier method
        '''
        super(NonlinearFiberWithPMD, self).__init__(alpha, D, length, reference_length)
        self.gamma = gamma
        if is_dgd:
            try:
                self.dgd_coef = kwargs['dgd_coef']
            except KeyError as e:
                self.dgd_coef = 0.1
        else:
            self.dgd_coef = 0

        self.step_length = step_length
        self.nplates = self.length / self.step_length
        self.nplates = int(np.floor(self.nplates))

        if self.nplates * self.step_length < self.length:
            self.last_step = self.length - self.nplates * self.step_length
        else:
            self.last_step = 0

        self.dgd = self.dgd_coef * np.sqrt(self.step_length * self.nplates) * 1e-12  # s

        if self.last_step != 0:
            self.last_dgd = self.dgd_coef * np.sqrt(self.last_step)
        else:
            self.last_dgd = 0

        self.dgdrms = np.sqrt((3 * np.pi) / 8) * self.dgd / np.sqrt(self.nplates)

        if self.last_dgd != 0:
            self.dgdrms_last = np.sqrt((3 * np.pi) / 8) * self.last_dgd / np.sqrt(1)
        else:
            self.dgdrms_last = 0

    @property
    def betat(self):
        return 1

    def vector_prop(self, signal: SignalInterface.WdmSignal):
        print("The Mankov equation of  will be solved using split step fourier method")
        sample_x = signal[0, :]
        sample_y = signal[1, :]

        sample_x_gpu = cp.asarray(sample_x)
        sample_y_gpu = cp.asarray(sample_y)

        wave_length = signal.center_wave_length

        beta2 = self.beta2(wave_length=wave_length)
        freq = fftfreq(signal.sample_number_in_fiber, 1 / signal.fs_in_fiber)
        omeg = 2 * np.pi * freq
        betat = -0.5 * omeg ** 2 * beta2
        db1 = self.dgdrms * omeg
        db1_last = self.dgdrms_last * omeg

        sample_x_gpu, sample_y_gpu = self.__vector_prop(sample_x_gpu, sample_y_gpu, betat, self.gamma, db1, db1_last)
        sample_x_cpu = cp.asnumpy(sample_x_gpu)
        sample_y_cpu = cp.asnumpy(sample_y_gpu)
        return sample_x_cpu, sample_y_cpu

    def __call__(self, signal):

        signal[0, :], signal[1, :] = self.vector_prop(signal)
        return signal

    def __vector_prop(self, ux, uy, betat, gamma, db1, db1_last):
        betat = cp.asarray(betat)
        db1 = cp.asarray(db1)
        db1_last = cp.asarray(db1_last)

        gamma = gamma * 8 / 9
        halfalpha = 0.5 * self.alpha_lin
        # bar = progressbar.ProgressBar(max_value=self.nplates)
        for i in range(self.nplates):
            ux, uy = self.__vector_nonlinear_step(ux, uy, gamma, self.step_length)
            ux, uy = self.__vector_linear_step(ux, uy, betat, db1, self.step_length)
            ux = ux * math.exp(-halfalpha * self.step_length)
            uy = uy * math.exp(-halfalpha * self.step_length)
            # bar.update(i + 1)

        if self.last_step:
            print(f"the last step {self.last_step}m is going to be propagated")
            ux, uy = self.__vector_nonlinear_step(ux, uy, gamma, self.last_step)
            ux, uy = self.__vector_linear_step(ux, uy, betat, db1_last, self.last_step)
            ux = ux * math.exp(-halfalpha * self.last_step)
            uy = uy * math.exp(-halfalpha * self.last_step)

        return ux, uy

    def __vector_linear_step(self, ux, uy, betat, db1, step_length):
        ux = cfft(ux)
        uy = cfft(uy)
        phi = np.random.rand(1, 1) * np.pi - 0.5 * np.pi
        kapa = 0.5 * np.arcsin(2 * np.random.rand(1, 1) - 1)

        rotation_matrix = np.array([[np.cos(phi) * np.cos(kapa) + 1j * np.sin(phi) * np.sin(kapa),
                                     np.sin(phi) * np.cos(kapa) - 1j * np.cos(phi) * np.sin(kapa)],
                                    [-np.sin(phi) * np.cos(kapa) - 1j * np.cos(phi) * np.sin(kapa),
                                     np.cos(phi) * np.cos(kapa) - 1j * np.sin(phi) * np.sin(kapa)]])

        rotation_matrix_conj = rotation_matrix.T.conj()
        # rotate to principle state to of the fiber
        uux = rotation_matrix[0, 0] * ux + rotation_matrix[0, 1] * uy
        uuy = rotation_matrix[1, 0] * ux + rotation_matrix[1, 1] * uy

        # betat = -1/2*beta2*omeg**2
        disp = betat * step_length
        #
        linear_operator_xpol = (0.5 * db1 + disp) * 1j
        linear_operator_ypol = (disp - 0.5 * db1) * 1j
        # linear_operator_xpol = disp * 1j
        # linear_operator_ypol = disp * 1j

        uux = cp.exp(linear_operator_xpol) * uux
        uuy = cp.exp(linear_operator_ypol) * uuy

        ux = rotation_matrix_conj[0, 0] * uux + rotation_matrix_conj[0, 1] * uuy
        uy = rotation_matrix_conj[1, 0] * uux + rotation_matrix_conj[1, 1] * uuy

        ux = cp.ifft(ux)
        uy = cp.ifft(uy)

        return ux, uy

    def __vector_nonlinear_step(self, ux, uy, gamma_mankorv, step_length):
        '''

        :param ux: samples of x-pol
        :param uy: samples of y-pol
        :param gamma_mankorv: 8/9*gamma，represent average over 那个啥球上
        :return: samples after nonlinear propagation
        '''
        leff = self.leff(step_length)
        power = cp.abs(ux) ** 2 + cp.abs(uy) ** 2
        gamma_mankorv = gamma_mankorv * leff
        ux = ux * cp.exp(1j * gamma_mankorv * power)
        uy = uy * cp.exp(1j * gamma_mankorv * power)
        return ux, uy

    def __str__(self):
        string = super().__str__()
        string = f'{string}\n' \
            f'step length for split fourier method is {self.step_length}'

        return string

    def __repr__(self):
        return self.__str__()


if __name__ == "__main__":
    pass
