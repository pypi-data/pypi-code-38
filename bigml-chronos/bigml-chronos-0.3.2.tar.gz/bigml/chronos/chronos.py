# -*- coding: utf-8 -*-
#!/usr/bin/env python

from bigml.chronos import formats, util
from datetime import date, datetime, timedelta
from functools import partial
from isoweek import Week
import pytz

def _formatter_basic(date_format, date):
    return util.custom_strptime(date,date_format)

def _formatter_basic_iso_date(date):
    return util.custom_strptime(date, "%Y%m%d%z")

def _formatter_basic_week_date(weekdate):
    iso_year,iso_week,iso_day = \
        util.try_read(weekdate, util.read_week_date)
    week = Week(iso_year,iso_week)
    return util.date_from_week(week, iso_day)

def _formatter_basic_week_date_time(date):
    iso_year, iso_week, iso_day, time = \
         util.try_read(date, util.read_week_date_time, msecs=True)
    week = Week(iso_year,iso_week)
    return util.date_from_week(week, iso_day) + time

def _formatter_basic_week_date_time_no_ms(date):
    iso_year, iso_week, iso_day, time = \
        util.try_read(date, util.read_week_date_time, msecs= False)
    week = Week(iso_year,iso_week)
    return util.date_from_week(week, iso_day) + time

def _formatter_iso_date(date):
    return util.custom_strptime(date, "%Y-%m-%d%z")

def _formatter_iso_date_time(date):
    return util.custom_strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")

def _formatter_iso_instant(date):
    return util.custom_strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")

def _formatter_iso_local_date(date):
    return util.custom_strptime(date, "%Y-%m-%d")

def _formatter_iso_local_date_time(date):
    return util.custom_strptime(date, "%Y-%m-%dT%H:%M:%S.%f")

def _formatter_iso_local_time(date):
    return util.custom_strptime(date, "%H:%M:%S.%f")

def _formatter_iso_offset_date(date):
    return util.custom_strptime(date, "%Y-%m-%d%z")

def _formatter_iso_offset_date_time(date):
    return util.custom_strptime(date, "%Y-%m-%dT%H:%M:%S.%f%z")

def _formatter_iso_offset_time(date):
    return util.custom_strptime(date, "%H:%M:%S.%f%z")

def _formatter_iso_ordinal_date(date):
    year = date[:4]
    day = int(date.split("-")[1][:3])
    tz = date.split("-")[1][3:]
    return util.custom_strptime(year+tz, "%Y%z") + timedelta(days=day-1)

def _formatter_iso_time(date):
    return util.custom_strptime(date, "%H:%M:%S.%f%z")

def _formatter_iso_week_date(weekdate):
    iso_year,iso_week,iso_day, timezone = \
        util.try_read(weekdate, util.read_iso_week_date, tz=True)
    week = Week(iso_year,iso_week)
    return util.date_from_week(week, iso_day)

def _formatter_iso_zoned_date_time(date):
    return _formatter_iso_date_time(date)

def _formatter_rfc_1123_date_time(date):
    return util.custom_strptime(date, "%a, %d %b %Y %H:%M:%S GMT")

def _formatter_timestamp(timestamp):
    return datetime.fromtimestamp(int(timestamp), tz=pytz.utc)

def _formatter_timestamp_msecs(timestamp):
    return datetime.fromtimestamp(float(timestamp)/1000, tz=pytz.utc)

def _formatter_odata_format(date):
    return _formatter_timestamp_msecs(date[6:-2])

def _formatter_week_date(weekdate):
    iso_year,iso_week,iso_day, timezone = \
        util.try_read(weekdate, util.read_iso_week_date, tz=False)
    week = Week(iso_year,iso_week)
    return util.date_from_week(week, iso_day)

def _formatter_week_date_time(date):
    iso_year, iso_week, iso_day, time = \
        util.try_read(date, util.read_hypen_week_date_time, msecs=True)
    week = Week(iso_year,iso_week)
    return util.date_from_week(week, iso_day) + time

def _formatter_week_date_time_no_ms(date):
    iso_year, iso_week, iso_day, time = \
        util.try_read(date, util.read_hypen_week_date_time, msecs=False)
    week = Week(iso_year,iso_week)
    return util.date_from_week(week, iso_day) + time

def _formatter_weekyear_week(weekdate):
    iso_year,iso_week = \
        util.try_read(weekdate, util.read_iso_week_date_no_day)
    week = Week(iso_year,iso_week)
    return util.date_from_week(week)

def _formatter_weekyear_week_day(weekdate):
    iso_year,iso_week, iso_day, tz = \
        util.read_iso_week_date(weekdate, tz=False)
    week = Week(iso_year,iso_week)
    return util.date_from_week(week, iso_day)

custom_formatters = {"basic-iso-date": _formatter_basic_iso_date,
                     "basic-week-date": _formatter_basic_week_date,
                     "basic-week-date-time": _formatter_basic_week_date_time,
                     "basic-week-date-time-no-ms":
                     _formatter_basic_week_date_time_no_ms,
                     "iso-date": _formatter_iso_date,
                     "iso-date-time": _formatter_iso_date_time,
                     "iso-instant": _formatter_iso_instant,
                     "iso-local-date": _formatter_iso_local_date,
                     "iso-local-date-time": _formatter_iso_local_date_time,
                     "iso-local-time": _formatter_iso_local_time,
                     "iso-offset-date": _formatter_iso_offset_date,
                     "iso-offset-date-time": _formatter_iso_offset_date_time,
                     "iso-offset-time": _formatter_iso_offset_time,
                     "iso-ordinal-date": _formatter_iso_ordinal_date,
                     "iso-time": _formatter_iso_time,
                     "iso-week-date": _formatter_iso_week_date,
                     "iso-zoned-date-time": _formatter_iso_zoned_date_time,
                     "odata-format": _formatter_odata_format,
                     "rfc-1123-date-time": _formatter_rfc_1123_date_time,
                     "timestamp": _formatter_timestamp,
                     "timestamp-msecs": _formatter_timestamp_msecs,
                     "week-date": _formatter_week_date,
                     "week-date-time": _formatter_week_date_time,
                     "week-date-time-no-ms": _formatter_week_date_time_no_ms,
                     "weekyear-week": _formatter_weekyear_week,
                     "weekyear-week-day": _formatter_weekyear_week_day}

def _is_valid_format(fmt):
    return fmt in formats.dateformats.keys()

def _is_custom_format(fmt):
    return fmt == "[custom]"

def _get_formatter(format_name):
    if _is_valid_format(format_name):
        dateformat = formats.dateformats[format_name]
        if _is_custom_format(dateformat):
            return custom_formatters[format_name]
        else:
            return partial(_formatter_basic, dateformat)
    else:
        raise ValueError("Timeformat specified is not valid")

def parse_with_format(format_name, date):
    '''Creates a datetime object from a string representing a date
    and its format

    :param string format_name: The name of the date format
    :param string date: A string representing a datetime
    :raises: :class:`ValueError`: format_name not valid
    :raises: :class:`ValueError`: the date can't be parsed with format_name
    :returns: A Python date object
    :rtype: datetime
    '''
    formatter = _get_formatter(format_name)
    return formatter(date)

def _try_parse_with_format(format_name, date):
    output_date = None
    try:
        output_date = parse_with_format(format_name, date)
    except (ValueError, IndexError) as e:
        pass
    return output_date

def find_format(date):
    '''Finds the format name of a string representing a date.
    This format can be passed to the function parse_with_format
    to parse the date.

    :param string date: A string representing a datetime
    :raises: :class:`ValueError`: Cannot find a format
    :returns: The format of the date
    :rtype: string
    '''
    result = [[_try_parse_with_format(fmt,date), fmt] \
              for fmt in formats.dateformats]
    filtered_result = [item for item in result if item[0] is not None]
    if(len(filtered_result)==0):
        raise ValueError("Cannot find a format for the specified date")
    return filtered_result[0][1]

def parse(date):
    '''Creates a datetime object from a string representing a date
    trying all the possible formats

    :param string date: A string representing a datetime
    :raises: :class:`ValueError`: Cannot find a format for the date
    :returns: A Python date object
    :rtype: datetime
    '''
    date_format = find_format(date)
    return parse_with_format(date_format,date)
