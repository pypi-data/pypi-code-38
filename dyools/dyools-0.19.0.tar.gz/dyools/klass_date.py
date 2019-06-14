from __future__ import (absolute_import, division, print_function, unicode_literals)

import calendar
from datetime import datetime, date

from dateutil.parser import parse as dtparse
from dateutil.relativedelta import relativedelta
from past.builtins import basestring


class Date(object):
    DATE_HASH_FORMAT = '%Y%m%d'
    DATETIME_HASH_FORMAT = '%Y%m%d_%H%M%S'
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DATE_FR_FORMAT = "%d/%m/%Y"
    DATETIME_FR_FORMAT = "%d/%m/%Y %H:%M:%S"

    def __init__(self, *args, **kwargs):
        dt = False
        fmt = kwargs.pop('fmt', False)
        if len(args) == 1:
            item = args[0]
            if isinstance(item, basestring):
                if fmt:
                    dt = datetime.strptime(item, fmt)
                elif len(item) == 10:
                    fmt = self.DATE_FORMAT
                    dt = datetime.strptime(item, fmt)
                elif len(item) == 19:
                    fmt = self.DATETIME_FORMAT
                    dt = datetime.strptime(item, fmt)
                else:
                    dt = dtparse(item)
                    if ':' in item:
                        fmt = self.DATETIME_FORMAT
                    else:
                        fmt = self.DATE_FORMAT
            elif isinstance(item, datetime):
                dt = item
                fmt = fmt or self.DATETIME_FORMAT
            elif isinstance(item, date):
                dt = datetime(item.year, item.month, item.day)
                fmt = fmt or self.DATE_FORMAT
            elif isinstance(item, Date):
                dt = item.dt
                fmt = fmt or item.fmt
        else:
            if not args and not kwargs:
                dt = datetime.now()
            else:
                dt = datetime(*args, **kwargs)
            if len(args) + len(kwargs) == 3:
                fmt = fmt or self.DATE_FORMAT
            else:
                fmt = fmt or self.DATETIME_FORMAT
        assert fmt and dt, "The format of date [%s] is not valid" % item
        self.dt = dt
        self.fmt = fmt

    def relativedelta(self, **kwargs):
        self.apply(**kwargs)
        return self.dt.strftime(self.fmt)

    def apply(self, **kwargs):
        sub = kwargs.get('sub', False) == True
        if 'sub' in kwargs: del kwargs['sub']
        if sub:
            self.dt = self.dt - relativedelta(**kwargs)
        else:
            self.dt = self.dt + relativedelta(**kwargs)
        return self

    def set_format(self, fmt):
        self.fmt = fmt
        return self

    def first_day(self):
        dt = self.dt + relativedelta(day=1)
        return dt.strftime(self.fmt)

    def last_day(self):
        dt = self.dt + relativedelta(day=calendar.monthrange(self.dt.year, self.dt.month)[1])
        return dt.strftime(self.fmt)

    def to_datetime(self):
        return self.dt

    def to_date(self):
        return self.dt.date()

    def to_str(self, fmt=False):
        return self.dt.strftime(fmt or self.fmt)

    def to_fr(self):
        if self.fmt == self.DATE_FORMAT:
            return self.dt.strftime(self.DATE_FR_FORMAT)
        else:
            return self.dt.strftime(self.DATETIME_FR_FORMAT)

    def is_between(self, dt_start, dt_stop):
        dt_start = Date(dt_start) if dt_start else False
        dt_stop = Date(dt_stop) if dt_stop else False
        dt = self
        if dt_start and dt_stop:
            if dt_stop < dt_start:
                dt_start, dt_stop = dt_stop, dt_start
            return dt >= dt_start and dt <= dt_stop
        elif dt_start:
            return dt >= dt_start
        elif dt_stop:
            return dt <= dt_stop
        else:
            return True

    @classmethod
    def date_range(cls, dt_start, dt_stop=False, **kwargs):
        dt = Date(dt_start)
        stop = dt_stop
        if stop:
            dt_stop = Date(dt_stop)
        if not kwargs:
            kwargs = {'days': 1}
        while True:
            yield dt.to_str()
            dt = dt.apply(**kwargs)
            if stop and dt_stop.to_str() < dt.to_str():
                break

    def _apply_add_sub(self, other, sub=False):
        kwargs = {}
        mapping = {
            'y': 'years',
            'm': 'months',
            'd': 'days',
            'H': 'hours',
            'M': 'minutes',
            'S': 'seconds',
        }
        assert isinstance(other, (basestring, int)), "format of [%s] is invalid" % other
        if isinstance(other, basestring):
            coef = 1
            if other and other[0] in ['+', '-']:
                coef, other = other[0], other[1:]
                coef = -1 if coef == '-' else 1
            assert len(other) > 1 and other[-1] in mapping.keys(), "format of [%s] is invalid" % other
            assert other[:-1].isdigit(), "format of [%s] is invalid" % other
            kwargs[mapping[other[-1]]] = coef * int(other[:-1])
        elif isinstance(other, int):
            kwargs['days'] = other
        if sub: kwargs['sub'] = True
        return self.relativedelta(**kwargs)

    def __sub__(self, other):
        if isinstance(other, Date):
            return relativedelta(self.to_datetime(), other.to_datetime())
        return self._apply_add_sub(other, sub=True)

    def __add__(self, other):
        return self._apply_add_sub(other)

    def __str__(self):
        return self.dt.strftime(self.fmt)

    def __repr__(self):
        return self.dt.strftime(self.fmt)

    def __lt__(self, other):
        return self.to_str() < Date(other).to_str()

    def __le__(self, other):
        return self.to_str() <= Date(other).to_str()

    def __eq__(self, other):
        return self.to_str() == Date(other).to_str()

    def __ne__(self, other):
        return self.to_str() != Date(other).to_str()

    def __gt__(self, other):
        return self.to_str() > Date(other).to_str()

    def __ge__(self, other):
        return self.to_str() >= Date(other).to_str()
