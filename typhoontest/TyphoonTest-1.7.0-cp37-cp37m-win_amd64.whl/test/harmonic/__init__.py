"""This package contains functions for frequency-domain operations and transformations."""
from . import impl as _impl
from .impl import FFTResult


def thd(signal, fundamental, max_harmonic, during=None):
    """Calculates signal THD

    Parameters
    ----------
    signal : Series
        A Pandas Series with the signal the THD value is to be calculated.
    fundamental : int
        Fundamental frequency of the signal
    max_harmonic : int
        Maximum harmonic (with respect to fundamental) to be taken into consideration in the calculation.
    during : 2-element tuple of float/int or Timedelta
        Period of signal to consider for the calculation.

    Returns
    -------
    thd : float
        Calculated THD value.

    Examples
    --------
    >>> import typhoon.test.signals as signals
    >>> import typhoon.test.harmonic as harmonic

    >>> serie = signals.pandas_sine(1, 60, 1, 1e-6)
    >>> serie += signals.pandas_sine(0.5, 120, 1, 1e-6)

    >>> thd = harmonic.thd(serie, 60, 10)
    """
    return _impl.thd(signal, fundamental, max_harmonic, during)


def frequency_content(signal, max_frequency, during=None):
    """Calculates the list of harmonic components for a signal using FFT.

    Parameters
    ----------
    signal : Series
        A Pandas Series with the signal the harmonic components are to be calculated.
    max_frequency : int
        Maximum frequency to be taken into consideration in the results.
    during : 2-element tuple of float/int or Timedelta
        Period of signal to consider for the calculation.

    Returns
    -------
    result : FFTResult
        Result of the frequency analysis.

    Examples
    --------
    >>> import typhoon.test.signals as signals
    >>> import typhoon.test.harmonic as harmonic

    >>> serie = signals.pandas_sine(amplitude=100, frequency=60) # zeroed signal
    >>> serie += signals.pandas_sine(amplitude=10, frequency=120)
    >>> serie += signals.pandas_sine(amplitude=2, frequency=180)
    >>> content = harmonic.frequency_content(serie, 200)

    >>> plot(content.freqs, content.fft)
    >>> content(60)
    >>> content(10)
    >>> content(2)
    """
    return _impl.frequency_content(signal, max_frequency, during)

def signal_frequency_zc(signal, during=None, mode="half-cycle"):
    """Calculates frequency of the  signal.

    Measures time between neighboring zero-crossing moments. This method is suitable for sine, square or triangle
    signals. Returns pandas Series with the same length as signal. Frequency in the non-zero crossing moments is
    obtained by zero-order hold.

    Parameters
    ----------
    signal: Series
        A Pandas Series containing signal which frequency need to be calculated
    during : 2-element tuple of float/int or Timedelta
        Period of signal to consider for the calculation.
    mode: string
        String that activates one of two possible modes: for "half-cycle" every zero-crossing is detected, while for
        "full-cycle" every second zero-crossing is detected

    Returns
    -------
    result: pandas.Series
        Series with the calculated frequency values.

    Examples
    --------

    >>> import typhoon.test.signals as signals
    >>> import typhoon.test.harmonic as harmonic
    >>> # sine signal which lasts for one second, sampled 10000 times
    >>> series = signals.pandas_sine(amplitude=10, frequency=50, Ts=1e-4, duration=1)
    >>> frequency = harmonic.signal_frequency_zc(serie)
    returns the Series of the measured frequency(50). The length of the Series is 10000.
    """
    return _impl.signal_frequency_zc(signal, during, mode)