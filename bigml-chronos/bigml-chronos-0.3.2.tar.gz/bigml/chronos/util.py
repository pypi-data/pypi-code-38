# -*- coding: utf-8 -*-
#!/usr/bin/env python

from datetime import datetime,timedelta
import sys
import re
import pytz

def try_read(date, read_fn, **kwargs):
    try:
        output_date =  read_fn(str(date), **kwargs)
    except Exception as e:
        raise ValueError("Date specified is not correct " + str(date))
    return output_date

def date_with_timezone(date, date_format, tz):
    hours = int(tz[1:3])
    minutes = int(tz[3:5])
    mod_date = date.replace(tz, "")
    parsed_date = datetime.strptime(mod_date, date_format)
    if(tz[0]=="+"):
        return parsed_date - timedelta(hours=hours, minutes=minutes)
    else:
        return parsed_date + timedelta(hours=hours, minutes=minutes)

def parse_timezoned_date(date, date_format, tz):
    mod_date_format = date_format.replace("%z","")
    if ("Z" in date):
        return datetime.strptime(date.replace("Z",""), mod_date_format)
    elif (len(tz) > 0):
        return date_with_timezone(date, mod_date_format, tz[-1][0])

def custom_strptime(date,date_format):
    tz = re.findall("((\+|-)[0-9]{4})", date)
    contains_tz = ("%z" in date_format and (("Z" in date) or (len(tz) > 0)))
    if(contains_tz and sys.version_info < (3,2,0)):
        return parse_timezoned_date(date, date_format, tz)
    elif("%z" in date_format):
        return datetime.strptime(date,date_format).astimezone(pytz.UTC)
    else:
        return datetime.strptime(date,date_format)

def read_week_date(weekdate, **kwargs):
    # Input format: 1969W291
    iso_year = int(weekdate.split("W")[0])
    iso_week = int(weekdate.split("W")[1][:2])
    iso_day =  int(weekdate.split("W")[1][-1])
    return iso_year, iso_week, iso_day

def read_iso_week_date_no_day(weekdate, **kwargs):
    # Input format: 1969-W29
    iso_year = int(weekdate[:4])
    iso_week = int(weekdate.split("W")[1][:2])
    return iso_year, iso_week

def read_iso_week_date(weekdate, **kwargs):
    # Input format: 1969-W29-1Z
    tz = kwargs.get("tz")
    iso_year, iso_week = read_iso_week_date_no_day(weekdate)
    iso_day =  int(weekdate.split("-")[-1][0])
    timezone = weekdate.split("-")[-1][1:] if tz else None
    return iso_year, iso_week, iso_day, timezone

def read_week_date_time(weekdatetime, **kwargs):
    # Input format: 1969W291T173639.592Z
    msecs = kwargs.get("msecs")
    if msecs:
        pattern, reset_hour =  "%H%M%S.%f%z", "000000.000Z"
    else:
        pattern, reset_hour =  "%H%M%S%z", "000000Z"
    (iso_year, iso_week, iso_day) = read_week_date(weekdatetime.split("T")[0])
    time = custom_strptime(weekdatetime.split("T")[1], pattern)
    only_time =  time - custom_strptime(reset_hour, pattern)
    return  iso_year, iso_week, iso_day, only_time

def read_hypen_week_date_time(weekdatetime, **kwargs):
    # Input format: 969-W29-1T17:36:39.592Z
    msecs = kwargs.get("msecs")
    if msecs:
        pattern, reset_hour =  "%H:%M:%S.%f%z", "00:00:00.000Z"
    else:
        pattern, reset_hour =  "%H:%M:%S%z", "00:00:00Z"
    weekdate = weekdatetime.split("T")[0]
    (iso_year, iso_week, iso_day, tz) = \
        read_iso_week_date(weekdate, tz=False)
    time = custom_strptime(weekdatetime.split("T")[1], pattern)
    only_time =  time - custom_strptime(reset_hour, pattern)
    return  iso_year, iso_week, iso_day, only_time

def weekdate(iso_year, iso_week, iso_weekday):
     # Input format: 1969W291
     weekdate = str(iso_year) + "W" + str(iso_week).zfill(2)
     weekdate +=  str(iso_weekday)
     return weekdate

def date_from_week(week, iso_day=0):
    iso_format = "%Y-%m-%d"
    return custom_strptime(week.day(iso_day-1).isoformat(), iso_format)
