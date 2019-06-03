# ------------------------------------------------------------------------------
# Joyous Holidays
# ------------------------------------------------------------------------------
import datetime as dt
from ..utils.manythings import hrJoin
from django.conf import settings
from .parser import parseHolidays

class Holidays:
    srcs = []

    @classmethod
    def register(self, src):
        self.srcs.append(src)

    @classmethod
    def parseSettings(self):
        holidaySettings = getattr(settings, "JOYOUS_HOLIDAYS", "")
        if holidaySettings:
            self.register(parseHolidays(holidaySettings))

    def __init__(self):
        pass

    def get(self, date):
        holidays = []
        for src in self.srcs:
            holiday = src.get(date)
            if holiday:
                holidays.append(holiday)
        return hrJoin(holidays)

# ------------------------------------------------------------------------------
