# -*- coding: utf-8 -*-
""" This package contains high-level functions to analyze desired characteristics from time series signals. """
from . import impl as _impl
from .impl import AnalysisResult


def assert_analysis(result, expectation):
    """
    Assertion helper for AnalysisResult objects, printing the result message in the AssertionError if raised.

    Is equivalent to

    >>> assert result == expectation, result.msg

    Parameters
    ----------
    result : AnalysisResult
        Result object from one of the analysis functions
    expectation : bool
        Desired result to assert (True or False)

    Raises
    ------
    AssertionError
        In case result is different from expectation.

    """
    return _impl.assert_analysis(result, expectation)


def find(signal, region, value, from_region=None, during=None, alias=None):
    """
    Like the function typhoon.test.signals.find_all, it finds the desired characteristic on the signal. The difference
    is that find function looks only for the first occurrence of described behaviour, while find_all function returns the
    list of all moments where that condition is met.

    Parameters
    ----------
    signal : pandas.Series
        Signal to be tested for.
    region : string
        Can be "at", "outside", "above" or "below". The option "outside" means "above" or "below".
    value : float or tuple
        Defines the region as a single number or range.
    from_region : string
        Defines which region the signal should be prior to the desired region. Use this to detect transitions.
    during : tuple
        Time period (as a range) to be considered for analysis.
    alias : string
        Custom alias for the returned time.

    Returns
    -------
    result : Timedelta
        Time of detected behavior

    Raises
    ------
    Exception
        If the desired characteristic could not be detected.

    Examples
    --------
    First moment when Power is inside the range. Detects even if signal already starts in the range.

    >>> t = find(capture["P"], region="at", value=(900,1000))

    Almost same as before but require the signal to be outside the range prior entering it. Detects the transition to the range from above or below

    >>> t = find(capture["P"], region="at", value=(900,1000), from_region="outside")

    Detecting a rising edge, when power goes above 1000

    >>> t = find(capture["P"], region="above", value=1000, from_region="below")

    See Also
    --------
    typhoon.test.signals.find_all
    typhoon.test.signals.find_edges
    typhoon.test.capture.wait_until

    """
    return _impl.find(signal, region, value, from_region, during, alias)

def find_all(signal, region, value, from_region=None, during=None, only_first_index=False):
    """
    Finds a desired characteristic on a signal.

    Parameters
    ----------
    signal : pandas.Series
        Signal to be tested for.
    region : string
        Can be "at", "outside", "above" or "below". The option "outside" means "above" or "below".
    value : float or tuple
        Defines the region as a single number or range.
    from_region : string
        Defines which region the signal should be prior to the desired region. Use this to detect transitions.
    during : tuple
        Time period (as a range) to be considered for analysis.
    only_first_index: bool
        If set to True, only Timedelta of the first occurence of the described behaviour is returned. Otherwise, every
        time the condition is met is returned in the list.

    Returns
    -------
    result : list of Timedelta
        All moments in which the signal meets described behaviour

    Examples
    --------
    Find all  rising edges of the sine signal with zero as threshold value

    >>> from typhoon.test.signals import pandas_sine, find_all
    >>> sine_sig = pandas_sine(frequency=50, duration=0.05, Ts=1e-6)
    >>> rising_edges = find_all(sine_sig, region="above", value=0, from_region="below")

    Find all  falling edges of the sine signal with zero as threshold value

    >>> from typhoon.test.signals import pandas_sine, find_all
    >>> sine_sig = pandas_sine(frequency=50, duration=0.05, Ts=1e-6)
    >>> falling_edges = find_all(sine_sig, region="below", value=0, from_region="above")

    Find all the moments when signal enters the specified region (with assumption that signal is already captured)
    
    >>> entering_moments = find_all(captured_sig, region=at, value=(900, 1000), from_region="outside")


    See Also
    --------
    typhoon.test.signals.find
    typhoon.test.signals.find_edges
    typhoon.test.capture.wait_until

    """
    return _impl.find_all(signal, region, value, from_region, during, only_first_index=False)


def find_edges(signal, value, rising=False, falling=False, during=None):
    """
    Find edges around a given value in a signal.

    Parameters
    ----------
    signal : pandas.Series
        Signal to be tested for.
    value : float
        Defines the value around which detect the edge crossings.
    rising : bool
        Detect rising edges in this signal.
    falling : bool
        Detect falling edges in this signal.
    during : tuple
        Time period (as a range) to be considered for analysis.

    Returns
    -------
    result : list of Timedelta
        Instants corresponding to the found edges in the signal.

    Notes
    -----
    At least one option considering ``falling`` or ``rising`` should be defined as ``True``.

    Examples
    --------
    Finding zero-crossings in a sine wave:

    >>> from typhoon.test.signals import pandas_sine
    >>> sig = pandas_sine(amplitude=10, frequency=50, duration=0.030)  # 30 ms = 1 and a half cycle
    >>> zero_crossings = find_edges(sig, value=0, rising=True, falling=True)
    >>> zero_crossings[0]
    10 ms
    >>> zero_crossings[1]
    20 ms

    See Also
    --------
    typhoon.test.signals.find
    typhoon.test.signals.find_all

    """
    return _impl.find_edges(signal, value, rising, falling, during)


def is_constant(signal, at_value, during=None, strictness=1):
    """
    Checks if signal is always inside defined range.

    Parameters
    ----------
    signal : pandas.Series
        Signal to be tested for.
    at_value : tuple/list or number
        Band inside with signal should always be. Can be passed as a tuple/list with two elements for a range, or as a single value for an exact value.
    during : tuple
        Time period (as a range) to be considered for analysis.
    strictness : float
        Number between 0.0 and 1.0 that determines percentage of time signal should be inside the defined range for test to pass.

    Returns
    -------
    result : AnalysisResult
        Result of the analysis.

    Examples
    --------
    >>> val = 220
    >>> tol = val * 0.01
    >>> result = is_constant(capture["Va_rms"], at_value=(val-tol, val+tol))
    >>> assert result == True, result.msg

    or

    >>> from typhoon.test.ranges import around
    >>> result = is_constant(capture["Va_rms"], at_value=around(val, tol_p=0.01))
    >>> assert result == True, result.msg

    A more compact and readable function is obteined using assertion helpers:

    >>> assert_is_constant(capture["Va_rms"], at_value=around(val, tol_p=0.01))

    See Also
    --------
    typhoon.test.signals.AnalysisResult
    typhoon.test.signals.assert_is_constant

    """
    return _impl.is_constant(signal, at_value, during, strictness)

def is_first_order(signal, time_constant, init_value, final_value, tol, during=None, strictness=1, time_tol=0):
    """
    Checks if signal represents first order response.

    Verifies that signal follows exponential equation defined with formula:
    x(t) = x(inf) + (x(0) - x(inf)) * exp(-t / tau)    (1)
    t represents the time axis of the signal.
    Parameters
    ----------
    signal: pandas.Series
        Signal to be tested for.
    time_constant: float
        Time constant of the signal; represents tau in formula (1).
    init_value: float
        Initial value of the signal; represents x(0) in formula (1)
    final_value: float
        Stationary state value of the signal; represents x(inf) in formula (1).
    tol: float
        Tolerance around which the signal can stay with respect to reference ramp when determining if result is True or
        False.
    during: 2-element tuple of numbers or Timedelta
        Time period (as a range) to be considered for analysis.
    strictness: float
        Number between 0.0 and 1.0 that determines percentage of time signal should be inside the defined range for
        test to pass.
    time_tol: float or timedelta
        Time tolerance - argument which allows that signal is leading or lagging up to specified time in seconds,
        compared to created reference.

    Returns
    -------
    result : AnalysisResult
        Result of the analysis.

    Examples
    ------
    >>> import typhoon.test.signals as signals
    >>> tau = 0.1
    >>> init = 0
    >>> fin = 10
    >>> exp_sig = signals.pandas_first_order(tau, init, fin) # first order response signal
    >>> assert signals.is_first_order(exp_sig, tau, init, fin, tol=0.01*fin)
    """
    return _impl.is_first_order(signal, time_constant, init_value,final_value, tol, during, strictness, time_tol)


def is_step(signal, from_value, to_value, at_t, during=None, strictness=1, find_start=True):
    """
    Checks if signal is a step with specified characteristics.

    Verifies if signal starts at a starting value (from_value), then leaves it towards a final value (to_value). The transition should take place during the time specified by the time range at_t.

    Parameters
    ----------
    signal : pandas.Series
        Signal to be tested for.
    from_value : 2-element tuple/list or value
        Band inside which signal should be initially. Can be passed as a tuple/list with two elements for a range, or as a single value for an exact value.
    to_value : 2-element tuple/list or value
        Band signal should reach. Can be passed as a tuple/list with two elements for a range, or as a single value for an exact value.
    at_t : 2-element tuple/list of float or Timedelta
        Time during which signal should step from one range to the other. Range defined as a 2-element tuple with numbers or timedeltas.
    during : 2-element tuple of numbers or Timedelta
        Time period (as a range, 2-element tuple) to be considered for analysis.

    Returns
    -------
    result : AnalysisResult
        Result of the analysis.

    Examples
    --------
    A step should happen at around 9 seconds

    >>> result = is_step(capture["enable"], from_value=1, to_value=0, at_t=around(9,tol=1)))
    >>> assert result == True, result.msg

    A more concise method is to use the assertion helper functions:

    >>> assert_is_step(capture["enable"], from_value=1, to_value=0, at_t=around(9,tol=1)))

    See Also
    --------
    typhoon.test.signals.AnalysisResult
    typhoon.test.signals.assert_is_step
    """
    return _impl.is_step(signal, from_value, to_value, at_t, during, strictness, find_start)


def is_ramp(signal, slope, tol, during=None, strictness=1, time_tol=0):
    """Checks if signal is a ramp with desired slope.

    Parameters
    ----------
    signal : pandas.Series
        Signal to be tested for.
    slope : float
        Ramp slope that signal should have, in units per second.
    tol : float
        Tolerance around which the signal can stay with respect to reference ramp when determining if result is True
        or False.
    during : tuple
        Time period (as a range) to be considered for analysis.
    strictness : float
        Number between 0.0 and 1.0 that determines percentage of time signal should be inside the defined range for
        test to pass.
    time_tol: float or timedelta
        Time tolerance - argument which allows that signal is leading or lagging up to specified time in seconds,
        compared to created reference.

    Returns
    -------
    result : AnalysisResult
        Result of the analysis.

    Examples
    --------
    Signal should have a slope of 1 unit per second considering simulation from t=2 to t=5, signal can vary inside range of ±0.5:

    >>> result = is_ramp(signal, slope=1, tol=0.5, during=(2,5))
    >>> assert result == True

    A more concise way of asserting is using the assertion helper functions:

    >>> assert_is_ramp(signal, slope=1, tol=0.5, during=(2,5))

    See Also
    --------
    typhoon.test.signals.AnalysisResult
    typhoon.test.signals.assert_is_ramp
    """
    return _impl.is_ramp(signal, slope, tol, during, strictness, time_tol)


def follows_reference(signal, ref_signal, tol, during=None, strictness=1, time_tol=0):
    """Checks if signal follows a reference signal within given tolerances.

    Parameters
    ----------
    signal : pandas.Series
        Signal to be tested for.
    ref_signal : pandas.Series
        Reference signal the tested signal should follow.
    tol : float
        Tolerance around which the signal can stay with respect to reference signal when determining if analyis result
        is ``True`` or ``False``.
    during : tuple
        Time period (as a range) to be considered for analysis.
    strictness : float
        Number between 0.0 and 1.0 that determines percentage of time signal should be inside the defined range for
        test to pass.
    time_tol: float or timedelta
        Time tolerance - argument which allows that signal is leading or lagging up to specified time in seconds,
        compared to created reference.

    Returns
    -------
    result : AnalysisResult
        Result of the analysis.

    Notes
    -----
    The reference signal needs not to be on the same sampling rate of the signal to be compared, as they will be
    normalized in a single dataframe using pandas' `interpolate
    <https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.interpolate.html>` function.

    Examples
    --------
    Implementation of is_constant function, comparing if signal is always around 10 ±0.5

    >>> t0 = signal.index[0]
    >>> tf = signal.index[-1]
    >>> v0 = sum(at_value)/len(at_value)
    >>> tol = abs(at_value[0]-v0)

    >>> ref_ramp = pd.Series({t0:v0,tf:v0})
    >>> result = follows_reference(signal, ref_ramp, tol, strictness, result)

    Implementation of is_ramp function with slope of 1 unit per second:

    >>> t0 = signal.index[0]
    >>> v0 = signal.values[0]
    >>> tf = signal.index[-1]
    >>> dt = tf - t0
    >>> dtbase = td("1s")
    >>> # equivalent to dt * (slope/dtbase) e.g. slope with 100 units per microsecond y = 10 + (1us * 100/1us) = 110
    >>> vf = v0 + (dt/dtbase)*slope
    >>> # Build signal with two points, providing ramp
    >>> ref_ramp = pd.Series({t0:v0,tf:vf})
    >>> result = follows_reference(capture['P'], ref_ramp, tol=0.5)

    See Also
    --------
    typhoon.test.signals.AnalysisResult
    typhoon.test.signals.assert_follows_reference
    """
    return _impl.follows_reference(signal, ref_signal, tol, during, strictness, time_tol)


def assert_is_step(signal, from_value, to_value, at_t, during=None, strictness=1, find_start=True):
    """
    Assertion helper for ``is_step`` function. Has the same signature.

    Is equivalent to:

    >>> result = is_step(*args, **kwargs)
    >>> assert_analysis(result, True)

    Raises
    ------
    AssertionError
        In case result is different from ``True``.

    See Also
    --------
    typhoon.test.signals.is_step
    """
    return _impl.assert_is_step(signal, from_value, to_value, at_t, during, strictness, find_start)


def assert_is_constant(signal, at_value, during=None, strictness=1):
    """
    Assertion helper for ``is_constant`` function. It has the same signature.

    Is equivalent to:

    >>> result = is_constant(*args, **kwargs)
    >>> assert_analysis(result, True)

    Raises
    ------
    AssertionError
        In case result is different from ``True``.

    See Also
    --------
    typhoon.test.signals.is_constant
    """
    return _impl.assert_is_constant(signal, at_value, during, strictness)

def assert_is_first_order(signal, time_constant, init_value, final_value, tol, during=None, strictness=1, time_tol=0):
    """
    Assertion helper for ``is_first_order`` function. It has the same signature.

    Is equivalent to:

    >>> result = is_first_order(*args, **kwargs)
    >>> assert_analysis(result, True)

    Raises
    ------
    AssertionError
        In case result is different from ``True``.

    See Also
    --------
    typhoon.test.signals.is_first_order
    """
    return _impl.assert_is_first_order(signal, time_constant, init_value, final_value, tol, during,
                                       strictness, time_tol)


def assert_is_ramp(signal, slope, tol, during=None, strictness=1, time_tol=0):
    """
    Assertion helper for ``is_ramp`` function. Has the same signature.

    Is equivalent to:

    >>> result = is_ramp(*args, **kwargs)
    >>> assert_analysis(result, True)

    Raises
    ------
    AssertionError
        In case result is different from ``True``.

    See Also
    --------
    typhoon.test.signals.is_ramp
    """
    return _impl.assert_is_ramp(signal, slope, tol, during, strictness, time_tol)


def assert_follows_reference(signal, ref_signal, tol, during=None, strictness=1, time_tol=0):
    """
    Assertion helper for ``follows_reference`` function. Has the same signature.

    Is equivalent to:

    >>> result = follows_reference(*args, **kwargs)
    >>> assert_analysis(result, True)

    Raises
    ------
    AssertionError
        In case result is different from ``True``.

    See Also
    --------
    typhoon.test.signals.follows_reference
    """
    return _impl.assert_follows_reference(signal, ref_signal, tol, during, strictness, time_tol)


def pandas_sine(amplitude=1, frequency=60, duration=1, phase=0, Ts=1e-4):
    """
    Generates a pandas Series with a sine wave with given characteristics.

    Parameters
    ----------
    amplitude : float
        Sine amplitude
    frequency : float
        Sine frequency, in Hz
    duration : float
        Time duration of the whole signal, in seconds
    phase : float
        Phase of the sine wave
    Ts : float
        Sampling rate of the sine wave.

    Returns
    -------
    : Series
        Timeseries signal of the sine wave.


    Notes
    -----
    This function can typically be used to easily get a pandas Series for learning and quick testing
    purposes.


    Examples
    --------
    >>> from typhoon.test.signals import pandas_sine
    >>> sine = pandas_sine()  # with default parameters
    >>> print(sine)

    See Also
    --------
    typhoon.test.signals.pandas_3ph_sine
    """
    sp = _impl.sp
    pd = _impl.pd
    t = sp.arange(0, duration, Ts)
    y = amplitude * sp.sin(2 * sp.pi * frequency * t + phase*sp.pi/180)

    tp = pd.to_timedelta(t, unit="s")
    serie = pd.Series(data=y, index=tp, name="Sine")
    return serie


def pandas_3ph_sine(amplitude=1, frequency=60, duration=1, Ts=1e-4):
    """
    Generates a pandas DataFrame with a set of three balanced sine waves with given characteristics.

    Parameters
    ----------
    amplitude : float
        Sine amplitude
    frequency : float
        Sine frequency, in Hz
    duration : float
        Time duration of the whole signal, in seconds
    Ts : float
        Sampling rate of the sine wave.

    Returns
    -------
    : DataFrame
        Set of three-phase sinusoidal signals.

    Notes
    -----
    This function can typically be used to easily get a DataFrame for learning and quick testing
    purposes.

    Examples
    --------
    >>> from typhoon.test.signals import pandas_3ph_sine
    >>> sines = pandas_3ph_sine()  # with default parameters
    >>> print(sines)


    See Also
    --------
    typhoon.test.signals.pandas_sine
    """
    sp = _impl.sp
    pd = _impl.pd
    sines = {"sine1": pandas_sine(amplitude, frequency, duration, 0, Ts),
             "sine2": pandas_sine(amplitude, frequency, duration, -120, Ts),
             "sine3": pandas_sine(amplitude, frequency, duration, -240, Ts)
             }
    return pd.DataFrame(sines)

def pandas_first_order(tau, init, final, duration=1, Ts=1e-4):
    """
    Generates pandas Series as the first order response signal with given characteristics.

    Parameters
    ----------
    tau: float
        Time constant of the signal
    init: float
        Initial value of the signal
    final: float
        Final value of the signal
    duration: float
        Time duration of the whole signal, in seconds
    Ts: float
        Sampling rate of the signal.

    Returns
    -------
    : pandas Series
        First order response signal as Timeseries
    """
    sp = _impl.sp
    pd = _impl.pd
    t = sp.arange(0, duration, Ts)
    y = final + (init - final) * sp.exp(-t  / tau)

    tp = pd.to_timedelta(t, unit="s")
    serie = pd.Series(data=y, index=tp, name="First_order")
    return serie
