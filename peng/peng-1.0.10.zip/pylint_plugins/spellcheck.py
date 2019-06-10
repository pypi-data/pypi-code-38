# spellcheck.py
# Copyright (c) 2018-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0325,C0411,E1101,E1123,E1129
# pylint: disable=R0205,R0903,R0912,R0914,R1718,W0611,W0702,W1113

# Standard library imports
from fnmatch import fnmatch
import os
import platform
import re
import sys

# PyPI imports
try:
    import hunspell

    NATIVE = True
except:
    NATIVE = False
from pylint.interfaces import IRawChecker
from pylint.checkers import BaseChecker

# Intra-package imports
from common import (
    _find_ref_fname,
    _grep,
    _make_abspath,
    _read_file,
    _shcmd,
    _tostr,
    which,
    StreamFile,
    TmpFile,
)


###
# Global variables
###
REF_WHITELIST = os.path.join("data", "whitelist.en.pws")
REF_EXCLUDE = os.path.join("data", "exclude-spelling")


###
# Functions
###
def check_spelling(fname, whitelist_fname="", exclude_fname=""):
    """Check spelling against whitelist."""
    fname = os.path.abspath(fname)
    whitelist_fname = whitelist_fname.strip() or _find_ref_fname(fname, REF_WHITELIST)
    exclude_fname = exclude_fname.strip() or _find_ref_fname(fname, REF_EXCLUDE)
    obj = Hunspell(NATIVE, whitelist_fname, exclude_fname)
    return obj.check(fname)


###
# Classes
###
class Hunspell(object):
    """
    Alternate implementation of CyHunspell.

    Useful when incompatibilities between libhunspell requirements of CyHunspell and
    the installed hunspell package.
    """

    def __init__(self, native, whitelist_fname, exclude_fname):
        """Check that hunspell binary can be found."""
        if not which("hunspell"):
            print("hunspell binary not found, skipping")
        self.native = native
        self.cmd = ["hunspell"]
        self.whitelist = []
        if whitelist_fname:
            whitelist_fname = os.path.abspath(whitelist_fname)
            if not os.path.exists(whitelist_fname):
                print("WARNING: Whitelist file {0} not found".format(whitelist_fname))
            else:
                self.cmd += ["-p", whitelist_fname]
                with open(whitelist_fname, "r") as fobj:
                    self.whitelist = [item.strip() for item in fobj]
        self.cmd += ["-l"]
        self.exclude_fname = None
        if exclude_fname:
            exclude_fname = os.path.abspath(exclude_fname)
            if not os.path.exists(exclude_fname):
                print("WARNING: exclude file {0} not found".format(exclude_fname))
            self.exclude_fname = exclude_fname

    def check(self, fname):
        """Check file."""
        if os.path.exists(self.exclude_fname):
            patterns = [_make_abspath(item) for item in _read_file(self.exclude_fname)]
            if any(fnmatch(fname, pattern) for pattern in patterns):
                return []
        ret = []
        if not self.native:
            # hunspell has trouble with apostrophes and other delimiters out-of-the-box
            words = []
            with open(fname, "r") as fobj:
                for line in fobj:
                    for word in re.split("[^a-zA-Z]", line.strip()):
                        words.append(word)
            with TmpFile(lambda x: x.write(os.linesep.join(words))) as temp_fname:
                stdout, _ = _shcmd(self.cmd + [temp_fname])
            words = sorted(list(set([word.strip() for word in stdout if word.strip()])))
            if words:
                ldict = _grep(fname, words)
                for word, lines in [(word, ldict[word]) for word in words]:
                    for lnum in lines:
                        ret.append((lnum, (word,)))
        else:
            spell_obj = hunspell.Hunspell("en_US")
            ret = []
            with open(fname, "r") as fobj:
                for num, line in enumerate(fobj):
                    line = line.strip()
                    for word in re.split("[^a-zA-Z]", line):
                        if (not spell_obj.spell(word)) and (word not in self.whitelist):
                            ret.append((num + 1, (word,)))
        return ret


class SpellChecker(BaseChecker):
    """Check for spelling."""

    __implements__ = IRawChecker

    MISSPELLED_WORD = "spellchecker"

    name = "spellchecker"
    msgs = {"W9904": ("Misspelled word %s", MISSPELLED_WORD, "Misspelled word")}

    options = (
        (
            "whitelist",
            {
                "default": "",
                "type": "string",
                "metavar": "<whitelist>",
                "help": "Whitelist",
            },
        ),
        (
            "exclude",
            {
                "default": "",
                "type": "string",
                "metavar": "<exclude file>",
                "help": "File with patterns used to exclude files from spell checking",
            },
        ),
    )

    def process_module(self, node):
        """Process a module. Content is accessible via node.stream() function."""
        if which("hunspell"):
            sdir = os.path.dirname(os.path.abspath(__file__))
            whitelist_fname = _tostr(self.config.whitelist)
            exclude_fname = _tostr(self.config.exclude)
            if whitelist_fname:
                whitelist_fname = os.path.abspath(os.path.join(sdir, whitelist_fname))
            if exclude_fname:
                exclude_fname = os.path.abspath(os.path.join(sdir, exclude_fname))
            for line, args in check_spelling(
                node.file, whitelist_fname=whitelist_fname, exclude_fname=exclude_fname
            ):
                self.add_message(self.MISSPELLED_WORD, line=line, args=args)
        else:
            print("hunspell binary not found, skipping")


def register(linter):
    """Register checker."""
    linter.register_checker(SpellChecker(linter))


def main():
    """Script entry point for testing."""
    fname = sys.argv[1]
    whitelist_fname = sys.argv[2] if len(sys.argv) >= 3 else ""
    exclude_fname = sys.argv[3] if len(sys.argv) >= 4 else ""
    out = check_spelling(
        fname, whitelist_fname=whitelist_fname, exclude_fname=exclude_fname
    )
    print(out)


if __name__ == "__main__":
    main()
