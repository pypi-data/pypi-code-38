"""
Miscellaneous utilities
"""
import difflib
import glob
import logging
import os
from typing import Iterable, List, Optional

import pkg_resources
from xfmt import base

logger = logging.getLogger(__name__)


def _chunk_lines(lines: Iterable[str], fromfile: str) -> Iterable[str]:
    chunk = []  # type: List[str]
    for line in lines:
        if line == "--- {}\n".format(fromfile):
            yield "".join(chunk)
            chunk = []
        chunk.append(line)
    yield "".join(chunk)


def diff(before: str, after: str, path: Optional[str] = None) -> List[str]:
    """Produce feedback from the difference between two versions.
    """
    if path is None:
        fromfile = "actual"
        tofile = "expected"
    else:
        fromfile = tofile = path

    lines = difflib.unified_diff(
        before.splitlines(keepends=True),
        after.splitlines(keepends=True),
        fromfile=fromfile,
        tofile=tofile,
    )
    chunks = list(_chunk_lines(lines, fromfile))
    return chunks[1:]  # First chunk is empty


def collect(top: str) -> Iterable[str]:
    """Collect file paths to be formatted.
    """
    if not os.path.isdir(top):
        if os.path.isfile(top):
            raise ValueError("Collecting from file is meaningless")
        else:
            raise RuntimeError("Huh? {}".format(top))
    paths = filter(os.path.isfile, glob.iglob(os.path.join(top, "**"), recursive=True))
    yield from (os.path.relpath(p, top) for p in paths)


def check(path: str, formatters: List[base.Formatter], fixes: bool) -> List[str]:
    """Check format of file.
    """
    assert formatters
    formatter_matched = False
    feedback = []  # type:  List[str]
    for formatter in formatters:
        if formatter.match(path):
            formatter_matched = True
            if fixes:
                feedback.extend(formatter.fix(path))
            else:
                feedback.extend(formatter.check(path))

    if not formatter_matched:
        raise LookupError("Path did not match any pattern")

    return feedback


def _gen_formatters() -> Iterable[base.Formatter]:
    for entry_point in pkg_resources.iter_entry_points("xfmt.formatter"):
        factory_func = entry_point.load()
        yield factory_func()


def get_formatters():
    """Instantiate all registered formatters.
    """
    return list(_gen_formatters())
