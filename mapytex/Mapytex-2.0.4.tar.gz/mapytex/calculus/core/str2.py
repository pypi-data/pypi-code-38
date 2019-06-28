#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Converting a string with coroutines
"""

from functools import partial
from decimal import Decimal, InvalidOperation
from .coroutine import *
from .operator import is_operator
from .MO import moify_cor
from .random.leaf import look_for_rdleaf

__all__ = ["str2"]


class ParsingError(Exception):
    pass


def maybe_it_is(cara):
    """ Return a function which return

    Maybe if cara startwith the argument and True if it is cara

    :exemple:

    >>> it_is_pipo = maybe_it_is("pipo")
    >>> it_is_pipo("pi")
    'maybe'
    >>> it_is_pipo("pipo")
    True
    >>> it_is_pipo("uo")
    False
    >>> it_is_iuo = maybe_it_is("iuo")
    >>> it_is_iuo("pi")
    False
    >>> it_is_iuo("iuo")
    True
    >>> it_is_iuo("uo")
    False
    """

    def func(c):
        if c == cara:
            return True
        elif cara.startswith(c):
            return "maybe"
        else:
            return False

    return func


def something_in(cara_list):
    """ Return a function which sais whether a caracter is in cara_list or not
    """

    def func(c):
        if c in cara_list:
            return True
        else:
            return False

    return func


@coroutine
def lookfor(condition, replace=lambda x: "".join(x)):
    """ Sink which is looking for term and yield replace founded patern 
    with the lenght of the accumulation.

    It can be reset by sending None

    :param condition: conditional function which returns a boolean or "maybe"
    :param replace: function which make a final transformation to the founded
    string. Id by default.

    :example:

    >>> lf = lookfor(maybe_it_is("pipo"), lambda x: 'remp')
    >>> acc = ""
    >>> for i in 'popipo':
    ...    a = lf.send(i)
    ...    if a == "maybe":
    ...        acc += i
    ...    elif a:
    ...        acc = ""
    ...        print(a)
    ...    else:
    ...        print(acc + i)
    ...        acc = ""
    po
    remp
    >>> lf = lookfor(maybe_it_is("po") , lambda x: ''.join(x).upper())
    >>> acc = ""
    >>> for i in 'popipo':
    ...    a = lf.send(i)
    ...    if a == "maybe":
    ...        acc += i
    ...    elif a:
    ...        acc = ""
    ...        print(a)
    ...    else:
    ...        print(acc + i)
    ...        acc = ""
    PO
    pi
    PO
    >>> lf = lookfor(maybe_it_is("pi") , lambda x: 1)
    >>> acc = ""
    >>> for i in 'popipop':
    ...    a = lf.send(i)
    ...    if a == "maybe":
    ...        acc += i
    ...    elif a:
    ...        acc = ""
    ...        print(a)
    ...    else:
    ...        print(acc + i)
    ...        acc = ""
    po
    1
    po
    >>> # the p in still processing
    >>> acc = ""
    >>> for i in 'iop':
    ...    a = lf.send(i)
    ...    if a == "maybe":
    ...        acc += i
    ...    elif a:
    ...        acc = ""
    ...        print(a)
    ...    else:
    ...        print(acc + i)
    ...        acc = ""
    1
    o
    >>> # the p in still processing
    >>> lf.throw(RESTAAART)
    False
    >>> # p has been forgot
    >>> acc = ""
    >>> for i in 'ipopi':
    ...    a = lf.send(i)
    ...    if a == "maybe":
    ...        acc += i
    ...    elif a:
    ...        acc = ""
    ...        print(a)
    ...    else:
    ...        print(acc + i)
    ...        acc = ""
    i
    po
    1

    """
    acc = []
    ans = False
    while True:
        try:
            c = (yield ans)
        except RESTAAART as err:
            acc = []
            ans = False
        else:
            if c is not None:
                acc.append(c)
            found = condition("".join([str(i) for i in acc]))
            if found == "maybe":
                ans = "maybe"
            elif found:
                ans = replace(acc)
                acc = []
            else:
                ans = False
                acc = []


@coroutine
def remember_lookfor(lookfor):
    """ Coroutine which remember sent value before the lookfor finds something

    :example:

    >>> lkf = lookfor(maybe_it_is("pipo"), lambda x: 'remp')
    >>> rmb_lkf = remember_lookfor(lkf)
    >>> for i in 'popipopi':
    ...    print(rmb_lkf.send(i))
    maybe
    False
    maybe
    maybe
    maybe
    ['p', 'o', 'remp']
    maybe
    maybe
    >>> for i in 'popi':
    ...    print(rmb_lkf.send(i))
    maybe
    ['remp']
    maybe
    maybe
    >>> rmb_lkf.throw(RESTAAART)
    ['p', 'i']
    >>> for i in 'popi':
    ...    print(rmb_lkf.send(i))
    maybe
    False
    maybe
    maybe

    """
    acc = []
    mb_acc = []
    ans = False
    while True:
        try:
            c = (yield ans)
        except RESTAAART as err:
            lookfor.throw(err)
            ans = acc + mb_acc
            acc = []
            mb_acc = []
        else:
            lkf_state = lookfor.send(c)
            if lkf_state == "maybe":
                mb_acc.append(c)
                ans = "maybe"
            elif lkf_state:
                ans = acc + [lkf_state]
                acc = []
                mb_acc = []
            else:
                acc += mb_acc
                mb_acc = []
                acc.append(c)
                ans = False


@coroutine
def concurent_broadcast(target, lookfors=[]):
    """ Coroutine which broadcasts multiple lookfor coroutines and reinitializes
    them when one found something

    Same as parallelized_lookfor but coroutine version

    :param target: target to send data to
    :param lookfors: list of lookfor coroutines

    :example:
    >>> lf1 = lookfor(maybe_it_is("abc"), lambda x: "".join(x).upper())
    >>> searcher = concurent_broadcast(list_sink, [lf1])
    >>> for i in "azabcab":
    ...    searcher.send(i)
    >>> a = searcher.throw(STOOOP)
    >>> print(a)
    ['a', 'z', 'ABC', 'a', 'b']

    >>> lf2 = lookfor(maybe_it_is("az"))
    >>> searcher = concurent_broadcast(list_sink, [lf1, lf2])
    >>> for i in "azabcabazb":
    ...    searcher.send(i)
    >>> a = searcher.throw(STOOOP)
    >>> print(a)
    ['az', 'ABC', 'a', 'b', 'az', 'b']
    
    >>> lfop = lookfor(something_in("+-*/()"), lambda x: f"op{x}")
    >>> searcher = concurent_broadcast(list_sink, [lfop])
    >>> for i in '12+3+234':
    ...    searcher.send(i)
    >>> a = searcher.throw(STOOOP)
    >>> print(a)
    ['1', '2', "op['+']", '3', "op['+']", '2', '3', '4']

    >>> # need to remake a searcher otherwise it remenbers old ans
    >>> searcher = concurent_broadcast(list_sink, [lfop])
    >>> for i in '12*(3+234)':
    ...    searcher.send(i)
    >>> a = searcher.throw(STOOOP)
    >>> print(a)
    ['1', '2', "op['*']", "op['(']", '3', "op['+']", '2', '3', '4', "op[')']"]

    >>> lfsqrt = lookfor(maybe_it_is("sqrt"), lambda x: f"op['sqrt']")
    >>> searcher = concurent_broadcast(list_sink, [lfop, lfsqrt])
    >>> for i in '3+2*sqrt(3)':
    ...    searcher.send(i)
    >>> a = searcher.throw(STOOOP)
    >>> print(a)
    ['3', "op['+']", '2', "op['*']", "op['sqrt']", "op['(']", '3', "op[')']"]
    """
    try:
        target_ = target()
    except TypeError:
        target_ = target

    lookfors_ = [remember_lookfor(lkf) for lkf in lookfors]

    try:
        while True:
            found = False
            tok = yield
            if tok is not None:
                for lf in lookfors_:
                    lf_ans = lf.send(tok)
                    if lf_ans and lf_ans != "maybe":
                        found = lf_ans
                        break

                if found:
                    for lf in lookfors_:
                        lf.throw(RESTAAART)
                    for i in found:
                        target_.send(i)
    except STOOOP as err:
        for lf in lookfors_:
            last = lf.throw(RESTAAART)
        for i in last:
            target_.send(i)
        yield target_.throw(err)


@coroutine
def missing_times(target):
    """ Coroutine which send a "*" when it's missing

    Cases where a "*" is missing:
     - 2x or yx or )x
     - 2( or y( or )(

    :param target: target to send data to

    :example:

    >>> miss_time = missing_times(list_sink)
    >>> for i in "2a":
    ...    miss_time.send(i)
    >>> a = miss_time.throw(STOOOP)
    >>> print(a)
    ['2', '*', 'a']
    >>> miss_time = missing_times(list_sink)
    >>> for i in "ab":
    ...    miss_time.send(i)
    >>> a = miss_time.throw(STOOOP)
    >>> print(a)
    ['a', '*', 'b']
    >>> miss_time = missing_times(list_sink)
    >>> for i in "a(":
    ...    miss_time.send(i)
    >>> a = miss_time.throw(STOOOP)
    >>> print(a)
    ['a', '*', '(']
    >>> miss_time = missing_times(list_sink)
    >>> for i in "2(":
    ...    miss_time.send(i)
    >>> a = miss_time.throw(STOOOP)
    >>> print(a)
    ['2', '*', '(']
    >>> miss_time = missing_times(list_sink)
    >>> for i in ")(":
    ...    miss_time.send(i)
    >>> a = miss_time.throw(STOOOP)
    >>> print(a)
    [')', '*', '(']

    >>> miss_time = missing_times(list_sink)
    >>> for i in "3+4":
    ...    miss_time.send(i)
    >>> a = miss_time.throw(STOOOP)
    >>> print(a)
    ['3', '+', '4']
    """
    try:
        target_ = target()
    except TypeError:
        target_ = target

    previous = None
    try:
        while True:
            tok = yield
            if not previous is None:
                previous = None

                if isinstance(tok, str):
                    if tok == "(":
                        target_.send("*")
                    elif not is_operator(tok) and tok != ")":
                        target_.send("*")

            if isinstance(tok, int) or (
                isinstance(tok, str) and not is_operator(tok) and not tok == "("
            ):
                previous = tok

            target_.send(tok)

    except STOOOP as err:
        yield target_.throw(err)


@coroutine
def lookforNumbers(target):
    """ Coroutine which parse numbers


    :exemple:
    >>> str2list = lookforNumbers(list_sink)
    >>> for i in "12+1234*67":
    ...    str2list.send(i)
    >>> a = str2list.throw(STOOOP)
    >>> print(a)
    [12, '+', 1234, '*', 67]

    >>> str2list = lookforNumbers(list_sink)
    >>> for i in "1.2+12.34*67":
    ...    str2list.send(i)
    >>> a = str2list.throw(STOOOP)
    >>> print(a)
    [Decimal('1.2'), '+', Decimal('12.34'), '*', 67]

    >>> str2list = lookforNumbers(list_sink)
    >>> for i in "12.3.4*67":
    ...    str2list.send(i)
    Traceback (most recent call last):
        ...
    mapytex.calculus.core.str2.ParsingError: Can't build decimal with '12.3'
    >>> str2list = lookforNumbers(list_sink)
    >>> for i in ".34*67":
    ...    a = str2list.send(i)
    Traceback (most recent call last):
        ...
    mapytex.calculus.core.str2.ParsingError: Can't build decimal with ''

    >>> str2list = lookforNumbers(list_sink)
    >>> for i in "12-34":
    ...    str2list.send(i)
    >>> a = str2list.throw(STOOOP)
    >>> print(a)
    [12, '+', -34]
    >>> str2list = lookforNumbers(list_sink)
    >>> for i in "-12+34":
    ...    str2list.send(i)
    >>> a = str2list.throw(STOOOP)
    >>> print(a)
    [-12, '+', 34]
    >>> str2list = lookforNumbers(list_sink)
    >>> for i in "3-1.2":
    ...    str2list.send(i)
    >>> a = str2list.throw(STOOOP)
    >>> print(a)
    [3, '+', Decimal('-1.2')]
    >>> str2list = lookforNumbers(list_sink)
    >>> for i in "3-(1.2)":
    ...    str2list.send(i)
    >>> a = str2list.throw(STOOOP)
    >>> print(a)
    [3, '+', '-', '(', Decimal('1.2'), ')']

    """
    try:
        target_ = target()
    except TypeError:
        target_ = target

    current = ""
    try:
        while True:
            tok = yield
            if tok is not None:
                try:
                    int(tok)
                except (ValueError, TypeError):
                    if tok == ".":
                        if current.replace("-", "", 1).isdigit():
                            current += tok
                        else:
                            raise ParsingError(f"Can't build decimal with '{current}'")
                    elif tok == "-":
                        if current == "":
                            current = tok
                        elif current == ("("):
                            target_.send(current)
                            current = "-"
                        elif is_operator(current):
                            if current == "-":
                                current = "+"
                            else:
                                target_.send(current)
                                current = "-"
                        else:
                            try:
                                target_.send(typifiy_numbers(current))
                            except (InvalidOperation, TypeError):
                                target_.send(current)
                            target_.send("+")
                            current = tok
                    else:
                        if current == "":
                            current = tok
                        elif is_operator(current) and is_operator(tok):
                            raise ParsingError(
                                f"Can't parse with 2 operators next to each other"
                            )
                        else:
                            try:
                                target_.send(typifiy_numbers(current))
                            except (InvalidOperation, TypeError):
                                target_.send(current)
                            current = tok
                else:
                    if current == "":
                        current = tok
                    elif current == "-":
                        current += tok
                    elif current.replace(".", "", 1).replace("-", "", 1).isdigit():
                        # make sure no double dotted number can't reach this place!
                        current += tok
                    else:
                        target_.send(current)
                        current = tok

    except STOOOP as err:
        if current:
            try:
                target_.send(typifiy_numbers(current))
            except (InvalidOperation, TypeError):
                target_.send(current)
        yield target_.throw(err)


def typifiy_numbers(number):
    """ Transform a str number into a integer or a decimal """
    try:
        return int(number)
    except ValueError:
        return Decimal(number)


@coroutine
def pparser(target):
    """ Parenthesis parser sink

    :example:

    >>> pp = pparser(list_sink)
    >>> for i in "buio":
    ...    pp.send(i)
    >>> a = pp.throw(STOOOP)
    >>> a
    ['b', 'u', 'i', 'o']
    >>> pp = pparser(list_sink)
    >>> for i in "agg(bcz)e(i(o))":
    ...    pp.send(i)
    >>> a = pp.throw(STOOOP)
    >>> a
    ['a', 'g', 'g', ['b', 'c', 'z'], 'e', ['i', ['o']]]

    """
    target_ = target()

    try:
        while True:
            caract = yield
            if caract == "(":
                a = yield from pparser(target)
                target_.send(a)
            elif caract == ")":
                a = target_.throw(STOOOP)
                return a
            else:
                target_.send(caract)
    except STOOOP as err:
        yield target_.throw(err)


@coroutine
def list_sink():
    """  Testing sink for coroutines

    :example:

    >>> sink = list_sink()
    >>> for i in '12+34 * 3':
    ...    sink.send(i)
    >>> a = sink.throw(STOOOP)
    >>> a
    ['1', '2', '+', '3', '4', ' ', '*', ' ', '3']

    """
    ans = list()
    try:
        while True:
            c = (yield)
            if c is not None:
                ans.append(c)
    except STOOOP:
        yield ans


def str2(sink, convert_to_mo=True):
    """ Return a pipeline which parse an expression with the sink as an endpoint

    :example:

    >>> str2nestedlist = str2(list_sink)
    >>> exp = "12+3*4"
    >>> t = str2nestedlist(exp)
    >>> print(t)
    [<MOnumber 12>, '+', <MOnumber 3>, '*', <MOnumber 4>]
    >>> str2nestedlist = str2(list_sink, False)
    >>> exp = "12+3*4"
    >>> t = str2nestedlist(exp)
    >>> print(t)
    [12, '+', 3, '*', 4]
    >>> exp = "12*3+4"
    >>> t = str2nestedlist(exp)
    >>> print(t)
    [12, '*', 3, '+', 4]
    >>> exp = "12*(3+4)"
    >>> t = str2nestedlist(exp)
    >>> print(t)
    [12, '*', [3, '+', 4]]
    >>> exp = "12(3+4)"
    >>> t = str2nestedlist(exp)
    >>> print(t)
    [12, '*', [3, '+', 4]]
    >>> exp = "2a(3+4)"
    >>> t = str2nestedlist(exp)
    >>> print(t)
    [2, '*', 'a', '*', [3, '+', 4]]
    >>> exp = "-12(3-4)"
    >>> t = str2nestedlist(exp)
    >>> print(t)
    [-12, '*', [3, '+', -4]]
    >>> exp = "-a(3-4)"
    >>> t = str2nestedlist(exp)
    >>> print(t)
    ['-', 'a', '*', [3, '+', -4]]
    >>> exp = "3-a"
    >>> t = str2nestedlist(exp)
    >>> print(t)
    [3, '+', '-', 'a']
    >>> exp = "1-(3+4)"
    >>> t = str2nestedlist(exp)
    >>> print(t)
    [1, '+', '-', [3, '+', 4]]
    >>> exp = "1+3x^2"
    >>> t = str2nestedlist(exp)
    >>> print(t)
    [1, '+', 3, '*', 'x', '^', 2]
    >>> exp = "1+(3+4)*2"
    >>> t = str2nestedlist(exp)
    >>> print(t)
    [1, '+', [3, '+', 4], '*', 2]
    >>> exp = "6x + (8 + 3) * x"
    >>> t = str2nestedlist(exp)
    >>> print(t)
    [6, '*', 'x', '+', [8, '+', 3], '*', 'x']

    >>> from .tree import MutableTree
    >>> str2tree = str2(MutableTree.sink)
    >>> exp = "12+3*4"
    >>> t = str2tree(exp)
    >>> print(t)
    +
     > 12
     > *
     | > 3
     | > 4
    >>> exp = "12*3+4"
    >>> t = str2tree(exp)
    >>> print(t)
    +
     > *
     | > 12
     | > 3
     > 4
    >>> exp = "12*(3+4)"
    >>> t = str2tree(exp)
    >>> print(t)
    *
     > 12
     > +
     | > 3
     | > 4
    >>> exp = "12(3+4)"
    >>> t = str2tree(exp)
    >>> print(t)
    *
     > 12
     > +
     | > 3
     | > 4
    >>> exp = "-12(3-4)"
    >>> t = str2tree(exp)
    >>> print(t)
    *
     > -12
     > +
     | > 3
     | > -4
    >>> exp = "-a(3-4)"
    >>> t = str2tree(exp)
    >>> print(t)
    -
     > None
     > *
     | > a
     | > +
     | | > 3
     | | > -4
    >>> exp = "3 - a"
    >>> t = str2tree(exp)
    >>> print(t)
    +
     > 3
     > -
     | > None
     | > a

    >>> exp = "a - 3"
    >>> t = str2tree(exp)
    >>> print(t)
    +
     > a
     > -3

    >>> exp = "1-(3+4)"
    >>> t = str2tree(exp)
    >>> print(t)
    +
     > 1
     > -
     | > None
     | > +
     | | > 3
     | | > 4
    >>> exp = "1+(3+4)*2"
    >>> t = str2tree(exp)
    >>> print(t)
    +
     > 1
     > *
     | > +
     | | > 3
     | | > 4
     | > 2

    >>> exp = "2*4-1"
    >>> t = str2tree(exp)
    >>> print(t)
    +
     > *
     | > 2
     | > 4
     > -1
    >>> exp = "3+4x"
    >>> t = str2tree(exp)
    >>> print(t)
    +
     > 3
     > *
     | > 4
     | > x
    >>> exp = "3x^2"
    >>> t = str2tree(exp)
    >>> print(t)
    *
     > 3
     > ^
     | > x
     | > 2
    >>> exp = "3+4x^5"
    >>> t = str2tree(exp)
    >>> print(t)
    +
     > 3
     > *
     | > 4
     | > ^
     | | > x
     | | > 5


    """
    lfop = lookfor(is_operator)
    operator_corout = partial(concurent_broadcast, lookfors=[lfop])

    def pipeline(expression):
        if convert_to_mo:
            str2_corout = lookforNumbers(
                operator_corout(missing_times(moify_cor(pparser(sink))))
            )
        else:
            str2_corout = lookforNumbers(operator_corout(missing_times(pparser(sink))))

        for i in expression.replace(" ", ""):
            str2_corout.send(i)
        a = str2_corout.throw(STOOOP)

        return a

    return pipeline


def rdstr2(sink):
    """ Return a pipeline which parse random expression and with sink as endpoint

    :example:
    >>> rdstr2list = rdstr2(list_sink)
    >>> rdstr2list("{a}+{a*b}-2")
    [<RdLeaf a>, '+', <RdLeaf a*b>, '+', <MOnumber - 2>]
    """
    lfop = lookfor(is_operator)
    operator_corout = partial(concurent_broadcast, lookfors=[lfop])

    def pipeline(expression):
        str2_corout = look_for_rdleaf(
            lookforNumbers(operator_corout(missing_times(moify_cor(pparser(sink)))))
        )

        for i in expression.replace(" ", ""):
            str2_corout.send(i)
        a = str2_corout.throw(STOOOP)

        return a

    return pipeline


def rdstr2(sink):
    """ Return a pipeline which parse random expression and with sink as endpoint

    :example:
    >>> rdstr2list = rdstr2(list_sink)
    >>> rdstr2list("{a}+{a*b}-2")
    [<RdLeaf a>, '+', <RdLeaf a*b>, '+', <MOnumber - 2>]
    """
    lfop = lookfor(is_operator)
    operator_corout = partial(concurent_broadcast, lookfors=[lfop])

    def pipeline(expression):
        str2_corout = look_for_rdleaf(
            lookforNumbers(operator_corout(missing_times(moify_cor(pparser(sink)))))
        )

        for i in expression.replace(" ", ""):
            str2_corout.send(i)
        a = str2_corout.throw(STOOOP)

        return a

    return pipeline


str2nestedlist = str2(list_sink)


# -----------------------------
# Reglages pour 'vim'
# vim:set autoindent expandtab tabstop=4 shiftwidth=4:
# cursor: 16 del
