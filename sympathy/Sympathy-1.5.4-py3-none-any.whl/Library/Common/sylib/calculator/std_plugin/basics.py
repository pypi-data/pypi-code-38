# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import inspect
import collections

import numpy as np

from sylib.calculator import plugins


class LogicOperator(object):
    @staticmethod
    def nand(arr1, arr2):
        """
        Logical nand operator. Equivalent to np.logical_not(np.logical_and).
        """
        return np.logical_not(np.logical_and(arr1, arr2))

    @staticmethod
    def nor(arr1, arr2):
        """
        Logical nor operator. Equivalent to np.logical_not(np.logical_or).
        """
        return np.logical_not(np.logical_or(arr1, arr2))


class Statistics(object):
    @staticmethod
    def median(arr):
        """
        Median. Equivalent to np.ma.median except for the case where all values
        are masked. This function then returns NaN.
        """
        res = np.ma.median(arr)
        if res is np.ma.masked:
            res = np.float64('nan')
        return res


# TODO: docstrings and eval text should match better.
ARITHMETICS_OPS = [
    ("+ (plus)", "${signal0} + ${signal1}", "Plus"),
    ("- (minus)", "${signal0} - ${signal1}", "Minus"),
    ("* (times)", "${signal0} * ${signal1}", "Multiplication"),
    ("** (power)", "${signal0} ** ${signal1}", "Power."),
    ("/ (division)", "${signal0} / ${signal1}",
     "Division. Note that if both inputs are integers the result will also be "
     "truncated to an integer."),
    ("// (floor division)", "${signal0} // ${signal1}", "floor division or "
                                                        "integer division"),
    ("% (remainder)", "${signal0} % ${signal1}", inspect.getdoc(np.mod)),
    ("divmod (floor division and remainder)", "divmod(${signal0}, ${signal1})",
     inspect.getdoc(divmod)),
]


# TODO: docstrings and eval text should match better.
COMPARATORS = [
    ("== (equal)", "${signal0} == ${signal1}", inspect.getdoc(np.equal)),
    ("!= (not equal)", "${signal0} != ${signal1}",
     inspect.getdoc(np.not_equal)),
    ("> (more than)", "${signal0} > ${signal1}", inspect.getdoc(np.greater)),
    ("< (less than)", "${signal0} < ${signal1}", inspect.getdoc(np.less)),
    (">= (more or equal)", "${signal0} >= ${signal1}",
     inspect.getdoc(np.greater_equal)),
    ("<= (less or equal)", "${signal0} <= ${signal1}",
     inspect.getdoc(np.less_equal)),
]


LOGIC_OPS = [
    ("not", "np.logical_not(${signal0})",
     inspect.getdoc(np.logical_not)),
    ("and", "np.logical_and(${signal0}, ${signal1})",
     inspect.getdoc(np.logical_and)),
    ("or", "np.logical_or(${signal0}, ${signal1})",
     inspect.getdoc(np.logical_or)),
    ("all", "all(${signal0})",
     inspect.getdoc(all)),
    ("any", "any(${signal0})",
     inspect.getdoc(any)),
    ("xor", "np.logical_xor(${signal0}, ${signal1})",
     inspect.getdoc(np.logical_xor)),
    ("nand", "ca.nand(${signal0}, ${signal1})",
     inspect.getdoc(LogicOperator.nand)),
    ("nor", "ca.nor(${signal0}, ${signal1})",
     inspect.getdoc(LogicOperator.nor)),
]


# TODO: docstrings and eval text should match better.
BITWISE = [
    ("~ (not)", "~${signal0}", inspect.getdoc(np.bitwise_not)),
    ("& (and)", "${signal0} & ${signal1}", inspect.getdoc(np.bitwise_and)),
    ("| (or)", "${signal0} | ${signal1}", inspect.getdoc(np.bitwise_or)),
    ("^ (xor)", "${signal0} ^ ${signal1}", inspect.getdoc(np.bitwise_xor)),
    ("<< (left shift)", "${signal0} << value", inspect.getdoc(np.left_shift)),
    (">> (right shift)", "${signal0} >> value",
     inspect.getdoc(np.right_shift)),
]


OPERATORS = collections.OrderedDict([
    ("Arithmetics", ARITHMETICS_OPS),
    ("Comparators", COMPARATORS),
    ("Logics", LOGIC_OPS),
    ("Bitwise", BITWISE),
])


STATISTICS = [
    ("Sum", "sum(${signal0})", inspect.getdoc(sum)),
    ("Min", "min(${signal0})", inspect.getdoc(min)),
    ("Max", "max(${signal0})", inspect.getdoc(max)),
    ("Mean", "np.mean(${signal0})", inspect.getdoc(np.mean)),
    ("Standard deviation", "np.std(${signal0})", inspect.getdoc(np.std)),
    ("Median", "ca.median(${signal0})", inspect.getdoc(np.ma.median)),
    ("Percentile", "np.percentile(${signal0}, value)",
     inspect.getdoc(np.percentile)),
]


GUI_DICT = collections.OrderedDict([
        ("Operators", OPERATORS),
        ("Statistics", STATISTICS),
    ])
