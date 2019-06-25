# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Iterator


def year_range(d1: datetime, d2: datetime) -> Iterator[datetime]:
    '''
    Get years from d1 to d2 inclusively. If the last year is beyond d2, it will not be returned.

    :param d1: start time.
    :type d1: datetime
    :param d2: end time.
    :type d2: datetime

    :return: years within the range.
    :rtype: Generator[datetime]
    '''
    while d1 <= d2:
        yield d1
        d1 += relativedelta(years=1)


def month_range(d1: datetime, d2: datetime) -> Iterator[datetime]:
    '''
    Get months from d1 to d2 inclusively. If the last month is beyond d2, it will not be returned.

    :param d1: start time.
    :type d1: datetime
    :param d2: end time.
    :type d2: datetime

    :return: months within the range.
    :rtype: Generator[datetime]
    '''
    while d1 <= d2:
        yield d1
        d1 += relativedelta(months=1)


def day_range(d1: datetime, d2: datetime) -> Iterator[datetime]:
    '''
    Get days from d1 to d2 inclusively. If the last day is beyond d2, it will not be returned.

    :param d1: start time.
    :type d1: datetime
    :param d2: end time.
    :type d2: datetime

    :return: days within the range.
    :rtype: Generator[datetime]
    '''
    while d1 <= d2:
        yield d1
        d1 += relativedelta(days=1)
