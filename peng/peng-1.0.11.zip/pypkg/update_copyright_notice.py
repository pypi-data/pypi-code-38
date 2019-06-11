#!/usr/bin/env python
# update_copyright_notice.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
from __future__ import print_function
import datetime
import os
import re
import sys

# Intra-package imports
import pypkg.functions


###
# Functions
###
def read_file(fname):
    """Read file in Python 2 or Python 3."""
    try:
        with open(fname, "r") as fobj:
            return fobj.readlines()
    except UnicodeDecodeError:
        with open(fname, "r", encoding="utf-8") as fobj:
            return fobj.readlines()


def update_copyright_notice():
    """Update copyright notice in project files."""
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    regexp = re.compile(".*Copyright \\(c\\) 2013-(\\d\\d\\d\\d) Pablo Acosta-Serafini")
    ext_exclude = [
        "pyc",
        "png",
        "html",
        "odg",
        "pdf",
        "svg",
        "so",
        "npz",
        "pip",
        "dic",
        "aff",
    ]
    dir_exclude = [
        ".tox",
        ".eggs",
        ".cache",
        os.path.join("docs", "_build"),
        pypkg.functions.get_pkg_name() + ".egg-info",
        ".git",
    ]
    year = datetime.datetime.now().year
    template = "Copyright (c) 2013-{0} Pablo Acosta-Serafini"
    header_printed = False
    for fname in pypkg.functions.dir_tree(pkg_dir, dir_exclude, ext_exclude):
        lines = read_file(fname)
        ret = []
        save_file = False
        for line in lines:
            rmatch = regexp.match(line)
            if rmatch:
                file_year = int(rmatch.group(1))
                if file_year != year:
                    save_file = True
                    line = line.replace(
                        template.format(file_year), template.format(year)
                    )
            ret.append(line)
        if save_file:
            if not header_printed:
                header_printed = True
                print("Updating copyright notice")
            print("   File {0}".format(fname))
            with open(fname, "w") as fobj:
                fobj.write("".join(ret))


if __name__ == "__main__":
    update_copyright_notice()
