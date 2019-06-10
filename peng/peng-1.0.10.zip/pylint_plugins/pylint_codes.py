# pylint_codes.py
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import re
import sys
import tokenize

# PyPI imports
from pylint.interfaces import IRawChecker
from pylint.checkers import BaseChecker


###
# Global variables
###
TEMPLATE = r"#\s*pylint:\s*disable\s*=\s*([\w|\s|\s*,\s*]+)"
EOL = re.compile(r"(.*)\s*" + TEMPLATE + r"\s*$")
SOLINE = re.compile(r"(^\s*)#\s*pylint\s*:\s*disable\s*=\s*([\w|\s|,]+)\s*")

###
# Functions
###
def _get_comments(fname):
    func = tokenize.generate_tokens
    with open(fname, "r") as fobj:
        for tokennum, tokenval, (num, _), _, _ in func(fobj.readline):
            if tokennum == tokenize.COMMENT:
                yield num, tokenval


def check_pylint(fname, codes):
    """Check that there are no repeated Pylint codes per file."""
    # pylint: disable=R0914
    repeated_pylint_codes, pylint_codes_at_eol, unsorted_pylint_codes = codes
    file_tokens = []
    ret = []
    for num, comment in _get_comments(fname):
        line_match = SOLINE.match(comment)
        eol_match = EOL.match(comment)
        if eol_match and (not line_match):
            ret.append((pylint_codes_at_eol, num))
        if line_match:
            unsorted_tokens = line_match.groups()[1].rstrip().split(",")
            sorted_tokens = sorted(unsorted_tokens)
            if any([item in file_tokens for item in sorted_tokens]):
                ret.append((repeated_pylint_codes, num))
            if unsorted_tokens != sorted_tokens:
                ret.append((unsorted_pylint_codes, num))
            file_tokens.extend(sorted_tokens)
    return ret


###
# Classes
###
class PylintCodesChecker(BaseChecker):
    """Check Pylint disable codes are unique, sorted and not at end of source line."""

    __implements__ = IRawChecker

    REPEATED_PYLINT_CODES = "repeated-pylint-disable-codes"
    PYLINT_CODES_AT_EOL = "pylint-disable-codes-at-eol"
    UNSORTED_PYLINT_CODES = "unsorted-pylint-disable-codes"

    name = "pylint-codes"
    msgs = {
        "W9901": (
            "Repeated Pylint disable codes",
            REPEATED_PYLINT_CODES,
            "There are repeated Pylint disable codes throughout the file",
        ),
        "W9902": (
            "Pylint disable code(s) at EOL",
            PYLINT_CODES_AT_EOL,
            "There are Pylint disable codes at end of code line",
        ),
        "W9903": (
            "Unsorted Pylint disable codes",
            UNSORTED_PYLINT_CODES,
            "There are unsorted Pylint disable codes",
        ),
    }
    options = ()

    def process_module(self, node):
        # pylint: disable=R0201
        """Process a module. Content is accessible via node.stream() function."""
        codes = (
            self.REPEATED_PYLINT_CODES,
            self.PYLINT_CODES_AT_EOL,
            self.UNSORTED_PYLINT_CODES,
        )
        for code, lineno in check_pylint(node.file, codes):
            self.add_message(code, line=lineno)


def register(linter):
    """Register checker."""
    linter.register_checker(PylintCodesChecker(linter))


def main():
    """Script entry point for testing."""
    lint_file = sys.argv[1]

    obj = PylintCodesChecker()
    codes = (
        obj.REPEATED_PYLINT_CODES,
        obj.PYLINT_CODES_AT_EOL,
        obj.UNSORTED_PYLINT_CODES,
    )
    for code, lineno in check_pylint(lint_file, codes):
        print((code, lineno))


if __name__ == "__main__":
    main()
