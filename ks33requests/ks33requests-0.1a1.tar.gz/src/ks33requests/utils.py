from datetime import datetime
from email.utils import formatdate
from time import mktime


def http_format_date(dt: datetime = None) -> str:
    if not dt:
        dt = datetime.now()
    stamp = mktime(dt.timetuple())
    return formatdate(timeval=stamp, localtime=False, usegmt=True)
