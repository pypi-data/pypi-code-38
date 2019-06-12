from j5basic import TzInfo
from virtualtime import datetime_tz, _underlying_datetime_type
import datetime
import threading
import time
import pytz
import imp
import random

"""Utilities for dealing with time."""

def utcnow():
    """Return now in UTC with the tzinfo properly set."""
    return datetime_tz.datetime_tz.now().astimezone(pytz.utc)

def localsecondnow():
    """Provides the current local time with microseconds set to 0."""
    return datetime_tz.datetime_tz.now().replace(microsecond=0)

def localminutenow():
    """Provides the current local time with seconds and microseconds set to 0."""
    return datetime_tz.datetime_tz.now().replace(second=0,microsecond=0)

# NB: There is a copy of totalseconds_float in virtualtime, to prevent circular imports - changes should be applied to both
def totalseconds_float(timedelta):
    """Return the total number of seconds represented by a datetime.timedelta object, including fractions of seconds"""
    return timedelta.seconds + (timedelta.days * 24 * 60 * 60) + timedelta.microseconds/1000000.0

def totalmilliseconds(timedelta):
    """Return the total number of milliseconds represented by a datetime.timedelta object."""
    return timedelta.microseconds/1000.0 + (totalseconds(timedelta) * 1000)

def totalseconds(timedelta):
    """Return the total number of seconds represented by a datetime.timedelta object, excluding fractions of seconds"""
    return timedelta.seconds + (timedelta.days * 24 * 60 * 60)

def totalhours(timedelta):
    """Return the total number of hours represented by a datetime.timedelta object."""
    return float(totalseconds(timedelta)) / 3600

def hoursandminutes(timedelta):
    """Expresses a timedelta object as a tuple containing hours and minutes.  Seconds are rounded."""
    th = totalhours(timedelta)
    wh = int(th)
    tm = (th - wh) * 60
    wm = int(tm)

    return (wh,wm)

def timedelta_to_tuple(timedelta):
    """Expresses a timedelta object as a tuple containing days, hours, minutes and seconds (rounded)"""
    d = timedelta.days
    s_total = timedelta.seconds
    h = s_total // 3600
    m = (s_total // 60) % 60
    s = s_total % 60
    return (d, h, m, s)

def tuple_to_timedelta(td_tuple):
    """Converts a days, hours, minutes and seconds tuple to a timedelta object"""
    d, h, m, s = td_tuple
    return datetime.timedelta(days=d, hours=h, minutes=m, seconds=s)

def timedelta_to_str(timedelta):
    """Expresses a timedelta as a human-readable string"""
    d, h, m, s = timedelta_to_tuple(timedelta)
    if d:
        return "%dd %02d:%02d:%02d" % (d, h, m, s)
    else:
        return "%02d:%02d:%02d" % (h, m, s)

def str_to_timedelta(td_str):
    """Parses a human-readable time delta string to a timedelta"""
    if "d" in td_str:
        day_str, time_str = td_str.split("d", 1)
        d = int(day_str.strip())
    else:
        time_str = td_str
        d = 0
    time_str = time_str.strip()
    if not time_str:
        return datetime.timedelta(days=d)
    colon_count = time_str.count(":")
    if (not colon_count) or colon_count > 2:
        raise ValueError("Time format [dd d] hh:mm[:ss] or dd d")
    elif colon_count == 1:
        h_str, m_str = time_str.split(":", 1)
        h, m, s = int(h_str.strip()), int(m_str.strip()), 0
    elif colon_count == 2:
        h_str, m_str, s_str = time_str.split(":", 2)
        h, m, s = int(h_str.strip()), int(m_str.strip()), int(s_str.strip())
    return tuple_to_timedelta((d, h, m, s))

def timetuple_to_datetime(t):
    """Convert a timetuple to a datetime object.
       """
    return datetime_tz.datetime_tz(*(t[:6]))

# deprecated alias
timetuple2datetime = timetuple_to_datetime

def _findall(text, substr):
     # Also finds overlaps
     sites = []
     i = 0
     while 1:
         j = text.find(substr, i)
         if j == -1:
             break
         sites.append(j)
         i=j+1
     return sites

_NEEDS_STRFTIME_PATCH = True
try:
    _underlying_datetime_type(1,1,1).strftime("%Y-%m-%d")
    _NEEDS_STRFTIME_PATCH = False
except ValueError:
    pass

if _NEEDS_STRFTIME_PATCH:
    def strftime(d, format_str):
        """Adjusted version of datetime's strftime that handles dates before 1900"""
        if hasattr(d, "year") and d.year < 1900:
            # Python datetime doesn't support formatting dates before 1900.
            # Since the Gregorian calendar has a cycle of 400 years, flip the date into the future
            # and adjust the year directly in the format string
            year = d.year
            while year < 1900: year += 400
            d1 = d.replace(year=year)
            d2 = d.replace(year=year+400)
            ys1 = "%04d" % year
            ys2 = "%04d" % (year + 400)
            y = "%d" % d.year
            replacers = {(ys1, ys2): "%d" % d.year}
            s1 = d1.strftime(format_str)
            s2 = d2.strftime(format_str)
            p1 = _findall(s1, ys1)
            p2 = _findall(s2, ys2)
            sites = [site for site in p1 if site in p2]
            rs1 = list(s1)
            rs2 = list(s2)
            for site in sites:
                rs1[site:site+len(ys1)] = list(y)
                rs2[site:site+len(ys2)] = list(y)
            if rs1 != rs2:
                raise ValueError("Error trying to calculate strftime(%r, %s): unexpected underlying values" % (d, format_str))
            return "".join(rs1)
        return d.strftime(format_str)
else:
    def strftime(d, format_str):
        return d.strftime(format_str)

def safestrptime(*args, **kwargs):
    #DEPRECATED: This method is deprecated, just use time.strptime instead.

    #the previous version of this function caused deadlocks on _strptime occasionally, another fix for the issue it
    #was solving has been implemented
    return time.strptime(*args, **kwargs)
