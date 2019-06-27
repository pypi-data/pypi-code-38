# -*- coding: utf-8 -*-

"""package benutils
author  Matt Davis, minor modifications: Benoit Dubois
website http://github.com/jiffyclub(/1294443)
details
Functions for converting dates to/from JD and MJD. Assumes dates are historical
dates, including the transition from the Julian calendar to the Gregorian
calendar in 1582. No support for proleptic Gregorian/Julian calendars.

Note: The Python datetime module assumes an infinitely valid Gregorian calendar.
The Gregorian calendar took effect after 10-15-1582 and the dates 10-05 through
10-14-1582 never occurred. Python datetime objects will produce incorrect
time deltas if one date is from before 10-15-158
"""

import math
import datetime as dt


# =============================================================================
def mjd_to_jd(mjd):
    """Convert Modified Julian Day to Julian Day.
    :param mjd: Modified Julian Day (float)
    :returns: Julian Day (float)
    """
    return mjd + 2400000.5


# =============================================================================
def jd_to_mjd(jd):
    """Convert Julian Day to Modified Julian Day.
    :param jd: Julian Day (float)
    :returns: Modified Julian Day (float)
    """
    return jd - 2400000.5


# =============================================================================
def date_to_mjd(year, month, day):
    """Convert a date to Modified Julian Day.
    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet',
    4th ed., Duffet-Smith and Zwart, 2011.
    --------
    Examples: Convert 6 a.m., February 17, 1985 to Julian Day
    --------
    >>> date_to_mjd(1985,2,17.25)
    46113.25
    --------
    :param year: Year as integer. Years preceding 1 A.D. should be 0 or
                 negative. The year before 1 A.D. is 0, 10 B.C. is year -9 (int)
    :param month: Month as integer, Jan = 1, Feb. = 2, etc. (int)
    :param day: Day, may contain fractional part. (float)
    :returns: Modified Julian Day (float)
    """
    if month == 1 or month == 2:
        yearp = year - 1
        monthp = month + 12
    else:
        yearp = year
        monthp = month
    # this checks where we are in relation to October 15, 1582, the beginning
    # of the Gregorian calendar.
    if (year < 1582) or \
       (year == 1582 and month < 10) or \
       (year == 1582 and month == 10 and day < 15):
        # before start of Gregorian calendar
        b = 0
    else:
        # after start of Gregorian calendar
        a = math.trunc(yearp / 100.)
        b = 2 - a + math.trunc(a / 4.)
    if yearp < 0:
        c = math.trunc((365.25 * yearp) - 0.75)
    else:
        c = math.trunc(365.25 * yearp)
    d = math.trunc(30.6001 * (monthp + 1))
    mjd = b + c + d + day - 679006
    return mjd


# =============================================================================
def mjd_to_date(mjd):
    """Convert Modified Julian Day to date.
    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet',
    4th ed., Duffet-Smith and Zwart, 2011.
    --------
    Examples
    --------
    >>> mjd_to_date(46113.25)
    (1985, 2, 17.25)
    ----------
    :param mjd : Modified Julian Day (float)
    :returns: Tuple containing year as integer, month as integer and day as
              float. Years preceding 1 A.D. should be 0 or negative. The year
              before 1 A.D. is 0, 10 B.C. is year -9. Month are decimal number,
              Jan = 1, Feb. = 2, etc. Day, may contain fractional part
              (int, int, float)
    """
    mjd += 2400001.0
    f, i = math.modf(mjd)
    i = int(i)
    a = math.trunc((i - 1867216.25)/36524.25)
    if i > 2299160:
        b = i + 1 + a - math.trunc(a / 4.)
    else:
        b = i
    c = b + 1524
    d = math.trunc((c - 122.1) / 365.25)
    e = math.trunc(365.25 * d)
    g = math.trunc((c - e) / 30.6001)
    day = c - e + f - math.trunc(30.6001 * g)
    if g < 13.5:
        month = g - 1
    else:
        month = g - 13
    if month > 2.5:
        year = d - 4716
    else:
        year = d - 4715
    return year, month, day


# =============================================================================
def hmsm_to_days(hour=0, _min=0, sec=0, micro=0):
    """Convert hours, minutes, seconds, and microseconds to fractional days.
    --------
    Examples
    --------
    >>> hmsm_to_days(hour=6)
    0.25
    --------
    :param hour: Hour number. Defaults to 0. (int)
    :param min: Minute: number. Defaults to 0. (int)
    :param sec: Second number. Defaults to 0. (int)
    :param micro: Microsecond number. Defaults to 0. (int)
    :returns: Fractional days. (float)
    """
    days = sec + (micro / 1.e6)
    days = _min + (days / 60.)
    days = hour + (days / 60.)
    return days / 24.


# =============================================================================
def days_to_hmsm(days):
    """Convert fractional days to hours, minutes, seconds, and microseconds.
    Precision beyond microseconds is rounded to the nearest microsecond.
    Raises 'ValueError' if `days` is >= 1.
    --------
    Examples
    --------
    >>> days_to_hmsm(0.1)
    (2, 24, 0, 0)
    --------
    :param day: A fractional number of days. Must be less than 1. (float)
    :returns: Tuple containing hour number as integer, minute number as integer,
              second number as integer and microsecond number as integer
              (int, int, int, int)
    """
    hours = days * 24.
    hours, hour = math.modf(hours)
    mins = hours * 60.
    mins, _min = math.modf(mins)
    secs = mins * 60.
    secs, sec = math.modf(secs)
    micro = round(secs * 1.e6)
    return int(hour), int(_min), int(sec), int(micro)


# =============================================================================
def datetime_to_mjd(date):
    """Convert a `datetime.datetime` object to Modified Julian Day.
    --------
    Examples
    --------
    >>> d = datetime.datetime(1985,2,17,6)
    >>> d
    datetime.datetime(1985, 2, 17, 6, 0)
    >>> mjdutil.datetime_to_mjd(d)
    2446113.75
    --------
    :param date: `datetime.datetime` instance (`datetime.datetime` instance)
    :returns: Modified Julian day (float)
    """
    days = date.day + hmsm_to_days(date.hour, date.minute, date.second, \
                                   date.microsecond)
    return date_to_mjd(date.year, date.month, days)


# =============================================================================
def mjd_to_datetime(mjd):
    """Convert a Modified Julian Day to an `jdutil.datetime` object.
    --------
    Examples
    --------
    >>> mjd_to_datetime(2446113.75)
    datetime(1985, 2, 17, 6, 0)
    --------
    :param mjd: Modified Julian day (float)
    :returns: `jdutil.datetime` equivalent of Modified Julian day
               (`jdutil.datetime` object)
    """
    from datetime import datetime
    year, month, day = mjd_to_date(mjd)
    frac_days, day = math.modf(day)
    day = int(day)
    hour, _min, sec, micro = days_to_hmsm(frac_days)
    return datetime(year, month, day, hour, _min, sec, micro)


# =============================================================================
def timedelta_to_days(td):
    """
    Convert a `datetime.timedelta` object to a total number of days.
    --------
    Examples
    --------
    >>> td = datetime.timedelta(4.5)
    >>> td
    datetime.timedelta(4, 43200)
    >>> timedelta_to_days(td)
    4.5
    --------
    :params td: `datetime.timedelta` instance
    :returns: Total number of days in the `datetime.timedelta` object (float).
    """
    seconds_in_day = 24. * 3600.
    days = td.days + (td.seconds + (td.microseconds * 10.e6)) / seconds_in_day
    return days


# =============================================================================
class datetime(dt.datetime):
    """A subclass of `datetime.datetime` that performs math operations by first
    converting to Julian Day, then back to a `jdutil.datetime` object.
    Addition works with `datetime.timedelta` objects, subtraction works with
    `datetime.timedelta`, `datetime.datetime`, and `jdutil.datetime` objects.
    Not all combinations work in all directions, e.g.
    `timedelta - datetime` is meaningless.
    See Also
    --------
    datetime.datetime : Parent class.
    """

    def __add__(self, other):
        if not isinstance(other, dt.timedelta):
            s = "jdutil.datetime supports '+' only with datetime.timedelta"
            raise TypeError(s)
        days = timedelta_to_days(other)
        combined = datetime_to_mjd(self) + days
        return mjd_to_datetime(combined)

    def __radd__(self, other):
        if not isinstance(other, dt.timedelta):
            s = "jdutil.datetime supports '+' only with datetime.timedelta"
            raise TypeError(s)
        days = timedelta_to_days(other)
        combined = datetime_to_mjd(self) + days
        return mjd_to_datetime(combined)

    def __sub__(self, other):
        if isinstance(other, dt.timedelta):
            days = timedelta_to_days(other)
            combined = datetime_to_mjd(self) - days
            return mjd_to_datetime(combined)
        elif isinstance(other, (datetime, dt.datetime)):
            diff = datetime_to_mjd(self) - datetime_to_mjd(other)
            return dt.timedelta(diff)
        else:
            s = "jdutil.datetime supports '-' with: "
            s += "datetime.timedelta, jdutil.datetime and datetime.datetime"
            raise TypeError(s)

    def __rsub__(self, other):
        if not isinstance(other, (datetime, dt.datetime)):
            s = "jdutil.datetime supports '-' with: "
            s += "jdutil.datetime and datetime.datetime"
            raise TypeError(s)
        diff = datetime_to_mjd(other) - datetime_to_mjd(self)
        return dt.timedelta(diff)

    def to_jd(self):
        """
        :returns: the date converted to Julian Day.
        """
        return mjd_to_jd(datetime_to_mjd(self))

    def to_mjd(self):
        """
        :returns: the date converted to Modified Julian Day.
        """
        return jd_to_mjd(self)


# =============================================================================
if __name__ == '__main__':
    #
    MJD = 46113.25
    DATE = mjd_to_date(MJD)
    print("date:", DATE)
    #
    YEAR = 1985
    MONTH = 2
    DAY = 17.25
    MJD = date_to_mjd(YEAR, MONTH, DAY)
    print("mjd:", MJD)
