import re
from datetime import datetime
import pytz


class MassSpectrometerDateHandler:

    @staticmethod
    def convert_date_to_unix_time(date):
        year = MassSpectrometerDateHandler._extract_year(date)
        month = MassSpectrometerDateHandler._extract_month(date)
        day = MassSpectrometerDateHandler._extract_day(date)
        hour = MassSpectrometerDateHandler._extract_hour(date)
        mins = MassSpectrometerDateHandler._extract_mins(date)
        secs = MassSpectrometerDateHandler._extract_secs(date)
        microsecs = MassSpectrometerDateHandler._extract_microsecs(date)
        d = datetime(year, month, day, hour, mins, secs, microsecs, tzinfo=pytz.utc)
        return d.timestamp()

    @staticmethod
    def _extract_year(date):
        year = re.findall('\d\d\d\d', date)[0]
        return int(year)

    @staticmethod
    def _extract_month(date):
        month = re.findall('\d+(?=/)', date)[0]
        return int(month)

    @staticmethod
    def _extract_day(date):
        day = re.findall('(?<=/)\d+(?=/)', date)[0]
        return int(day)

    @staticmethod
    def _extract_hour(date):
        hour = re.findall('(?<=\s)\d+(?=:)', date)[0]
        if 'AM' in date:
            if int(hour) == 12:
                return 0
            return int(hour)
        if int(hour)== 12:
            return int(hour)
        return int(hour) + 12

    @staticmethod
    def _extract_mins(date):
        mins = re.findall('(?<=:)\d+(?=:)', date)[0]
        return int(mins)

    @staticmethod
    def _extract_secs(date):
        secs = re.findall('(?<=:)\d+', date)[1]
        return int(secs)

    @staticmethod
    def _extract_microsecs(date):
        millisecs = re.findall('(?<=\.)\d+', date)[0]
        return int(millisecs) * 1000
