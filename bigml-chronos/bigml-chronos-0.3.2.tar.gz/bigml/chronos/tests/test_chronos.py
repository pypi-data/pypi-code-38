# -*- coding: utf-8 -*-
#!/usr/bin/env python

from bigml.chronos import chronos, formats, util
from datetime import datetime, date, timedelta

original_date = datetime(1969, 7, 14, 17, 36, 39, 592000)
valid_dates = [["basic-date-time","19690714T173639.592Z"],
               ["basic-date-time","19690714T163639.592-0100"],
               ["basic-date-time","19690714T183639.592+0100"],
               ["basic-date-time","19690714T185639.592+0120"],
               ["basic-date-time-no-ms","19690714T173639Z"],
               ["basic-iso-date","19690714Z"],
               ["basic-ordinal-date-time","1969195T173639.592Z"],
               ["basic-ordinal-date-time-no-ms","1969195T173639Z"],
               ["basic-t-time","T173639.592Z"],
               ["basic-t-time-no-ms","T173639Z"],
               ["basic-time","173639.592Z"],
               ["basic-time-no-ms","173639Z"],
               ["basic-week-date","1969W291"],
               ["basic-week-date-time","1969W291T173639.592Z"],
               ["basic-week-date-time-no-ms","1969W291T173639Z"],
               ["clock-minute","5:36 PM"],
               ["clock-minute-nospace","5:36PM"],
               ["clock-second","5:36:39 PM"],
               ["clock-second-nospace","5:36:39PM"],
               ["date","1969-07-14"],
               ["date-hour","1969-07-14T17"],
               ["date-hour-minute","1969-07-14T17:36"],
               ["date-hour-minute-second","1969-07-14T17:36:39"],
               ["date-hour-minute-second-fraction","1969-07-14T17:36:39.592"],
               ["date-hour-minute-second-fraction-with-solidus",
                "1969/07/14T17:36:39.592"],
               ["date-hour-minute-second-ms","1969-07-14T17:36:39.592"],
               ["date-hour-minute-second-ms-with-solidus",
                "1969/07/14T17:36:39.592"],
               ["date-hour-minute-second-with-solidus","1969/07/14T17:36:39"],
               ["date-hour-minute-with-solidus","1969/07/14T17:36"],
               ["date-hour-with-solidus","1969/07/14T17"],
               ["date-time","1969-07-14T17:36:39.592Z"],
               ["date-time-no-ms","1969-07-14T17:36:39Z"],
               ["date-time-no-ms-with-solidus","1969/07/14T17:36:39Z"],
               ["date-time-with-solidus","1969/07/14T17:36:39.592Z"],
               ["date-with-solidus","1969/07/14"],
               ["eu-date","14/7/1969"],
               ["eu-date-clock-minute","14/7/1969 5:36 PM"],
               ["eu-date-clock-minute-nospace","14/7/1969 5:36PM"],
               ["eu-date-clock-second","14/7/1969 5:36:39 PM"],
               ["eu-date-clock-second-nospace","14/7/1969 5:36:39PM"],
               ["eu-date-millisecond","14/7/1969 17:36:39.592"],
               ["eu-date-minute","14/7/1969 17:36"],
               ["eu-date-second","14/7/1969 17:36:39"],
               ["eu-ddate","14.7.1969"],
               ["eu-ddate-clock-minute","14.7.1969 5:36 PM"],
               ["eu-ddate-clock-minute-nospace","14.7.1969 5:36PM"],
               ["eu-ddate-clock-second","14.7.1969 5:36:39 PM"],
               ["eu-ddate-clock-second-nospace","14.7.1969 5:36:39PM"],
               ["eu-ddate-millisecond","14.7.1969 17:36:39.592"],
               ["eu-ddate-minute","14.7.1969 17:36"],
               ["eu-ddate-second","14.7.1969 17:36:39"],
               ["eu-sdate","14-7-1969"],
               ["eu-sdate-clock-minute","14-7-1969 5:36 PM"],
               ["eu-sdate-clock-minute-nospace","14-7-1969 5:36PM"],
               ["eu-sdate-clock-second","14-7-1969 5:36:39 PM"],
               ["eu-sdate-clock-second-nospace","14-7-1969 5:36:39PM"],
               ["eu-sdate-millisecond","14-7-1969 17:36:39.592"],
               ["eu-sdate-minute","14-7-1969 17:36"],
               ["eu-sdate-second","14-7-1969 17:36:39"],
               ["hour-minute","17:36"],
               ["hour-minute-second","17:36:39"],
               ["hour-minute-second-fraction","17:36:39.592"],
               ["hour-minute-second-ms","17:36:39.592"],
               ["iso-date","1969-07-14Z"],
               ["iso-date-time","1969-07-14T17:36:39.592Z"],
               ["iso-instant","1969-07-14T17:36:39.592Z"],
               ["iso-local-date","1969-07-14"],
               ["iso-local-date-time","1969-07-14T17:36:39.592"],
               ["iso-local-time","17:36:39.592"],
               ["iso-offset-date","1969-07-14Z"],
               ["iso-offset-date-time","1969-07-14T17:36:39.592Z"],
               ["iso-offset-time","17:36:39.592Z"],
               ["iso-ordinal-date","1969-195Z"],
               ["iso-time","17:36:39.592Z"],
               ["iso-week-date","1969-W29-1Z"],
               ["iso-zoned-date-time","1969-07-14T17:36:39.592Z"],
               ["mysql","1969-07-14 17:36:39"],
               ["no-t-date-hour-minute","1969-7-14 17:36"],
               ["odata-format","/Date(-14711000408)/"],
               ["ordinal-date-time","1969-195T17:36:39.592Z"],
               ["ordinal-date-time-no-ms","1969-195T17:36:39Z"],
               ["rfc-1123-date-time","Mon, 14 Jul 1969 17:36:39 GMT"],
               ["rfc822","Mon, 14 Jul 1969 17:36:39 +0000"],
               ["t-time","T17:36:39.592Z"],
               ["t-time-no-ms","T17:36:39Z"],
               ["time","17:36:39.592Z"],
               ["time-no-ms","17:36:39Z"],
               ["timestamp","-14711000"],
               ["timestamp-msecs","-14711000408"],
               ["twitter-time","Mon Jul 14 17:36:39 +0000 1969"],
               ["twitter-time-alt","1969-7-14 17:36:39 +0000"],
               ["twitter-time-alt-2","1969-7-14 17:36 +0000"],
               ["twitter-time-alt-3","Mon Jul 14 17:36 +0000 1969"],
               ["us-date","7/14/1969"],
               ["us-date-clock-minute","7/14/1969 5:36 PM"],
               ["us-date-clock-minute-nospace","7/14/1969 5:36PM"],
               ["us-date-clock-second","7/14/1969 5:36:39 PM"],
               ["us-date-clock-second-nospace","7/14/1969 5:36:39PM"],
               ["us-date-millisecond","7/14/1969 17:36:39.592"],
               ["us-date-minute","7/14/1969 17:36"],
               ["us-date-second","7/14/1969 17:36:39"],
               ["us-sdate","7-14-1969"],
               ["us-sdate-clock-minute","7-14-1969 5:36 PM"],
               ["us-sdate-clock-minute-nospace","7-14-1969 5:36PM"],
               ["us-sdate-clock-second","7-14-1969 5:36:39 PM"],
               ["us-sdate-clock-second-nospace","7-14-1969 5:36:39PM"],
               ["us-sdate-millisecond","7-14-1969 17:36:39.592"],
               ["us-sdate-minute","7-14-1969 17:36"],
               ["us-sdate-second","7-14-1969 17:36:39"],
               ["week-date","1969-W29-1"],
               ["week-date-time","1969-W29-1T17:36:39.592Z"],
               ["week-date-time-no-ms","1969-W29-1T17:36:39Z"],
               ["weekyear-week","1969-W29"],
               ["weekyear-week-day","1969-W29-1"],
               ["year-month","1969-07"],
               ["year-month-day","1969-07-14"]]

def test_week_dates():
    '''The conversion from ISO8601 can be tricky. Even if some dates are
       correctly parsed, the parser may fail with others. Let's test
       many years.'''
    initial = date(1900,7,13)
    for i in range (365*200):
        test_date = initial + timedelta(days=i)
        (iso_year, iso_week, iso_weekday) = test_date.isocalendar()
        weekdate = util.weekdate(iso_year, iso_week, iso_weekday)
        assert test_date == chronos._formatter_basic_week_date(weekdate).date()

def check_date(output_date, format_name):
    if "year" in format_name:
        assert original_date.year == output_date.year
    if "month" in format_name:
        assert original_date.month == output_date.month
    if "date" in format_name:
        assert original_date.year == output_date.year
        assert original_date.month == output_date.month
        assert original_date.day == output_date.day
    if "hour" in format_name:
        assert original_date.hour == output_date.hour
    if "minute" in format_name:
        assert original_date.minute == output_date.minute
    if "second" in format_name:
        assert original_date.second == output_date.second
    if "time" in format_name:
        assert original_date.hour == output_date.hour
        assert original_date.minute == output_date.minute

def test_valid_dates():
    for item in valid_dates:
        output = chronos.parse_with_format(item[0], item[1])
        check_date(output, item[0])

def test_without_format():
    chronos.parse("1969-07-14")
    chronos.parse("Mon Jul 14 17:36 +0000 1969")
    chronos.parse("1969-W29-1T17:36:39Z")
    chronos.parse("7/14/1969 5:36:39PM")
    chronos.parse("14/7/1969 5:36 PM")

def test_check_everything_tested():
    dateformats = set(formats.dateformats.keys())
    testformats = set([f[0] for f in valid_dates])
    to_test = dateformats - testformats
    assert len(to_test)==0, "There are some formats not tested: " + str(to_test)
    return
