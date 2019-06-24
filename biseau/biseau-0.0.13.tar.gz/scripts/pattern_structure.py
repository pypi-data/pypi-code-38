# encoding: utf8
""" Compute pattern concepts applied to integer data and using intervals.

"""

import os
import clyngor


NAME = 'Integer Pattern Concepts'
TAGS = {'FCA'}
ERASE_CONTEXT = False
INPUTS = {'rel/3'}
OUTPUTS = {'ext/2', 'int/2'}

ASP_CODE_SEARCH_CONCEPTS = """
object(O):- rel(O,_,_).
condition(C):- rel(_,C,_).
val(X):- rel(_,_,X).

% Choose a subset of objects
{ ext(O): rel(O,_,_) }.

% The intervals for choosen objects.
interval(C,Min,Max):- condition(C) ; Min=#min{V,O: rel(O,C,V), ext(O)}
                                   ; Max=#max{V,O: rel(O,C,V), ext(O)}.

% Object is valid on Condition.
ok(O,C):- rel(O,C,V) ; interval(C,Min,Max) ; Min<=V ; V<=Max.
% Object is valid for all Conditions.
ok(O):- object(O) ; ok(O,C): condition(C).
% Avoid any model that do not include maximal number of objects.
:- not ext(O) ; ok(O).

% Object is non-valid if value is not in the interval.
% ko(O):- rel(O,C,V) ; interval(C,Min,Max) ; V<Min.
% ko(O):- rel(O,C,V) ; interval(C,Min,Max) ; V>Max.
% Avoid any model that do not include maximal number of objects.
% :- object(O) ; not ext(O) ; not ko(O).
"""


def run_on(context:str, *,
           careful_parsing:bool=True):
    """
    careful_parsing -- use a slower but more robust parser for input atoms
    """
    models = clyngor.solve(inline=context + ASP_CODE_SEARCH_CONCEPTS, stats=False).by_predicate
    if careful_parsing:
        models = models.careful_parsing
    for idx, model in enumerate(models):
        # print('MODEL', idx)
        yield 'concept({}).\n'.format(idx)
        extents = model.get('ext', ())
        for extent in extents:
            # print(extent, end='')
            yield 'ext({},{}). '.format(idx, extent[0])
        # print()
        intervals = model.get('interval', ())
        for interval in intervals:
            # print(interval, '', end='')
            if not interval:  # empty interval, no extent
                yield 'int({},interval({},0,100)). '.format(idx, idx)
            else:
                yield 'int({},interval({})). '.format(idx, ','.join(map(str, interval)))
        # print()
        yield '\n'
