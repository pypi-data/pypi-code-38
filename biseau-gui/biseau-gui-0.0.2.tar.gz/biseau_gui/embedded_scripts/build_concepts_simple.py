# encoding: utf8
"""Biseau script.

Compute concepts as a single model.

"""

import os
import clyngor


NAME = 'Formal Concepts (simple, no options)'
TAGS = {'FCA'}
INPUTS = {'rel/2'}
OUTPUTS = {'ext/2', 'int/2'}
ASP_CONCEPTS_SRC = 'data/asp/yield_concepts_simple.lp'


def run_on(context:str):
    """Get current ASP encoded context, yield parts of the new context.
    """
    models = clyngor.solve(ASP_CONCEPTS_SRC, inline=context, stats=False).by_predicate
    for idx, model in enumerate(models):
        yield 'concept({}).\n'.format(idx)
        for key in ('ext', 'int'):
            for arg in model.get(key, ()):
                yield '{}({},{}). '.format(key, idx, arg[0])
        yield '\n'
