import datetime


def now(local=False):
    if local:
        return datetime.datetime.now()
    else:
        return datetime.datetime.utcnow()


def delta(milliseconds=0):
    return datetime.timedelta(milliseconds=milliseconds)


MS = 1
SEC = 1000 * MS
MIN = 60 * SEC
HUR = 60 * MIN
DAY = 24 * HUR


def iso_format(sep='T'):
    return "%Y-%m-%d{sep}%H:%M:%S.%f".format(sep=sep)


def strf(dt, fmt=None):
    if dt is None:
        return None
    if fmt is None:
        fmt = iso_format(' ')
    return dt.strftime(fmt)


def strp(s, fmt=None):
    if s is None:
        return None
    if fmt is None:
        fmt = iso_format(' ')
    return datetime.datetime.strptime(s, fmt)