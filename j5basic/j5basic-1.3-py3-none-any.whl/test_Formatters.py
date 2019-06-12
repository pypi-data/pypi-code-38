from j5test import IterativeTester
from j5test import DictDim
from j5basic import Formatters
import datetime

class FormatTestResource(object):
    def __init__(self,formatter,result_type,data_result_list):
        self.formatter = formatter
        self.result_type = result_type
        self.data_result_list = data_result_list # tuple of (input, result) pairs

class TestFormatters(IterativeTester.IterativeTester):

    FORMAT_TESTS = {
        'float': FormatTestResource(Formatters.FloatFormatter("%.2f"),Formatters.FormattedFloat,[
                    (5.5,"5.50"),
                    (10.617,"10.62"),
                    ("5.15","5.15"),
                    ('foo',None),
                    (Formatters.FormattedFloat("%.2f",10.2234),"10.22")
                 ]),
        'int': FormatTestResource(Formatters.IntFormatter("%03d"),Formatters.FormattedInt,[
                    (55,"055"),
                    (101,"101"),
                    ("515","515"),
                    ('foo',None),
                    ('5.5',None),
                    (Formatters.FormattedInt("%03d",55),"055")
                 ]),
        'datetime': FormatTestResource(Formatters.DatetimeFormatter("%Y:%m:%d %H:%M:%S"),Formatters.FormattedDatetime,[
                    (datetime.datetime(1993,11,3,12,51,50),"1993:11:03 12:51:50"),
                    ("1994:12:07 13:17:25","1994:12:07 13:17:25"),
                    ("1994:15:09 13:51:19",None),
                    (Formatters.FormattedDatetime("%Y:%m:%d %H:%M:%S",1996,9,3,12,51,50),"1996:09:03 12:51:50"),
                    (Formatters.FormattedDatetime("%Y:%m:%d %H:%M:%S",1896,9,3,12,51,50),"1896:09:03 12:51:50"),
                 ]),
        'time': FormatTestResource(Formatters.TimeFormatter("%H %S %M"),Formatters.FormattedTime,[
                    (datetime.time(21,51,12),"21 12 51"),
                    ("13 17 51","13 17 51"),
                    ("moo",None),
                    (Formatters.FormattedTime("%H %S %M",19,17,8),"19 08 17")
                 ]),
        'date': FormatTestResource(Formatters.DateFormatter("%Y %d %m"),Formatters.FormattedDate,[
                    (datetime.date(1987,11,30),"1987 30 11"),
                    ("1990 13 12","1990 13 12"),
                    ("moo",None),
                    (Formatters.FormattedDate("%Y %d %m",2001,11,5),"2001 05 11"),
                    (Formatters.FormattedDate("%Y %d %m",1801,11,5),"1801 05 11"),
                 ]),
        'loosedatetime': FormatTestResource(Formatters.LooseDatetimeFormatter("%Y:%m:%d %H:%M:%S"),Formatters.FormattedDatetime,[
                    (datetime.datetime(1994,12,6,15,51,52),"1994:12:06 15:51:52"),
                    ("1994:11:07 15:51:53","1994:11:07 15:51:53"),
                    ("2005:12:01","2005:12:01"),
                    ("15:51:02","15:51:02"),
                    ("12:01",None),
                    ("moo",None),
                    (Formatters.FormattedDatetime("%Y:%m:%d %H:%M:%S",1999,6,7,16,15,47),"1999:06:07 16:15:47"),
                    (Formatters.FormattedDatetime("%Y:%m:%d %H:%M:%S",1799,6,7,16,15,47),"1799:06:07 16:15:47"),
                 ]),
        # test unicode format strings. Some of the formatted times are unicode and some are not...
        'udatetime': FormatTestResource(Formatters.DatetimeFormatter("%Y:%m:%d %H:%M:%S"),Formatters.FormattedDatetime,[
                    (datetime.datetime(1993,11,3,12,51,50),"1993:11:03 12:51:50"),
                    ("1994:12:07 13:17:25","1994:12:07 13:17:25"),
                    ("1994:15:09 13:51:19",None),
                    (Formatters.FormattedDatetime("%Y:%m:%d %H:%M:%S",1996,9,3,12,51,50),"1996:09:03 12:51:50")
                 ]),
        'utime': FormatTestResource(Formatters.TimeFormatter("%H %S %M"),Formatters.FormattedTime,[
                    (datetime.time(21,51,12),"21 12 51"),
                    ("13 17 51","13 17 51"),
                    ("moo",None),
                    (Formatters.FormattedTime("%H %S %M",19,17,8),"19 08 17")
                 ]),
        'udate': FormatTestResource(Formatters.DateFormatter("%Y %d %m"),Formatters.FormattedDate,[
                    (datetime.date(1987,11,30),"1987 30 11"),
                    ("1990 13 12","1990 13 12"),
                    ("moo",None),
                    (Formatters.FormattedDate("%Y %d %m",2001,11,5),"2001 05 11")
                 ]),
        'uloosedatetime': FormatTestResource(Formatters.LooseDatetimeFormatter("%Y:%m:%d %H:%M:%S"),Formatters.FormattedDatetime,[
                    (datetime.datetime(1994,12,6,15,51,52),"1994:12:06 15:51:52"),
                    ("1994:11:07 15:51:53","1994:11:07 15:51:53"),
                    ("2005:12:01","2005:12:01"),
                    ("15:51:02","15:51:02"),
                    ("12:01",None),
                    ("moo",None),
                    (Formatters.FormattedDatetime("%Y:%m:%d %H:%M:%S",1999,6,7,16,15,47),"1999:06:07 16:15:47")
                 ]),
    }

    DIMENSIONS = { "ftest" : [ DictDim.DictDim(FORMAT_TESTS) ] }

    def ftest_format(self,formatresource):
        format = formatresource.formatter.format
        result_type = formatresource.result_type

        for data, expected in formatresource.data_result_list:
            result = format(data)
            if result is None:
                assert result == expected
            else:
                assert type(result) == result_type
                assert str(result) == expected

    def ftest_datetime_replace(self,formatresource):
        """Calling .replace(...) on FormattedDate* objects can result in
           FormattedDate* objects with missing attributes (unless prevented).
           """
        formatter = formatresource.formatter
        result_type = formatresource.result_type

        if not issubclass(result_type,datetime.date):
            return

        for i, (data, expected) in enumerate(formatresource.data_result_list):
            if expected is None:
                continue

            result = formatter.format(data)
            new = result.replace(year=result.year)

            if type(formatter) is Formatters.LooseDatetimeFormatter:
                assert(new.format_str)
            else:
                assert(new.format_str == result.format_str)


