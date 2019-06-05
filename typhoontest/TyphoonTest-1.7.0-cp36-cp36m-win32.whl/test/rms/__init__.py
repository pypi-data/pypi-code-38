from . import impl as _impl


def window_rms(signal, window_length=None, max_frequency=1000):
    '''Calculates RMS value of the signal using sliding window technique.

    Parameters
    ----------
    signal : Series
        A Pandas Series with the signal the RMS value is to be calculated.
    window_length : float/int or Timedelta
        Duration in seconds (if float/int) of the window used in the calculation. Defaults to None, in which case the period of the strongest frequency found on the signal will be used for window period.
    max_frequency : float/int or Timedelta
        Maximum frequency to be considered then finding automatically the storngest frequency for the signal. Default: 1000

    Returns
    -------
    rms : Series
        Time series with the same length as signal with the calculated RMS value.

    Examples
    --------
    >>> from typhoon.test.signals import assert_is_constant, pandas_sine
    >>> from typhoon.test.rms import window_rms
    >>> from typhoon.test.ranges import around, after
    >>> from typhoon.types.timedelta import Timedelta as td
    >>> from numpy import sqrt

    >>> sine = pandas_sine(amplitude=220*sqrt(2), frequency=60)
    >>> period = td(1/60)
    >>> rms = window_rms(sine, period)
    >>> assert_is_constant(rms, at_value=around(220, tol_p=0.01), strictness=1, during=after(period))
    '''
    return _impl.window_rms(signal, window_length, max_frequency)
