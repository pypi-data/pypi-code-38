# encoding: utf-8
from __future__ import absolute_import, division, print_function

import contextlib
import functools
import glob
import hashlib
import inspect
import io
import os
import re
import shutil
import signal
import stat
import sys
import warnings
# https://stackoverflow.com/questions/35446015/
from collections import Counter, OrderedDict
from datetime import datetime

from .errors import ConsistencyError, DataPoolIOError


def hexdigest(data):
    """computes md5 hex digtes of given data of type bytes"""
    assert isinstance(data, bytes)
    digester = hashlib.md5()
    digester.update(data)
    return digester.hexdigest()


def hexdigest_file(path):
    data = open(path, "rb").read()
    return hexdigest(data)


def is_writeable(path):
    return bool(os.stat(path).st_mode & stat.S_IWUSR)


def check_is_writeable(folder, path=""):
    if not is_writeable(os.path.join(folder, path)):
        raise DataPoolIOError("can not write to {}".format(os.path.join(folder, path)))


def reformat_row(row, limit):
    """breaks cell to consecutive lines if len of cell content is beyond limit"""
    new_rows = []
    while True:
        new_rows.append([cell[:limit] for cell in row])
        row = [cell[limit:] for cell in row]
        if all(len(c) == 0 for c in row):
            break
    return new_rows


def format_table(header, rows, max_col_size=40, indent="", max_rows=None):
    file = io.StringIO()
    print_table(header, rows, max_col_size, indent, file, max_rows)
    return file.getvalue()


def print_table(
    header, rows, max_col_size=40, indent="", file=sys.stderr, max_rows=None
):
    """pretty print table for given headers and rows.

    headers  list of strings
    rows:    list of list of values
    """

    if max_rows is not None and len(rows) > max_rows:
        inter_row = "skipped {} rows ...".format(len(rows) - max_rows)
        n = max_rows // 2
        rows = rows[:n] + rows[-(max_rows - n) + 1 :]
    else:
        n = None

    headers = reformat_row(header, max_col_size)
    new_rows = []
    for row in rows:
        new_rows.extend(reformat_row(list(map(str, row)), max_col_size))

    rows = new_rows

    col_sizes = list(map(len, headers[0]))
    for row in headers[1:] + rows:
        col_sizes = list(max(s, len(c)) for (s, c) in zip(col_sizes, map(str, row)))

    formatters = ["%-{}s".format(s) for s in col_sizes]
    for header in headers:
        for name, f in zip(header, formatters):
            print(indent, end="", file=file)
            print(f % name, end="  ", file=file)
        print(file=file)
    for c in col_sizes:
        print(indent, end="", file=file)
        print("-" * c, end="  ", file=file)
    print(file=file)

    def p(row):
        for cell, f in zip(row, formatters):
            print(indent, end="", file=file)
            print(f % cell, end="  ", file=file)
        print(file=file)

    if n is None:
        for row in rows:
            p(row)
    else:
        for row in rows[:n]:
            p(row)
        print(indent, inter_row, file=file, sep="")
        for row in rows[n:]:
            p(row)


def print_signals(signals, indent="", file=sys.stdout):
    assert isinstance(signals, list)
    assert all(isinstance(s, dict) for s in signals)
    has_xyz = all("x" in s and "y" in s and "z" in s for s in signals)
    has_site = all("site" in s for s in signals)
    if not (has_xyz or has_site):
        raise ConsistencyError("all signals must have either (x, y, z) or site fields")

    if has_xyz:
        header = ("timestamp", "parameter", "value", "x", "y", "z")
    else:
        header = ("timestamp", "parameter", "value", "site")

    rows = [[s.get(field) for field in header] for s in signals]
    print_table(header, rows, indent=indent, file=file)


def find_executable(name, default=None):
    for folder in os.environ["PATH"].split(os.pathsep):
        path = os.path.join(folder, name)
        if os.path.exists(path):
            if os.access(path, os.X_OK):
                return path
    return default


def abs_folder(path):
    return os.path.dirname(os.path.abspath(path))


def here():
    """determines folder containing the caller of this function"""
    # we go one step up in the call stack and read __file__ as set there:
    return abs_folder(inspect.stack()[1].frame.f_globals["__file__"])


class TimeoutError(Exception):
    pass


def run_timed(function, args=None, kwargs=None, timeout_in_seconds=None):
    """run given function with given args / kwargs, stopping execution if the function execution
    needs more than timeout_in_seconds seconds.

    In case timeout_in_seconds is None we wait until the function execution ends.
    """

    args = () if args is None else args
    kwargs = {} if kwargs is None else kwargs

    if timeout_in_seconds is None:
        return function(*args, **kwargs)

    def handle_timeout(*a):
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        raise TimeoutError()

    # we use signalt.setitimer here, signal.alarm only accepts integer values for the time span
    signal.setitimer(signal.ITIMER_REAL, timeout_in_seconds)
    signal.signal(signal.SIGALRM, handle_timeout)
    try:
        return function(*args, **kwargs)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)


def list_folder_recursive(folder, skip_hidden=True, also_folders=True, check=False):
    folder = os.path.normpath(folder)  # remove eventually preceedings dots
    for (dirname, dirnames, files) in sorted(os.walk(folder)):
        if check:
            check_is_writeable(dirname)
            for dirname_ in dirnames:
                check_is_writeable(dirname, dirname_)
            for file_ in files:
                check_is_writeable(dirname, file_)

        if dirname.startswith(".") and skip_hidden:
            continue

        if also_folders:
            yield os.path.relpath(os.path.normpath(dirname), folder)

        for file in sorted(files):
            if file.startswith(".") and skip_hidden:
                continue
            yield os.path.relpath(os.path.normpath(os.path.join(dirname, file)), folder)


def copy(from_, to):
    """copies file from from_ to to, if target folder does not exist all needed intermediate
    folders are created"""
    assert os.path.exists(from_)
    target_folder = os.path.dirname(to)
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    shutil.copyfile(from_, to)


def iter_to_list(function):
    """decorator which transforms a generator function to a classic function returning a list
    with the values created by the generator.
    """

    @functools.wraps(function)
    def inner(*a, **kw):
        return list(function(*a, **kw))

    return inner


def is_int(txt):
    try:
        int(txt)
        return True
    except ValueError:
        return False


def enumerate_filename(*pathes):
    next_numbers = []
    parts = []
    for path in pathes:
        filename = os.path.basename(path)
        dirname = os.path.dirname(path)

        name_stem, ext = os.path.splitext(filename)
        # remove trailing "_NNN" if exists:
        name_stem = re.split("_\d+$", name_stem)[0]

        stem = os.path.join(dirname, name_stem)
        parts.append((stem, ext))
        files = glob.glob(stem + "*" + ext)
        appendices = [file[len(stem) : -len(ext)].lstrip("_") for file in files]
        numbers = [int(a) for a in appendices if is_int(a)]
        if not numbers:
            next_number = 0
        else:
            next_number = max(numbers) + 1
        next_numbers.append(next_number)
    next_number = max(next_numbers)
    return [stem + "_{:d}".format(next_number) + ext for stem, ext in parts]


def is_number(value):
    try:
        float(value)
    except ValueError:
        return False
    return True


def update_and_report_change(dbo, domain_obj, fieldname):
    existing = getattr(dbo, fieldname)
    new = getattr(domain_obj, fieldname)
    if existing != new:
        setattr(dbo, fieldname, new)
        yield dbo


def write_pid_file(config):
    try:
        with open(config.server.pid_file, "w") as fh:
            fh.write(str(os.getpid()))
    except IOError as e:
        raise DataPoolIOError(str(e))
    # only owner can read and write, group and others can only read:
    os.chmod(config.server.pid_file, 0o644)


def is_server_running(config):
    return os.path.exists(config.server.pid_file)


def remove_pid_file(config):
    if os.path.exists(config.server.pid_file):
        os.unlink(config.server.pid_file)


@contextlib.contextmanager
def open_and_create_folders(path, mode="r"):
    dirname = os.path.dirname(path)
    try:
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(path, "w") as fh:
            yield fh
    except IOError as e:
        raise DataPoolIOError(str(e))


def parse_timestamp(value):
    """parse for match with %Y, then %Y-%m, ...."""
    fmt = "%Y-%m-%d:%H:%M:%S"
    for end_index in range(2, len(fmt) + 1, 3):
        try:
            return datetime.strptime(value, fmt[:end_index])
        except ValueError:
            continue
    raise ValueError(
        "datetime {} is not of format '{}' or contains invalid values".format(
            value, fmt
        )
    )


class OrderedCounter(Counter, OrderedDict):
    "Counter that remembers the order elements are first seen"

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, OrderedDict(self))

    def __reduce__(self):
        return self.__class__, (OrderedDict(self),)


def warn_if_generator_is_not_used(function):
    assert inspect.isgeneratorfunction(function), "decorator only works for generators"

    @functools.wraps(function)
    def wrapped(*a, **kw):
        return _iter_checker(function(*a, **kw))

    return wrapped


class _iter_checker:
    def __init__(self, function):
        self.function = function
        self.iterated = False
        stack = inspect.stack()[-1]
        self.lineno = stack.lineno
        self.filename = stack.filename

    def __iter__(self, *a, **kw):
        self.iterated = True
        return iter(self.function)

    def __del__(self):
        if not self.iterated:
            warnings.warn(
                "generator created in {}, line number {} was never used "
                "for iteration".format(self.filename, self.lineno)
            )
