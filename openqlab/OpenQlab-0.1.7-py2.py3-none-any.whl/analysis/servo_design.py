""":obj:`OpenQlab.ServoDesign` helps with designing a standard servo circuit."""
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from scipy import signal
from tabulate import tabulate
from ..conversion import db
from .. import plots
from ..io import DataContainer
from ..conversion.utils import human_readable

# TODO update documentation in servodesign.rst`


class Filter(ABC):
    """
    A container for a second-order analog filter section. Poles and zeros are in units of Hz.

    Parameters
    ----------
    description: :obj:`str`
        A short description of this filter section
    z: :obj:`array-like`
        A zero or list of zeros
    p: :obj:`array-like`
        A pole or list of poles
    k: :obj:`float`
        Gain
    """

    def __init__(self, enabled=True):
        self._enabled = enabled
        self.update()

    def update(self):
        z, p, k = self.calculate()
        self._zeros = np.atleast_1d(z)
        self._poles = np.atleast_1d(p)
        self._gain = k
        if len(self._zeros) > 2 or len(self._poles) > 2:
            raise Exception('Filters of higher than second order are not supported.')

    @abstractmethod
    def calculate(self):
        """
        Calculate must be implemented by the specific filter class.

        It should recalculate the zpk and return it.

        Returns
        -------
        :code:`z, p, k`
        """
        pass

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, state):
        if type(state) != bool:
            raise TypeError('State has to be a boolean value.')
        self._enabled = state
        self.update()

    @property
    def cF(self):
        return self._cF

    @cF.setter
    def cF(self, value):
        self._cF = value
        self.update()

    @property
    def second_parameter(self):
        return self._second_parameter

    @second_parameter.setter
    def second_parameter(self, value):
        self._second_parameter = value
        self.update()

    @property
    @abstractmethod
    def description(self):
        pass

    @property
    def description_long(self):
        # what is this for?
        return self.description

    @property
    def zeros(self):
        return self._zeros

    @property
    def poles(self):
        return self._poles

    @property
    def gain(self):
        return self._gain

    def discrete_SOS(self, fs):
        """
        Return a discrete-time second order section of this filter, with sampling
        frequency `fs`.
        """
        return signal.zpk2sos(*self.discrete_zpk(fs))

    def discrete_zpk(self, fs):
        """
        Return the discrete-time transfer function of this filter, evaluated
        for a sampling frequency of `fs`.
        """
        z, p, k = self._prewarp(fs)
        return signal.bilinear_zpk(z, p, k, fs)

    def _prewarp(self, fs):
        """
        Prewarp frequencies of poles and zeros, to correct for the nonlinear
        mapping of frequencies between continuous-time and discrete-time domain.

        Parameters
        ----------
        fs: :obj:`float`
            the sampling frequency

        Returns
        -------
        z: :obj:`numpy.ndarray`
            prewarped zeroes
        p: :obj:`numpy.ndarray`
            prewarped poles
        """
        warp = lambda x: 2 * fs * x / abs(x) * np.tan(abs(x / fs) * np.pi)
        # since we're calculating in Hz, we need to scale the gain as well
        # by 2pi for each pole and 1/2pi for each zero
        gain = self._gain * (2 * np.pi) ** self._relative_degree()
        return warp(self._zeros), warp(self._poles), gain

    def _relative_degree(self):
        return len(self._poles) - len(self._zeros)

    def _repr_pretty_(self, p, cycle):
        p.text(tabulate([['zeros', 'poles', 'gain'],
                         [self.description, self.zeros, self.poles, self.gain]],
                        headers='firstrow'))



class Integrator(Filter):
    """
    Create an integrator with corner frequency 'cF', compensated for unity gain at high frequencies.

    Parameters
    ----------
    cF: :obj:`float`
        The corner frequency.
    sF: :obj:`float`, optional
        Frequency were the ~1/f slope starts, defaults to 0.001 * `cF`.
    """

    def __init__(self, cF, sF=None, enabled=True):
        #self._description_long = 'The Integrator filter takes a corner frequency and an optional ~1/f slope frequency.'
        self._cF = cF
        self._second_parameter = sF
        super().__init__(enabled)

    def calculate(self):
        z = -self.cF
        if self.sF is None:
            self._second_parameter = self.cF * 0.001
        p = -self.sF
        k = 1.0  # Gain = 1
        return z, p, k

    @property
    def description(self):
        return 'Int {0}'.format(human_readable(self.cF, 'Hz'))

    @property
    def sF(self):
        return self.second_parameter

    @sF.setter
    def sF(self, value):
        self.second_parameter = value


class Differentiator(Filter):
    """
    Create a differentiator with corner frequency `cF`, compensated for unity gain at low frequencies.

    Parameters
    ----------
    cF: :obj:`float`
        The corner frequency.
    sF: :obj:`float`, optional
        Frequency were the ~f slope stops, defaults to 1000 * `cF`.

    """

    def __init__(self, cF, sF=None, enabled=True):
        self._cF = cF
        self._second_parameter = sF
        super().__init__(enabled)

    def calculate(self):
        z = -self.cF
        if self.sF is None:
            self._second_parameter = self.cF * 1000
        p = -self.sF
        k = self.sF / self.cF
        return z, p, k

    @property
    def description(self):
        return 'Diff {0}'.format(human_readable(self.cF, 'Hz'))

    @property
    def sF(self):
        return self.second_parameter

    @sF.setter
    def sF(self, value):
        self.second_parameter = value


class Lowpass(Filter):
    """
    Create a 2nd-order lowpass filter with variable quality factor `Q`.

    The default `Q` of ``1/sqrt(2)`` results in a Butterworth filter with flat passband.

    Parameters
    ----------
    cF: :obj:`float`
        The corner frequency.

    """

    def __init__(self, cF, Q=0.707, enabled=True):
        self._cF = cF
        self._second_parameter = Q

        super().__init__(enabled)

    def calculate(self):
        z = []
        cF = self.cF
        Q = self.Q
        p = [-cF / (2 * Q) + ((cF / (2 * Q)) ** 2 - cF ** 2) ** 0.5,
             -cF / (2 * Q) - ((cF / (2 * Q)) ** 2 - cF ** 2) ** 0.5]
        k = cF * cF

        return z, p, k

    @property
    def description(self):
        return 'LP2 {0}, Q={1:.4g}'.format(human_readable(self.cF, 'Hz'), self.Q)

    @property
    def Q(self):
        return self.second_parameter

    @Q.setter
    def Q(self, value):
        self.second_parameter = value


class Notch(Filter):
    """
    Create a notch filter at frequency `cF` with a quality factor `Q`, where the -3dB filter bandwidth ``bw`` is given by ``Q = cF/bw``.

    Parameters
    ----------
    cF: :obj:`float`
        Frequency to remove from the spectrum
    Q: :obj:`float`
        Quality factor of the notch filter. Defaults to 1.
    """

    def __init__(self, cF, Q=1, enabled=True):
        self._cF = cF
        self._second_parameter = Q

        super().__init__(enabled)

    def calculate(self):
        cF = self.cF
        Q = self.Q
        z = [cF * 1j, -cF * 1j]
        p = [-cF / (2 * Q) + ((cF / (2 * Q)) ** 2 - cF ** 2) ** 0.5,
             -cF / (2 * Q) - ((cF / (2 * Q)) ** 2 - cF ** 2) ** 0.5]
        k = 1
        return z, p, k

    @property
    def description(self):
        return 'Notch {0}, Q={1:.4g}'.format(human_readable(self.cF, 'Hz'), self.Q)

    @property
    def Q(self):
        return self.second_parameter

    @Q.setter
    def Q(self, value):
        self.second_parameter = value


class ServoDesign:
    """
    A Servo (controller) design class.

    Current purpose is mainly filter handling and should be used as follows:

    The object itself holds a set of (currently maximum) 5 filters. Filter types can be defined as new subclasses to the Filter class.

    The FILTER UTILITY section contains all methods handling filter operations, including clear and read. Filters should be added using either 'add' or 'addIndexed'. Normal 'add' will simply append the filter to the list and fail when the list is fullself. 'addIndexed' however will overwrite the the filter at the current position and fail in case an index out of range was specified.
    """

    MAX_FILTERS = 5
    SAMPLING_RATE = 200e3  # ADwin usually runs with 200 kHz

    def __init__(self):
        self._plant = None
        self.clear()

    ####################################
    # FILTER UTILITY
    ####################################

    @property
    def filters(self):
        """
        Return the global class field filterListself.

        Returns
        -------
        filterList: list
            The global field containing a list of available filters.
        """
        return self._filters

    def clear(self):
        self._filters = []
        self.gain = 1.0

    def _get_first_none_entry(self):
        for i in range(len(self.filters)):
            if self.filters[i] is None:
                return i

    def _add_filter_on_index(self, filter, index):
        if index >= self.MAX_FILTERS:
            raise IndexError('Max {0} filters are allowed.'.format(self.MAX_FILTERS))
        # Fill up the list with none filters if necessary
        while index > len(self._filters) - 1:
            self._filters.append(None)
        self._filters[index] = filter

    def add(self, filter, index=None):
        """
        Add a filter to the servo. Up to {0} filters can be added.

        Parameters
        ----------
        filter: :obj:`Filter`
            the Filter object to be added
        """.format(self.MAX_FILTERS)
        if len(self) >= self.MAX_FILTERS and index is None:
            raise Exception('Cannot add more than {0} filters to servo.'.format(self.MAX_FILTERS))

        if not isinstance(filter, Filter):
            raise TypeError('filter must be a Filter() object')

        if index is None:
            index = self._get_first_none_entry()

        if index is None:
            self._filters.append(filter)
        else:
            self._add_filter_on_index(filter, index)

    def get(self, index):
        """
        Return the filter at given index, None if no filter at position.

        Parameters
        ----------
        index: Integer
            index to look for Filter at. Min 0, max {}.
        Returns
        -------
        :obj:'Filter'
        """.format(self.MAX_FILTERS - 1)
        if not (0 <= index <= self.MAX_FILTERS - 1):
            raise IndexError('Filter index must be between 0 and {}.'.format(
            self.MAX_FILTERS - 1))
        if index >= len(self._filters):
            return None
        else:
            return self._filters[index]

    def remove(self, index):
        """
        Remove a filter from the servo. Effectively sets the slot at the given index to None, if it has been set before.

        Parameters
        ----------
        index: Integer
            the Integer specifying the filters index. Min 0, max {}.
        """.format(self.MAX_FILTERS - 1)
        if not (0 <= index <= self.MAX_FILTERS - 1):
            raise IndexError('Filter index must be between 0 and {}.'.format(
            self.MAX_FILTERS - 1))
        # only set a filter to None if array is already specified at index
        if index < len(self._filters):
            self._filters[index] = None

    def __len__(self):
        """
        Length of real filters in this ServoDesign.

        If some filter places are `None` they are not counted for this length.
        To get the length of the whole list, use `len(ServoDesign.filters)`.

        Returns
        -------
        :obj:`int`
            Number of filters.
        """
        len = 0
        for f in self._filters:
            if f is not None:
                len += 1
        return len

    ####################################
    # Add Filters the old way
    ####################################

    def integrator(self, fc, fstop=None, enabled=True):
        """
        Add an integrator with corner frequency `fc`, compensated for unity gain at high frequencies.

        Parameters
        ----------
        fc: :obj:`float`
            The corner frequency.
        fstop: :obj:`float`, optional
            Frequency were the ~1/f slope starts, defaults to 0.001 * `fc`.
        """
        self.add(Integrator(fc, fstop, enabled))

    def differentiator(self, fc, fstop=None, enabled=True):
        """
        Add a differentiator with corner frequency `fc`, compensated for unity gain at low frequencies.

        Parameters
        ----------
        fc: :obj:`float`
            The corner frequency.
        fstop: :obj:`float`, optional
            Frequency were the ~f slope stops, defaults to 1000 * `fc`.
        """
        self.add(Differentiator(fc, fstop, enabled))

    def lowpass(self, fc, Q=0.707, enabled=True):
        """
        Add a 2nd-order lowpass filter with variable quality factor `Q`.

        The default `Q` of ``1/sqrt(2)`` results in a Butterworth filter with flat passband.

        Parameters
        ----------
        parameter: :obj:`type`
            parameter description
        """
        self.add(Lowpass(fc, Q, enabled))

    def notch(self, fc, Q=1, enabled=True):
        """
        Add a notch filter at frequency `fc` with a quality factor `Q`, where the -3dB filter bandwidth ``bw`` is given by ``Q = fc/bw``.

        Parameters
        ----------
        fc: :obj:`float`
            Frequency to remove from the spectrum
        Q: :obj:`float`
            Quality factor of the notch filter

        Returns
        -------
        :obj:`Servo`
            the servo object with added notch filter
        """
        self.add(Notch(fc, Q, enabled))

    ####################################
    # CLASS UTILITY
    ####################################

    def log_gain(self, gain):
        """
        Add gain specified in dB (amplitude scale, i.e. 6dB is a factor of 2).

        Parameters
        ----------
        gain: :obj:`float`
            Gain that should be added
        """
        self.gain *= db.to_lin(gain / 2)

    def zpk(self):
        """
        Return combined zeros, poles and gain for all filters.

        Returns
        -------
        zeros: :obj:`numpy.ndarray`
            The zeros of the combined servo
        poles: :obj:`numpy.ndarray`
            The poles of the combined servo
        gain: :obj:`float`
            Gain of the combined servo
        """
        filters = [f for f in self._filters if (f is not None) and f.enabled]
        if filters:
            zeros = np.concatenate([f.zeros for f in filters])
            poles = np.concatenate([f.poles for f in filters])
        else:
            zeros = np.array([])
            poles = np.array([])
        gain = self.gain
        for f in filters:
            gain *= f.gain
        return zeros, poles, gain

    @property
    def plant(self):
        """
        Set the system that the servo should control (usually called the plant),
        which needs to be given as a :obj:`pandas.DataFrame` containing two
        columns with amplitude and phase frequency response. The index is
        assumed to contain the frequencies.
        """
        return self._plant

    @plant.setter
    def plant(self, value):
        if value is None:
            self._plant = None
            return
        if not isinstance(value, pd.DataFrame):
            raise TypeError('Plant must be a pandas DataFrame object')
        if not value.shape[1] >= 2:
            raise Exception('At least two columns (amplitude, phase) required')

        value = self._handle_keysight_files(value)

        self._plant = value

    def _handle_keysight_files(self, df):
        value = df.copy()
        # Extra handling for Keysight files
        columns = ['Amplitude (Vpp)', 'Gain (dB)', 'Phase (deg)']
        if value.index.name == 'Frequency (Hz)' and value.columns.tolist() == columns:
            del value['Amplitude (Vpp)']
        return value

    def _apply(self, freq, ampl=None, phase=None):
        x, a, p = signal.bode(self.zpk(), freq)

        df = pd.DataFrame(data=np.column_stack((a, p)), index=freq,
                          columns=['Servo A', 'Servo P'])
        df.index.name = 'Frequency (Hz)'
        if ampl is not None:
            df['Servo+TF A'] = ampl + a
        if phase is not None:
            df['Servo+TF P'] = phase + p
        return df

    def plot(self, freq=None, plot=True, correct_latency=False):
        """
        Plot the servo response over the frequencies given in `freq`.

        If a plant was set for this servo, then `freq` is ignored and the
        frequency list from the plant is used instead. If both plant and freq are None,
        a list is created from [0,...,10]kHz using numpy.logspace.

        Parameters
        ----------
        freq: :obj:`numpy.ndarray`
            frequencies for plotting calculation.
            Default is 1 to 1e5, with 1000 steps.
        plot: :obj:`bool`
            returns a DataFrame if `False`.
            Defaults to `True`
        correct_latency: :obj:`bool` or :obj`float`
            If the data has been taken piping through ADwin an extra phase has been added.
            This can be corrected by giving ADwins sample rate (Default 200 kHz).

        Returns
        -------
        :obj:`matplotlib.figure.Figure` or :obj:`pandas.DataFrame`
            Retuns a DataFrame or a plot
        """
        if self.plant is None and freq is None:
            freq = np.logspace(0, 5, num=1000)

        if self.plant is None:
            df = self._apply(freq)
            dfA = df['Servo A']
            dfP = df['Servo P']
        else:
            df = self._apply(self.plant.index,
                             self.plant.iloc[:, 0], self.plant.iloc[:, 1])
            # Correct latency for the plant
            if correct_latency:
                if isinstance(correct_latency, bool):
                    correct_latency = self.SAMPLING_RATE
                print(type(correct_latency))
                df['Servo+TF P'] = df['Servo+TF P'] + 360 * df.index / correct_latency
            dfA = df[['Servo A', 'Servo+TF A']]
            dfP = df[['Servo P', 'Servo+TF P']]

        if not plot:
            return df

        # Plotting

        plt = plots.amplitude_phase(dfA, dfP)
        # add 0dB and -135deg markers
        plt.axes[0].hlines(0, *plt.axes[0].get_xlim(),
                           colors=(0.6, 0.6, 0.6), linestyles='dashed')
        plt.axes[1].hlines(-135, *plt.axes[1].get_xlim(),
                           colors=(0.6, 0.6, 0.6), linestyles='dashed')
        return plt

    def discrete_form(self, fs=SAMPLING_RATE, filename=None):
        """
        Convert the servo and its filters to a digital, discrete-time representation in terms of second-order sections at a sampling frequency of `fs`.

        If `filename` is given, write the filter coefficients in
        machine-readable format into this file.

        .. todo:: this should probably return a usable form of this filter for
                  plotting the discrete-time response (using signal.dbode)

        Returns
        -------
        :obj:`dict`
            a dictionary containing sample rate, gain and SOS coefficients for
            each filter
        """
        coeffs = []
        for f in self._filters:
            if f is not None:
                coeffs.append(f.discrete_SOS(fs).flatten())
        filters = {}
        for f, d in zip(self._filters, coeffs):
            if f is not None:
                filters[f.description] = d

        data = {
            'fs': fs,
            'gain': self.gain,
            'filters': filters
        }

        if filename:
            with open(filename, 'w') as fp:
                fp.write('Sampling rate: {0}\n'.format(data['fs']))
                fp.write('Gain: {0:.10g}\n'.format(data['gain']))
                for desc, c in data['filters'].items():
                    fp.write(
                        (
                                '{desc}: {c[0]:.10g} {c[1]:.10g} {c[2]:.10g} ' + '{c[3]:.10g} {c[4]:.10g} {c[5]:.10g}\n').format(
                            desc=desc, c=c)
                    )

        return data

    def _repr_pretty_(self, p, cycle):
        p.text(str(self))

    def __str__(self):
        data = []
        for f in self._filters:
            if f is not None:
                data.append([f.description, f.zeros, f.poles, f.gain])
        return tabulate([['zeros', 'poles', 'gain'], ['Gain', [], [], self.gain]] + data,
                        headers='firstrow')

    def __getstate__(self):
        state = self.__dict__.copy()
        plant = state['_plant']
        if isinstance(plant, pd.DataFrame):
            state['_plant'] = plant.to_json(orient='split')

        return state

    def __setstate__(self, state):
        if state['_plant'] is not None:
            state['_plant'] = DataContainer.from_json(state['_plant'], orient='split')
        self.__dict__ = state
