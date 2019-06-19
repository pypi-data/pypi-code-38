import arrow
from datetime import datetime
import pendulum
import re


def _human_to_dt(ts):
    t = arrow.utcnow()

    if ts == 'now':
        return t

    if ts == 'hour':
        return t.replace(minute=0, second=0, microsecond=0)

    if ts == 'day':
        return t.replace(hour=0, minute=0, second=0, microsecond=0)

    if ts == 'week':
        return t.replace(day=7, hour=0, minute=0, second=0, microsecond=0)

    if ts == 'month':
        return t.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _is_valid(ts):
    if isinstance(ts, arrow.Arrow):
        return ts

    t = _human_to_dt(ts)
    if t:
        return t

    try:
        t = pendulum.parse(ts)
    except pendulum.parsing.exceptions.ParserError:
        pass

    t = arrow.get(ts)
    if t:
        return t


def _format_ts(match):
    ts = '{}-{}-{}T{}:{}:{}Z'.format(match.group(1), match.group(2),
                                     match.group(3), match.group(4),
                                     match.group(5), match.group(6))

    t = arrow.get(ts, 'YYYY-MM-DDTHH:mm:ss')
    return t


def _fudge_arrow(ts):
    t = None
    try:
        t = arrow.get(ts)

    except ValueError as e:
        match = re.search(r'^(\d{4})(\d{2})(\d{2})T?(\d{2})(\d{2})(\d{2})Z?$',
                          ts)
        if match:
            return _format_ts(match)

    except arrow.parser.ParserError as e:
        return

    if not t:
        return

    if t.year > 1980:
        return t

    if type(ts) == datetime:
        ts = str(ts)

    if len(ts) == 8:
        ts = '{}T00:00:00Z'.format(ts)
        t = arrow.get(ts, 'YYYYMMDDTHH:mm:ss')

    if t.year < 1970:
        return


def parse_timestamp(ts):
    if isinstance(ts, datetime):
        return arrow.get(ts)

    valid = _is_valid(ts)
    if valid:
        return valid

    valid = _fudge_arrow(ts)
    if valid:
        return valid

    raise TypeError('Invalid Timestamp: %s' % ts)
