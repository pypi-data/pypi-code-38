# encoding: utf8
"""Build frequent concepts, allowing one to generate the iceberg lattice.


"""
import clyngor
import tkinter as tk
from functools import partial

NAME = 'Frequent concepts'
TAGS = {'FCA', 'Iceberg Lattice'}
INPUTS = {'rel/2'}
OUTPUTS = {'ext/1', 'int/1'}

ASP_SRC_CONCEPTS = 'data/asp/yield_frequent_concepts.lp'
RATIO_FIELD = partial(tk.Scale, from_=0, to=1, resolution=0.001, orient=tk.HORIZONTAL)


def run_on(models:str, *,
           minsupp_obj:RATIO_FIELD=0.85,
           minsupp_att:RATIO_FIELD=0.):
    """

    minsupp_obj -- minimal support for objects, defining frequent concepts.
    minsupp_att -- minimal support for attributes, defining frequent concepts.

    """
    # print('EXTRACT CONTEXT DATA…')
    model = next(models.by_predicate)
    # print(model)
    assert model.get('allow_non_concept') is None
    if model.get('rel') is None:
        return ''

    # compute minimal number of objects/attributes in the concepts
    min_nb_obj, min_nb_att = 0, 0
    if minsupp_obj > 0:
        nb_obj = len(frozenset(obj for obj, _ in model.get('rel')))
        min_nb_obj = int(float(minsupp_obj) * int(nb_obj))
    if minsupp_att > 0:
        nb_att = len(frozenset(att for _, att in model.get('rel')))
        min_nb_att = int(float(minsupp_att) * int(nb_att))

    # print('COMPUTING FREQUENT CONCEPTS…')
    inlined = clyngor.utils.answer_set_to_str(model, atom_sep='.') + '.'
    models = clyngor.solve(ASP_SRC_CONCEPTS, inline=inlined, constants={
        'minsupp_obj': min_nb_obj,
        'minsupp_att': min_nb_att,
    }).by_predicate

    for idx, model in enumerate(models):
        yield 'concept({}).\n'.format(idx)
        for key in ('ext', 'int', 'specext', 'specint'):
            thgs = model.get(key, ())
            for thg in thgs:
                thg, = thg  # first arg only: obj and att have an arity of 1
                yield '{}({},{}). '.format(key, idx, thg)
        yield '\n'
