"""
This module containes methods for performing common tasks with timestamps
"""

def timestamp_from_string(s):
    """
    Locate a timestamp in a string with common separators

    Arguments
    =========
    s: str
        String to parse and search for timestamp component

    Returns
    =======
    ts: pandas.Timestamp
        Timestamp in string. If no timestamp found, `None` is returned
    """
    import pandas

    ts = None
    for sub in s.split("_"):
        try:
            ts = utc_timestamp(sub)
            break
        except:
            pass

    return ts


def utc_timestamp(ts):
    """
    Cast string to Timestamp, convert or localize to UTC
    """
    import pandas

    ts = pandas.Timestamp(ts)
    if not ts.tzinfo:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")

    return ts
