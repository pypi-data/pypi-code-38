from datetime import datetime
from tzlocal import get_localzone

local_timezone = get_localzone()

def local_now():
    time = local_timezone.localize(datetime.now())
    return time

def local_now_ios8061_str():
    time = local_now().strftime('%Y-%m-%dT%H:%M:%S%z')
    return time
