__author__ = 'SHASHANK'

from dateutil.parser import parse
from datetime import datetime
from dateutil import rrule
from .constants import SCHEME_HOLIDAYS, HOLIDAYS


class DateUtils:

    def __init__(self):
        rs = rrule.rruleset()
        [rs.exdate(datetime.strptime(HOLIDAY, "%Y-%m-%d")) for HOLIDAY in HOLIDAYS]

        r = rrule.rrule(rrule.YEARLY, count=366, byweekday=[rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR], dtstart=datetime.strptime("2019-01-01", "%Y-%m-%d"))
        rs.rrule(r)

        self.working_day_list = list(rs._iter())
        self.mf_scheme_non_working_day_list = {key: [datetime.strptime(val, "%Y-%m-%d") for val in vals] for (key, vals) in SCHEME_HOLIDAYS.items()}

    def get_next_date(self, date, days=1, orientation=1):

        if orientation:
            ind = min(self.working_day_list, key=lambda x: (date.date() - x.date()).days if x < date else 0)
            return self.working_day_list[self.working_day_list.index(ind) + days]
        else:
            ind = min(self.working_day_list, key=lambda x: (date.date() - x.date()).days if x < date else 5000)
            return self.working_day_list[self.working_day_list.index(ind) + days]

    def is_scheme_holiday(self, date, scheme_id):
        return date in self.mf_scheme_non_working_day_list.get(scheme_id, [])
