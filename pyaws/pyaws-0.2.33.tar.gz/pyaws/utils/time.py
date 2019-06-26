"""
Summary:
    - Command-line Interface (CLI) Utilities Module
    - Python3

Module Functions:
    - convert_strtime_datetime:
        Convert human-readable datetime string into a datetime object for
        conducting time operations.
    - convert_timedelta:
        Convert a datetime duration object into human-readable components
        (weeks, days, hours, etc).
    - convert_dt_time:
        Convert datetime objects to human-readable string output with Formatting
"""
import datetime
import inspect
import logging
from pyaws._version import __version__

logger = logging.getLogger(__version__)
logger.setLevel(logging.INFO)


def convert_strtime_datetime(dt_str):
    """
    Summary.
        Converts datetime isoformat string to datetime (dt) object

    Args:
        :dt_str (str): input string in '2017-12-30T18:48:00.353Z' form
         or similar

    Returns:
        TYPE:  datetime object

    """
    dt, _, us = dt_str.partition(".")
    dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    us = int(us.rstrip("Z"), 10)
    return dt + datetime.timedelta(microseconds=us)


class TimeDelta():
    def __init__(self, duration):
        """
        Summary.

            Time difference Class

        Args:
            :duration (datetime timedelta object)

        Returns:
            days, hours, minutes, seconds, TYPE: tuple of int

        """
        self.days, self.hours, self.minutes, self.seconds = self.convert_timedelta(duration)

    def convert_timedelta(self, duration):
        """
        Summary.

            Convert duration into component time units

        Args:
            :duration (datetime.timedelta): time duration to convert

        Returns:
            days, hours, minutes, seconds | TYPE: tuple (integers)

        """
        try:
            days, seconds = duration.days, duration.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = (seconds % 60)
        except Exception:
            logger.exception(
                    f'{inspect.stack()[0][3]}: Input must be datetime.timedelta object'
                )
            return 0, 0, 0, 0
        return days, hours, minutes, seconds


def convert_timedelta(duration):
    """
    Summary:
        Convert duration into component time units
    Args:
        :duration (datetime.timedelta): time duration to convert
    Returns:
        days, hours, minutes, seconds | TYPE: tuple (integers)
    """
    try:
        days, seconds = duration.days, duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)
    except Exception:
        logger.exception(
                f'{inspect.stack()[0][3]}: Input must be datetime.timedelta object'
            )
        return 0, 0, 0, 0
    return days, hours, minutes, seconds


def convert_dt_time(duration, return_iter=False):
    """
    Summary:
        convert timedelta objects to human readable output
    Args:
        :duration (datetime.timedelta): time duration to convert
        :return_iter (tuple):  tuple containing time sequence
    Returns:
        days, hours, minutes, seconds | TYPE: tuple (integers), OR
        human readable, notated units | TYPE: string
    """
    try:
        days, hours, minutes, seconds = convert_timedelta(duration)
        if return_iter:
            return days, hours, minutes, seconds
        # string format conversions
        if days > 0:
            format_string = (
                '{} day{}, {} hour{}'.format(
                 days, 's' if days != 1 else '', hours, 's' if hours != 1 else ''))
        elif hours > 1:
            format_string = (
                '{} hour{}, {} minute{}'.format(
                 hours, 's' if hours != 1 else '', minutes, 's' if minutes != 1 else ''))
        else:
            format_string = (
                '{} minute{}, {} sec{}'.format(
                 minutes, 's' if minutes != 1 else '', seconds, 's' if seconds != 1 else ''))
    except AttributeError as e:
        logger.exception(
            '%s: Type mismatch when converting timedelta objects (Code: %s)' %
            (inspect.stack()[0][3], str(e)))
        raise e
    except Exception as e:
        logger.exception(
            '%s: Unknown error when converting datetime objects (Code: %s)' %
            (inspect.stack()[0][3], str(e)))
        raise e
    return format_string
