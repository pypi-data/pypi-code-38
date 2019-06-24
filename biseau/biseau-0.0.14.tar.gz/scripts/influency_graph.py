# encoding: utf8
"""

Populate existing lattice representation with the data of influency graph.


"""

import os
import clyngor
from collections import defaultdict


NAME = 'Influency graph'
TAGS = {'FCA'}
TAGS = {'FCA', 'initial example'}  # todel
ERASE_CONTEXT = False

INPUTS = {'smaller/2', 'link/2', 'specext/2', 'specint/2'}
OUTPUTS = {'link/2', 'dot_property/3'}

ASP_FILTER_LATTICE_SYMMETRY = """
keep(N) :- concept(N,_) ; Om=#min{O:ext(N,O)} ; Am=#min{A:int(N,A)} ; Am>=Om.
#show.
#show link(A,B): link(A,B), keep(A), keep(B).
#show concept(C): keep(C).
"""  # TODO
ASP_COLORIZE = """
bigger(C1,C2) :- smaller(C2,C1).
color(C,green) :- not bigger(D,C): specint(D,_) ; bigger(_,C).
color(C,red) :- not smaller(D,C): specext(D,_) ; smaller(_,C).
"""
ASP_SHOW_INFLUENCES = """
link(S,T)                          :- influence(S,T,_).
dot_property(S,T,constraint,false) :- influence(S,T,_).
dot_property(S,T,arrowhead,normal) :- influence(S,T,_).
dot_property(S,T,color,red)        :- influence(S,T,_).
dot_property(S,T,fontcolor,red)    :- influence(S,T,_).
dot_property(S,T,label,L)          :- influence(S,T,L).
"""
ASP_AMBIGOUS_CANDIDATE = """
concept(C,obj,N) :- concept(C) ; ext(C,N).
concept(C,att,N) :- concept(C) ; int(C,N).

ambigous_candidate(C1,C2,N,M):-
    C1!=C2
    ; concept(C1,obj,N) ; concept(C1,att,M)
    ; concept(C2,S,N) ; concept(C2,S,M)
    ; not included(C1,C2)
    .
included(C1,C2) :- C1!=C2 ; concept(C2,T,X): concept(C1,U,X) ; concept(C1,U,_) ; concept(C2,T,_).

#show.
#show ambigous_candidate/4.
#show concept/3.
"""


def run_on(context:str, *,
           colorize:bool=True,
           show_influences:bool=True,
           keep_influences_symmetry:bool=False):
    """
    colorize -- show AOC poset min/max concepts in red and green
    show_influences -- render the influence edges in red
    keep_influences_symmetry -- keep only a non-redoundant subset of influencies
    """
    # get influences between concepts
    influences = defaultdict(lambda: (set(), set()))
    concepts = defaultdict(lambda: (set(), set()))
    # print(context)
    models = clyngor.solve(
        inline=context+ASP_AMBIGOUS_CANDIDATE,
        stats=False, constants={'allow_non_concept': 1},
    ).careful_parsing.by_predicate
    # print('CMD:', models.command)
    for model in models:
        for src, trg, ea, eb in model.get('ambigous_candidate', ()):
            influences[src, trg][0].add(ea)
            influences[src, trg][1].add(eb)
        for concept, objset, elem in model.get('concept', ()):
            concepts[concept][0 if objset == 'obj' else 1].add(elem)
    # print('INFLUENCES:', dict(influences))
    # print('  CONCEPTS:', dict(concepts))
    # yield influencies relations
    def ismotif(concept, concepts=concepts) -> bool:
        "True if given concept is a motif"
        obj, att = concepts[concept]
        return min(obj) <= min(att)
    prettyfy = lambda s: '{' + ','.join(sorted(tuple(s))) + '}'
    for (src, trg), (objs, atts) in influences.items():
        if not keep_influences_symmetry and not (ismotif(src) and ismotif(trg)):
            continue
        yield f'influence({src},{trg},"{prettyfy(objs) + "×" + prettyfy(atts)}").'
    if show_influences:
        yield ASP_SHOW_INFLUENCES
    if colorize:
        yield ASP_COLORIZE
