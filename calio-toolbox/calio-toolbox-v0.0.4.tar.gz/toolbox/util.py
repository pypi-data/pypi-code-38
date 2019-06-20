import pytz
from tzlocal import get_localzone

def same_date(utc_dt1, utc_dt2, timezone=None):
    #print(utc_dt1, utc_dt2)
    dt1 = pytz.utc.localize(utc_dt1)
    dt2 = pytz.utc.localize(utc_dt2)

    if timezone is None:
        local_tz = get_localzone()
    else:
        local_tz = pytz.timezone(timezone)

    local_dt1 = dt1.astimezone(local_tz)
    local_dt2 = dt2.astimezone(local_tz)

    #print(local_dt1.date(), local_dt2.date())
    return local_dt1.date() == local_dt2.date()

def dlog(msg):
    try:
        #traceback.print_stack()
        print(msg)
    except UnicodeDecodeError:
        print(msg.encode('utf-8'))

class bcolors:
    RED   = "\033[1;31m"
    BLUE  = "\033[1;34m"
    CYAN  = "\033[1;36m"
    GREEN = "\033[0;32m"
    RESET = "\033[0;0m"
    BOLD    = "\033[;1m"
    REVERSE = "\033[;7m"
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def red(str):
    return bcolors.RED + str + bcolors.RESET

def cyan(str):
    return bcolors.CYAN + str + bcolors.RESET

def green(str):
    return bcolors.GREEN + str + bcolors.RESET
