#!/usr/bin/env python
# requirements_to_rst.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0912,R0914,R0915,R1717,R1718

import os
import textwrap

from pypkg.functions import get_supported_interps, json_load


###
# Global variables
###
LINE_WIDTH = 72


###
# Functions
###
def def_links(mobj):
    """Define Sphinx requirements links."""
    fdict = json_load(os.path.join("data", "requirements.json"))
    sdeps = sorted(fdict.keys())
    olines = []
    for item in sdeps:
        olines.append(
            ".. _{name}: {url}\n".format(
                name=fdict[item]["name"], url=fdict[item]["url"]
            )
        )
    ret = []
    for line in olines:
        wobj = textwrap.wrap(line, width=LINE_WIDTH, subsequent_indent="   ")
        ret.append("\n".join([item for item in wobj]))
    mobj.out("\n".join(ret))


def make_common_entry(plist, pyver, suffix, req_ver):
    """Generate Python interpreter version entries for 2.x or 3.x series."""
    prefix = "Python {pyver}.x{suffix}".format(pyver=pyver, suffix=suffix)
    plist.append("{prefix}{ver}".format(prefix=prefix, ver=ops_to_words(req_ver)))


def make_multi_entry(plist, pkg_pyvers, ver_dict):
    """Generate Python interpreter version entries."""
    for pyver in pkg_pyvers:
        pver = pyver[2] + "." + pyver[3:]
        plist.append("Python {0}: {1}".format(pver, ops_to_words(ver_dict[pyver])))


def op_to_words(item):
    """Translate >=, ==, <= to words."""
    sdicts = [
        {"==": ""},
        {">=": " or newer"},
        {">": "newer than "},
        {"<=": " or older"},
        {"<": "older than "},
        {"!=": "except "},
    ]
    for sdict in sdicts:
        prefix = list(sdict.keys())[0]
        suffix = sdict[prefix]
        if item.startswith(prefix):
            if prefix == "==":
                return item[2:]
            if prefix == "!=":
                return suffix + item[2:]
            if prefix in [">", "<"]:
                return suffix + item[1:]
            return item[2:] + suffix
    raise RuntimeError("Inequality not supported")


def ops_to_words(item):
    """Translate requirement specification to words."""
    unsupp_ops = ["~=", "==="]
    # Ordered for  "pleasant" word specification
    supp_ops = [">=", ">", "==", "<=", "<", "!="]
    tokens = sorted(item.split(","), reverse=True)
    actual_tokens = []
    for req in tokens:
        for op in unsupp_ops:
            if req.startswith(op):
                raise RuntimeError("Unsupported version specification: {0}".format(op))
        for op in supp_ops:
            if req.startswith(op):
                actual_tokens.append(op)
                break
        else:
            raise RuntimeError("Illegal comparison operator: {0}".format(op))
    if len(list(set(actual_tokens))) != len(actual_tokens):
        raise RuntimeError("Multiple comparison operators of the same type")
    if "!=" in actual_tokens:
        return (
            " and ".join([op_to_words(token) for token in tokens[:-1]])
            + " "
            + op_to_words(tokens[-1])
        )
    return " and ".join([op_to_words(token) for token in tokens])


def proc_requirements(mobj):
    """Get requirements in reStructuredText format."""
    pyvers = ["py{0}".format(item.replace(".", "")) for item in get_supported_interps()]
    py2vers = sorted([item for item in pyvers if item.startswith("py2")])
    py3vers = sorted([item for item in pyvers if item.startswith("py3")])
    fdict = json_load(os.path.join("data", "requirements.json"))
    olines = [""]
    sdict = dict([(item["name"], item) for item in fdict.values()])
    for real_name in sorted(sdict.keys()):
        pkg_dict = sdict[real_name]
        if pkg_dict["cat"] == ["rtd"]:
            continue
        plist = [] if not pkg_dict["optional"] else ["optional"]
        # Convert instances that have a single version for all Python
        # interpreters into a full dictionary of Python interpreter and
        # package versions # so as to apply the same algorithm in all cases
        if isinstance(pkg_dict["ver"], str):
            pkg_dict["ver"] = dict([(pyver, pkg_dict["ver"]) for pyver in pyvers])
        pkg_pyvers = sorted(pkg_dict["ver"].keys())
        pkg_py2vers = sorted(
            [item for item in pkg_dict["ver"].keys() if item.startswith("py2")]
        )
        req_vers = list(set(pkg_dict["ver"].values()))
        req_py2vers = list(
            set([pkg_dict["ver"][item] for item in py2vers if item in pkg_dict["ver"]])
        )
        req_py3vers = list(
            set([pkg_dict["ver"][item] for item in py3vers if item in pkg_dict["ver"]])
        )
        if (len(req_vers) == 1) and (pkg_pyvers == pyvers):
            plist.append(ops_to_words(req_vers[0]))
        elif (
            (pkg_pyvers == pyvers)
            and (len(req_py2vers) == 1)
            and (len(req_py3vers) == 1)
        ):
            make_common_entry(plist, "2", ": ", req_py2vers[0])
            make_common_entry(plist, "3", ": ", req_py3vers[0])
        elif (
            (pkg_pyvers == pyvers)
            and (len(req_py2vers) == len(py2vers))
            and (len(req_py3vers) == 1)
            and (pkg_dict["ver"][pkg_py2vers[-1]] == req_py3vers[0])
        ):
            py2dict = dict(
                [
                    (key, value)
                    for key, value in pkg_dict["ver"].items()
                    if key.startswith("py2") and (key != pkg_py2vers[-1])
                ]
            )
            make_multi_entry(plist, py2vers[:-1], py2dict)
            pver = pkg_py2vers[-1][2] + "." + pkg_py2vers[-1][3:]
            plist.append(
                "Python {pyver} or newer: {ver}".format(
                    pyver=pver, ver=ops_to_words(req_py3vers[0])
                )
            )
        elif (
            (pkg_pyvers == pyvers)
            and (len(req_py2vers) == len(py2vers))
            and (len(req_py3vers) == 1)
        ):
            py2dict = dict(
                [
                    (key, value)
                    for key, value in pkg_dict["ver"].items()
                    if key.startswith("py2")
                ]
            )
            make_multi_entry(plist, py2vers, py2dict)
            make_common_entry(plist, "3", ": ", req_py3vers[0])
        elif (
            (pkg_pyvers == pyvers)
            and (len(req_py3vers) == len(py3vers))
            and (len(req_py2vers) == 1)
        ):
            py3dict = dict(
                [
                    (key, value)
                    for key, value in pkg_dict["ver"].items()
                    if key.startswith("py3")
                ]
            )
            make_common_entry(plist, "2", ": ", req_py2vers[0])
            make_multi_entry(plist, py3vers, py3dict)
        elif (len(req_vers) == 1) and (pkg_pyvers == py2vers):
            make_common_entry(plist, "2", " only, ", req_vers[0])
        elif (len(req_vers) == 1) and (pkg_pyvers == py3vers):
            make_common_entry(plist, "3", " only, ", req_vers[0])
        else:
            make_multi_entry(plist, pkg_pyvers, pkg_dict["ver"])
        olines.append(
            "    * `{name}`_ ({par})".format(
                name=pkg_dict["name"], par=", ".join(plist)
            )
        )
    ret = []
    for line in olines:
        wobj = textwrap.wrap(line, width=LINE_WIDTH, subsequent_indent="      ")
        ret.append("\n".join([item for item in wobj]))

    mobj.out("\n\n".join(ret) + "\n\n")
