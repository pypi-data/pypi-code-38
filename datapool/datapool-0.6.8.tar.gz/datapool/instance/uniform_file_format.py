# encoding: utf-8
from __future__ import absolute_import, division, print_function

import csv
import datetime
import io
import os

from datapool.utils import iter_to_list


def _check_header(header, *, must_specify_source=False):

    header = list(header)

    if "site" in header:
        header.remove("site")
    else:
        for n in "xyz":
            if n not in header:
                raise ValueError(
                    "header {!r} must have either 'site' or 'x', 'y' and 'z'".format(
                        header
                    )
                )
            header.remove(n)

    header = set(header)
    fix_column_names = set(("timestamp", "parameter", "value"))

    if must_specify_source:
        fix_column_names |= set(("source",))

    if header != fix_column_names:
        missing = ["'{}'".format(name) for name in fix_column_names - header]
        invalid = ["'{}'".format(name) for name in header - fix_column_names]
        msg = ""
        if missing:
            msg += "missing: {}".format(", ".join(sorted(missing)))
        if invalid:
            msg += "invalid: {}".format(", ".join(sorted(invalid)))
        raise ValueError("invalid header ({})".format(msg))


@iter_to_list
def read_from_file(path, *, must_specify_source=False):
    if not os.path.exists(path):
        raise ValueError("{} does not exist".format(path))

    with open(path, "r", encoding="ascii") as fh:
        yield from _read_from_fh(fh, must_specify_source)


@iter_to_list
def read_from_string(data, *, must_specify_source=False):
    fh = io.StringIO(data)
    yield from _read_from_fh(fh, must_specify_source)


def can_be_converted_to_float(value):
    try:
        value = float(value)
    except ValueError:
        return False
    return True


def parse_timestamp(timestamp):
    return datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")


def _read_from_fh(fh, must_specify_source):
    reader = csv.reader(fh, delimiter=";")
    header = [f.strip() for f in next(reader)]
    _check_header(header, must_specify_source=must_specify_source)
    for i, row in enumerate(reader):
        if len(row) < len(header):
            # i + 1, we skipped header
            raise ValueError("row {} ({!r}) is incomplete".format(i + 1, row))
        if len(row) > len(header):
            # i + 1, we skipped header
            raise ValueError("row {} ({!r}) is to long".format(i + 1, row))

        row = (cell.strip() for cell in row)
        row_dict = dict(zip(header, row))
        yield row_dict


@iter_to_list
def check_rows(row_dicts, must_specify_source=False):

    if not row_dicts:
        return

    for i, row_dict in enumerate(row_dicts):

        value = row_dict["value"]
        if not can_be_converted_to_float(value):
            yield "row {}: value '{}' is not a float".format(i, value)
        else:
            row_dict["value"] = float(value)

        timestamp = row_dict["timestamp"]
        try:
            row_dict["timestamp"] = parse_timestamp(timestamp)
        except ValueError:
            yield "row {}: timstamp '{}' either has wrong format or is invalid".format(
                i, timestamp
            )

        if must_specify_source:
            if not row_dict["source"].strip():
                yield "row {}: source is empty".format(i)

        has_xyz = all(name in row_dict and row_dict[name] is not None for name in "xyz")
        not_empty = ("parameter",)
        if not has_xyz:
            not_empty += ("site",)

        for name in not_empty:
            if row_dict[name].strip() == "":
                yield "row {}: field {} is empty".format(i, name)


@iter_to_list
def to_signals(row_dicts):

    for row in row_dicts:
        for f in "xyz":
            if f in row:
                row["coord_" + f] = row[f]
                del row[f]

    from .domain_objects import Signal

    return list(map(Signal, row_dicts))
