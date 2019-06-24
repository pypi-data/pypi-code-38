# encoding: utf8
"""Biseau script.

Compute concepts and AOC poset as a single model.


"""

import os
import clyngor


NAME = 'Concepts'
TAGS = {'FCA', 'initial example'}
ERASE_CONTEXT = False

ASP_CONCEPTS = {
    'formal': 'data/asp/yield_concepts.lp',
    'object_oriented': 'data/asp/yield_object_oriented_concepts.lp',
    'property_oriented': 'data/asp/yield_property_oriented_concepts.lp',
}
ASP_AOCPOSET = 'data/asp/yield_aocposet.lp'
ASP_AOCPOSET_ONLY = 'data/asp/yield_aocposet_only.lp'
ASP_SUPINFIMUMS = 'data/asp/build_inum.lp'
ASP_NOSYMMETRY = 'data/asp/no-symmetry.lp'


def _output_predicates(type, only_aoc, supremum_and_infimum, remove_symmetry, careful_parsing):
    keys = ('concept', 'specext', 'specint')
    keys += () if only_aoc else ('ext', 'int')
    return frozenset(keys)


def outputs(type, only_aoc, supremum_and_infimum, remove_symmetry, careful_parsing):
    return frozenset(key + ('/1' if key == 'concept' else '/2') for key in
                     _output_predicates(type, only_aoc, supremum_and_infimum, remove_symmetry, careful_parsing))
INPUTS = {'rel/2'}
OUTPUTS = outputs(type='formal', only_aoc=False, supremum_and_infimum=True, remove_symmetry=False, careful_parsing=False)


def run_on(context:str, *,
           type:tuple(sorted(tuple(ASP_CONCEPTS.keys())))='formal',
           only_aoc:bool=False,
           supremum_and_infimum:bool=True,
           remove_symmetry:bool=False,
           careful_parsing:bool=True):
    """
    type -- type of concepts to yield
    only_aoc -- do not yield ext/2 and int/2
    supremum_and_infimum -- yield supremum and infimum, even if not in data
    remove_symmetry -- remove concepts with minimal item not in objects sets (has meaning only for symmetric contexts)
    careful_parsing -- use a slower but more robust parser for input atoms
    """
    codes = (
        [ASP_CONCEPTS.get(type, ASP_CONCEPTS['formal']), ASP_AOCPOSET]
        + ([ASP_AOCPOSET_ONLY] if only_aoc else [])
        + ([ASP_NOSYMMETRY] if remove_symmetry else [])
    )
    models = clyngor.solve(
        codes, inline=context, stats=False,
        constants={'allow_non_concept': int(supremum_and_infimum)},
    ).by_predicate
    if careful_parsing:
        models = models.careful_parsing
    keys = _output_predicates(type, only_aoc, supremum_and_infimum, remove_symmetry, careful_parsing)
    for idx, model in enumerate(models):
        yield 'concept({}).\n'.format(idx)
        for key in keys:
            thgs = model.get(key, ())
            for thg in thgs:
                thg, = thg  # first arg only: obj and att have an arity of 1
                yield '{}({},{}). '.format(key, idx, thg)
        yield '\n'
