# trace_ex_eng_functions.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import docs.support.trace_support


def trace_module(no_print=True):
    """Trace eng functions module exceptions."""
    mname = "functions"
    fname = "peng"
    module_prefix = "peng.{0}.".format(mname)
    callable_names = (
        "no_exp",
        "peng",
        "peng_float",
        "peng_frac",
        "peng_int",
        "peng_mant",
        "peng_power",
        "peng_suffix",
        "peng_suffix_math",
    )
    return docs.support.trace_support.run_trace(
        mname, fname, module_prefix, callable_names, no_print
    )


if __name__ == "__main__":
    trace_module(False)
