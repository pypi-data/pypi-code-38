import calendar
import time
import os
import json

import datetime
from decimal import Decimal

RATE_PRECISION_MULTIPLIER = Decimal(10 ** 4)


def rate_to_int(r: Decimal) -> int:
    return int(r * RATE_PRECISION_MULTIPLIER)


def str_to_eth_time(datestr) -> int:
    """

    :param datestr: is in this format, with a UTC timezone: 'Jul 9, 2009 @ 20:02:58 UTC'
    :return: unix time, used to represent time in Nomisma contracts
    """
    return calendar.timegm(time.strptime(datestr, '%b %d, %Y @ %H:%M:%S UTC'))


def from_abi(name):
    with open(os.path.join(os.path.dirname(__file__), 'abi', name)) as f:
        return json.load(f)


def datetime_to_eth_time(d: datetime.datetime) -> int:
    return int(d.timestamp())


def date_to_eth_time(d: datetime.date) -> int:
    return int(datetime.datetime.combine(d, datetime.time(0, 0, 0, 0), tzinfo=datetime.timezone.utc).timestamp())
