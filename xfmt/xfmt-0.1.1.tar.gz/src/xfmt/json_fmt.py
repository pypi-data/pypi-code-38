"""
Formatting functions for json
"""
import json
import os
from typing import List

from xfmt import base
from xfmt.misc import diff

JSON_PRETTY_KWARGS = {"indent": 4, "separators": (",", ": "), "sort_keys": True}


def fix_content_json(before: str) -> str:
    """Fix json formatting, returning the pretty version.
    """
    data = json.loads(before)
    after = json.dumps(data, **JSON_PRETTY_KWARGS)  # type: ignore
    return after


def check_content_json(before: str) -> List[str]:
    """Check json formatting, returning any differences to the pretty version.
    """
    after = fix_content_json(before)
    if before == after:
        return []
    return diff(before, after)


def fix_file_json(path: str) -> List[str]:
    """Fix json formatting, returning any changes that have been made.
    """
    with open(path, "r") as fp:
        before = fp.read()

    after = fix_content_json(before)

    if before == after:
        return []

    with open(path, "w") as fp:
        fp.write(after)

    return diff(before, after)


def check_file_json(path: str) -> List[str]:
    """Check json formatting, returning any changes that should be made.
    """
    with open(path, "r") as fp:
        before = fp.read()

    after = fix_content_json(before)
    if before == after:
        return []

    return diff(before, after, path)


class JsonFormatter(base.Formatter):
    """Plugin for checking the format of json files.
    """

    def check(self, path):
        return check_file_json(path)

    def fix(self, path: str):
        return fix_file_json(path)

    def match(self, path):
        _, ext = os.path.splitext(path)
        return ext == ".json"
