# Author: Victor Maryama
# Typhoon HIL

""" This package contains higher-level, simpler versions of functions already
released HIL API."""

from . import impl as _impl


def wait(secs):
    """
    Waits a defined amount of seconds.

    Parameters
    ----------
    secs : Timedelta-like or float
        Time to wait for. If float, it is considered as seconds. Works with anything that can be converted to timedelta.

    Returns
    -------
    time : Timedelta
        Time after wait has elapsed.

    Examples
    --------

    >>> import typhoon.api.hil as hil
    >>> import typhoon.test.capture as capture
    >>> print(hil.get_sim_time())
    >>> capture.wait(2)
    >>> print(hil.get_sim_time())

    """
    return _impl.wait(secs)


def start_capture(
        duration,
        offset_absolute=0,
        offset_relative=None,
        rate="Max",
        signals=(),
        trigger_source="Forced",
        trigger_threshold=None,
        trigger_edge=None,
        trigger_use_first_occurence=True,
        fileName="",
        executeAt=None,
        timeout=None,
        absolute_time=False,
                        ):
    """Sets up capture settings and start capture.

    It is a simplified version of regular Typhoon HIL API *start_capture()* function, with all the settings in just one function. It also omits some arguments that could be derived automatically.

    For more details refer to HIL API documentation.

    Parameters
    ----------
    duration
        Total capture duration, in seconds, including offset
    offset_absolute
        Duration in seconds of the data captured before the trigger. Can't be greater than *duration*.
    offset_relative
        Relative duration, in percentage, of the data capture before the trigger. Can't be greater than 100.
    rate
        Sampling rate in samples per second
    signals
        List of signals to be captured. No distinction is made between analog or digital as there cannot exist two signals with the same name
    trigger_source
        Signal to be used to trigger the capture
    trigger_threshold
        Level the trigger_source signal should attain to start capture
    trigger_edge
        Direction of the trigger_source signal should have, when attaining trigger_threshold, to start capture. Can be
        "rising" or "falling".
    trigger_use_first_occurence
        If offset duration is larger than available before trigger, to consider only the amount available (setting to True) or ignore trigger and look for another one later on (setting to False).
    fileName
        File name to save captured data
    executeAt
        If set, simulation time when this start_capture will take effect
    timeout
        Maximum allowed time to wait before a trigger
    absolute_time
        If True, time index of capture time is real time

    Returns
    -------
    namedtuple
        With the following attributes:
    t : Timedelta
        The time of the capture start
    duration : float
        Adjusted capture duration
    rate : float
        Rate based on system constraints.

    Notes
    -----
    At least one signal should be defined.

    Users should only use either *offset_absolute* or *offset_relative*. If both are defined, offset_relative will be used.

    *trigger_source* defaults to "Forced" if not defined. If defined with a value other than that, *trigger_threshold* and *trigger_edge* should be defined too.

    The sampling rate and duration can be arbitrarily defined, however they might not be valid depending on HIL constraints. When this is the case, the closest possible settings will be used, showed as a warning and returned from the function call.

    *trigger_use_first_occurence* should only be used as False when dealing with pure periodic signals and when offset should be strictly respected.

    Examples
    --------
    Forced capture start, printing returned values:

    >>> from typhoon.test.capture import start_capture
    >>> capture_info = start_capture(duration=10, rate=10000)
    >>> print(capture_info.t)
    >>> print(capture_info.duration)
    >>> print(capture_info.rate)

    No offset, using analog signal as trigger:

    >>> start_capture(duration=rtspec.duration+2,
                      rate=500,
                      signals=["Probe val", "enable inv", "enable ref"],
                      trigger_source="Probe val",
                      trigger_edge="Rising edge"
                      trigger_threshold=277
                      timeout=10)

    Using absolute offset and trigger on digital signal:

    >>> start_capture(duration=4,
                      offset_absolute=2,
                      rate=500,
                      signals=["P", "operating"],
                      trigger_source="operating",
                      trigger_threshold=0.5,
                      trigger_edge="Rising edge",
                      timeout=10)

    See Also
    --------
    typhoon.test.capture.get_capture_results

    """
    return _impl.start_capture(
        duration,
        offset_absolute,
        offset_relative,
        rate,
        signals,
        trigger_source,
        trigger_threshold,
        trigger_edge,
        trigger_use_first_occurence,
        fileName,
        executeAt,
        timeout,
        absolute_time,
    )


def wait_capture_finish(sleep=0.5):
    """
    Blocks until capture stops.

    Parameters
    ----------
    sleep
        To avoid busy waiting, defines the time between polls for capture finish.

    Returns
    -------
    time : Timedelta
        Time after capture has finished.
    """
    return _impl.wait_capture_finish(sleep)


def get_capture_results(wait_capture=False):
    """
    Return capture results as a Pandas DataFrame.

    Parameters
    ----------
    wait_capture
        If True, blocks until capture finishes. If False, immediately stops capture and return captured results so far.

    Returns
    -------
    pandas.DataFrame
        All captured signals, selectable by name, with time index

    Examples
    --------
    Importing libraries

    >>> from typhoon.test.capture import start_capture, get_capture_results

    Returning results immediately

    >>> start_capture(duration=20, rate=100000, signals=["P", "Va_rms"])
    >>> # do something in meantime which takes 10 seconds...
    >>> capture = get_capture_results() # returns capture up to 10 seconds

    Waiting whole capture duration

    >>> start_capture(duration=20, rate=100000, signals=["P", "Va_rms"])
    >>> # do something in meantime which takes 10 seconds...
    >>> capture = get_capture_results(wait_capture=True) # waits until the 20 second capture elapses

    Individual signals can be accessed in a dict-like fashion:

    >>> print(capture) #pandas DataFrame
    >>> print(capture["P"]) #pandas Series

    The values can be accessed using:

    >>> capture["P"].values # return array

    The index is a TimedeltaIndex, which contains Typhoon custom Timedeltas:

    >>> index = capture["P"].index
    >>> index[0] # Time for first point (Timedelta)
    >>> index[0].total_seconds() # returns a float with time as seconds

    You can slice using time directly using time, for example here from 10 seconds onwards:

    >>> capture["P"]["10s":]

    Some TyphoonTest functions return timedeltas, which also can be used for slicing:

    >>> from typhoon.test.signals import find
    >>> t_fullpower = find(capture["P"], region="at", value=100000)
    >>> capture["P"][t_fullpower-"1s":t_fullpower] # slices the period 1 second before t_fullpower

    Other DataFrame and Series example

    >>> from typhoon.test.signals import pandas_3ph_sine
    >>> df = pandas_3ph_sine()
    >>> df
    >>> sine1 = df["sine1"]
    >>> sine1

    See Also
    --------
    typhoon.test.capture.start_capture
    typhoon.types.timedelta.Timedelta

    References
    ----------
    `Pandas Documentation <https://pandas.pydata.org/pandas-docs/stable/>`_
    """
    return _impl.get_capture_results(wait_capture)


def read(name, avg_reads=1, alias=None):
    """
    Reads asynchronously a signal once (one time poll).

    Parameters
    ----------
    name
        Name of the signal to read.
    avg_reads
        Defines how many reads to do to return an average of read values
    alias
        Specifies an alias for this returned value

    Returns
    -------
    AliasFloat
        Value read for given signal.

    Examples
    --------
    Instead of using the lower level HIL API commands:

    >>> val = hil.read_analog_signal("P")
    >>> val = hil.read_digital_signal("HIL0 digital input 10")

    user can use directly

    >>> from typhoon.test.capture import read
    >>> val = read("P")
    >>> val = read("HIL0 digital input 10")

    """
    return _impl.read(name, avg_reads, alias)


def wait_until(name, region, value, from_region=None, interval=1, timeout=60, alias=None):
    """
    Waits until signal meets specified conditions.

    Parameters
    ----------
    name
        Same as find function (see below)
    region
        Same as find function (see below)
    value
        Same as find function (see below)
    from_region
        Same as find function (see below)
    interval
        Time between reads of the signal.
    timeout
        Time after which, if the signals has not yet met the desired behavior, function will fail.
    alias
        Alias to give for this specific event.

    Returns
    -------
    Timedelta
        Time when signal meets the behavior

    Raises
    ------
    Exception
        If timeout is reached without meeting the behavior.

    Examples
    --------

    First moment when Power is inside the range, polling every one second, fails if not satisfied within 10 seconds. Detects even if signal already starts in the range.

    >>> t = wait_until("P", region="at", value=(900,1000), interval=1, timeout=10)

    Almost same as before but require the signal to be outside the range prior entering it. Detects the transition to the range from above or below

    >>> t = wait_until("P", region="at", value=(900,1000), from_region="outside", interval=1, timeout=10)

    Detecting a rising edge, when power goes above 1000

    >>> t = wait_until("P", region="above", value=1000, from_region="below", interval=1, timeout=10)

    Notes
    -----
    This behaves very similarly to the find() function from analysis module. The difference is that this one executes in real-time, whereas the find() function checks an already captured signal.

    See Also
    --------
    typhoon.test.signals.find
    """
    return _impl.wait_until(name, region, value, from_region, interval, timeout, alias)
