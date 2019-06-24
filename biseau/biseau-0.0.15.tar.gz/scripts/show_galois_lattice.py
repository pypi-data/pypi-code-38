# encoding: utf8
"""Generalist mappings, allowing user to easily tune the galois lattice visualization.

"""
import textwrap


NAME = 'Show Galois Lattice'
TAGS = {'FCA', 'initial example'}
INPUTS = {'specint/2', 'specext/2', 'concept/1', 'under/2'}
OUTPUTS = {'annot/3', 'link/2', 'obj_property/3'}


def source_view(concept_uid, use_aoc_as_label, arrows:bool, prettify:bool, dpi:int):
    _ = lambda s, c=True: (textwrap.dedent(s.strip()) if c else '')
    return '% SHOW GALOIS LATTICE\n' + '\n\n'.join((
        _("""% Build the lattice.
link(X,Y):- under(X,Y)."""),
        _("""% I want AOC poset to be written.
annot(upper,X,A):- {s}int(X,A).
annot(lower,X,O):- {s}ext(X,O).
""".format(s='spec' if use_aoc_as_label else '')),
        _("""
% Show the concept uid as node label.
label(X,X):- concept(X).
""", concept_uid),
        _("""
% Get a good visualization.
obj_property(graph,dpi,{}).
""".format(dpi), int(str(dpi).strip('"')) > 0),
        _("""
% Delete arrows head.
obj_property(edge,arrowhead,none).
""", not arrows),
        _("""
% Some objects properties to prettify the visualization.
obj_property(edge,labeldistance,\"1.5\").
obj_property(edge,minlen,2).
""", prettify),
    ))


def run_on(context, *,
           concept_uid:bool=True,
           use_aoc_as_label:bool=True,
           arrows:bool=False,
           prettify:bool=True,
           dpi:int=300):
    """

    concept_uid -- show the concept unique id as node label
    use_aoc_as_label -- use the AOC poset to avoid too crowded lattice (do not works well with object/property oriented lattices)
    arrows -- show arrows of edges
    prettify -- set of various settings that improve the lattice feeling of the graph
    dpi -- increase it for sharper visualization

    """
    return source_view(concept_uid, use_aoc_as_label, arrows, prettify, dpi)
