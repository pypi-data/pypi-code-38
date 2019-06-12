# Copyright (c) 2018, Michael Boyle
# See LICENSE file for details: <https://github.com/moble/scri/blob/master/LICENSE>

from __future__ import print_function, division, absolute_import
import warnings
import numpy as np
import quaternion
import spherical_functions as sf
from scipy.interpolate import splev, splrep, InterpolatedUnivariateSpline, interp1d
import scipy.interpolate as interpolate

from . import Inertial, h
from .waveform_base import WaveformBase, waveform_alterations


class DiscreteSamplingMixin(object):
    @property
    def vartheta(self):
        return self._vartheta

    @vartheta.setter
    def vartheta(self, new_vartheta):
        raise AttributeError("Can't change vartheta.  This can only be done at initialization.")

    @property
    def varphi(self):
        return self._varphi

    @varphi.setter
    def varphi(self, new_varphi):
        raise AttributeError("Can't change varphi.  This can only be done at initialization.")

    @property
    def dt(self):
        return self._dt

    @dt.setter
    def dt(self, new_dt):
        raise AttributeError("Can't change dt.  This can only be done at initialization.")

    @property
    def sampling_frequency(self):
        return 1.0 / self.dt

    @sampling_frequency.setter
    def sampling_frequency(self, new_df):
        raise AttributeError("Can't change sampling_frequency.  This is a computed value.")

    @property
    def nyquist_frequency(self):
        return 0.5 / self.dt

    @nyquist_frequency.setter
    def nyquist_frequency(self, new_nf):
        raise AttributeError("Can't change nyquist_frequency.  This is a computed value.")


class WaveformInDetector(DiscreteSamplingMixin, WaveformBase):
    """Object containing the h+ and hx waveforms observed by a detector at a point

    Note that the data is stored as a complex quantity referred to as `h`, which represents `h+` - 1j*`hx`.  Note the
    minus sign.  The `hplus` and `hcross` components are given as properties of this object, which return the real
    part and negative imaginary part, respectively.  This unfortunate sign is due to the fact that `h` is generally
    defined as an object of spin-weight s=-2.

    Also note that the data may not actually represent `h`; it may represent `Psi4` or any other spin-weighted
    quantity.

    Finally, while the data stored are complex, gravitational-wave detectors do not (yet) measure both polarizations.
    This becomes important when taking the Fourier transform; usually the real part should be taken before applying
    the transform, to agree with standard data-analysis formulas.  On the other hand, both parts are required when
    trying to find the optimal match, because optimizing over the phase requires Fourier transforms of both parts.

    """

    def __init__(self, *args, **kwargs):
        """Initializer for WaveformInDetector object

        This is not a convenient function for constructing these objects.  See `WaveformInDetector.from_modes` for a
        more useful function.

        """
        self._vartheta = float(kwargs.pop('vartheta', 0.0))
        self._varphi = float(kwargs.pop('varphi', 0.0))
        self._dt = float(kwargs.pop('dt', 1./4096.))
        super(WaveformInDetector, self).__init__(*args, **kwargs)

    @classmethod
    def from_modes(cls, modes, vartheta=0.0, varphi=0.0, dt=1./4096., **kwargs):
        """Initializer for WaveformInDetector object given WaveformModes object

        Parameters
        ----------
        modes: WaveformModes object
            This is the object to be evaluated
        vartheta: float, defaults to 0.0
            Polar angle giving position of detector relative to the inertial frame of `modes`
        varphi: float, defaults to 0.0
            Azimuthal angle giving position of detector relative to the inertial frame of `modes`
        dt: float, defaults to 1/4096.
            This is the sampling time step (inverse sampling frequency) of the detector in seconds.  LIGO's sampling
            frequency is always a multiple of 1024 Hz.  Advanced LIGO acquires data at 16384 Hz, but downsamples for
            most purposes.  Also note that the Nyquist frequency (maximum unambiguous frequency) is half the sampling
            frequency.

        Optional keyword parameters
        ---------------------------
        sYlm_threshold: float, defaults to 1e-14
            If the value of the sYlm is below this threshold, the mode will not contribute to the result.  If the frame
            is different at each time step, the sYlm values must *all* be below this threshold.
        detector_response: complex, defaults to 1+0j
            The amplitude of this quantity multiplies the amplitude of the input, and the phase multiplies the phase.
            This quantity is usually denoted F = F+ + i * Fx, and is very closely related to the antenna pattern.

        """

        if modes.m_is_scaled_out or modes.r_is_scaled_out:
            raise ValueError("The input `modes` object has `m_is_scaled_out`={0}".format(modes.m_is_scaled_out)
                             + " and `r_is_scaled_out`={0}".format(modes.r_is_scaled_out)
                             + "\nDid you forget to transform to physical units with `modes.SI_units`?")

        n_steps = int((modes.t[-1]-modes.t[0])/dt)
        t = modes.t[0]+dt*np.arange(n_steps)
        data = np.zeros((n_steps,), dtype=np.complex)
        sYlm_threshold = float(kwargs.pop('sYlm_threshold', 1.0e-14))
        F = complex(kwargs.pop('detector_response', 1+0j))

        # Calling the interpolating functions too frequently will slow things down tremendously, because python is slow,
        # though they are fundamentally fortran routines.  So we can't call for each time step.  On the other hand,
        # interpolating all modes at each time step results in too much data -- typically 77 times as much as the result
        # of this function will be.  So it seems like the best option is to interpolate each mode separately, and add to
        # the result as we go.

        # Get a new look at that data, for easier interpolation
        mode_data = modes.data_2d.view(dtype=float)

        # Interpolate the frame to the given time steps
        if modes.frame.size == 0:
            frame = np.array([quaternion.one])
        elif modes.frame.size == 1:
            frame = np.copy(modes.frame)
        else:
            frame = quaternion.squad(modes.frame, modes.t, t)

        # Now get the rotor to be used in evaluating the SWSH [see Eq. (B4c) of arxiv:1409.4431]
        R = (~frame) * quaternion.from_spherical_coords(vartheta, varphi)

        # Loop over modes
        for i_m in range(modes.n_modes):
            # Calculate SWSH modes
            sYlm = F * sf.SWSH(R, modes.spin_weight, modes.LM[i_m])

            if np.max(np.abs(sYlm)) < sYlm_threshold:
                continue
            else:
                # Interpolate the modes to the needed time steps
                interpolated_mode = (InterpolatedUnivariateSpline(modes.t, mode_data[:, 2*i_m])(t)
                                     + 1j*InterpolatedUnivariateSpline(modes.t, mode_data[:, 2*i_m+1])(t))
                # Multiply by SWSH modes and add to data
                data += sYlm * interpolated_mode

        w = cls(vartheta=vartheta, varphi=varphi, dt=dt,
                t=t, frame=np.empty((0,), dtype=np.quaternion), data=data,
                history=modes.history+[''],
                frameType=Inertial, dataType=modes.dataType,
                r_is_scaled_out=False, m_is_scaled_out=False,
                constructor_statement=('WaveformInDetector.from_modes'
                    + '({0}, vartheta={1}, varphi={2}, dt={3}, '.format(modes, vartheta, varphi, dt)
                    + 'sYlm_threshold={0}, detector_response={1}'.format(sYlm_threshold, F)
                    + ', '.join(['{0}={1}'.format(key, val) for key, val in kwargs.items()]) + ')'))
        return w

    @property
    def h_plus(self):
        return self.data.real

    @property
    def h_cross(self):
        return -self.data.imag

    @waveform_alterations
    def ensure_validity(self, alter=True, assertions=False):
        """Try to ensure that the `WaveformInDetector` object is valid

        See `WaveformBase.ensure_validity` for the basic tests.  This function also includes a test that `t` and `dt`
        are consistent.

        """
        import numbers

        errors = []
        alterations = []

        if assertions:
            from .waveform_base import test_with_assertions
            test = test_with_assertions
        else:
            from .waveform_base import test_without_assertions
            test = test_without_assertions

        test(errors,
             np.allclose(self.t, self.t[0]+self.dt*np.arange(0, self.n_times), atol=1e-15, rtol=1e-15),
             'np.allclose(self.t, self.t[0]+self.dt*np.arange(0, self.n_times), atol=1e-15, rtol=1e-15) '
             + '\n# t[0]={0}, dt={1}, n_times={2}'.format(self.t[0], self.dt, self.n_times)
             + '\n# t={0}'.format(self.t)
        )
        test(errors,
             self.data.ndim == 1,
             'self.data.ndim == 1 # self.data.ndim={0}'.format(self.data.ndim))

        # Call the base class's version
        super(WaveformInDetector, self).ensure_validity(alter, assertions)

        self.__history_depth__ -= 1
        self._append_history('WaveformInDetector.ensure_validity' +
                             '({0}, alter={1}, assertions={2})'.format(self, alter, assertions))

        return True

    @waveform_alterations
    def copy_without_data(self):
        W = super(WaveformInDetector, self).copy_without_data()
        W._vartheta, W._varphi = self.vartheta, self.varphi
        W._dt = self.dt
        W.__history_depth__ -= 1
        W._append_history('{0} = {1}.copy_without_data()'.format(W, self))
        return W

    def __repr__(self):
        # "The goal of __str__ is to be readable; the goal of __repr__ is to be unambiguous." --- stackoverflow
        rep = super(WaveformInDetector, self).__repr__()
        rep += "\n# vartheta={0}, varphi={1}, dt={2}".format(self.vartheta, self.varphi, self.dt)
        return rep
