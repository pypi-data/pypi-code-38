# -*- coding: utf-8 -*-
from datetime import timedelta, datetime, time
from random import randrange
from string import Formatter
from warnings import warn

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware


def years_ago(years, from_date = None):
    if from_date is None:
        from_date = timezone.now()
    try:
        return from_date.replace(year = from_date.year - years)
    except:
        return from_date.replace(month = 2, day = 28, year = from_date.year - years)

# @og slabe rozwiazanie - do przebudowy
def get_default_start_date():
    warn(u"Use timezone.now() instead.", DeprecationWarning)
    return timezone.now().date()

# @og nie mozna podawac arg, do przebudowy!
def get_default_end_date(days_active):
    warn(u"Use in_14_days(), in_30_days(), in_60_days() or in_90_days() instead.", DeprecationWarning)
    return (timezone.now() + timedelta(days = days_active)).date()

def in_7_days():
    return timezone.now() + timedelta(days = 7)

def in_14_days():
    return timezone.now() + timedelta(days = 14)

def in_30_days():
    return timezone.now() + timedelta(days = 30)

def in_60_days():
    return timezone.now() + timedelta(days = 60)

def in_90_days():
    return timezone.now() + timedelta(days = 90)

def str_to_hour(value):
    warn(u"Use str_to_time() instead.", DeprecationWarning)
    return str_to_time(value)

def str_to_time(value, fmt = '%H:%M'):
    return datetime.strptime(value, fmt).time()

def hour_to_str(value):
    warn(u"Use time_to_str() instead.", DeprecationWarning)
    return time_to_str(value)

def time_to_str(value, fmt = '%H:%M'):
    return time.strftime(value, fmt)

def date_to_str(value, fmt = '%Y-%m-%d'):
    return datetime.strftime(value, fmt)

def datetime_to_str(value, fmt = '%Y-%m-%d %H:%M'):
    return datetime.strftime(value, fmt)

def timedelta_to_str(tdelta, fmt='{D:02}d {H:02}h {M:02}m {S:02}s', inputtype='timedelta'):
    """Convert a datetime.timedelta object or a regular number to a custom-
    formatted string, just like the stftime() method does for datetime.datetime
    objects.

    The fmt argument allows custom formatting to be specified.  Fields can 
    include seconds, minutes, hours, days, and weeks.  Each field is optional.

    Some examples:
        '{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s' (default)
        '{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
        '{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
        '{H}h {S}s'                       --> '72h 800s'

    The inputtype argument allows tdelta to be a regular number instead of the  
    default, which is a datetime.timedelta object.  Valid inputtype strings: 
        's', 'seconds', 
        'm', 'minutes', 
        'h', 'hours', 
        'd', 'days', 
        'w', 'weeks'
    """

    # Convert tdelta to integer seconds.
    if inputtype == 'timedelta':
        remainder = int(tdelta.total_seconds())
    elif inputtype in ['s', 'seconds']:
        remainder = int(tdelta)
    elif inputtype in ['m', 'minutes']:
        remainder = int(tdelta)*60
    elif inputtype in ['h', 'hours']:
        remainder = int(tdelta)*3600
    elif inputtype in ['d', 'days']:
        remainder = int(tdelta)*86400
    elif inputtype in ['w', 'weeks']:
        remainder = int(tdelta)*604800

    f = Formatter()
    desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
    possible_fields = ('W', 'D', 'H', 'M', 'S')
    constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    values = {}
    for field in possible_fields:
        if field in desired_fields and field in constants:
            values[field], remainder = divmod(remainder, constants[field])
    return f.format(fmt, **values)

def str_to_date(date_str, fmt = '%Y-%m-%d'):
    return datetime.strptime(date_str, fmt)

def str_to_datetime(date_str, fmt = '%Y-%m-%d %H:%M'):
    return datetime.strptime(date_str, fmt)

def str_to_aware_datetime(date_str):
    result = parse_datetime(date_str)
    if not is_aware(result):
        result = make_aware(result)
    return result

def daterange(start_date, end_date):
    for delta in range(int((end_date - start_date).days)):
        yield start_date + timedelta(days = delta + 1)

def check_timestamp(string, minutes = 3):
    try:
        timestamp = datetime.datetime.fromtimestamp(float(string))
        return abs(datetime.datetime.now() - timestamp) < datetime.timedelta(minutes = minutes)
    except ValueError:
        return False

def get_random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds = random_second)
