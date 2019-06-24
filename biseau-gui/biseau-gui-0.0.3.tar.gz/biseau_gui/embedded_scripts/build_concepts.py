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
    'formal': r"""
        #const allow_non_concept=0.
        % Generate the concept.
        ext(X):- rel(X,_) ; rel(X,Y): int(Y).
        int(Y):- rel(_,Y) ; rel(X,Y): ext(X).
        % Avoid non-concept (no object or no attribute)
        :- not ext(_) ; allow_non_concept=0.
        :- not int(_) ; allow_non_concept=0.
        % clingo 5.2.0 or less
        % :- not ext(X):ext(X).
        % :- not int(Y):int(Y).
        #show.
        #show ext/1.
        #show int/1.
        """,
    'object_oriented': r"""
        #const allow_non_concept=0.
        % Generate the object-oriented concepts.
        ext(X):- rel(X,Y) ; int(Y).                      % object is linked to any attribute.
        not_ext(Nx):- rel(Nx,_) ; not ext(Nx).           % object is either in extent or not.
        int(Y):- rel(_,Y) ; not rel(Nx,Y): not_ext(Nx).  % attribute is only linked to objects in extent.
        % Avoid non-concept (no object or no attribute)
        :- not ext(_) ; allow_non_concept=0.
        :- not int(_) ; allow_non_concept=0.
        #show.
        #show ext/1.
        #show int/1.
        """,
    'property_oriented': r"""
        #const allow_non_concept=0.
        % Generate the object-oriented concepts.
        int(Y):- rel(X,Y) ; ext(X).                      % attribute is linked to any object.
        not_int(Ny):- rel(_,Ny) ; not int(Ny).           % attribute is either in intent or not.
        ext(X):- rel(X,_) ; not rel(X,Ny): not_int(Ny).  % object is only linked to attributes in intent.
        % Avoid non-concept (no object or no attribute)
        :- not ext(_) ; allow_non_concept=0.
        :- not int(_) ; allow_non_concept=0.
        #show.
        #show ext/1.
        #show int/1.
        """,
}
CONCEPT_TYPES = tuple(sorted(tuple(ASP_CONCEPTS.keys())))
ASP_AOCPOSET = """
% Is outsider any object or attribute that is linked to attribute or object not in concept.
outsider(X):- ext(X) ; rel(X,Z) ; not int(Z).
outsider(Y):- int(Y) ; rel(Z,Y) ; not ext(Z).
% We seek for specext and specint, the specific part of each concept.
specext(X):- ext(X) ; not outsider(X).
specint(Y):- int(Y) ; not outsider(Y).
#show specext/1.
#show specint/1.
"""
ASP_AOCPOSET_ONLY = ":- not specext(_) ; not specint(_)."
ASP_SUPINFIMUMS = "1 { sup ; inf } 1.  ext(X):- rel(X,_) ; sup.  int(Y):- rel(_,Y) ; inf."


def _output_predicates(type, only_aoc, supremum_and_infimum, careful_parsing):
    keys = ('concept', 'specext', 'specint')
    keys += () if only_aoc else ('ext', 'int')
    return frozenset(keys)


def outputs(type, only_aoc, supremum_and_infimum, careful_parsing):
    return frozenset(key + ('/1' if key == 'concept' else '/2') for key in
                     _output_predicates(type, only_aoc, supremum_and_infimum, careful_parsing))
INPUTS = {'rel/2'}
OUTPUTS = outputs(type='formal', only_aoc=False, supremum_and_infimum=True, careful_parsing=False)


def run_on(context:str, *,
           type:CONCEPT_TYPES='formal',
           only_aoc:bool=False,
           supremum_and_infimum:bool=True,
           careful_parsing:bool=True):
    """
    type -- type of concepts to yield
    only_aoc -- do not yield ext/2 and int/2
    supremum_and_infimum -- yield supremum and infimum, even if not in data
    careful_parsing -- use a slower but more robust parser for input atoms
    """
    codes = (
        [ASP_CONCEPTS.get(type, ASP_CONCEPTS['formal']), ASP_AOCPOSET]
        + ([ASP_AOCPOSET_ONLY] if only_aoc else []))
    models = clyngor.solve(
        inline='\n'.join(codes) + context, stats=False, use_clingo_module=False,
        constants={'allow_non_concept': int(supremum_and_infimum)},
    ).by_predicate
    if careful_parsing:
        models = models.careful_parsing
    keys = _output_predicates(type, only_aoc, supremum_and_infimum, careful_parsing)
    for idx, model in enumerate(models):
        yield 'concept({}).\n'.format(idx)
        for key in keys:
            thgs = model.get(key, ())
            for thg in thgs:
                thg, = thg  # first arg only: obj and att have an arity of 1
                yield '{}({},{}). '.format(key, idx, thg)
        yield '\n'
