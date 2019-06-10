# trace_support.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0411,E0401,E0611,W0212

# Standard library imports
from __future__ import print_function
import collections
import copy
import datetime
import os
import warnings

# PyPI imports
with warnings.catch_warnings():
    from _pytest.warning_types import PytestWarning

    warnings.filterwarnings("ignore", category=PytestWarning)
    import pytest
import pmisc
import pexdoc.exdoc


###
# Functions
###
def trace_pars(mname):
    """Define trace parameters."""
    pickle_fname = os.path.join(os.path.dirname(__file__), "{0}.pkl".format(mname))
    ddir = os.path.dirname(os.path.dirname(__file__))
    moddb_fname = os.path.join(ddir, "moddb.json")
    in_callables_fname = moddb_fname if os.path.exists(moddb_fname) else None
    out_callables_fname = os.path.join(ddir, "{0}.json".format(mname))
    noption = os.environ.get("NOPTION", None)
    exclude = ["_pytest", "execnet"]
    partuple = collections.namedtuple(
        "ParTuple",
        [
            "pickle_fname",
            "in_callables_fname",
            "out_callables_fname",
            "noption",
            "exclude",
        ],
    )
    return partuple(
        pickle_fname, in_callables_fname, out_callables_fname, noption, exclude
    )


def run_trace(
    mname,
    fname,
    module_prefix,
    callable_names,
    no_print,
    module_exclude=None,
    callable_exclude=None,
    debug=False,
):
    """Run module tracing."""
    # pylint: disable=R0913
    module_exclude = [] if module_exclude is None else module_exclude
    callable_exclude = [] if callable_exclude is None else callable_exclude
    par = trace_pars(mname)
    start_time = datetime.datetime.now()
    with pexdoc.exdoc.ExDocCxt(
        exclude=par.exclude + module_exclude,
        pickle_fname=par.pickle_fname,
        in_callables_fname=par.in_callables_fname,
        out_callables_fname=par.out_callables_fname,
        _no_print=no_print,
    ) as exdoc_obj:
        fname = os.path.realpath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "tests",
                "test_{0}.py".format(fname),
            )
        )
        test_cmd = (
            ["--color=yes"]
            + (["-s", "-vv"] if debug else ["-q", "-q", "-q"])
            + ["--disable-warnings"]
            + ["-x"]
            + ([par.noption] if par.noption else [])
            + ["-m " + mname]
            + [fname]
        )
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=PytestWarning)
            if pytest.main(test_cmd):
                raise RuntimeError("Tracing did not complete successfully")
    stop_time = datetime.datetime.now()
    if not no_print:
        print(
            "Auto-generation of exceptions documentation time: {0}".format(
                pmisc.elapsed_time_string(start_time, stop_time)
            )
        )
        for callable_name in callable_names:
            callable_name = module_prefix + callable_name
            print("\nCallable: {0}".format(callable_name))
            print(exdoc_obj.get_sphinx_doc(callable_name, exclude=callable_exclude))
            print("\n")
    return copy.copy(exdoc_obj)
