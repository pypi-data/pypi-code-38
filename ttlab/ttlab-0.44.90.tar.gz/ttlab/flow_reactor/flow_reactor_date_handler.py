from datetime import datetime
import re
import pytz


class FlowReactorDateHandler:

    @staticmethod
    def convert_date_to_unix_time(date):
        year = FlowReactorDateHandler._extract_year(date)
        month = FlowReactorDateHandler._extract_month(date)
        day = FlowReactorDateHandler._extract_day(date)
        hour = FlowReactorDateHandler._extract_hour(date)
        mins = FlowReactorDateHandler._extract_mins(date)
        secs = FlowReactorDateHandler._extract_secs(date)
        d = datetime(year, month, day, hour, mins, secs, tzinfo=pytz.utc)
        return d.timestamp()

    @staticmethod
    def _extract_year(date):
        year = re.findall('\d\d\d\d', date)[0]
        return int(year)

    @staticmethod
    def _extract_month(date):
        month = re.findall('(?<=-)\d+(?=-)', date)[0]
        return int(month)

    @staticmethod
    def _extract_day(date):
        day = re.findall('(?<=-)\d+(?=\s)', date)[0]
        return int(day)

    @staticmethod
    def _extract_hour(date):
        hour = re.findall('(?<=\s)\d+(?=\.)', date)[0]
        return int(hour)

    @staticmethod
    def _extract_mins(date):
        mins = re.findall('(?<=\.)\d+(?=\.)', date)[0]
        return int(mins)

    @staticmethod
    def _extract_secs(date):
        secs = re.findall('(?<=\.)\d+', date)[1]
        return int(secs)

    @staticmethod
    def _extract_microsecs(date):
        millisecs = re.findall('(?<=\.)\d+', date)[0]
        return int(millisecs) * 1000
