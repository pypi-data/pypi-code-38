#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
# Copyright (C) 2009-2019 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""tools to help manipulating time and dates"""

from sat.core.constants import Const as C
from sat.core.i18n import _
import datetime
from dateutil import tz, parser
from dateutil.relativedelta import relativedelta
from dateutil.utils import default_tzinfo
from babel import dates
import calendar
import time
import re

RELATIVE_RE = re.compile(ur"(?P<date>.*?)(?P<direction>[-+]?) *(?P<quantity>\d+) *"
                         ur"(?P<unit>(second|minute|hour|day|week|month|year))s?"
                         ur"(?P<ago> +ago)?", re.I)
YEAR_FIRST_RE = re.compile(ur"\d{4}[^\d]+")
TZ_UTC = tz.tzutc()
TZ_LOCAL = tz.gettz()
# used to replace values when something is missing
DEFAULT_DATETIME = datetime.datetime(2000, 01, 01)


def date_parse(value, default_tz=TZ_UTC):
    """Parse a date and return corresponding unix timestamp

    @param value(unicode): date to parse, in any format supported by parser
    @param default_tz(datetime.tzinfo): default timezone
    @return (int): timestamp
    """
    value = unicode(value).strip()
    dayfirst = False if YEAR_FIRST_RE.match(value) else True

    dt = default_tzinfo(
        parser.parse(value, default=DEFAULT_DATETIME, dayfirst=dayfirst),
        default_tz)
    return calendar.timegm(dt.utctimetuple())

def date_parse_ext(value, default_tz=TZ_UTC):
    """Extended date parse which accept relative date

    @param value(unicode): date to parse, in any format supported by parser
        and with the hability to specify X days/weeks/months/years in the past or future.
        Relative date are specified either with something like `[main_date] +1 week`
        or with something like `3 days ago`, and it is case insensitive. [main_date] is
        a date parsable by parser, or empty to specify current date/time.
        "now" can also be used to specify current date/time.
    @param default_tz(datetime.tzinfo): same as for date_parse
    @return (int): timestamp
    """
    m = RELATIVE_RE.match(value)
    if m is None:
        return date_parse(value, default_tz=default_tz)

    if m.group(u"direction") and m.group(u"ago"):
        raise ValueError(
            _(u"You can't use a direction (+ or -) and \"ago\" at the same time"))

    if m.group(u"direction") == u'-' or m.group(u"ago"):
        direction = -1
    else:
        direction = 1

    date = m.group(u"date").strip().lower()
    if not date or date == u"now":
        dt = datetime.datetime.now(tz.tzutc())
    else:
        dt = default_tzinfo(parser.parse(date, dayfirst=True))

    quantity = int(m.group(u"quantity"))
    key = m.group(u"unit").lower() + u"s"
    delta_kw = {key: direction * quantity}
    dt = dt + relativedelta(**delta_kw)
    return calendar.timegm(dt.utctimetuple())


def date_fmt(timestamp, fmt="short", date_only=False, auto_limit=7, auto_old_fmt="short",
             auto_new_fmt="relative", locale_str=C.DEFAULT_LOCALE, tz_info=TZ_UTC):
    """format date according to locale

    @param timestamp(basestring, float): unix time
    @param fmt(str): one of:
        - short: e.g. u'31/12/17'
        - medium: e.g. u'Apr 1, 2007'
        - long: e.g. u'April 1, 2007'
        - full: e.g. u'Sunday, April 1, 2007'
        - relative: format in relative time
            e.g.: 3 hours
            note that this format is not precise
        - iso: ISO 8601 format
            e.g.: u'2007-04-01T19:53:23Z'
        - auto: use auto_old_fmt if date is older than auto_limit
            else use auto_new_fmt
        - auto_day: shorcut to set auto format with change on day
            old format will be short, and new format will be time only
        or a free value which is passed to babel.dates.format_datetime
        (see http://babel.pocoo.org/en/latest/dates.html?highlight=pattern#pattern-syntax)
    @param date_only(bool): if True, only display date (not datetime)
    @param auto_limit (int): limit in days before using auto_old_fmt
        use 0 to have a limit at last midnight (day change)
    @param auto_old_fmt(unicode): format to use when date is older than limit
    @param auto_new_fmt(unicode): format to use when date is equal to or more recent
        than limit
    @param locale_str(unicode): locale to use (as understood by babel)
    @param tz_info(datetime.tzinfo): time zone to use

    """
    timestamp = float(timestamp)
    if fmt == "auto_day":
        fmt, auto_limit, auto_old_fmt, auto_new_fmt = "auto", 0, "short", "HH:mm"
    if fmt == "auto":
        if auto_limit == 0:
            now = datetime.datetime.now(tz_info)
            # we want to use given tz_info, so we don't use date() or today()
            today = datetime.datetime(year=now.year, month=now.month, day=now.day,
                                      tzinfo=now.tzinfo)
            today = calendar.timegm(today.utctimetuple())
            if timestamp < today:
                fmt = auto_old_fmt
            else:
                fmt = auto_new_fmt
        else:
            days_delta = (time.time() - timestamp) / 3600
            if days_delta > (auto_limit or 7):
                fmt = auto_old_fmt
            else:
                fmt = auto_new_fmt

    if fmt == "relative":
        delta = timestamp - time.time()
        return dates.format_timedelta(
            delta, granularity="minute", add_direction=True, locale=locale_str
        )
    elif fmt in ("short", "long"):
        if date_only:
            dt = datetime.fromtimestamp(timestamp, tz_info)
            return dates.format_date(dt, format=fmt, locale=locale_str)
        else:
            return dates.format_datetime(timestamp, format=fmt, locale=locale_str,
                                        tzinfo=tz_info)
    elif fmt == "iso":
        if date_only:
            fmt = "yyyy-MM-dd"
        else:
            fmt = "yyyy-MM-ddTHH:mm:ss'Z'"
        return dates.format_datetime(timestamp, format=fmt)
    else:
        return dates.format_datetime(timestamp, format=fmt, locale=locale_str,
                                     tzinfo=tz_info)
