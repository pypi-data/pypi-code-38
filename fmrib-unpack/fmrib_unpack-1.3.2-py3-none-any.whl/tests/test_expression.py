#!/usr/bin/env python
#
# test_expression.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import io

import pytest

import pyparsing as pp

import pandas as pd

import funpack.expression as expression

from . import gen_DataTableFromDataFrame


_test_data = """
index 10 20 30
1 1 2 3
2 4 5 6
3 7  9
4 10 11 12
5 13  15
""".strip().replace(' ', '\t')

_test_cols = {
    10 : '10',
    20 : '20',
    30 : '30',
}


_expr_tests = [
    (  'v10 == 1',  [1, 0, 0, 0, 0]),
    (  'v10 != 1',  [0, 1, 1, 1, 1]),
    (  'v10 >  7',  [0, 0, 0, 1, 1]),
    (  'v10 >= 7',  [0, 0, 1, 1, 1]),
    (  'v10 <  7',  [1, 1, 0, 0, 0]),
    (  'v10 <= 7',  [1, 1, 1, 0, 0]),
    ('~(v10 == 1)', [0, 1, 1, 1, 1]),
    ('~(v10 != 1)', [1, 0, 0, 0, 0]),

    ('v20 == na', [0, 0, 1, 0, 1]),
    ('v20 != na', [1, 1, 0, 1, 0]),

    (  'v10 >= 7 && v30 < 10',                [0, 0, 1, 0, 0]),
    ('~(v10 >= 7 && v30 < 10)',               [1, 1, 0, 1, 1]),
    ( 'v10 >= 4 &&  v30 < 10  || v20 != na',  [1, 1, 1, 1, 0]),
    ('(v10 >= 4 &&  v30 < 10) || v20 != na',  [1, 1, 1, 1, 0]),
    ( 'v10 >= 4 && (v30 < 10  || v20 != na)', [0, 1, 1, 1, 0]),


    # bad
    ('10 == 1',        'error'),
    ('10 ==',          'error'),
    ('v10',            'error'),
    ('v10 ==',         'error'),
    ('v10 1',          'error'),
    ('v10 == 1 &&',    'error'),
    ('v10 == 1 && 24', 'error'),
    ('abcde',          'error'),
]


def test_Expression():

    def vine(e):
        vs = []
        if 'v10' in e: vs.append(10)
        if 'v20' in e: vs.append(20)
        if 'v30' in e: vs.append(30)
        return vs

    data =  pd.read_csv(io.StringIO(_test_data), sep='\t')
    dt = gen_DataTableFromDataFrame(data)

    for expr, expected in _expr_tests:

        if expected == 'error':
            with pytest.raises(pp.ParseException):
                e = expression.Expression(expr)
            continue
        else:
            e = expression.Expression(expr)

        assert sorted(e.variables) == sorted(vine(expr))

        coldata = {vid : col  for vid, col in _test_cols.items()}
        result  = e.evaluate(dt, coldata)

        assert len(result) == len(expected)
        assert all([bool(r) == bool(e) for r, e in zip(result, expected)])


def test_calculaetExpressionEvaluationOrder():

    def makexprs(exprstrs):
        exprs = []
        for exprstr in exprstrs:
            expr = [expression.Expression(e) for e in exprstr.split(',')]
            if len(expr) == 1:
                expr = expr[0]
            exprs.append(expr)
        return exprs

    vids = [1, 2, 3, 4, 5, 7]
    exprs = [
        'v3 == 0',             # 1 depends on 3
        'v3  > 2',             # 2 depends on 3
        'v4 != na',            # 3 depends on 4
        'v5 != na, v6 == na',  # 4 depends on 5 and 6
        'v6 < 0',              # 5 depends on 6
        'v8 == 34'             # 7 depends on 8
    ]

    expected = [
        (0, [1, 2, 7]),
        (1, [3]),
        (2, [4]),
        (3, [5]),
    ]

    exprs = makexprs(exprs)
    result = expression.calculateExpressionEvaluationOrder(vids, exprs)
    assert result == expected


    vids = [1, 2]
    exprs = ['v2 == 20, v3 > 400',
             'v3 < 200']
    expected = [(0, [1]),
                (1, [2])]
    exprs = makexprs(exprs)
    result = expression.calculateExpressionEvaluationOrder(vids, exprs)
    assert result == expected

    vids = [1, 2]
    exprs = ['v3 > 400, v2 == 20',
             'v3 < 200']
    expected = [(0, [1]),
                (1, [2])]
    exprs = makexprs(exprs)
    result = expression.calculateExpressionEvaluationOrder(vids, exprs)
    assert result == expected


    # error on self-dependency
    with pytest.raises(ValueError):
        vids  = [1, 2]
        exprs = ['v1 == 1', 'v4 == 42']
        expression.calculateExpressionEvaluationOrder(vids, makexprs(exprs))

    # error on circular-dependency
    with pytest.raises(ValueError):
        vids  = [1, 2]
        exprs = ['v2 == 1', 'v1 == 2']
        expression.calculateExpressionEvaluationOrder(vids, makexprs(exprs))


    # length mismatch
    with pytest.raises(ValueError):
        vids  = [1, 2, 3]
        exprs = ['v2 == 1']
        expression.calculateExpressionEvaluationOrder(vids, makexprs(exprs))
