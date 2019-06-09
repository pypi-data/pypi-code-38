import functools
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from dateutil.rrule import rrule, MONTHLY, YEARLY


DATESTR_FMT = "%Y%m%d"


def parse_date(date, fmt=None):
    if isinstance(date, datetime):
        d = date
    elif isinstance(date, str):
        d = parse(date)
    if fmt is not None:
        return d.strftime(fmt)
    return d


def get_first_date(date, of='year', fmt=None):
    d = parse_date(date)
    if of == 'year':
        y, m, d = d.year, 1, 1
    else:
        y, m, d = d.year, d.month, 1
    fdate = datetime(y, m, d)
    return parse_date(fdate, fmt=fmt)


def get_last_date(date, of='year', fmt=None):
    d = parse_date(date)
    if of == 'year':
        ndate = d + relativedelta(years=1)
    else:
        ndate = d + relativedelta(months=1)
    nfdate = get_first_date(ndate, of=of)
    ldate = nfdate - relativedelta(days=1)
    return parse_date(ldate, fmt=fmt)

 

def slice_date_range(start_date, end_date, by='year', fmt=DATESTR_FMT, **kwargs):
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    ini_start_date = get_first_date(start_date, of=by)
    fin_end_date = get_last_date(end_date, of=by)
    freq = YEARLY if by == 'year' else MONTHLY
    date_list = list(rrule(freq=freq, dtstart=ini_start_date,
                           until=fin_end_date, interval=1))
    if start_date not in date_list:
        date_list.insert(0, start_date)
    for i, d in enumerate(date_list):
        if d < start_date:
            continue
        s = d
        e = get_last_date(s, of=by)
        if e >= end_date:
            e = end_date
        yield parse_date(s, fmt), parse_date(e, fmt)

def slice_dates(by='month'):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, start_date=None, end_date=None, **kwargs):
            for s, e in slice_date_range(start_date, end_date, by=by, fmt=DATESTR_FMT, **kwargs):
                r = func(*args, start_date=s, end_date=e, **kwargs)
                yield r
        return wrapper
    return decorator
