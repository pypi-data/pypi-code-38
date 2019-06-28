"""Formatting functions for python using black
"""
import os

import black  # type: ignore
from xfmt import base, misc


class BlackFormatter(base.Formatter):
    """Plugin for checking the format of python files using black.
    """

    def __init__(self):
        self._include = black.re_compile_maybe_verbose(black.DEFAULT_INCLUDES)

    def check(self, path):
        mode = black.FileMode.AUTO_DETECT
        if os.path.splitext(path)[1] == ".pyi":
            mode |= black.FileMode.PYI

        with open(path, "rb") as buf:
            before, _, _ = black.decode_bytes(buf.read())

        try:
            after = black.format_file_contents(
                before,
                line_length=black.DEFAULT_LINE_LENGTH,  # No customization yet
                fast=False,  # Heed black cautions against using fast
                mode=mode,
            )
        except black.NothingChanged:
            return []

        return misc.diff(before, after, path)

    def fix(self, path: str):
        mode = black.FileMode.AUTO_DETECT
        if os.path.splitext(path)[1] == ".pyi":
            mode |= black.FileMode.PYI

        with open(path, "rb") as buf:
            before, encoding, newline = black.decode_bytes(buf.read())

        try:
            after = black.format_file_contents(
                before,
                line_length=black.DEFAULT_LINE_LENGTH,  # No customization yet
                fast=False,  # Heed black cautions against using fast
                mode=mode,
            )
        except black.NothingChanged:
            return []

        with open(path, "w", encoding=encoding, newline=newline) as f:
            f.write(after)

        return misc.diff(before, after, path)

    def match(self, path):
        match = self._include.search(path)
        return bool(match)
