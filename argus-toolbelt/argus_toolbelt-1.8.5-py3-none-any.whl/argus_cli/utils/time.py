"""Utility functions for parsing and formatting time in plugins

If you're wondering why we're multiplying by 1000,
it's because Argus is written in Java and requires milis, not seconds.
"""
from datetime import datetime, timedelta

import dateparser as dateparser


def date_or_relative(time_string: str):
    """Convince function that merges date-time and time diff formats"""
    return dateparser.parse(time_string).timestamp() * 1e3


def time_diff(time_string: str):
    """Converts the input from one unit to milliseconds"""
    return (datetime.now() - dateparser.parse(time_string)).total_seconds() * 1e3


def timestamp_to_period(timestamp: int, format="iso"):
    """Converts a timestamp to a ISO8601 style period with days"""
    clock_time = datetime.utcfromtimestamp(timestamp)
    if format == "iso":
        return "P{days:03}DT{hours:02}:{minutes:02}:{seconds:02}".format(
            days=timedelta(seconds=timestamp).days,
            hours=clock_time.hour, minutes=clock_time.minute, seconds=clock_time.second
        )
    if format == "minutes":
        return "{minutes} minutes".format(
            minutes=timedelta(seconds=timestamp).total_seconds() // 60,
        )


def timestamp_to_date(timestamp: int):
    """Converts a timestamp to a ISO8601 style date and time"""
    return datetime.fromtimestamp(timestamp).isoformat()
