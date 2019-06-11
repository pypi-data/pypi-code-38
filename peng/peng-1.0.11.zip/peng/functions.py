"""
Define general engineering functions.

[[[cog
import os, sys
if sys.hexversion < 0x03000000:
    import __builtin__
else:
    import builtins as __builtin__
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_eng_functions
exobj_eng = trace_ex_eng_functions.trace_module(no_print=True)
]]]
[[[end]]]
"""
# functions.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0413,E0611,R0914,R0915,R1710,W0105,W0611,W0631

# Standard library imports
import collections
import copy
from decimal import Decimal
import decimal
import math
import re
import textwrap
import os
import sys

if sys.hexversion < 0x03000000:  # pragma: no cover
    from itertools import izip_longest as zip_longest
else:  # pragma: no cover
    from itertools import zip_longest
import warnings

# PyPI imports
if os.environ.get("READTHEDOCS", "") != "True":
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        import numpy as np
import pexdoc.exh
from pexdoc.ptypes import non_negative_integer
import pyparsing

# Intra-package imports imports
from .ptypes import engineering_notation_number, engineering_notation_suffix

pyparsing.ParserElement.enablePackrat()


###
# Global variables
###
_OP_PREC = [
    "|",
    "^",
    "&",
    ["<<", ">>"],
    ["+", "-"],
    ["*", "/", "//", "%"],
    ["+", "-", "~"],
    "**",
]

_POWER_TO_SUFFIX_DICT = dict(
    (exp, prf) for exp, prf in zip(range(-24, 27, 3), "yzafpnum kMGTPEZY")
)
_SUFFIX_TO_POWER_DICT = dict(
    (value, key) for key, value in _POWER_TO_SUFFIX_DICT.items()
)
_SUFFIX_POWER_DICT = dict(
    (key, float(10 ** value)) for key, value in _SUFFIX_TO_POWER_DICT.items()
)

EngPower = collections.namedtuple("EngPower", ["suffix", "exp"])
"""Constructor for engineering notation suffix."""

NumComp = collections.namedtuple("NumComp", ["mant", "exp"])
"""Constructor for number components representation."""


###
# Functions
###
def _build_expr(tokens, higher_oplevel=-1, ldelim="(", rdelim=")"):
    """Build mathematical expression from hierarchical list."""
    # Numbers
    if isinstance(tokens, str):
        return tokens
    # Unary operators
    if len(tokens) == 2:
        return "".join(tokens)
    # Multi-term operators
    oplevel = _get_op_level(tokens[1])
    stoken = ""
    for num, item in enumerate(tokens):
        if num % 2 == 0:
            stoken += _build_expr(item, oplevel, ldelim=ldelim, rdelim=rdelim)
        else:
            stoken += item
    if (oplevel < higher_oplevel) or (
        (oplevel == higher_oplevel) and (oplevel in _OP_PREC_PAR)
    ):
        stoken = ldelim + stoken + rdelim
    return stoken


def _get_op_level(operator, nops=2):
    # There is no error checking that operator is not in the
    # operator precedence group, it is assumed that only valid
    # operators are in mathematical expression at higher function
    # levels and/or at API entry point
    for num, item in enumerate(_OP_PREC):  # pragma: no cover
        if operator in item:
            if operator not in ["+", "-"]:
                return num
            if (nops == 2) and item == ["+", "-"]:
                return num
            if (nops == 1) and item == ["+", "-", "~"]:
                return num


# Operators groups that need parenthesis around expression if lower in parse
# tree and next level up has the same operator precedence level
_OP_PREC_PAR = [_get_op_level("<<"), _get_op_level("*")]


def _next_rdelim(items, pos):
    """Return position of next matching closing delimiter."""
    for num, item in enumerate(items):
        if item > pos:
            break
    else:
        raise RuntimeError("Mismatched delimiters")
    del items[num]
    return item


def _get_functions(expr, ldelim="(", rdelim=")"):
    """Parse function calls."""
    tpars = _pair_delims(expr, ldelim=ldelim, rdelim=rdelim)
    alphas = "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    fchars = "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "0123456789" "_"
    tfuncs = []
    for lnum, rnum in tpars:
        if lnum and expr[lnum - 1] in fchars:
            for cnum, char in enumerate(reversed(expr[:lnum])):
                if char not in fchars:
                    break
            else:
                cnum = lnum
            tfuncs.append(
                {
                    "fname": expr[lnum - cnum : lnum],
                    "expr": expr[lnum + 1 : rnum],
                    "start": lnum - cnum,
                    "stop": rnum,
                }
            )
            if expr[lnum - cnum] not in alphas:
                raise RuntimeError(
                    "Function name `{0}` is not valid".format(expr[lnum - cnum : lnum])
                )
    return tfuncs


def _pair_delims(expr, ldelim="(", rdelim=")"):
    """Pair delimiters."""
    # Find where remaining delimiters are
    lindex = reversed([num for num, item in enumerate(expr) if item == ldelim])
    rindex = [num for num, item in enumerate(expr) if item == rdelim]
    # Pair remaining delimiters
    return [(lpos, _next_rdelim(rindex, lpos)) for lpos in lindex][::-1]


def _parse_expr(text, ldelim="(", rdelim=")"):
    """Parse mathematical expression using PyParsing."""
    var = pyparsing.Word(pyparsing.alphas + "_", pyparsing.alphanums + "_")
    point = pyparsing.Literal(".")
    exp = pyparsing.CaselessLiteral("E")
    number = pyparsing.Combine(
        pyparsing.Word("+-" + pyparsing.nums, pyparsing.nums)
        + pyparsing.Optional(point + pyparsing.Optional(pyparsing.Word(pyparsing.nums)))
        + pyparsing.Optional(
            exp + pyparsing.Word("+-" + pyparsing.nums, pyparsing.nums)
        )
    )
    atom = var | number
    oplist = [
        (pyparsing.Literal("**"), 2, pyparsing.opAssoc.RIGHT),
        (pyparsing.oneOf("+ - ~"), 1, pyparsing.opAssoc.RIGHT),
        (pyparsing.oneOf("* / // %"), 2, pyparsing.opAssoc.LEFT),
        (pyparsing.oneOf("+ -"), 2, pyparsing.opAssoc.LEFT),
        (pyparsing.oneOf("<< >>"), 2, pyparsing.opAssoc.LEFT),
        (pyparsing.Literal("&"), 2, pyparsing.opAssoc.LEFT),
        (pyparsing.Literal("^"), 2, pyparsing.opAssoc.LEFT),
        (pyparsing.Literal("|"), 2, pyparsing.opAssoc.LEFT),
    ]
    # Get functions
    expr = pyparsing.infixNotation(
        atom, oplist, lpar=pyparsing.Suppress(ldelim), rpar=pyparsing.Suppress(rdelim)
    )
    return expr.parseString(text)[0]


def _remove_consecutive_delims(expr, ldelim="(", rdelim=")"):
    """Remove consecutive delimiters."""
    tpars = _pair_delims(expr, ldelim=ldelim, rdelim=rdelim)
    # Flag superfluous delimiters
    ddelim = []
    for ctuple, ntuple in zip(tpars, tpars[1:]):
        if ctuple == (ntuple[0] - 1, ntuple[1] + 1):
            ddelim.extend(ntuple)
    ddelim.sort()
    # Actually remove delimiters from expression
    for num, item in enumerate(ddelim):
        expr = expr[: item - num] + expr[item - num + 1 :]
    # Get functions
    return expr


def _remove_extra_delims(expr, ldelim="(", rdelim=")", fcount=None):
    """
    Remove unnecessary delimiters (parenthesis, brackets, etc.).

    Internal function that can be recursed
    """
    if not expr.strip():
        return ""
    fcount = [0] if fcount is None else fcount
    tfuncs = _get_functions(expr, ldelim=ldelim, rdelim=rdelim)
    # Replace function call with tokens
    for fdict in reversed(tfuncs):
        fcount[0] += 1
        fdict["token"] = "__" + str(fcount[0])
        expr = expr[: fdict["start"]] + fdict["token"] + expr[fdict["stop"] + 1 :]
        fdict["expr"] = _remove_extra_delims(
            fdict["expr"], ldelim=ldelim, rdelim=rdelim, fcount=fcount
        )
    # Parse expression with function calls removed
    expr = _build_expr(
        _parse_expr(expr, ldelim=ldelim, rdelim=rdelim), ldelim=ldelim, rdelim=rdelim
    )
    # Insert cleaned-up function calls
    for fdict in tfuncs:
        expr = expr.replace(
            fdict["token"], fdict["fname"] + ldelim + fdict["expr"] + rdelim
        )
    return expr


def _split_every(text, sep, count, lstrip=False, rstrip=False):
    """
    Return list of the words in the string, using count of a separator as delimiter.

    :param text: String to split
    :type  text: string

    :param sep: Separator
    :type  sep: string

    :param count: Number of separators to use as delimiter
    :type  count: integer

    :param lstrip: Flag that indicates whether whitespace is removed
                   from the beginning of each list item (True) or not
                   (False)
    :type  lstrip: boolean

    :param rstrip: Flag that indicates whether whitespace is removed
                   from the end of each list item (True) or not (False)
    :type  rstrip: boolean

    :rtype: tuple
    """
    ltr = "_rl "[2 * lstrip + rstrip].strip()
    func = lambda x: getattr(x, ltr + "strip")() if ltr != "_" else x
    items = text.split(sep)
    groups = zip_longest(*[iter(items)] * count, fillvalue="")
    joints = (sep.join(group).rstrip(sep) for group in groups)
    return tuple(func(joint) for joint in joints)


def _to_eng_tuple(number):
    """
    Return tuple with mantissa and exponent of number formatted in engineering notation.

    :param number: Number
    :type  number: integer or float

    :rtype: tuple
    """
    # pylint: disable=W0141
    # Helper function: split integer and fractional part of mantissa
    #  + ljust ensures that integer part in engineering notation has
    #    at most 3 digits (say if number given is 1E4)
    #  + rstrip ensures that there is no empty fractional part
    split = lambda x, p: (x.ljust(3 + neg, "0")[:p], x[p:].rstrip("0"))
    # Convert number to scientific notation, a "constant" format
    mant, exp = to_scientific_tuple(number)
    mant, neg = mant.replace(".", ""), mant.startswith("-")
    # New values
    new_mant = ".".join(filter(None, split(mant, 1 + (exp % 3) + neg)))
    new_exp = int(3 * math.floor(exp / 3))
    return NumComp(new_mant, new_exp)


@pexdoc.pcontracts.contract(number="number")
def no_exp(number):
    r"""
    Convert number to string guaranteeing result is not in scientific notation.

    :param number: Number to convert
    :type  number: integer or float

    :rtype: string

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for peng.functions.no_exp

    :raises: RuntimeError (Argument \`number\` is not valid)

    .. [[[end]]]
    """
    mant, exp = to_scientific_tuple(number)
    if not exp:
        return str(number)
    floating_mant = "." in mant
    mant = mant.replace(".", "")
    if exp < 0:
        return "0." + "0" * (-exp - 1) + mant
    if not floating_mant:
        return mant + "0" * exp + (".0" if isinstance(number, float) else "")
    lfpart = len(mant) - 1
    if lfpart < exp:
        return (mant + "0" * (exp - lfpart)).rstrip(".")
    return mant


@pexdoc.pcontracts.contract(
    number="int|float", frac_length="non_negative_integer", rjust=bool
)
def peng(number, frac_length, rjust=True):
    r"""
    Convert a number to engineering notation.

    The absolute value of the number (if it is not exactly zero) is bounded to
    the interval [1E-24, 1E+24)

    :param number: Number to convert
    :type  number: integer or float

    :param frac_length: Number of digits of fractional part
    :type  frac_length: `NonNegativeInteger
                        <https://pexdoc.readthedocs.io/en/stable/
                        ptypes.html#nonnegativeinteger>`_

    :param rjust: Flag that indicates whether the number is
                  right-justified (True) or not (False)
    :type  rjust: boolean

    :rtype: string

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for peng.functions.peng

    :raises:
     * RuntimeError (Argument \`frac_length\` is not valid)

     * RuntimeError (Argument \`number\` is not valid)

     * RuntimeError (Argument \`rjust\` is not valid)

    .. [[[end]]]

    The supported engineering suffixes are:

    +----------+-------+--------+
    | Exponent | Name  | Suffix |
    +==========+=======+========+
    | 1E-24    | yocto | y      |
    +----------+-------+--------+
    | 1E-21    | zepto | z      |
    +----------+-------+--------+
    | 1E-18    | atto  | a      |
    +----------+-------+--------+
    | 1E-15    | femto | f      |
    +----------+-------+--------+
    | 1E-12    | pico  | p      |
    +----------+-------+--------+
    | 1E-9     | nano  | n      |
    +----------+-------+--------+
    | 1E-6     | micro | u      |
    +----------+-------+--------+
    | 1E-3     | milli | m      |
    +----------+-------+--------+
    | 1E+0     |       |        |
    +----------+-------+--------+
    | 1E+3     | kilo  | k      |
    +----------+-------+--------+
    | 1E+6     | mega  | M      |
    +----------+-------+--------+
    | 1E+9     | giga  | G      |
    +----------+-------+--------+
    | 1E+12    | tera  | T      |
    +----------+-------+--------+
    | 1E+15    | peta  | P      |
    +----------+-------+--------+
    | 1E+18    | exa   | E      |
    +----------+-------+--------+
    | 1E+21    | zetta | Z      |
    +----------+-------+--------+
    | 1E+24    | yotta | Y      |
    +----------+-------+--------+

    For example:

        >>> import peng
        >>> peng.peng(1235.6789E3, 3, False)
        '1.236M'
    """
    # The decimal module has a to_eng_string() function, but it does not seem
    # to work well in all cases. For example:
    # >>> decimal.Decimal('34.5712233E8').to_eng_string()
    # '3.45712233E+9'
    # >>> decimal.Decimal('34.57122334E8').to_eng_string()
    # '3457122334'
    # It seems that the conversion function does not work in all cases
    #
    # Return formatted zero if number is zero, easier to not deal with this
    # special case through the rest of the algorithm
    if number == 0:
        number = "0.{zrs}".format(zrs="0" * frac_length) if frac_length else "0"
        # Engineering notation numbers can have a sign, a 3-digit integer part,
        # a period, and a fractional part of length frac_length, so the
        # length of the number to the left of, and including, the period is 5
        return "{0} ".format(number.rjust(5 + frac_length)) if rjust else number
    # Low-bound number
    sign = +1 if number >= 0 else -1
    ssign = "-" if sign == -1 else ""
    anumber = abs(number)
    if anumber < 1e-24:
        anumber = 1e-24
        number = sign * 1e-24
    # Round fractional part if requested frac_length is less than length
    # of fractional part. Rounding method is to add a '5' at the decimal
    # position just after the end of frac_length digits
    exp = 3.0 * math.floor(math.floor(math.log10(anumber)) / 3.0)
    mant = number / 10 ** exp
    # Because exponent is a float, mantissa is a float and its string
    # representation always includes a period
    smant = str(mant)
    ppos = smant.find(".")
    if len(smant) - ppos - 1 > frac_length:
        mant += sign * 5 * 10 ** (-frac_length - 1)
        if abs(mant) >= 1000:
            exp += 3
            mant = mant / 1e3
        smant = str(mant)
        ppos = smant.find(".")
    # Make fractional part have frac_length digits
    bfrac_length = bool(frac_length)
    flength = ppos - (not bfrac_length) + frac_length + 1
    new_mant = smant[:flength].ljust(flength, "0")
    # Upper-bound number
    if exp > 24:
        new_mant, exp = (
            "{sign}999.{frac}".format(sign=ssign, frac="9" * frac_length),
            24,
        )
    # Right-justify number, engineering notation numbers can have a sign,
    # a 3-digit integer part and a period, and a fractional part of length
    # frac_length, so the length of the number to the left of the
    # period is 4
    new_mant = new_mant.rjust(rjust * (4 + bfrac_length + frac_length))
    # Format number
    num = "{mant}{suffix}".format(
        mant=new_mant, suffix=_POWER_TO_SUFFIX_DICT[exp] if exp else " " * bool(rjust)
    )
    return num


@pexdoc.pcontracts.contract(snum="engineering_notation_number")
def peng_float(snum):
    r"""
    Return floating point equivalent of a number represented in engineering notation.

    :param snum: Number
    :type  snum: :ref:`EngineeringNotationNumber`

    :rtype: string

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.functions.peng_float

    :raises: RuntimeError (Argument \`snum\` is not valid)

    .. [[[end]]]

    For example:

        >>> import peng
        >>> peng.peng_float(peng.peng(1235.6789E3, 3, False))
        1236000.0
    """
    # This can be coded as peng_mant(snum)*(peng_power(snum)[1]), but the
    # "function unrolling" is about 4x faster
    snum = snum.rstrip()
    power = _SUFFIX_POWER_DICT[" " if snum[-1].isdigit() else snum[-1]]
    return float(snum if snum[-1].isdigit() else snum[:-1]) * power


@pexdoc.pcontracts.contract(snum="engineering_notation_number")
def peng_frac(snum):
    r"""
    Return the fractional part of a number represented in engineering notation.

    :param snum: Number
    :type  snum: :ref:`EngineeringNotationNumber`

    :rtype: integer

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.functions.peng_frac

    :raises: RuntimeError (Argument \`snum\` is not valid)

    .. [[[end]]]

    For example:

        >>> import peng
        >>> peng.peng_frac(peng.peng(1235.6789E3, 3, False))
        236
    """
    snum = snum.rstrip()
    pindex = snum.find(".")
    if pindex == -1:
        return 0
    return int(snum[pindex + 1 :] if snum[-1].isdigit() else snum[pindex + 1 : -1])


def peng_int(snum):
    r"""
    Return the integer part of a number represented in engineering notation.

    :param snum: Number
    :type  snum: :ref:`EngineeringNotationNumber`

    :rtype: integer

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for peng.functions.peng_int

    :raises: RuntimeError (Argument \`snum\` is not valid)

    .. [[[end]]]

    For example:

        >>> import peng
        >>> peng.peng_int(peng.peng(1235.6789E3, 3, False))
        1
    """
    return int(peng_mant(snum))


@pexdoc.pcontracts.contract(snum="engineering_notation_number")
def peng_mant(snum):
    r"""
    Return the mantissa of a number represented in engineering notation.

    :param snum: Number
    :type  snum: :ref:`EngineeringNotationNumber`

    :rtype: float

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.functions.peng_mant

    :raises: RuntimeError (Argument \`snum\` is not valid)

    .. [[[end]]]

    For example:

        >>> import peng
        >>> peng.peng_mant(peng.peng(1235.6789E3, 3, False))
        1.236
    """
    snum = snum.rstrip()
    return float(snum if snum[-1].isdigit() else snum[:-1])


@pexdoc.pcontracts.contract(snum="engineering_notation_number")
def peng_power(snum):
    r"""
    Return engineering suffix and its floating point equivalent of a number.

    :py:func:`peng.peng` lists the correspondence between suffix and floating
    point exponent.

    :param snum: Number
    :type  snum: :ref:`EngineeringNotationNumber`

    :rtype: named tuple in which the first item is the engineering suffix and
            the second item is the floating point equivalent of the suffix
            when the number is represented in engineering notation.


    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.functions.peng_power

    :raises: RuntimeError (Argument \`snum\` is not valid)

    .. [[[end]]]

    For example:

        >>> import peng
        >>> peng.peng_power(peng.peng(1235.6789E3, 3, False))
        EngPower(suffix='M', exp=1000000.0)
    """
    suffix = " " if snum[-1].isdigit() else snum[-1]
    return EngPower(suffix, _SUFFIX_POWER_DICT[suffix])


@pexdoc.pcontracts.contract(snum="engineering_notation_number")
def peng_suffix(snum):
    r"""
    Return the suffix of a number represented in engineering notation.

    :param snum: Number
    :type  snum: :ref:`EngineeringNotationNumber`

    :rtype: string

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.functions.peng_suffix

    :raises: RuntimeError (Argument \`snum\` is not valid)

    .. [[[end]]]

    For example:

        >>> import peng
        >>> peng.peng_suffix(peng.peng(1235.6789E3, 3, False))
        'M'
    """
    snum = snum.rstrip()
    return " " if snum[-1].isdigit() else snum[-1]


@pexdoc.pcontracts.contract(suffix="engineering_notation_suffix", offset=int)
def peng_suffix_math(suffix, offset):
    r"""
    Return engineering suffix from a starting suffix and an number of suffixes offset.

    :param suffix: Engineering suffix
    :type  suffix: :ref:`EngineeringNotationSuffix`

    :param offset: Engineering suffix offset
    :type  offset: integer

    :rtype: string

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.functions.peng_suffix_math

    :raises:
     * RuntimeError (Argument \`offset\` is not valid)

     * RuntimeError (Argument \`suffix\` is not valid)

     * ValueError (Argument \`offset\` is not valid)

    .. [[[end]]]

    For example:

        >>> import peng
        >>> peng.peng_suffix_math('u', 6)
        'T'
    """
    # pylint: disable=W0212
    eobj = pexdoc.exh.addex(ValueError, "Argument `offset` is not valid")
    try:
        return _POWER_TO_SUFFIX_DICT[_SUFFIX_TO_POWER_DICT[suffix] + 3 * offset]
    except KeyError:
        eobj(True)


def remove_extra_delims(expr, ldelim="(", rdelim=")"):
    r"""
    Remove unnecessary delimiters in mathematical expressions.

    Delimiters (parenthesis, brackets, etc.) may be removed either because
    there are multiple consecutive delimiters enclosing a single expressions or
    because the delimiters are implied by operator precedence rules. Function
    names must start with a letter and then can contain alphanumeric characters
    and a maximum of one underscore

    :param expr: Mathematical expression
    :type  expr: string

    :param ldelim: Single character left delimiter
    :type  ldelim: string

    :param rdelim: Single character right delimiter
    :type  rdelim: string

    :rtype: string

    :raises:
     * RuntimeError (Argument \`expr\` is not valid)

     * RuntimeError (Argument \`ldelim\` is not valid)

     * RuntimeError (Argument \`rdelim\` is not valid)

     * RuntimeError (Function name `*[function_name]*` is not valid)

     * RuntimeError (Mismatched delimiters)
    """
    op_group = ""
    for item1 in _OP_PREC:
        if isinstance(item1, list):
            for item2 in item1:
                op_group += item2
        else:
            op_group += item1
    iobj = zip([expr, ldelim, rdelim], ["expr", "ldelim", "rdelim"])
    for item, desc in iobj:
        if not isinstance(item, str):
            raise RuntimeError("Argument `{0}` is not valid".format(desc))
    if (len(ldelim) != 1) or ((len(ldelim) == 1) and (ldelim in op_group)):
        raise RuntimeError("Argument `ldelim` is not valid")
    if (len(rdelim) != 1) or ((len(rdelim) == 1) and (rdelim in op_group)):
        raise RuntimeError("Argument `rdelim` is not valid")
    if expr.count(ldelim) != expr.count(rdelim):
        raise RuntimeError("Mismatched delimiters")
    if not expr:
        return expr
    vchars = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        ".0123456789"
        r"_()[]\{\}" + rdelim + ldelim + op_group
    )
    if any([item not in vchars for item in expr]) or ("__" in expr):
        raise RuntimeError("Argument `expr` is not valid")
    expr = _remove_consecutive_delims(expr, ldelim=ldelim, rdelim=rdelim)
    expr = expr.replace(ldelim + rdelim, "")
    return _remove_extra_delims(expr, ldelim=ldelim, rdelim=rdelim)


def round_mantissa(arg, decimals=0):
    """
    Round floating point number(s) mantissa to given number of digits.

    Integers are not altered. The mantissa used is that of the floating point
    number(s) when expressed in `normalized scientific notation
    <https://en.wikipedia.org/wiki/Scientific_notation#Normalized_notation>`_

    :param arg: Input data
    :type  arg: integer, float, Numpy vector of integers or floats, or None

    :param decimals: Number of digits to round the fractional part of the
                     mantissa to.
    :type  decimals: integer

    :rtype: same as **arg**

    For example::

        >>> import peng
        >>> peng.round_mantissa(012345678E-6, 3)
        12.35
        >>> peng.round_mantissa(5, 3)
        5
    """
    if arg is None:
        return arg
    if isinstance(arg, np.ndarray):
        foi = [isinstance(item, int) for item in arg]
        return np.array(
            [
                item if isint else float(to_scientific_string(item, decimals))
                for isint, item in zip(foi, arg)
            ]
        )
    if isinstance(arg, int):
        return arg
    return float(to_scientific_string(arg, decimals))


def pprint_vector(vector, limit=False, width=None, indent=0, eng=False, frac_length=3):
    r"""
    Format a list of numbers (vector) or a Numpy vector for printing.

    If the argument **vector** is :code:`None` the string :code:`'None'` is
    returned

    :param vector: Vector to pretty print or None
    :type  vector: list of integers or floats, Numpy vector or None

    :param limit: Flag that indicates whether at most 6 vector items are
                  printed (all vector items if its length is equal or less
                  than 6, first and last 3 vector items if it is not) (True),
                  or the entire vector is printed (False)
    :type  limit: boolean

    :param width: Number of available characters per line. If None the vector
                  is printed in one line
    :type  width: integer or None

    :param indent: Flag that indicates whether all subsequent lines after the
                   first one are indented (True) or not (False). Only relevant
                   if **width** is not None
    :type  indent: boolean

    :param eng: Flag that indicates whether engineering notation is used
                (True) or not (False)
    :type  eng: boolean

    :param frac_length: Number of digits of fractional part (only applicable
                        if **eng** is True)
    :type  frac_length: integer

    :raises: ValueError (Argument \`width\` is too small)

    :rtype: string

    For example:

        >>> from __future__ import print_function
        >>> import peng
        >>> header = 'Vector: '
        >>> data = [1e-3, 20e-6, 300e+6, 4e-12, 5.25e3, -6e-9, 700, 8, 9]
        >>> print(
        ...     header+peng.pprint_vector(
        ...         data,
        ...         width=30,
        ...         eng=True,
        ...         frac_length=1,
        ...         limit=True,
        ...         indent=len(header)
        ...     )
        ... )
        Vector: [    1.0m,   20.0u,  300.0M,
                             ...
                   700.0 ,    8.0 ,    9.0  ]
        >>> print(
        ...     header+peng.pprint_vector(
        ...         data,
        ...         width=30,
        ...         eng=True,
        ...         frac_length=0,
        ...         indent=len(header)
        ...     )
        ... )
        Vector: [    1m,   20u,  300M,    4p,
                     5k,   -6n,  700 ,    8 ,
                     9  ]
        >>> print(peng.pprint_vector(data, eng=True, frac_length=0))
        [    1m,   20u,  300M,    4p,    5k,   -6n,  700 ,    8 ,    9  ]
        >>> print(peng.pprint_vector(data, limit=True))
        [ 0.001, 2e-05, 300000000.0, ..., 700, 8, 9 ]
    """
    # pylint: disable=R0912,R0913
    num_digits = 12
    approx = lambda x: float(x) if "." not in x else round(float(x), num_digits)

    def limstr(value):
        str1 = str(value)
        iscomplex = isinstance(value, complex)
        str1 = str1.lstrip("(").rstrip(")")
        if "." not in str1:
            return str1
        if iscomplex:
            sign = "+" if value.imag >= 0 else "-"
            regexp = re.compile(
                r"(.*(?:[Ee][\+-]\d+)?)"
                + (r"\+" if sign == "+" else "-")
                + r"(.*(?:[Ee][\+-]\d+)?j)"
            )
            rvalue, ivalue = regexp.match(str1).groups()
            return (
                str(complex(approx(rvalue), approx(sign + ivalue.strip("j"))))
                .lstrip("(")
                .rstrip(")")
            )
        str2 = str(round(value, num_digits))
        return str2 if len(str1) > len(str2) else str1

    def _str(*args):
        """
        Convert numbers to string, optionally represented in engineering notation.

        Numbers may be integers, float or complex
        """
        ret = [
            (limstr(element) if not eng else peng(element, frac_length, True))
            if not isinstance(element, complex)
            else (
                limstr(element)
                if not eng
                else "{real}{sign}{imag}j".format(
                    real=peng(element.real, frac_length, True),
                    imag=peng(abs(element.imag), frac_length, True),
                    sign="+" if element.imag >= 0 else "-",
                )
            )
            for element in args
        ]
        return ret[0] if len(ret) == 1 else ret

    if vector is None:
        return "None"
    lvector = len(vector)
    if (not limit) or (limit and (lvector < 7)):
        items = _str(*vector)
        uret = "[ {0} ]".format(", ".join(items))
    else:
        items = _str(*(vector[:3] + vector[-3:]))
        uret = "[ {0}, ..., {1} ]".format(", ".join(items[:3]), ", ".join(items[-3:]))
    if (width is None) or (len(uret) < width):
        return uret
    # -4 comes from the fact that an opening '[ ' and a closing ' ]'
    # are added to the multi-line vector string
    if any([len(item) > width - 4 for item in items]):
        raise ValueError("Argument `width` is too small")
    # Text needs to be wrapped in multiple lines
    # Figure out how long the first line needs to be
    wobj = textwrap.TextWrapper(initial_indent="[ ", width=width)
    # uret[2:] -> do not include initial '[ ' as this is specified as
    # the initial indent to the text wrapper
    rlist = wobj.wrap(uret[2:])
    first_line = rlist[0]
    first_line_elements = first_line.count(",")
    # Reconstruct string representation of vector excluding first line
    # Remove ... from text to be wrapped because it is placed in a single
    # line centered with the content
    uret_left = (",".join(uret.split(",")[first_line_elements:])).replace("...,", "")
    wobj = textwrap.TextWrapper(width=width - 2)
    wrapped_text = wobj.wrap(uret_left.lstrip())
    # Construct candidate wrapped and indented list of vector elements
    rlist = [first_line] + [
        (" " * (indent + 2)) + item.rstrip() for item in wrapped_text
    ]
    last_line = rlist[-1]
    last_line_elements = last_line.count(",") + 1
    # "Manually" format limit output so that it is either 3 lines, first and
    # last line with 3 elements and the middle with '...' or 7 lines, each with
    # 1 element and the middle with '...'
    # If numbers are not to be aligned at commas (variable width) then use the
    # existing results of the wrap() function
    if limit and (lvector > 6):
        if (first_line_elements < 3) or (
            (first_line_elements == 3) and (last_line_elements < 3)
        ):
            rlist = [
                "[ {0},".format(_str(vector[0])),
                _str(vector[1]),
                _str(vector[2]),
                "...",
                _str(vector[-3]),
                _str(vector[-2]),
                "{0} ]".format(_str(vector[-1])),
            ]
            first_line_elements = 1
        else:
            rlist = [
                "[ {0},".format(", ".join(_str(*vector[:3]))),
                "...",
                "{0} ]".format(", ".join(_str(*vector[-3:]))),
            ]
        first_line = rlist[0]
    elif limit:
        rlist = [item.lstrip() for item in rlist]
    first_comma_index = first_line.find(",")
    actual_width = len(first_line) - 2
    if not eng:
        if not limit:
            return "\n".join(rlist)
        num_elements = len(rlist)
        return "\n".join(
            [
                "{spaces}{line}{comma}".format(
                    spaces=(" " * (indent + 2)) if num > 0 else "",
                    line=(
                        line.center(actual_width).rstrip()
                        if line.strip() == "..."
                        else line
                    ),
                    comma=(
                        ","
                        if (
                            (num < num_elements - 1)
                            and (not line.endswith(","))
                            and (line.strip() != "...")
                        )
                        else ""
                    ),
                )
                if num > 0
                else line
                for num, line in enumerate(rlist)
            ]
        )
    # Align elements across multiple lines
    if limit:
        remainder_list = [line.lstrip() for line in rlist[1:]]
    else:
        remainder_list = _split_every(
            text=uret[len(first_line) :],
            sep=",",
            count=first_line_elements,
            lstrip=True,
        )
    new_wrapped_lines_list = [first_line]
    for line in remainder_list[:-1]:
        new_wrapped_lines_list.append(
            "{0},".format(line).rjust(actual_width)
            if line != "..."
            else line.center(actual_width).rstrip()
        )
    # Align last line on fist comma (if it exists) or
    # on length of field if does not
    if remainder_list[-1].find(",") == -1:
        marker = len(remainder_list[-1]) - 2
    else:
        marker = remainder_list[-1].find(",")
    new_wrapped_lines_list.append(
        "{0}{1}".format((first_comma_index - marker - 2) * " ", remainder_list[-1])
    )
    return "\n".join(
        [
            "{spaces}{line}".format(spaces=" " * (indent + 2), line=line)
            if num > 0
            else line
            for num, line in enumerate(new_wrapped_lines_list)
        ]
    )


def to_scientific_string(number, frac_length=None, exp_length=None, sign_always=False):
    """
    Convert number or number string to a number string in scientific notation.

    Full precision is maintained if the number is represented as a string

    :param number: Number to convert
    :type  number: number or string

    :param frac_length: Number of digits of fractional part, None indicates
                        that the fractional part of the number should not be
                        limited
    :type  frac_length: integer or None

    :param exp_length: Number of digits of the exponent; the actual length of
                       the exponent takes precedence if it is longer
    :type  exp_length: integer or None

    :param sign_always: Flag that indicates whether the sign always
                        precedes the number for both non-negative and negative
                        numbers (True) or only for negative numbers (False)
    :type  sign_always: boolean

    :rtype: string

    For example:

        >>> import peng
        >>> peng.to_scientific_string(333)
        '3.33E+2'
        >>> peng.to_scientific_string(0.00101)
        '1.01E-3'
        >>> peng.to_scientific_string(99.999, 1, 2, True)
        '+1.0E+02'
    """
    # pylint: disable=W0702
    try:
        number = -1e20 if np.isneginf(number) else number
    except:
        pass
    try:
        number = +1e20 if np.isposinf(number) else number
    except:
        pass
    exp_length = 0 if not exp_length else exp_length
    mant, exp = to_scientific_tuple(number)
    fmant = float(mant)
    if (not frac_length) or (fmant == int(fmant)):
        return "{sign}{mant}{period}{zeros}E{exp_sign}{exp}".format(
            sign="+" if sign_always and (fmant >= 0) else "",
            mant=mant,
            period="." if frac_length else "",
            zeros="0" * frac_length if frac_length else "",
            exp_sign="-" if exp < 0 else "+",
            exp=str(abs(exp)).rjust(exp_length, "0"),
        )
    rounded_mant = round(fmant, frac_length)
    # Avoid infinite recursion when rounded mantissa is _exactly_ 10
    if abs(rounded_mant) == 10:
        rounded_mant = fmant = -1.0 if number < 0 else 1.0
        frac_length = 1
        exp = exp + 1
    zeros = 2 + (1 if (fmant < 0) else 0) + frac_length - len(str(rounded_mant))
    return "{sign}{mant}{zeros}E{exp_sign}{exp}".format(
        sign="+" if sign_always and (fmant >= 0) else "",
        mant=rounded_mant,
        zeros="0" * zeros,
        exp_sign="-" if exp < 0 else "+",
        exp=str(abs(exp)).rjust(exp_length, "0"),
    )


def to_scientific_tuple(number):
    """
    Return mantissa and exponent of a number in scientific notation.

    Full precision is maintained if the number is represented as a string

    :param number: Number
    :type  number: integer, float or string

    :rtype: named tuple in which the first item is the mantissa (*string*)
            and the second item is the exponent (*integer*) of the number
            when expressed in scientific notation

    For example:

        >>> import peng
        >>> peng.to_scientific_tuple('135.56E-8')
        NumComp(mant='1.3556', exp=-6)
        >>> peng.to_scientific_tuple(0.0000013556)
        NumComp(mant='1.3556', exp=-6)
    """
    # pylint: disable=W0632
    convert = not isinstance(number, str)
    # Detect zero and return, simplifies subsequent algorithm
    if (convert and (number == 0)) or (
        (not convert) and (not number.strip("0").strip("."))
    ):
        return ("0", 0)
    # Break down number into its components, use Decimal type to
    # preserve resolution:
    # sign  : 0 -> +, 1 -> -
    # digits: tuple with digits of number
    # exp   : exponent that gives null fractional part
    sign, digits, exp = Decimal(str(number) if convert else number).as_tuple()
    mant = (
        "{sign}{itg}{frac}".format(
            sign="-" if sign else "",
            itg=digits[0],
            frac=(
                ".{frac}".format(frac="".join([str(num) for num in digits[1:]]))
                if len(digits) > 1
                else ""
            ),
        )
        .rstrip("0")
        .rstrip(".")
    )
    exp += len(digits) - 1
    return NumComp(mant, exp)
