# trace_ex_eng_wave_functions.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import docs.support.trace_support


def trace_module(no_print=True):
    """Trace eng wave module exceptions."""
    mname = "wave_functions"
    fname = "peng"
    module_prefix = "peng.{0}.".format(mname)
    callable_names = (
        "acos",
        "acosh",
        "asin",
        "asinh",
        "atan",
        "atanh",
        "average",
        "ceil",
        "cos",
        "cosh",
        "db",
        "derivative",
        "exp",
        "floor",
        "imag",
        "integral",
        "log",
        "log10",
        "nintegral",
        "nmin",
        "nmax",
        "phase",
        "round",
        "sin",
        "sinh",
        "sqrt",
        "tan",
        "tanh",
        "wcomplex",
        "wfloat",
        "wint",
    )
    return docs.support.trace_support.run_trace(
        mname, fname, module_prefix, callable_names, no_print
    )


if __name__ == "__main__":
    trace_module(False)
