import datetime
import time
import ntplib
import numpy as np
from pandas import DataFrame, merge, Series

def datetimeToTimestampMs(dt, datetimeformat = "%Y-%m-%d %H:%M:%S.%f"):
    """
    Convert a given string or datetime object to a millisecond based timestamp.
    No conversion is performed when a timestamp (int) is given as an input.
    The format string can be set using the datetimeformat attribute.

    :type dt: datetime, str or int
    :param dt: The datetime or datetime string
    :return: Millisecond based timestamp. None when conversion not successful.
    :rtype: int
    """
    if isinstance(dt, datetime.datetime):
        return int(dt.timestamp()*1000)
    elif isinstance(dt, str):
        return int(datetime.datetime.strptime(dt, datetimeformat).timestamp()*1000)
    elif isinstance(dt, np.datetime64):
        return (dt - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
    elif isinstance(dt, np.float64):
        return int(dt.item()*1000.0)
    elif isinstance(dt, float):
        return int(dt*1000.0)
    elif isinstance(dt, int):
        return dt
    return None

def timestampMsToDatetime(ts):
    """
    Takes a timestamp and returns a datetime object.
    The timestamp is millisecond based and can be in float (default datetime convention) or an int.

    :type ts: float, int
    :param ts: The timestamp
    :return: datetime
    :rtype: datetime.datetime
    """
    if isinstance(ts, int):
        return datetime.datetime.utcfromtimestamp(float(ts/1000))
    else:
        return datetime.datetime.utcfromtimestamp(ts/1000)

def getTimeOffsetToUtc():
    """
    Get the offset of local time to UTC time at pool.ntp.org.
    :return: Offset in seconds
    :rtype: float
    """
    c = ntplib.NTPClient()
    response = c.request("pool.ntp.org", version=3)
    return response.offset

def pandasDfFromQueryResponse(query, fillNaMethod=None, dropTrailingNa=True, convertTimestamp=False, orderDesc=False):
    """
    Convert a kairosdb query response to pandas DataFrame.
    Timestamp contains timestamp in milliseconds.

    :type query: list
    :param query: The result from the query method (list of deserialised json responses from kairosdb (one for each metric))
    :type fillNaMethod: str
    :param fillNaMethod: Method to fill in missing values: ‘backfill’, ‘bfill’, ‘pad’, ‘ffill’, None, (default=None)
    :type dropTrailingNa: boolean
    :param dropTrailingNa: Drop trailing NaN values when set to true. Especially useful when end neither end param is specified (filters time delay when querying multiple metrics). Default: True
    :type convertTimestamp: boolean
    :param convertTimestamp: Convert the timestamp to datetime (Default: False)
    :type orderDesc: boolean
    :param orderDesc: Orders returned data points based on timestamp. Descending order when True, or ascending when False (default) 
    :rtype: pandas.DataFrame
    :return: Pandas DataFrame. 
    """
    result = None

    if query is None:
        raise KeyError("Provided query is invalid (missing 'queries' key)")

    metricCount = len(query)

    if metricCount <= 0:
        return None

    for m in range(0, metricCount):
        if len(query[m]['queries']) <= 0:
            continue
            
        try:
            mname = query[m]['queries'][0]['results'][0]['name']
        except:
            raise KeyError("Provided query is invalid (invalid results or name keys within 'queries')")

        try:
            mdf = DataFrame(query[m]['queries'][0]['results'][0]['values'], columns=["Timestamp", mname])
        except:
            raise KeyError("Provided query is invalid (invalid 'values' provided)")

        if result is None:
            result = mdf
        else:
            result = merge(result, mdf, on="Timestamp", how="outer")

    if result.empty:
        return result

    if dropTrailingNa:
        last = min(result.apply(Series.last_valid_index, axis=0))
        result = result.loc[0:last]

    if fillNaMethod is not None:
        result = DataFrame.fillna(result, method=fillNaMethod, axis=0)
        result.dropna(how='all',inplace=True)
        result.dropna(how='all',axis=1,inplace=True)

    if result.empty:
        return result

    if orderDesc:
        result.sort_values(by=["Timestamp"], axis=0, ascending=False, inplace=True)
    else:
        result.sort_values(by=["Timestamp"], axis=0, ascending=True, inplace=True)

    if result.empty:
        return result

    if convertTimestamp and ("Timestamp" in result):
        result["Timestamp"] = result["Timestamp"].map(timestampMsToDatetime)

    return result