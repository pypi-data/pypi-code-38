from datetime import datetime, timedelta
import pytz
import time
import calendar

def _utc_to_local(utc_dt, tz):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(tz)
    return tz.normalize(local_dt)

def get_ist_date():
    india = pytz.timezone('Asia/Kolkata')
    x = _utc_to_local(datetime.utcnow(), india)
    return x.strftime('%Y-%m-%d')

def get_ist_time():
    india = pytz.timezone('Asia/Kolkata')
    x = _utc_to_local(datetime.utcnow(), india)
    return x.strftime('%H:%M:%S')

def get_ist_datetime():
    india = pytz.timezone('Asia/Kolkata')
    x = _utc_to_local(datetime.utcnow(), india)
    return x.strftime('%Y%m%d%H%M%S')


def get_hawker_date(day_gap):
    india = pytz.timezone('Asia/Kolkata')
    x = _utc_to_local(datetime.utcnow(), india)
    if day_gap != 0:
       x = _utc_to_local(datetime.utcnow() -  timedelta(days=day_gap), india)
    return x.strftime('%Y%m%d')

def get_epoch_date(hawker_time):
    t = time.strptime(hawker_time, '%Y%m%d%H%M%S')
    return int(calendar.timegm(t)/60)