# encoding: utf-8
from __future__ import absolute_import, division, print_function

import datetime
import operator
from collections import OrderedDict
from enum import Enum

from ..database import create_session
from ..errors import ConsistencyError
from ..utils import (OrderedCounter, is_number, iter_to_list,
                     warn_if_generator_is_not_used)
from .converters import domain_object_to_dbo
from .db_objects import ParameterDbo, SignalDbo, SiteDbo, SourceDbo
from .domain_objects import Signal

REPORT_EVERY_N = 100000
COMMIT_EVERY_N = 100000


def _report_progress(template, i, items):
    n = len(items)
    if n == 0:
        return "task: {}, progress: {} of {} done".format(template, i, n)
    percent = round(100 * i / n, 1)
    return "task: {}, progress: {:.1f} % of {} done".format(template, percent, n)


class SignalKind(Enum):

    SIGNAL_EXISTS = 1
    NEW_SIGNAL = 2


def _check_fields(signal):
    assert isinstance(signal, Signal)

    if not isinstance(signal.timestamp, datetime.datetime):
        yield "'{}' is not a datetime object".format(signal.timestamp)

    if not is_number(signal.value):
        yield "'{}' is not a number".format(signal.value)

    if signal.parameter == "":
        yield "parameter field is empty"

    if "site" in signal:
        if signal.site == "":
            yield "site field is empty"

    for name in ("coord_x", "coord_y", "coord_z"):
        v = signal.get(name)
        if v is not None:
            if v != "":
                if not is_number(v):
                    yield "value '{}' in field {} is not valid".format(v, name)


def check_fields(signals):
    for (i, signal) in enumerate(signals):
        for msg in _check_fields(signal):
            yield "(row {}) {}".format(i, msg)


class Context:
    def __init__(self, engine):
        self.session = create_session(engine)
        self.source_name_to_id = None
        self.parameter_name_to_id = None
        self.site_name_to_id = None
        self.site_name_to_coordinates = None

    @property
    def query(self):
        return self.session.query

    def __del__(self):
        self.session.close()

    @property
    def add(self):
        return self.session.add

    @property
    def bulk_insert_mappings(self):
        return self.session.bulk_insert_mappings

    @property
    def commit(self):
        return self.session.commit

    def get_source_id(self, source_name):
        if self.source_name_to_id is None:
            self.load()
        return self.source_name_to_id.get(source_name)

    def get_parameter_id(self, parameter_name):
        if self.parameter_name_to_id is None:
            self.load()
        return self.parameter_name_to_id.get(parameter_name)

    def get_site_id(self, site_name):
        if self.site_name_to_id is None:
            self.load()
        return self.site_name_to_id.get(site_name)

    def get_site_coordinates(self, site_name):
        if self.site_name_to_coordinates is None:
            self.load()
        return self.site_name_to_coordinates.get(site_name)

    def load(self):
        self.source_name_to_id = {}
        q = self.query(SourceDbo.name, SourceDbo.source_id)
        for name, id_ in q.all():
            self.source_name_to_id[name] = id_

        self.parameter_name_to_id = {}
        q = self.query(ParameterDbo.name, ParameterDbo.parameter_id)
        for name, id_ in q.all():
            self.parameter_name_to_id[name] = id_

        self.site_name_to_id = {}
        self.site_name_to_coordinates = {}

        q = self.query(SiteDbo)
        for site in q.all():
            self.site_name_to_id[site.name] = site.site_id
            self.site_name_to_coordinates[site.name] = (
                site.coord_x,
                site.coord_y,
                site.coord_z,
            )


def check_and_commit(signals, engine):
    result = []
    for msg in check_and_commit_async(signals, engine, result):
        pass
    return result


def check_and_commit_async(signals, engine, result):
    context = Context(engine)
    yield "check signals against db"
    valid_signals, exceptions = [], []
    for item in check_signals_against_db(signals, engine, context):
        if isinstance(item, str):
            yield item
            continue
        if isinstance(item, Exception):
            exceptions.append(item)
            continue
        if isinstance(item, Signal):
            valid_signals.append(item)
            continue
        raise RuntimeError("should never happen")
    yield "got {} valid signals".format(len(valid_signals))
    if valid_signals:
        yield "commit signals to db"
        yield from _commit(valid_signals, engine, context)
    result[:] = valid_signals, exceptions


@warn_if_generator_is_not_used
def check_signals_against_db(signals, engine, context=None):

    if context is None:
        context = Context(engine)

    signals_to_check = []
    for i, result in enumerate(check_existing_fields(signals, context), 1):
        if i % REPORT_EVERY_N == 0:
            yield _report_progress("checked signal attributes against db", i, signals)
        if isinstance(result, ConsistencyError):
            yield result
        else:
            signals_to_check.append(result)

    if not signals_to_check:
        return

    i = 0
    for signal, kind, (new_value, db_value) in check_existing_signals(signals_to_check, context):
        i += 1
        if kind == SignalKind.SIGNAL_EXISTS:
            dimensions = "'{}', '{}', '{}'".format(
                signal.source, signal.parameter, signal.timestamp
            )
            if new_value != db_value:
                msg = "signal for ({}) having different value ({!r}) already in db ({!r})".format(
                    dimensions, new_value, db_value
                )
                yield ConsistencyError(msg)
        elif kind == SignalKind.NEW_SIGNAL:
            if i % REPORT_EVERY_N == 0:
                yield _report_progress(
                    "checked signal already in db", i, signals_to_check
                )
            yield signal
        else:
            raise RuntimeError("should never happen")


@iter_to_list
def check_signals_uniqueness(signals):

    fields = (
        "timestamp",
        "source",
        "parameter",
        "site",
        "coord_x",
        "coord_y",
        "coord_z",
        "value",
    )

    coordinates = [tuple(getattr(s, field) for field in fields) for s in signals]

    counts = OrderedCounter(coordinates)

    for (coordinate, count) in counts.most_common():
        if count == 1:
            break
        dt, source_name, parameter_name, site, coord_x, coord_y, coord_z, value = (
            coordinate
        )
        c_str = "{}, {}, {}, {}".format(
            dt.strftime("%Y-%m-%d %H:%M:%S"), source_name, parameter_name, value
        )
        yield ConsistencyError(
            "duplicate signal ({}) found {} times".format(c_str, count)
        )


def check_existing_fields(signals, context):
    """we check if entries source and parameter in given signals are
    defined in database"""

    reported_messages = set()

    def report(message):
        if message not in reported_messages:
            yield ConsistencyError(message)
            reported_messages.add(message)

    for signal in signals:
        parameter_name = signal.parameter
        source_name = signal.source
        source_id = context.get_source_id(source_name)
        parameter_id = context.get_parameter_id(parameter_name)

        if source_id is None:
            yield from report("source '{}' does not exist in db".format(source_name))

        if parameter_id is None:
            yield from report(
                "parameter '{}' does not exist in db".format(parameter_name)
            )

        site = signal.get("site")
        site_id = -1
        if site is not None:
            site_id = context.get_site_id(site)
            if site_id is None:
                yield from report("site '{}' does not exist in db".format(site))

        if source_id is not None and parameter_id is not None and site_id is not None:
            yield signal


def check_existing_signals(signals, context):
    """we check if signals already exist in database.
    """

    getter = operator.attrgetter

    def list_map(function, iterable):
        return list(map(function, iterable))

    timestamps = list_map(getter("timestamp"), signals)
    source_names = list_map(getter("source"), signals)
    parameter_names = list_map(getter("parameter"), signals)

    # fast query, but will produce false positives !
    source_ids = list_map(context.get_source_id, source_names)
    parameter_ids = list_map(context.get_parameter_id, parameter_names)

    min_ts = min(timestamps)
    max_ts = max(timestamps)
    q = context.query(
        SignalDbo.timestamp,
        SignalDbo.source_id,
        SignalDbo.parameter_id,
        SignalDbo.value,
    )
    q = q.filter(
        SignalDbo.source_id.in_(set(source_ids)),
        SignalDbo.parameter_id.in_(set(parameter_ids)),
        SignalDbo.timestamp.between(min_ts, max_ts),
    )

    possible_matches = q.all()

    # to remove duplicates and only keep first entry in case of duplicates:
    timestamps = reversed(timestamps)
    source_ids = reversed(source_ids)
    parameter_ids = reversed(parameter_ids)
    signals = reversed(signals)
    dimensions = zip(timestamps, source_ids, parameter_ids)
    dimension_to_signal = OrderedDict(zip(dimensions, signals))

    if possible_matches:

        # check, report and remove duplicate signals:
        for match in possible_matches:
            dimension, value = match[:-1], match[-1]
            if dimension in dimension_to_signal:
                signal = dimension_to_signal[dimension]
                yield dimension_to_signal[
                    dimension
                ], SignalKind.SIGNAL_EXISTS, (signal.value, value)
                del dimension_to_signal[dimension]

    # yield remaining signals in original order
    for signal in reversed(dimension_to_signal.values()):
        yield signal, SignalKind.NEW_SIGNAL, (None, None)


@warn_if_generator_is_not_used
def _commit(signals, engine, context=None):
    """marked as private because it should not be used directly,
       always use check_and_commit"""

    if context is None:
        context = Context(engine)

    signals_for_db = []

    yield "prepare signals for insert"

    for i, signal in enumerate(signals, 1):

        if i % REPORT_EVERY_N == 0:
            yield _report_progress("check attributes of signals against db", i, signals)
        signal = signal.copy()

        signal.parameter_id = context.get_parameter_id(signal.parameter)
        del signal.parameter

        signal.source_id = context.get_source_id(signal.source)
        del signal.source

        if "site" in signal:
            signal.site_id = context.get_site_id(signal.site)
            coord = context.get_site_coordinates(signal.site)
            if coord is not None:
                x, y, z = coord
                signal.coord_x = str(x)
                signal.coord_y = str(y)
                signal.coord_z = str(z)
            del signal.site
        else:
            signal.coord_x = signal.x
            signal.coord_y = signal.y
            signal.coord_z = signal.z
            del signal.x
            del signal.y
            del signal.z
        signals_for_db.append(signal)

    i = 0
    mappings = []
    while signals_for_db:
        i += 1
        # while + pop also reduces memory requierements compared to a for loop
        signal = signals_for_db.pop(0)
        mappings.append(signal)

        if i % COMMIT_EVERY_N == 0:
            context.bulk_insert_mappings(SignalDbo, mappings)
            mappings = []
        if (i - 1) % REPORT_EVERY_N == 0:
            yield _report_progress("commit signals to db", i - 1, signals_for_db)

    context.bulk_insert_mappings(SignalDbo, mappings)
    context.commit()
    yield "committed {} signals to db".format(len(signals))
