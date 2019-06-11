# header.py
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0205

# Standard library imports
from __future__ import print_function
import datetime
import os
import re
import sys

# PyPI imports
from pylint.interfaces import IRawChecker
from pylint.checkers import BaseChecker

# Intra-package imports
from common import _find_ref_fname, _read_file, _tostr, StreamFile


###
# Functions (common with hook)
###
def _check_header(fname, streamer, comment="#", header_ref=""):
    """Check that all files have header line and copyright notice."""
    # pylint: disable=W0702
    header_ref = header_ref.strip() or _find_ref_fname(fname, ".headerrc")
    if not header_ref:
        print(
            "Reference header file .headerrc not found, skipping header check",
            file=sys.stderr,
        )
        return []
    fullname = os.path.basename(os.path.abspath(fname))
    basename = os.path.basename(os.path.abspath(fname))
    current_year = datetime.datetime.now().year
    header_lines = []
    for line in _read_file(header_ref):
        line = line.format(
            comment=comment,
            fullname=fullname,
            basename=basename,
            current_year=current_year,
        )
        header_lines.append(re.compile("^" + line + "$"))
    linenos = []
    with streamer(fname) as stream:
        for (num, line), regexp in zip(_content_lines(stream, comment), header_lines):
            if not regexp.match(line):
                linenos.append(num)
    return linenos


def _content_lines(stream, comment="#"):
    """Return non-empty lines of a package."""
    shebang_line_regexp = re.compile(r"^#!.*[ \\/](bash|python)$")
    sl_mod_docstring = re.compile("('''|\"\"\").*('''|\"\"\")")
    encoding_dribble = "\xef\xbb\xbf"
    shebang_line = False
    in_mod_docstring = False
    mod_string_done = False
    cregexp = re.compile(r"^{0} -\*- coding: utf-8 -\*-\s*".format(comment))
    for num, line in enumerate(stream):
        line = _tostr(line).rstrip()
        if (not num) and line.startswith(encoding_dribble):
            line = line[len(encoding_dribble) :]
        # Skip shebang line
        if (not num) and shebang_line_regexp.match(line):
            shebang_line = True
            continue
        # Skip file encoding line
        if (num == int(shebang_line)) and cregexp.match(line):
            continue
        # Skip single-line module docstrings
        if (not num) and sl_mod_docstring.match(line):
            continue
        if (not num) and (not mod_string_done) and line.startswith('"""'):
            in_mod_docstring = True
            continue
        if in_mod_docstring and line.endswith('"""'):
            in_mod_docstring = False
            mod_string_done = True
            continue
        if (not mod_string_done) and in_mod_docstring:
            continue
        yield num + 1, line


###
# Plugin-specific classes and functions
###
class HeaderChecker(BaseChecker):
    """
    Check for header compliance.

    A compliant header includes the name of the file in the first usable line, and
    an up-to-date copyright notice.
    """

    __implements__ = IRawChecker

    NON_COMPLIANT_HEADER = "non-compliant-header"

    name = "header-compliance"
    msgs = {
        "W9900": (
            "Header does not meet code standard",
            NON_COMPLIANT_HEADER,
            (
                "Headers must have the name of the efile in the first usable line, "
                "and an up-to-date copyright notice"
            ),
        )
    }

    options = (
        (
            "header-ref",
            {
                "default": "",
                "type": "string",
                "metavar": "<header reference>",
                "help": "Header reference",
            },
        ),
    )

    def process_module(self, node):
        """Process a module. Content is accessible via node.stream() function."""
        # pylint: disable=E1101
        header_ref = self.config.header_ref.strip()
        sdir = os.path.dirname(os.path.abspath(__file__))
        if header_ref:
            header_ref = os.path.join(sdir, header_ref)
        fname = node.file
        linenos = _check_header(fname, StreamFile, header_ref=header_ref)
        for lineno in linenos:
            self.add_message(self.NON_COMPLIANT_HEADER, line=lineno)


def register(linter):
    """Register checker."""
    linter.register_checker(HeaderChecker(linter))


def main():
    """Script entry point for testing."""
    header_ref = sys.argv[1]
    lint_file = sys.argv[2]
    linenos = _check_header(lint_file, StreamFile, header_ref=header_ref)
    print(linenos)


if __name__ == "__main__":
    main()
