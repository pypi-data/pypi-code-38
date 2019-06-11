#!/usr/bin/env python
# gen_req_files.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0413,E0602

# Standard library imports
from __future__ import print_function
import os
import subprocess
import sys

# Intra-package imports
from pypkg.functions import get_supported_interps, json_load


###
# Functions
###
def freeze_pkg_vers(fnames):
    """Bound version of specific pacakges to what is already installed."""
    pobj = subprocess.Popen(
        ["pip", "freeze"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    lines, _ = pobj.communicate()
    if sys.hexversion >= 0x03000000:
        lines = lines.decode("utf-8")
    pkgs = {"numpy": "", "scipy": "", "matplotlib": ""}
    for line in lines.split("\n"):
        for pkg in pkgs:
            if line.startswith(pkg):
                pkgs[pkg] = line
    for fname in fnames:
        ilines = read_file(fname)
        olines = []
        for iline in ilines:
            iline = iline.rstrip()
            for pkg, oline in pkgs.items():
                if iline.startswith(pkg):
                    olines.append(oline)
                    break
            else:
                olines.append(iline)
        with open(fname, "w") as fobj:
            fobj.write("\n".join(olines))


def insert_element(items, item, pos):
    """Insert element at a given position even if larger than list size."""
    item = item + "\n"
    if (pos < len(items) - 1) and items[pos]:
        raise RuntimeError("Repeated order element")
    elif pos < len(items) - 1:
        items[pos] = item
    else:
        items.extend([""] * (pos + 1 - len(items)))
        items[pos] = item


def gen_req_files(freeze_ver=False):
    # pylint: disable=R0101,R0912,R0914
    """Generate requirements files."""
    fdict = json_load(os.path.join("data", "requirements.json"))
    pyvers = ["py{0}".format(item.replace(".", "")) for item in get_supported_interps()]
    odict = {"rtd": []}
    for pyver in pyvers:
        odict["main_{0}".format(pyver)] = []
        odict["tests_{0}".format(pyver)] = []
        odict["docs_{0}".format(pyver)] = []
    for pkg_name, pkg_dict in fdict.items():
        pkg_dict["cat"] = (
            pkg_dict["cat"] if isinstance(pkg_dict["cat"], list) else [pkg_dict["cat"]]
        )
        for cat in pkg_dict["cat"]:
            if cat not in ["main", "tests", "docs", "rtd"]:
                raise RuntimeError("Category {0} not recognized".format(cat))
            if cat == "rtd":
                ver = pkg_dict["ver"]
                if (not isinstance(pkg_dict["ver"], str)) and (
                    "py27" not in pkg_dict["ver"]
                ):
                    raise RuntimeError(
                        (
                            "Multi-interpreter versions does not"
                            "include Python 2.7 for category {0}".format(cat)
                        )
                    )
                elif not isinstance(pkg_dict["ver"], str):
                    # ReadTheDocs build environment is Python 2.7
                    ver = pkg_dict["ver"]["py27"]
                insert_element(
                    odict[cat],
                    "{pkg_name}{ver}".format(pkg_name=pkg_name, ver=ver),
                    pkg_dict["pos"],
                )
            else:
                if not isinstance(pkg_dict["ver"], dict):
                    for pyver in pyvers:
                        insert_element(
                            odict["{cat}_{ver}".format(cat=cat, ver=pyver)],
                            "{pkg_name}{ver}".format(
                                pkg_name=pkg_name, ver=pkg_dict["ver"]
                            ),
                            pkg_dict["pos"],
                        )
                else:
                    for pyver, pkg_ver in pkg_dict["ver"].items():
                        if pyver not in pyvers:
                            raise RuntimeError(
                                "Python version {0} not recognized".format(pyver)
                            )
                        insert_element(
                            odict["{cat}_{ver}".format(cat=cat, ver=pyver)],
                            "{pkg_name}{ver}".format(pkg_name=pkg_name, ver=pkg_ver),
                            pkg_dict["pos"],
                        )
    pkgdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reqdir = os.path.join(pkgdir, "requirements")
    fnames = []
    for cat in sorted(odict):
        odict[cat] = [item for item in odict[cat] if item]
        fname = os.path.join(reqdir, "{0}.pip".format(cat))
        fnames.append(fname)
        print("Generating file {0}".format(fname))
        with open(fname, "w") as fobj:
            fobj.writelines(odict[cat])
    if freeze_ver:
        freeze_pkg_vers(fnames)


def read_file(fname):
    """Read file in Python 2 or Python 3."""
    if sys.hexversion < 0x03000000:
        with open(fname, "r") as fobj:
            return fobj.readlines()
    else:
        try:
            with open(fname, "r") as fobj:
                return fobj.readlines()
        except UnicodeDecodeError:
            with open(fname, "r", encoding="utf-8") as fobj:
                return fobj.readlines()


if __name__ == "__main__":
    FREEZE_VER = False
    if (len(sys.argv) > 1) and (sys.argv[1].lower() == "freeze"):
        FREEZE_VER = True
    gen_req_files(FREEZE_VER)
