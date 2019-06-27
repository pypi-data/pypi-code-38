#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 lafrite <lafrite@Poivre>
#
# Distributed under terms of the MIT license.

"""
Tools to extract random leafs, random variables, generate random values and
fill new trees

Flow
----

Tree with RdLeaf
|
| Extract rdLeaf
|
List of leafs to generate
|
| extract_rv
|
List random variables to generate
|
| Generate
|
Dictionnary of generated random variables
|
| Compute leafs
|
Dictionnary of computed leafs
|
| Replace
|
Tree with RdLeaf replaced by generated values

:example:

>>> from ..tree import Tree
>>> rd_t = Tree("/", RdLeaf("a"), RdLeaf("a*k"))
>>> print(rd_t)
/
 > {a}
 > {a*k}
>>> leafs = extract_rdleaf(rd_t)
>>> leafs
['a', 'a*k']
>>> rd_varia = extract_rv(leafs)
>>> rd_varia # doctest: +SKIP
{'a', 'k'}
>>> generated = random_generator(rd_varia, conditions=['a%2+1'])
>>> generated # doctest: +SKIP
{'a': 7, 'k': 4}
>>> computed = compute_leafs(leafs, generated)
>>> computed # doctest: +SKIP
{'a': 7, 'a*k': 28}
>>> replaced = replace_rdleaf(rd_t, computed)
>>> print(replaced) # doctest: +SKIP
/
 > 7
 > 28

"""

from random import choice
from functools import reduce
from .leaf import RdLeaf


def extract_rdleaf(tree):
    """ Extract rdLeaf in a Tree

    :example:
    >>> from ..tree import Tree
    >>> rd_t = Tree("+", RdLeaf("a"), RdLeaf("a*k"))
    >>> extract_rdleaf(rd_t)
    ['a', 'a*k']
    >>> rd_t = Tree("+", RdLeaf("a"), 2)
    >>> extract_rdleaf(rd_t)
    ['a']
    """
    rd_leafs = []
    for leaf in tree.get_leafs():
        try:
            leaf.rdleaf
        except AttributeError:
            pass
        else:
            rd_leafs.append(leaf.name)
    return rd_leafs


def extract_rv(leafs):
    """ Extract the set of random values from the leaf list

    :param leafs: list of leafs
    :return: set of random values

    :example:
    >>> leafs = ["a", "a*k"]
    >>> extract_rv(leafs) == {'a', 'k'}
    True
    """
    rd_values = set()
    for leaf in leafs:
        for c in leaf:
            if c.isalpha():
                rd_values.add(c)
    return rd_values


def compute_leafs(leafs, generated_values):
    """ Compute leafs from generated random values

    :param generated_values: Dictionnary of name:generated value
    :param leafs: list of leafs
    :return: Dictionnary of evaluated leafs from generated values

    :example:
    >>> leafs = ["a", "a*k"]
    >>> generated_values = {"a":2, "k":3}
    >>> compute_leafs(leafs, generated_values)
    {'a': 2, 'a*k': 6}
    """
    return {leaf: eval(leaf, generated_values) for leaf in leafs}


def replace_rdleaf(tree, computed_leafs):
    """ Replace RdLeaf by the corresponding computed value

    >>> from ..tree import Tree
    >>> rd_t = Tree("+", RdLeaf("a"), RdLeaf("a*k"))
    >>> computed_leafs = {'a': 2, 'a*k': 6}
    >>> print(replace_rdleaf(rd_t, computed_leafs))
    +
     > 2
     > 6
    """

    def replace(leaf):
        try:
            return leaf.replace(computed_leafs)
        except AttributeError:
            return leaf

    return tree.map_on_leaf(replace)


def random_generator(
    rd_variables, conditions=[], rejected=[0], min_max=(-10, 10), variables_scope={}
):
    """ Generate random variables

    :param rd_variables: list of random variables to generate
    :param conditions: condition over variables
    :param rejected: Rejected values for the generator (default [0])
    :param min_max: (min, max) limits in between variables will be generated
    :param variables_scope: rejected and min_max define for individual variables
    :return: dictionnary of generated variables

    :example:
    >>> gene = random_generator(["a", "b"], 
    ...                  ["a > 0"],
    ...                  [0], (-10, 10),
    ...                  {"a": {"rejected": [0, 1]},
    ...                   "b": {"min_max": (-5, 0)}})
    >>> gene["a"] > 0
    True
    >>> gene["a"] != 0
    True
    >>> gene["b"] < 0
    True
    >>> gene = random_generator(["a", "b"], 
    ...                  ["a % b == 0"],
    ...                  [0, 1], (-10, 10))
    >>> gene["a"] not in [0, 1]
    True
    >>> gene["b"] in list(range(-10, 11))
    True
    >>> gene["a"] % gene["b"]
    0
    """
    complete_scope = build_variable_scope(
        rd_variables, rejected, min_max, variables_scope
    )
    choices_list = {
        v: list(
            set(
                range(
                    complete_scope[v]["min_max"][0], complete_scope[v]["min_max"][1] + 1
                )
            ).difference(complete_scope[v]["rejected"])
        )
        for v in rd_variables
    }

    # quantity_choices = reduce(lambda x,y : x*y,
    #                           [len(choices_list[v]) for v in choices_list])
    # TODO: améliorer la méthode de rejet avec un cache |dim. mai 12 17:04:11 CEST 2019

    generate_variable = {v: choice(choices_list[v]) for v in rd_variables}

    while not all([eval(c, __builtins__, generate_variable) for c in conditions]):
        generate_variable = {v: choice(choices_list[v]) for v in rd_variables}

    return generate_variable


def build_variable_scope(rd_variables, rejected, min_max, variables_scope):
    """ Build variables scope from incomplete one

    :param rd_variables: list of random variables to generate
    :param rejected: Rejected values for the generator 
    :param min_max: (min, max) limits in between variables will be generated
    :param variables_scope: rejected and min_max define for individual variables
    :return: complete variable scope

    :example:
    >>> completed = build_variable_scope(["a", "b", "c", "d"], [0], (-10, 10),
    ...                      {"a": {"rejected": [0, 1]},
    ...                       "b": {"min_max": (-5, 0)},
    ...                       "c": {"rejected": [2], "min_max": (0, 5)}})
    >>> complete = {'a': {'rejected': [0, 1], 'min_max': (-10, 10)}, 
    ...             'b': {'rejected': [0], 'min_max': (-5, 0)},
    ...             'c': {'rejected': [2], 'min_max': (0, 5)},
    ...             'd': {'rejected': [0], 'min_max': (-10, 10)}}
    >>> completed == complete
    True
    """
    complete_scope = variables_scope
    for v in rd_variables:
        try:
            complete_scope[v]
        except KeyError:
            complete_scope[v] = {"rejected": rejected, "min_max": min_max}
        else:
            try:
                complete_scope[v]["rejected"]
            except KeyError:
                complete_scope[v]["rejected"] = rejected
            try:
                complete_scope[v]["min_max"]
            except KeyError:
                complete_scope[v]["min_max"] = min_max
    return complete_scope
