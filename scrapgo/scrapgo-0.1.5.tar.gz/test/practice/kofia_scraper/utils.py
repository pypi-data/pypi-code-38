import functools
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from dateutil.rrule import rrule, MONTHLY, YEARLY

from .settings import OUTPUT_FILE_FORMAT, DEFAULT_AGO_DAYS, DATESTR_FMT, MIN_START_DATE
from scrapgo.lib.dataframe import TableFrame

def datetime2str(datetime, fmt=DATESTR_FMT, **kwargs):
    return datetime.strftime(fmt)


def get_today_str_date(fmt=DATESTR_FMT, **kwargs):
    today = datetime.today()
    str_today = today.strftime(fmt)
    return str_today


def get_ago_str_date(fmt=DATESTR_FMT, **kwargs):
    today = datetime.today()
    ago = today - relativedelta(**kwargs)
    str_ago = ago.strftime(fmt)
    return str_ago


def get_date_ago_range(start_date=None, end_date=None, days_ago=None, months_ago=None, years_ago=None, default_ago_days=7, **kwargs):
    end_date = end_date or get_today_str_date()

    if start_date:
        start_date = start_date
    elif days_ago:
        start_date = get_ago_str_date(days=days_ago)
    elif months_ago:
        start_date = get_ago_str_date(months=months_ago)
    elif years_ago:
        start_date = get_ago_str_date(years=years_ago)
    else:
        start_date = get_ago_str_date(days=default_ago_days)

    if start_date > end_date:
        raise ValueError('start_date > end_date')
    return start_date, end_date



def parse_date(date, fmt=None, **kwargs):
    if isinstance(date, datetime):
        d = date
    elif isinstance(date, str):
        d = parse(date)
    if fmt is not None:
        return d.strftime(fmt)
    return d


def get_first_date(date, of='year', fmt=None, **kwargs):
    d = parse_date(date)
    if of == 'year':
        y, m, d = d.year, 1, 1
    else:
        y, m, d = d.year, d.month, 1
    fdate = datetime(y, m, d)
    return parse_date(fdate, fmt=fmt)


def get_last_date(date, of='year', fmt=None, **kwargs):
    d = parse_date(date)
    if of == 'year':
        ndate = d + relativedelta(years=1)
    else:
        ndate = d + relativedelta(months=1)
    nfdate = get_first_date(ndate, of=of)
    ldate = nfdate - relativedelta(days=1)
    return parse_date(ldate, fmt=fmt)



def starts_after(table_name=None, date_column_name=None, where=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, start_date=None, end_date=None, output=None, **kwargs):
            if start_date is None:
                if output in OUTPUT_FILE_FORMAT:
                    start_date = get_ago_str_date(days=DEFAULT_AGO_DAYS)
                elif output in ['db'] and all((table_name, date_column_name)):
                    db = TableFrame(**kwargs)
                    start_date = db.max(table_name, date_column_name, where) or MIN_START_DATE
                else:
                    start_date = get_ago_str_date(days=DEFAULT_AGO_DAYS)
            if end_date is None:
                end_date = get_today_str_date()
            r = func(*args, start_date=start_date, end_date=end_date, output=output, **kwargs)
            return r
        return wrapper
    return decorator

def connect_db(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        db = TableFrame(**kwargs)
        return func(*args, db=db, **kwargs)
    return wrapper


def print_db_progress(total_count, index, print_on=1000, prefix="", postfix=""):
    if index % print_on == 0:
        now = datetime.now()
        pct = round((index*100)/total_count, 2)
        log = f"{prefix}{index}/{total_count}({pct}%) {now.strftime('%Y%m%d %H:%M:%S')}{postfix}"        
        print(log)
