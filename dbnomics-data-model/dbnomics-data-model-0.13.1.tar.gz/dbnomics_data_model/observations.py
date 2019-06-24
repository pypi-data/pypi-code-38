# dbnomics-data-model -- Define, validate and transform DBnomics data.
# By: Christophe Benz <christophe.benz@cepremap.org>
#
# Copyright (C) 2017-2018 Cepremap
# https://git.nomics.world/dbnomics/dbnomics-data-model
#
# dbnomics-data-model is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# dbnomics-data-model is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Functions manipulating time series observations in TSV format."""

import logging
import math
import re
from datetime import date, datetime, timedelta
from enum import Enum

from backports.datetime_fromisoformat import MonkeyPatch
from dateutil.relativedelta import relativedelta
from toolz import mapcat
from toolz.curried import get

MonkeyPatch.patch_fromisoformat()

log = logging.getLogger(__name__)


class Frequency(Enum):
    ANNUAL = 'annual'
    BI_ANNUAL = 'bi-annual'
    BI_MONTHLY = 'bi-monthly'
    QUARTERLY = 'quarterly'
    MONTHLY = 'monthly'
    WEEKLY = 'weekly'
    DAILY = 'daily'

    def to_dimension_code(self):
        return {
            Frequency.ANNUAL: "A",
            Frequency.BI_ANNUAL: "S",
            Frequency.BI_MONTHLY: "B",
            Frequency.QUARTERLY: "Q",
            Frequency.MONTHLY: "M",
            Frequency.WEEKLY: "W",
            Frequency.DAILY: "D",
        }[self]


day_range_re = "0[1-9]|[1-2][0-9]|3[0-1]"  # 01-31
month_range_re = "0[1-9]|1[0-2]"  # 01-12
week_range_re = "0[1-9]|[1-4][0-9]|5[0-3]"  # 01-53


period_format_strict_regex_list = [
    (Frequency.ANNUAL, re.compile(r"^(\d{4})$")),
    (Frequency.BI_ANNUAL, re.compile(r"^(\d{4})-S([1-2])$")),
    (Frequency.BI_MONTHLY, re.compile(r"^(\d{4})-B([1-6])$")),
    (Frequency.QUARTERLY, re.compile(r"^(\d{4})-Q([1-4])$")),
    (Frequency.MONTHLY, re.compile(r"^(\d{{4}})-({})$".format(month_range_re))),  # YYYY-[01-12]
    (Frequency.WEEKLY, re.compile(r"^(\d{{4}})-W({})$".format(week_range_re))),  # YYYY-W[01-53]
    # YYYY-[01-12]-[01-31]
    (Frequency.DAILY, re.compile(r"^(\d{{4}})-({})-({})$".format(month_range_re, day_range_re))),
]
NOT_AVAILABLE = "NA"


def iter_periods_dates(frequency: Frequency, min_date: date, max_date: date = None):
    current_date = min_date
    while True:
        yield current_date
        if max_date is not None and current_date >= max_date:
            break
        current_date = next_period_date(current_date, frequency)


def next_period_date(period_date: date, frequency: Frequency):
    """Return next period date, applying an increment to `period_date` corresponding to `frequency`.

    >>> next_period_date(date(2000, 1, 1), Frequency.ANNUAL)
    datetime.date(2001, 1, 1)
    >>> next_period_date(date(2000, 1, 1), Frequency.BI_ANNUAL)
    datetime.date(2000, 7, 1)
    >>> next_period_date(date(2000, 1, 1), Frequency.BI_MONTHLY)
    datetime.date(2000, 3, 1)
    >>> next_period_date(date(2000, 1, 1), Frequency.QUARTERLY)
    datetime.date(2000, 4, 1)
    >>> next_period_date(date(2000, 1, 1), Frequency.MONTHLY)
    datetime.date(2000, 2, 1)
    >>> next_period_date(date(2000, 1, 1), Frequency.WEEKLY)
    datetime.date(2000, 1, 8)
    >>> next_period_date(date(2000, 1, 1), Frequency.DAILY)
    datetime.date(2000, 1, 2)
    """
    if frequency == Frequency.ANNUAL:
        return period_date + relativedelta(years=1)
    elif frequency == Frequency.BI_ANNUAL:
        return period_date + relativedelta(months=6)
    elif frequency == Frequency.BI_MONTHLY:
        return period_date + relativedelta(months=2)
    elif frequency == Frequency.QUARTERLY:
        return period_date + relativedelta(months=3)
    elif frequency == Frequency.MONTHLY:
        return period_date + relativedelta(months=1)
    elif frequency == Frequency.WEEKLY:
        return period_date + relativedelta(weeks=1)
    elif frequency == Frequency.DAILY:
        return period_date + timedelta(days=1)
    else:
        assert False, frequency


def complete_series(periods_dates, values, frequency: Frequency,
                    all_periods_dates=None, complete_missing_periods=False):
    """Complete series by adding missing periods and "NA" (not available) values if missing.

    >>> complete_series([], [], Frequency.ANNUAL)
    ([], [])
    >>> complete_series([date(2000, 1, 1)], [10], Frequency.ANNUAL)
    ([datetime.date(2000, 1, 1)], [10])
    >>> complete_series([date(2000, 1, 1), date(2001, 1, 1)], [10, 11], Frequency.ANNUAL)
    ([datetime.date(2000, 1, 1), datetime.date(2001, 1, 1)], [10, 11])
    >>> complete_series([date(2000, 1, 1), date(2002, 1, 1)], [10, 12], Frequency.ANNUAL, complete_missing_periods=True)
    ([datetime.date(2000, 1, 1), datetime.date(2001, 1, 1), datetime.date(2002, 1, 1)], [10, 'NA', 12])
    >>> complete_series([date(2000, 1, 1), date(2002, 1, 1)], [10, 12], Frequency.ANNUAL, all_periods_dates=[date(1998, 1, 1), date(1999, 1, 1), date(2000, 1, 1), date(2002, 1, 1), date(2003, 1, 1)])
    ([datetime.date(1998, 1, 1), datetime.date(1999, 1, 1), datetime.date(2000, 1, 1), datetime.date(2002, 1, 1), datetime.date(2003, 1, 1)], ['NA', 'NA', 10, 12, 'NA'])
    >>> complete_series([date(2000, 1, 1), date(2002, 1, 1)], [10, 12], Frequency.ANNUAL, complete_missing_periods=True, all_periods_dates=[date(1998, 1, 1), date(1999, 1, 1), date(2000, 1, 1), date(2002, 1, 1), date(2003, 1, 1)])
    ([datetime.date(1998, 1, 1), datetime.date(1999, 1, 1), datetime.date(2000, 1, 1), datetime.date(2001, 1, 1), datetime.date(2002, 1, 1), datetime.date(2003, 1, 1)], ['NA', 'NA', 10, 'NA', 12, 'NA'])
    """
    assert len(periods_dates) == len(values), (periods_dates, values)
    if not periods_dates:
        return ([], [])

    completed_periods_dates = []
    completed_values = []
    value_by_period_date = dict(zip(periods_dates, values))
    for expected_period_date in iter_periods_dates(
            frequency,
            min_date=min(all_periods_dates) if all_periods_dates is not None else periods_dates[0],
            max_date=max(all_periods_dates) if all_periods_dates is not None else periods_dates[-1]):
        value = value_by_period_date.get(expected_period_date)
        if value is not None or complete_missing_periods or expected_period_date in all_periods_dates:
            completed_periods_dates.append(expected_period_date)
            completed_values.append(value if value is not None else NOT_AVAILABLE)
    return (completed_periods_dates, completed_values)


def complete_series_list(periods_dates_and_values_list, frequency: Frequency,
                         align_periods=False, complete_missing_periods=False):
    """Complete many series.

    See also: `complete_series`.

    >>> complete_series_list([], Frequency.ANNUAL)
    []

    # Annual:
    >>> complete_series_list([([date(2000, 1, 1), date(2001, 1, 1)], [10, 11]), ([date(2001, 1, 1), date(2002, 1, 1)], [21, 22])], Frequency.ANNUAL)
    [([datetime.date(2000, 1, 1), datetime.date(2001, 1, 1)], [10, 11]), ([datetime.date(2001, 1, 1), datetime.date(2002, 1, 1)], [21, 22])]
    >>> complete_series_list([([date(2000, 1, 1), date(2001, 1, 1)], [10, 11]), ([date(2001, 1, 1), date(2002, 1, 1)], [21, 22])], Frequency.ANNUAL, align_periods=True)
    [([datetime.date(2000, 1, 1), datetime.date(2001, 1, 1), datetime.date(2002, 1, 1)], [10, 11, 'NA']), ([datetime.date(2000, 1, 1), datetime.date(2001, 1, 1), datetime.date(2002, 1, 1)], ['NA', 21, 22])]
    >>> complete_series_list([([date(2000, 1, 1), date(2001, 1, 1)], [10, 11]), ([date(2001, 1, 1), date(2003, 1, 1)], [21, 22])], Frequency.ANNUAL, complete_missing_periods=True)
    [([datetime.date(2000, 1, 1), datetime.date(2001, 1, 1)], [10, 11]), ([datetime.date(2001, 1, 1), datetime.date(2002, 1, 1), datetime.date(2003, 1, 1)], [21, 'NA', 22])]
    >>> complete_series_list([([date(2000, 1, 1), date(2001, 1, 1)], [10, 11]), ([date(2001, 1, 1), date(2003, 1, 1)], [21, 22])], Frequency.ANNUAL, align_periods=True, complete_missing_periods=True)
    [([datetime.date(2000, 1, 1), datetime.date(2001, 1, 1), datetime.date(2002, 1, 1), datetime.date(2003, 1, 1)], [10, 11, 'NA', 'NA']), ([datetime.date(2000, 1, 1), datetime.date(2001, 1, 1), datetime.date(2002, 1, 1), datetime.date(2003, 1, 1)], ['NA', 21, 'NA', 22])]

    # Monthly:
    >>> complete_series_list([([date(2000, 1, 1), date(2000, 2, 1)], [10, 11]), ([date(2000, 2, 1), date(2000, 3, 1)], [21, 22])], Frequency.MONTHLY)
    [([datetime.date(2000, 1, 1), datetime.date(2000, 2, 1)], [10, 11]), ([datetime.date(2000, 2, 1), datetime.date(2000, 3, 1)], [21, 22])]
    >>> complete_series_list([([date(2000, 1, 1), date(2000, 2, 1)], [10, 11]), ([date(2000, 2, 1), date(2000, 3, 1)], [21, 22])], Frequency.MONTHLY, align_periods=True)
    [([datetime.date(2000, 1, 1), datetime.date(2000, 2, 1), datetime.date(2000, 3, 1)], [10, 11, 'NA']), ([datetime.date(2000, 1, 1), datetime.date(2000, 2, 1), datetime.date(2000, 3, 1)], ['NA', 21, 22])]
    """
    if not periods_dates_and_values_list:
        return []

    all_periods_dates = set(mapcat(lambda pair: pair[0], periods_dates_and_values_list)) \
        if align_periods \
        else None
    return [
        complete_series(periods_dates, values, frequency, all_periods_dates=all_periods_dates,
                        complete_missing_periods=complete_missing_periods)
        for periods_dates, values in periods_dates_and_values_list
    ]


def detect_frequency(period1, period2):
    """Return a tuple like `(frequency, normalize_period)` for the given `period`.

    `normalize_period` can be `None` if periods are already normalized,
    or a function taking a period as `str` and returning a normalized period as `str`.

    When the format of the periods is "daily", the frequency can be different,
    depending on the interval between the days (e.g. the frequency can be "quarterly" if the interval is 3 months).
    That's the purpose of this function, compared to `detect_period_format` which takes one period only.

    See also: `detect_period_format`, `detect_period_format_strict`

    # From period format corresponding to frequency:
    >>> detect_frequency('2014', '2015')
    (<Frequency.ANNUAL: 'annual'>, None)
    >>> detect_frequency('2014', '2016')
    (<Frequency.ANNUAL: 'annual'>, None)
    >>> detect_frequency('2014-S1', '2014-S2')
    (<Frequency.BI_ANNUAL: 'bi-annual'>, None)
    >>> detect_frequency('2014-S1', '2015-S2')
    (<Frequency.BI_ANNUAL: 'bi-annual'>, None)
    >>> detect_frequency('2014-Q1', '2014-Q2')
    (<Frequency.QUARTERLY: 'quarterly'>, None)
    >>> detect_frequency('2014-Q1', '2014-Q3')
    (<Frequency.QUARTERLY: 'quarterly'>, None)
    >>> detect_frequency('2014-B1', '2014-B2')
    (<Frequency.BI_MONTHLY: 'bi-monthly'>, None)
    >>> detect_frequency('2014-B1', '2014-B3')
    (<Frequency.BI_MONTHLY: 'bi-monthly'>, None)
    >>> detect_frequency('2014-01', '2014-02')
    (<Frequency.MONTHLY: 'monthly'>, None)
    >>> detect_frequency('2014-01', '2014-03')
    (<Frequency.MONTHLY: 'monthly'>, None)
    >>> detect_frequency('2014-W01', '2014-W02')
    (<Frequency.WEEKLY: 'weekly'>, None)
    >>> detect_frequency('2014-W01', '2014-W03')
    (<Frequency.WEEKLY: 'weekly'>, None)
    >>> detect_frequency('2014-01-01', '2014-01-02')
    (<Frequency.DAILY: 'daily'>, None)
    >>> detect_frequency('2014-01-01', '2014-01-03')
    (<Frequency.DAILY: 'daily'>, None)

    # From daily period format:
    >>> detect_frequency('2014-01-01', '2015-01-01')  # doctest: +ELLIPSIS
    (<Frequency.ANNUAL: 'annual'>, ...)
    >>> detect_frequency('2014-01-01', '2014-07-01')  # doctest: +ELLIPSIS
    (<Frequency.BI_ANNUAL: 'bi-annual'>, ...)
    >>> detect_frequency('2014-01-01', '2014-04-01')  # doctest: +ELLIPSIS
    (<Frequency.QUARTERLY: 'quarterly'>, ...)
    >>> detect_frequency('1919-03-31', '1919-06-30')  # doctest: +ELLIPSIS
    (<Frequency.QUARTERLY: 'quarterly'>, ...)
    >>> detect_frequency('2014-01-01', '2014-03-01')  # doctest: +ELLIPSIS
    (<Frequency.BI_MONTHLY: 'bi-monthly'>, ...)
    >>> detect_frequency('2014-01-01', '2014-02-01')  # doctest: +ELLIPSIS
    (<Frequency.MONTHLY: 'monthly'>, ...)
    >>> detect_frequency('2014-01-01', '2014-01-08')  # doctest: +ELLIPSIS
    (<Frequency.WEEKLY: 'weekly'>, ...)

    # Invalid or different period formats:
    >>> detect_frequency('2014', '2015-02')
    (None, None)
    >>> detect_frequency('2014', '2014Z2')
    (None, None)
    >>> detect_frequency('2014Z2', '2014')
    (None, None)
    >>> detect_frequency('2014Z2', '2014Z2')
    (None, None)
    """

    def make_normalize_period(frequency):
        def normalize_period(period):
            period_date = datetime.fromisoformat(period)
            return start_day_to_period(period_date, frequency)
        return normalize_period

    period1_format, normalize_period = detect_period_format(period1)
    period2_format, _ = detect_period_format(period2)

    if period1_format != period2_format:
        log.error("The 2 periods do not have the same format {!r}".format(
            ((period1, period1_format), (period2, period2_format))))
        return (None, None)

    elif period1_format == Frequency.DAILY:
        # Measure the interval between the two periods.
        date_1 = datetime.fromisoformat(period1)
        date_2 = datetime.fromisoformat(period2)
        date_diff = relativedelta(date_2, date_1)
        if date_diff.days == 1:
            return (Frequency.DAILY, None)
        elif date_diff.weeks == 1:
            return (Frequency.WEEKLY, make_normalize_period(Frequency.WEEKLY))
        elif date_diff.months == 1:
            return (Frequency.MONTHLY, make_normalize_period(Frequency.MONTHLY))
        elif date_diff.months == 2:
            return (Frequency.BI_MONTHLY, make_normalize_period(Frequency.BI_MONTHLY))
        elif date_diff.months == 3:
            return (Frequency.QUARTERLY, make_normalize_period(Frequency.QUARTERLY))
        elif date_diff.months == 6:
            return (Frequency.BI_ANNUAL, make_normalize_period(Frequency.BI_ANNUAL))
        elif date_diff.years == 1:
            return (Frequency.ANNUAL, make_normalize_period(Frequency.ANNUAL))
        else:
            # No specific interval detected, keep daily.
            return (Frequency.DAILY, None)

    return (period1_format, normalize_period)


def detect_period_format(period):
    """Return a tuple like `(period_format, normalize_period)` for the given `period`.

    `normalize_period` can be `None` if period is already normalized,
    or a function taking a period as `str` and returning a normalized period as `str`.

    First, the period format is detected using `detect_period_format_strict`.
    If not found, try to detect non-standard formats, among a variety of well-known invalid ones.

    Periods formats are described in [DBnomics data model](https://git.nomics.world/dbnomics/dbnomics-data-model/).

    See also: `detect_period_format_strict`, `detect_frequency`

    # Working examples:
    >>> detect_period_format("2014")
    (<Frequency.ANNUAL: 'annual'>, None)
    >>> detect_period_format("2014-S1")
    (<Frequency.BI_ANNUAL: 'bi-annual'>, None)
    >>> detect_period_format("2014-B1")
    (<Frequency.BI_MONTHLY: 'bi-monthly'>, None)
    >>> detect_period_format("2014-Q1")
    (<Frequency.QUARTERLY: 'quarterly'>, None)
    >>> detect_period_format("2014-01")
    (<Frequency.MONTHLY: 'monthly'>, None)
    >>> detect_period_format("2014-W01")
    (<Frequency.WEEKLY: 'weekly'>, None)
    >>> detect_period_format("2015-W53")
    (<Frequency.WEEKLY: 'weekly'>, None)
    >>> detect_period_format("2014-12-01")
    (<Frequency.DAILY: 'daily'>, None)
    >>> detect_period_format("2004-05-20")
    (<Frequency.DAILY: 'daily'>, None)

    # Unrecoverable overflow errors:
    >>> detect_period_format("2014-S3")
    (None, None)
    >>> detect_period_format("2014-B7")
    (None, None)
    >>> detect_period_format("2014-Q5")
    (None, None)
    >>> detect_period_format("2014-W54")
    (None, None)
    >>> detect_period_format("2014-12-32")
    (None, None)

    # Recoverable padding errors:
    >>> detect_period_format("2014-S01")  # doctest: +ELLIPSIS
    (<Frequency.BI_ANNUAL: 'bi-annual'>, ...)
    >>> detect_period_format("2014-B01")  # doctest: +ELLIPSIS
    (<Frequency.BI_MONTHLY: 'bi-monthly'>, ...)
    >>> detect_period_format("2014-Q01")  # doctest: +ELLIPSIS
    (<Frequency.QUARTERLY: 'quarterly'>, ...)
    >>> detect_period_format("2014-1")  # doctest: +ELLIPSIS
    (<Frequency.MONTHLY: 'monthly'>, ...)
    >>> detect_period_format("2014-W1")  # doctest: +ELLIPSIS
    (<Frequency.WEEKLY: 'weekly'>, ...)
    >>> detect_period_format("2014-12-1")  # doctest: +ELLIPSIS
    (<Frequency.DAILY: 'daily'>, ...)

    # Recoverable missing hyphen errors:
    >>> detect_period_format("2014S1")  # doctest: +ELLIPSIS
    (<Frequency.BI_ANNUAL: 'bi-annual'>, ...)
    >>> detect_period_format("2014B1")  # doctest: +ELLIPSIS
    (<Frequency.BI_MONTHLY: 'bi-monthly'>, ...)
    >>> detect_period_format("2014Q1")  # doctest: +ELLIPSIS
    (<Frequency.QUARTERLY: 'quarterly'>, ...)
    >>> detect_period_format("2014Q01")  # doctest: +ELLIPSIS
    (<Frequency.QUARTERLY: 'quarterly'>, ...)
    >>> detect_period_format("2014W1")  # doctest: +ELLIPSIS
    (<Frequency.WEEKLY: 'weekly'>, ...)
    >>> detect_period_format("2014W01")  # doctest: +ELLIPSIS
    (<Frequency.WEEKLY: 'weekly'>, ...)

    # Recoverable space errors:
    >>> detect_period_format("2014 S1")  # doctest: +ELLIPSIS
    (<Frequency.BI_ANNUAL: 'bi-annual'>, ...)
    >>> detect_period_format("2014 B1")  # doctest: +ELLIPSIS
    (<Frequency.BI_MONTHLY: 'bi-monthly'>, ...)
    >>> detect_period_format("2014 Q1")  # doctest: +ELLIPSIS
    (<Frequency.QUARTERLY: 'quarterly'>, ...)
    >>> detect_period_format("2014 Q01")  # doctest: +ELLIPSIS
    (<Frequency.QUARTERLY: 'quarterly'>, ...)
    >>> detect_period_format("2014 W1")  # doctest: +ELLIPSIS
    (<Frequency.WEEKLY: 'weekly'>, ...)
    >>> detect_period_format("2014 W01")  # doctest: +ELLIPSIS
    (<Frequency.WEEKLY: 'weekly'>, ...)

    # Unrecoverable missing hyphen errors:
    >>> detect_period_format("2014S3")
    (None, None)
    >>> detect_period_format("2014Q5")
    (None, None)
    >>> detect_period_format("2014Q05")
    (None, None)
    >>> detect_period_format("2014W54")
    (None, None)

    # Invalid formats:
    >>> detect_period_format("ABCDE")
    (None, None)
    >>> detect_period_format("2014Z01")
    (None, None)
    """

    # First try to detect the period format in a strict manner.

    period_format = detect_period_format_strict(period)
    if period_format is not None:
        return (period_format, None)

    # Fallback: try to detect non-standard period formats.

    def normalize_period(format_match):
        def _normalize_period(period):
            match = regex.match(period)
            return format_match(match) if match is not None else period
        return _normalize_period

    for period_format, regex, format_match in [
        (
            Frequency.BI_ANNUAL,
            re.compile(r"^(\d{4})[-\s]*[sS]0*([1-2])$"),
            lambda match: "{0}-S{1}".format(*match.groups()),
        ),
        (
            Frequency.BI_MONTHLY,
            re.compile(r"^(\d{4})[-\s]*[bB]0*([1-6])$"),
            lambda match: "{0}-B{1}".format(*match.groups()),
        ),
        (
            Frequency.QUARTERLY,
            re.compile(r"^(\d{4})[-\s]*[qQ]0*([1-4])$"),
            lambda match: "{0}-Q{1}".format(*match.groups()),
        ),
        (
            Frequency.MONTHLY,
            re.compile(r"^(\d{4})[-\s]*[mM]?0*(\d{1,2})$"),
            lambda match: "{0}-{1:>02}".format(*match.groups()),
        ),
        (
            Frequency.WEEKLY,
            re.compile(r"^(\d{4})[-\s]*[wW]0*([1-9]|[1-4][0-9]|5[0-2])$"),
            lambda match: "{0}-W{1:>02}".format(*match.groups()),
        ),
        (
            Frequency.DAILY,
            re.compile(r"^(\d{4})[-\s]*(0[1-9]|1[0-2])[-\s]*(0[1-9]|[1-9]|[1-2][0-9]|3[0-1])$"),
            lambda match: "{0}-{1:>02}-{1:>02}".format(*match.groups()),
        ),
    ]:
        match = regex.match(period)
        if match is not None:
            return (period_format, normalize_period(format_match))

    return (None, None)


def detect_period_format_strict(period):
    """Return a period format as `str` for the given `period`, or `None` if unable to detect.

    Periods formats are described in [DBnomics data model](https://git.nomics.world/dbnomics/dbnomics-data-model/).

    See also: `detect_period_format`, `detect_frequency`

    # Working examples:
    >>> detect_period_format_strict("2014")
    <Frequency.ANNUAL: 'annual'>
    >>> detect_period_format_strict("2014-S1")
    <Frequency.BI_ANNUAL: 'bi-annual'>
    >>> detect_period_format_strict("2014-B1")
    <Frequency.BI_MONTHLY: 'bi-monthly'>
    >>> detect_period_format_strict("2014-Q1")
    <Frequency.QUARTERLY: 'quarterly'>
    >>> detect_period_format_strict("2014-01")
    <Frequency.MONTHLY: 'monthly'>
    >>> detect_period_format_strict("2014-W01")
    <Frequency.WEEKLY: 'weekly'>
    >>> detect_period_format_strict("2015-W53")
    <Frequency.WEEKLY: 'weekly'>
    >>> detect_period_format_strict("2014-12-01")
    <Frequency.DAILY: 'daily'>
    >>> detect_period_format_strict("2004-05-20")
    <Frequency.DAILY: 'daily'>

    # Overflow errors:
    >>> detect_period_format_strict("2014-S0")
    >>> detect_period_format_strict("2014-S3")
    >>> detect_period_format_strict("2014-B0")
    >>> detect_period_format_strict("2014-B7")
    >>> detect_period_format_strict("2014-Q0")
    >>> detect_period_format_strict("2014-Q5")
    >>> detect_period_format_strict("2014-W00")
    >>> detect_period_format_strict("2014-W54")
    >>> detect_period_format_strict("2014-12-00")
    >>> detect_period_format_strict("2014-12-32")

    # Invalid formats:
    >>> detect_period_format_strict("ABCDE")
    >>> detect_period_format_strict("2014Z01")
    """
    for period_format, regex in period_format_strict_regex_list:
        if regex.match(period):
            return period_format
    return None


def iter_tsv_decoded_rows(raw_rows):
    for index, row in enumerate(raw_rows):
        if index > 0 and len(row) > 1:
            row = row[:]  # Do a shallow copy of row
            row[1] = value_to_float(row[1])
        yield row


def iter_tsv_rows(tsv_io):
    r"""Yield rows from a TSV as `StringIO`.
    Each row is a `list` like `[period, value, attribute1, attribute2, ...]`.
    The first row is the header. Attributes are optional.

    Examples:
    >>> from io import StringIO
    >>> def test(s): return list(iter_tsv_rows(StringIO(s)))
    >>> test("")
    []
    >>> test("     ")
    [['     ']]
    >>> test("period\tvalue")
    [['period', 'value']]
    >>> test("period\tvalue\n")
    [['period', 'value']]
    >>> test("period\tvalue\n2018\t0.2")
    [['period', 'value'], ['2018', '0.2']]
    >>> test("period\tvalue\n\n2018\t0.2")
    [['period', 'value'], ['2018', '0.2']]
    >>> test("period\tvalue\tattribute1\n2018\t0.2\tZ\n")
    [['period', 'value', 'attribute1'], ['2018', '0.2', 'Z']]
    >>> test("period\tvalue\tstatus\n\n2017\t0.1\t\n2018\t0.2\tE")
    [['period', 'value', 'status'], ['2017', '0.1', ''], ['2018', '0.2', 'E']]
    >>> test("period\tvalue\n2018\tNaN")
    [['period', 'value'], ['2018', 'NaN']]
    """
    for line in tsv_io:
        line = line.strip('\n')
        if not line:
            continue
        cells = line.split("\t")
        yield cells


def normalize_observations(observations):
    r"""Return a `tuple` like `(frequency, normalized_observations)` where:
    - `frequency` is a `str` guessed from values
    - `normalized_observations` is a `list` like `[period, value, attribute1, attribute2, ...]` where:
        - `period` is a `str`, normalized
        - `values` is a `float` or a `str` if conversion to `float` failed
        - `attributeN` is a `str`

    `observations` parameter is a `list` of observations. Observations values can be `str`, `int` or `float`.

    >>> normalize_observations([])
    (None, [])
    >>> normalize_observations([['PERIOD', 'VALUE']])
    (None, [['PERIOD', 'VALUE']])

    # Convert to float:
    >>> normalize_observations([['PERIOD', 'VALUE'], ['2010', '1'], ['2011', '2']])
    (<Frequency.ANNUAL: 'annual'>, [['PERIOD', 'VALUE'], ['2010', 1.0], ['2011', 2.0]])
    >>> normalize_observations([['PERIOD', 'VALUE'], ['2010', 1], ['2011', 2]])
    (<Frequency.ANNUAL: 'annual'>, [['PERIOD', 'VALUE'], ['2010', 1.0], ['2011', 2.0]])

    # Different number of cells:
    >>> normalize_observations([['PERIOD', 'VALUE'], ['2010']])
    (<Frequency.ANNUAL: 'annual'>, [['PERIOD', 'VALUE'], ['2010', 'NA']])

    # Invalid period formats:
    >>> normalize_observations([['PERIOD', 'VALUE'], ['2010 Q2', 1], ['2010 Q3', 2]])
    (<Frequency.QUARTERLY: 'quarterly'>, [['PERIOD', 'VALUE'], ['2010-Q2', 1.0], ['2010-Q3', 2.0]])
    >>> normalize_observations([['PERIOD', 'VALUE'], ['2010Z2', 1], ['2010Z3', 2]])
    (None, [['PERIOD', 'VALUE'], ['2010Z2', 1.0], ['2010Z3', 2.0]])

    # Invalid value:
    >>> normalize_observations([['PERIOD', 'VALUE'], ['2010', 'Z']])
    (<Frequency.ANNUAL: 'annual'>, [['PERIOD', 'VALUE'], ['2010', 'Z']])

    # Observations attributes:
    >>> normalize_observations([['PERIOD', 'VALUE', 'FLAG'], ['2010', 1, ""], ['2011', 2, 'E']])
    (<Frequency.ANNUAL: 'annual'>, [['PERIOD', 'VALUE', 'FLAG'], ['2010', 1.0, ''], ['2011', 2.0, 'E']])
    >>> normalize_observations([['PERIOD', 'VALUE', 'FLAG'], ['2010', 1, None], ['2011', 2, 'E']])
    (<Frequency.ANNUAL: 'annual'>, [['PERIOD', 'VALUE', 'FLAG'], ['2010', 1.0, ''], ['2011', 2.0, 'E']])

    # Period format different than frequency:
    >>> normalize_observations([['PERIOD', 'VALUE'], ['2010-01-01', 1], ['2010-04-01', 2]])
    (<Frequency.QUARTERLY: 'quarterly'>, [['PERIOD', 'VALUE'], ['2010-Q1', 1.0], ['2010-Q2', 2.0]])
    """
    if not observations:
        return (None, [])

    header = observations[0]
    if len(observations) < 2:
        return (None, observations)

    observation1 = observations[1]
    period1 = observation1[0]
    if len(observations) == 2:
        frequency, normalize_period = detect_period_format(period1)
    else:
        observation2 = observations[2]
        period2 = observation2[0]
        frequency, normalize_period = detect_frequency(period1, period2)

    def normalize_row(row):
        period = normalize_period(row[0]) \
            if normalize_period is not None \
            else row[0]
        value = value_to_float(get(1, row, None))
        attributes = [
            get(index, row, None) or ""
            for index, column_name in enumerate(header[2:], start=2)  # Skip period and value, already processed.
        ]
        return [period, value] + attributes

    rows = observations[1:]
    normalized_rows = list(map(normalize_row, rows))

    return (frequency, [header] + normalized_rows)


def period_to_start_day(period):
    """Return the start day of `period` as ISO-8601 date string.

    >>> period_to_start_day("")
    >>> period_to_start_day("2001")
    datetime.date(2001, 1, 1)
    >>> period_to_start_day("2001-S1")
    datetime.date(2001, 1, 1)
    >>> period_to_start_day("2001-S2")
    datetime.date(2001, 7, 1)
    >>> period_to_start_day("2001-B1")
    datetime.date(2001, 1, 1)
    >>> period_to_start_day("2001-B2")
    datetime.date(2001, 3, 1)
    >>> period_to_start_day("2001-B5")
    datetime.date(2001, 9, 1)
    >>> period_to_start_day("2001-B6")
    datetime.date(2001, 11, 1)
    >>> period_to_start_day("2001-Q1")
    datetime.date(2001, 1, 1)
    >>> period_to_start_day("2001-Q3")
    datetime.date(2001, 7, 1)
    >>> period_to_start_day("2001-Q4")
    datetime.date(2001, 10, 1)
    >>> period_to_start_day("2001-03")
    datetime.date(2001, 3, 1)
    >>> period_to_start_day("2001-11")
    datetime.date(2001, 11, 1)
    >>> period_to_start_day("2001-W01")
    datetime.date(2001, 1, 1)
    >>> period_to_start_day("2001-W02")
    datetime.date(2001, 1, 8)
    >>> period_to_start_day("2001-W11")
    datetime.date(2001, 3, 12)
    >>> period_to_start_day("2001-03-04")
    datetime.date(2001, 3, 4)
    >>> period_to_start_day("2001-11-12")
    datetime.date(2001, 11, 12)
    """
    for period_format, regex in period_format_strict_regex_list:
        match = regex.match(period)
        if match is not None:
            if period_format == Frequency.ANNUAL:
                year = match.group(1)
                return date(int(year), 1, 1)
            elif period_format == Frequency.BI_ANNUAL:
                year, index = match.groups()
                index = int(index)
                assert index in {1, 2}
                month = index * 6 - 5
                return date(int(year), month, 1)
            elif period_format == Frequency.BI_MONTHLY:
                year, index = match.groups()
                index = int(index)
                assert index in range(1, 7)
                month = index * 2 - 1
                return date(int(year), month, 1)
            elif period_format == Frequency.QUARTERLY:
                year, index = match.groups()
                index = int(index)
                assert index in range(1, 5)
                month = index * 3 - 2
                return date(int(year), month, 1)
            elif period_format == Frequency.MONTHLY:
                year, month = match.groups()
                return date(int(year), int(month), 1)
            elif period_format == Frequency.WEEKLY:
                return datetime.strptime("{}-1".format(period), "%Y-W%W-%w").date()
            elif period_format == Frequency.DAILY:
                year, month, day = match.groups()
                return date(int(year), int(month), int(day))
            else:
                assert False, period_format

    return None


def start_day_to_period(period_date: date, frequency: Frequency):
    """Return a period as `str` from `period_date` start day given `frequency`.

    >>> start_day_to_period(date(2000, 1, 1), Frequency.ANNUAL)
    '2000'
    >>> start_day_to_period(date(2000, 1, 1), Frequency.BI_ANNUAL)
    '2000-S1'
    >>> start_day_to_period(date(2000, 1, 1), Frequency.BI_MONTHLY)
    '2000-B1'
    >>> start_day_to_period(date(2000, 1, 1), Frequency.QUARTERLY)
    '2000-Q1'
    >>> start_day_to_period(date(2000, 4, 1), Frequency.QUARTERLY)
    '2000-Q2'
    >>> start_day_to_period(date(2000, 1, 1), Frequency.MONTHLY)
    '2000-01'
    >>> start_day_to_period(date(2000, 1, 1), Frequency.WEEKLY)
    '2000-W00'
    >>> start_day_to_period(date(2000, 1, 1), Frequency.DAILY)
    '2000-01-01'

    # `period_date` is not the start day:
    >>> start_day_to_period(date(2000, 2, 3), Frequency.ANNUAL)
    '2000'
    >>> start_day_to_period(date(2000, 2, 3), Frequency.BI_ANNUAL)
    '2000-S1'
    >>> start_day_to_period(date(2000, 6, 8), Frequency.BI_ANNUAL)
    '2000-S1'
    >>> start_day_to_period(date(2000, 8, 21), Frequency.BI_ANNUAL)
    '2000-S2'
    >>> start_day_to_period(date(2000, 12, 31), Frequency.BI_ANNUAL)
    '2000-S2'
    >>> start_day_to_period(date(2000, 2, 3), Frequency.BI_MONTHLY)
    '2000-B1'
    >>> start_day_to_period(date(2000, 3, 7), Frequency.BI_MONTHLY)
    '2000-B2'
    >>> start_day_to_period(date(2000, 2, 3), Frequency.QUARTERLY)
    '2000-Q1'
    >>> start_day_to_period(date(2000, 4, 6), Frequency.QUARTERLY)
    '2000-Q2'
    >>> start_day_to_period(date(2000, 2, 3), Frequency.MONTHLY)
    '2000-02'
    >>> start_day_to_period(date(2000, 5, 8), Frequency.MONTHLY)
    '2000-05'
    >>> start_day_to_period(date(2000, 2, 3), Frequency.WEEKLY)
    '2000-W05'
    """
    if frequency == Frequency.ANNUAL:
        return period_date.strftime("%Y")
    elif frequency == Frequency.BI_ANNUAL:
        return "{}-S{}".format(period_date.year, math.ceil(period_date.month / 6))
    elif frequency == Frequency.QUARTERLY:
        return "{}-Q{}".format(period_date.year, math.ceil(period_date.month / 3))
    elif frequency == Frequency.BI_MONTHLY:
        return "{}-B{}".format(period_date.year, math.ceil(period_date.month / 2))
    elif frequency == Frequency.MONTHLY:
        return period_date.strftime("%Y-%m")
    elif frequency == Frequency.WEEKLY:
        return period_date.strftime("%Y-W%W")
    elif frequency == Frequency.DAILY:
        return period_date.isoformat()
    else:
        assert False, frequency

    assert False, "Should never reach this line"


def value_to_float(value):
    """Try to convert a value to a `float`. Otherwise return "NA" if empty, or else original value.

    >>> value_to_float(None)
    'NA'
    >>> value_to_float(0.1)
    0.1
    >>> value_to_float("")
    'NA'
    >>> value_to_float(" ")
    'NA'
    >>> value_to_float("0")
    0.0
    >>> value_to_float("0.11")
    0.11
    >>> value_to_float(" -0.11 ")
    -0.11
    >>> value_to_float("NA")
    'NA'
    >>> value_to_float("NaN")
    'NaN'
    >>> value_to_float("ZZZ")
    'ZZZ'
    """
    if value is None:
        return NOT_AVAILABLE
    if isinstance(value, str):
        value = value.strip()
        if not value or value == NOT_AVAILABLE:
            return NOT_AVAILABLE
    try:
        float_value = float(value)
    except ValueError:
        return value
    if math.isfinite(float_value):
        return float_value
    return value
