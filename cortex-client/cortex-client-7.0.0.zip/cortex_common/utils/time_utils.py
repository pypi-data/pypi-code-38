"""
Copyright 2019 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import time
from typing import Any, Mapping

import arrow

__all__ = [
    'timeit',
    'derive_hour_from_date',
    'derive_day_from_date',
    'remap_date_formats',
    'seconds_between_times',
    'utc_timestamp',
]


def utc_timestamp() -> str:
    """
    Gets an ISO-8601 complient timestamp of the current UTC time.
    :return:
    """
    return str(arrow.utcnow())


def timeit(method):
    """
    A decorator that times the invocation of a method and returns it along with the response from the method as a tuple.
    :param method:
    :return:
    """
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        return ('%2.2f' % (te - ts), result)

    return timed


def derive_hour_from_date(iso_timestamp:str) -> dict:
    """
    Enriches an ISO UTC Timestamp ...
    :param iso_timestamp:
    :return:
    """
    d = arrow.get(iso_timestamp)
    return {
        "hour_number": int(d.format("H")),
        "hour": d.format("hhA"),
        "timezone": d.format("ZZ")
    }


def derive_day_from_date(iso_timestamp) -> str:
    """
    Derives the day from a ISO UTC Timestamp ...
    >>> derive_day_from_date('2019-03-27T21:18:21.760245+00:00') == '2019-03-27'
    :param iso_timestamp:
    :return:
    """
    return str(arrow.get(iso_timestamp).date())


def remap_date_formats(date_dict:Mapping[Any, arrow.Arrow], date_formats, original_format) -> Mapping[Any, arrow.Arrow]:
    """
    Maps a date from on format to another ...

    :param date_dict:
    :param date_formats:
    :param original_format:
    :return:
    """
    return {
        k: arrow.get(v, original_format).format(date_formats.get(k, original_format))
        for (k, v) in date_dict.items()
    }


def seconds_between_times(arrow_time_a:arrow.Arrow, arrow_time_b:arrow.Arrow) -> float:
    """
    Finds the amount of seconds between two arrow times ...
    :param arrow_time_a:
    :param arrow_time_b:
    :return:
    """
    return abs(arrow_time_a.float_timestamp - arrow_time_b.float_timestamp)


# def pick_random_time_between(faker:faker.Generator, start:arrow.Arrow, stop:arrow.Arrow) -> arrow.arrow:
#     return arrow.get(faker.date_time_between(start.datetime, stop.datetime))