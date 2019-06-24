# encoding: utf8
"""Routines manipulating the dot.

"""

import itertools
import pydot
from .asp_to_dot import VisualConfig


DEFAULT_DOT_FILE = 'out/out.dot'
DEFAULT_PROG_FILE = 'dot'


def _dot_from_properties(properties:dict or None, prefix:str=' ') -> str:
    """Return a dot '[]' expression where given properties are represented.

    If given properties are None, empty string will be output.

    """
    if properties:
        content = ' '.join(
            '{}="{}"'.format(field, value.replace('"', r'\"'))
            for field, value in properties.items()
        )
        return prefix + '[' + content + ']'
    else:
        return ''


def multiple_graphs_from_configs(visual_configs:[VisualConfig]) -> [[str]]:
    """Yield generators of lines of dot describing the given VisualConfig instances.

    Produce one graph per VisualConfig.
    See function counterpart, one_graph_from_configs.

    """
    for visual_config in visual_configs:
        yield itertools.chain(
            ['Digraph biseau_graph {\n'],
            _from_config(visual_config),
            ['}\n\n\n'],
        )


def one_graph_from_configs(visual_configs:[VisualConfig]) -> [str]:
    """Yield lines of dot describing the given VisualConfig instances.

    Produce only one graph,
    using the union of visual_configs to implement the view.

    """
    yield 'Digraph biseau_graph {\n'
    for visual_config in visual_configs:
        yield from _from_config(visual_config)
    yield '}'


def _from_config(visual_config:VisualConfig) -> [str]:
    """Yield lines of dot's graph describing the given VisualConfig instance.

    """
    arcs, nodes, properties, upper_annotations, lower_annotations, globals_props, ranks = visual_config
    for object, props in globals_props.items():
        yield '\t{}{};\n'.format(object, _dot_from_properties(props))
    if 'node' not in globals_props:
        yield '\tnode [shape=ellipse style=filled width=.25]\n'
    if 'edge' not in globals_props:
        yield '\tedge [arrowhead=none labeldistance=1.5 minlen=2]\n'
    treated_nodes = set()  # contains nodes already treated
    for node in nodes:
        if node not in treated_nodes:
            treated_nodes.add(node)
            yield from _dot_from_node(node, visual_config)
    for source, target in arcs:
        for node in source, target:
            if node not in treated_nodes:
                treated_nodes.add(node)
                yield from _dot_from_node(node, visual_config)
        yield '\t{}->{}{}\n'.format(source, target, _dot_from_properties(properties.get((source, target))))
    # build ranks
    for ranktype, nodes in ranks.items():
        yield '\t{{rank={}; {}}}\n'.format(ranktype, ';'.join(nodes))


def _dot_from_node(node, visual_config) -> [str]:
    "Yield dot content describing given node in given visual_config"
    arcs, nodes, properties, upper_annotations, lower_annotations, globals_props, ranks = visual_config
    node_dot_props = _dot_from_properties(properties.get(node))
    yield '\t{n}{d}\n'.format(n=node, d=node_dot_props)
    if lower_annotations.get(node):
        yield '\t{n} -> {n} {d}\n'.format(
            n=node, d=_dot_from_properties(lower_annotations[node]))
    if upper_annotations.get(node):
        yield '\t{n} -> {n} {d}\n'.format(
            n=node, d=_dot_from_properties(upper_annotations[node]))


def dot_to_png(dot_lines:iter, outfile:str, dotfile:str=DEFAULT_DOT_FILE,
               prog:str=DEFAULT_PROG_FILE):
    """Write in outfile a png render of the graph described in given dot lines"""
    dot_lines = ''.join(dot_lines)
    if dotfile:
        with open(dotfile, 'w') as fd:
            fd.write(dot_lines)
    graphs = iter(pydot.graph_from_dot_data(dot_lines))
    for graph in graphs:
        with open(outfile, 'wb') as fd:
            fd.write(graph.create(prog=prog or DEFAULT_PROG_FILE, format='png'))
        break

    # TODO: handle multiple graphs (see #10)
    for graph in graphs:
        print('WARNING: an additionnal graph as been found in the dot file.'
              'It will be ignored.')
        print(graph)
