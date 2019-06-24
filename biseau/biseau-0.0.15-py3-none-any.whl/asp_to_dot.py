# encoding: utf8
"""The core part of visualization, compiling ASP into dot.

"""

import textwrap as textwrap_module
from collections import namedtuple, defaultdict
from biseau import utils


RANK_TYPES = {'same', 'min', 'source', 'max', 'sink'}
DOTABLE_PREDICATES = {'link', 'node', 'color', 'shape', 'label', 'annot', 'dot_property', 'obj_property', 'textwrap', 'rank'}
VisualConfig = namedtuple('VisualConfig', 'arcs, nodes, properties, upper_annotations, lower_annotations, global_properties, ranks')
"""
    arcs -- iterable of 2-uplet (source's uid, target's uid)
    nodes -- set of nodes that may or may not be used by arcs
    properties -- map uid -> (field -> value) and (uid, uid) -> (field -> value)
    upper_annotations -- map uid -> {field -> value} specialized for annotations
    lower_annotations -- map uid -> {field -> value} specialized for annotations
    global_properties -- map object -> (field -> value), with object in (graph, edge, node)
    ranks -- map rank-type -> iterable of sets of node

Properties are mapping directly dot properties to nodes (single uid)
or edges (two uid). This allow user to build very precisely the output dot.

"""


def visual_config_from_asp(asp_models:iter, annotation_sep:str=' ') -> [VisualConfig]:
    """Yield VisualConfig instances initialized according to rules
    found in each given asp models.

    asp_models -- iterable of clyngor.Answers instances
    annotation_sep -- separator between each annotation content on same node

    """
    for model in asp_models.by_predicate:
        base_atoms = defaultdict(set)  # predicate -> {args}
        viz_atoms = defaultdict(lambda: defaultdict(set))  # level -> {predicate: {args}}
        for viz in model.get('viz', ()):
            if len(viz) == 1:
                pred, args = viz[0]
                base_atoms[pred].add(args)
            elif len(viz) == 2:  # the first param is here to define the level
                pred, args = viz[1]
                viz_atoms[int(viz[0])][pred].add(args)
        # put the predicate not in viz() in the base level
        for predicate in DOTABLE_PREDICATES:
            base_atoms[predicate] |= frozenset(model.get(predicate, ()))
        if viz_atoms:
            for level, atoms in viz_atoms.items():
                yield visual_config_from_atoms(atoms, base_atoms, annotation_sep)
        else:  # no viz atoms
            yield visual_config_from_atoms({}, base_atoms, annotation_sep)


def visual_config_from_atoms(atoms:dict, base_atoms:dict,
                             annotation_sep:str) -> VisualConfig:
    arcs, nodes = [], set()
    upper_annotations = defaultdict(lambda: defaultdict(set))
    lower_annotations = defaultdict(lambda: defaultdict(set))
    properties = defaultdict(lambda: defaultdict(set))  # node -> (property -> {value})
    global_properties = defaultdict(lambda: defaultdict(set))  # dot object -> (property -> value)
    ranks = defaultdict(set)  # rank-type -> {node}
    max_label_width = {}  # object: maximal text width
    labeldistance_multiplier = None

    def get_atoms_of_predicate(predicate:str):
        assert predicate in DOTABLE_PREDICATES, predicate
        yield from base_atoms.get(predicate, ())
        yield from atoms.get(predicate, ())

    def get_uid_from_atom(atom:str or tuple):
        if isinstance(atom, str):
            return atom
        elif isinstance(atom, tuple):
            if len(atom) == 2:  # a regular atom
                if len(atom[1]) == 0:
                    return atom[0]
                else:  # atom with args
                    return '{}({})'.format(atom[0], ','.join(map(get_uid_from_atom, atom[1])))
        raise ValueError(f"Malformed node uid of type '{type(atom)}' found: {atom}")

    for link in get_atoms_of_predicate('link'):
        if len(link) == 2:
            arcs.append(tuple(map(get_uid_from_atom, link)))
    for node in get_atoms_of_predicate('node'):
        if len(node) == 1:
            nodes.add(tuple(map(get_uid_from_atom, node))[0])
    for args in get_atoms_of_predicate('textwrap'):
        if len(args) == 1:  # global value
            max_label_width[None] = int(args[0])
        elif len(args) == 2:
            node, value = args
            max_label_width[node] = int(value)
        elif len(args) == 3:
            src, trg, value = args
            max_label_width[src, trg] = int(value)
    for annotation in get_atoms_of_predicate('annot'):
        if len(annotation) == 1:  # determine label distance multiplier
            labeldistance_multiplier = float(annotation[0].strip('"'))
        if len(annotation) == 3:
            type_, node, content = annotation
            node = get_uid_from_atom(node)
            if type_ == 'upper':
                upper_annotations[node]['taillabel'].add(content.strip('"'))
            elif type_ == 'lower':
                lower_annotations[node]['headlabel'].add(content.strip('"'))
            elif type_ == 'label':
                properties[node]['label'].add(content.strip('"'))
            else:
                print('Unknow annotation type: {}'.format(type_))
        elif len(annotation) == 4:  # other field
            type_, node, field, content = annotation
            node = get_uid_from_atom(node)
            if type_ == 'upper':
                upper_annotations[node][field].add(content.strip('"'))
            elif type_ == 'lower':
                lower_annotations[node][field].add(content.strip('"'))
    for property in get_atoms_of_predicate('dot_property'):
        if len(property) == 3:  # it's for node
            node, field, value = property
            node = get_uid_from_atom(node)
            properties[node][field.strip('"')].add(value.strip('"'))
        elif len(property) == 4:  # it's for edges
            src, trg, field, value = property
            src, trg = map(get_uid_from_atom, (src, trg))
            properties[src, trg][field.strip('"')].add(value.strip('"'))
    for ranking in get_atoms_of_predicate('rank'):
        if len(ranking) == 2:  # rank, node
            ranktype, node = ranking
            if ranktype not in RANK_TYPES:
                print("WARNING: atom rank({},{}) describe a rank with unknow "
                      "type {}. Expected types: {}."
                      "".format(*ranking, ranktype, ', '.join(RANK_TYPES)))
            ranks[ranktype].add(node)
    for colored in get_atoms_of_predicate('color'):
        if len(colored) == 2:  # node
            node, color = colored
            node = get_uid_from_atom(node)
            properties[node]['fillcolor'].add(color)
        elif len(colored) == 3:  # edge
            src, trg, color = colored
            src, trg = map(get_uid_from_atom, (src, trg))
            properties[src, trg]['color'].add(color)  # fillcolor do not exists for edges
    for shaped in get_atoms_of_predicate('shape'):
        if len(shaped) == 2:  # node
            node, shape = shaped
            node = get_uid_from_atom(node)
            properties[node]['shape'].add(shape)
    for labeled in get_atoms_of_predicate('label'):
        if len(labeled) == 2:  # node
            node, label = labeled
            node = get_uid_from_atom(node)
            properties[node]['label'].add(label)
        elif len(labeled) == 3:  # edge
            src, trg, label = labeled
            src, trg = map(get_uid_from_atom, (src, trg))
            properties[src, trg]['label'].add(label)
    for property in get_atoms_of_predicate('obj_property'):
        if len(property) == 3:
            obj, field, value = map(lambda s:str.strip(s, '"'), property)
            if obj not in {'graph', 'edge', 'node'}:
                print('WARNING: object property {} is unexpected, and may '
                      'lead to error in generation.'.format(obj))
            if field in global_properties:
                print('WARNING: object property {} set multiple times with {} replacing {}.'
                      ''.format(field, value, graph_properties[field]))
            global_properties[obj.strip('"')][field] = value

    # posttreat the data for later use
    arcs = tuple(arcs)
    def treat_texts(texts:iter, node, max_label_width=max_label_width) -> str:
        ret = annotation_sep.join(map(get_uid_from_atom, texts)).strip('"')
        text_width = max_label_width.get(node, max_label_width.get(None))
        if text_width:
            ret = textwrap_module.fill(ret, width=int(text_width))
        return ret

    for node in upper_annotations:
        props = upper_annotations[node]
        props.setdefault('color', 'transparent')
        props.setdefault('labelangle', '90')
        for key in tuple(props):
            if not isinstance(props[key], str):
                text = treat_texts(props[key], (node, node))
                props[key] = text
                if labeldistance_multiplier is not None:
                    text_size = len(text.replace('\\n', '\n').split('\n'))
                    # print('TEXT:', repr(text), text_size)
                    props['labeldistance'] = str(1 + labeldistance_multiplier * text_size)

    for node in lower_annotations:
        props = lower_annotations[node]
        props.setdefault('color', 'transparent')
        props.setdefault('labelangle', '270')
        for key in tuple(props):
            if not isinstance(props[key], str):
                text = treat_texts(props[key], (node, node))
                props[key] = text
                if labeldistance_multiplier is not None:
                    text_size = len(text.replace('\\n', '\n').split('\n'))
                    # print('TEXT:', repr(text), text_size)
                    props['labeldistance'] = str(1 + labeldistance_multiplier * text_size)

    for key in properties:
        if 'color' in properties[key]:
            try:
                properties[key]['color'] = utils.color_from_colors(properties[key]['color'])
            except ValueError:  # invalid color
                properties[key]['color'] = next(iter(properties[key]['color']))
        if 'fillcolor' in properties[key]:
            try:
                properties[key]['fillcolor'] = utils.color_from_colors(properties[key]['fillcolor'])
            except ValueError:  # invalid color
                properties[key]['fillcolor'] = next(iter(properties[key]['fillcolor']))
        for field in properties[key]:
            if field not in {'color', 'fillcolor'}:
                properties[key][field] = treat_texts(properties[key][field], key)

    return VisualConfig(
        arcs, frozenset(nodes), dict(properties), dict(upper_annotations), dict(lower_annotations),
        dict(global_properties), ranks
    )
