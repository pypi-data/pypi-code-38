# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import operator as op, functools as ft
from collections import defaultdict, OrderedDict
import io, yaml


class PrettyYAMLDumper(yaml.dumper.SafeDumper):

    def __init__(self, *args, **kws):
        self.pyaml_force_embed = kws.pop('force_embed', False)
        return super(PrettyYAMLDumper, self).__init__(*args, **kws)

    def represent_odict(dumper, data):
        value = list()
        node = yaml.nodes.MappingNode(
            'tag:yaml.org,2002:map', value, flow_style=None )
        if dumper.alias_key is not None:
            dumper.represented_objects[dumper.alias_key] = node
        for item_key, item_value in data.viewitems():
            node_key = dumper.represent_data(item_key)
            node_value = dumper.represent_data(item_value)
            value.append((node_key, node_value))
        node.flow_style = False
        return node

    def serialize_node(self, node, parent, index):
        if self.pyaml_force_embed: self.serialized_nodes.clear()
        return super(PrettyYAMLDumper, self).serialize_node(node, parent, index)

    @staticmethod
    def pyaml_transliterate(string):
        from unidecode import unidecode
        string_new = ''
        for ch in unidecode(string):
            if '0' <= ch <= '9' or 'A' <= ch <= 'Z' or 'a' <= ch <= 'z' or ch in '-_': string_new += ch
            else: string_new += '_'
        return string_new.lower()

    def anchor_node(self, node, hint=list()):
        if node in self.anchors:
            if self.anchors[node] is None and not self.pyaml_force_embed:
                self.anchors[node] = self.generate_anchor(node)\
                    if not hint else '{}'.format(
                        self.pyaml_transliterate(
                            '_-_'.join(map(op.attrgetter('value'), hint)) ) )
        else:
            self.anchors[node] = None
            if isinstance(node, yaml.nodes.SequenceNode):
                for item in node.value:
                    self.anchor_node(item)
            elif isinstance(node, yaml.nodes.MappingNode):
                for key, value in node.value:
                    self.anchor_node(key)
                    self.anchor_node(value, hint=hint+[key])

PrettyYAMLDumper.add_representer(defaultdict, PrettyYAMLDumper.represent_dict)
PrettyYAMLDumper.add_representer(set, PrettyYAMLDumper.represent_list)
PrettyYAMLDumper.add_representer(OrderedDict, PrettyYAMLDumper.represent_odict)


class UnsafePrettyYAMLDumper(PrettyYAMLDumper):

    def choose_scalar_style(self):
        if self.event.style != 'plain':
            return super(UnsafePrettyYAMLDumper, self).choose_scalar_style()
        else:
            return "'"

    def expect_block_sequence(self):
        self.increase_indent(flow=False, indentless=False)
        self.state = self.expect_first_block_sequence_item

    def expect_block_sequence_item(self, first=False):
        if not first and isinstance(self.event, yaml.events.SequenceEndEvent):
            self.indent = self.indents.pop()
            self.state = self.states.pop()
        else:
            self.write_indent()
            self.write_indicator('-', True, indention=True)
            self.states.append(self.expect_block_sequence_item)
            self.expect_node(sequence=True)

    def represent_stringish(dumper, data):
        # Will crash on bytestrings with weird chars in them,
        #  because we can't tell if it's supposed to be e.g. utf-8 readable string
        #  or an arbitrary binary buffer, and former one *must* be pretty-printed
        # PyYAML's Representer.represent_str does the guesswork and !!binary or !!python/str
        # Explicit crash on any bytes object might be more sane, but also annoying
        # Use something like base64 to encode such buffer values instead
        # Having such binary stuff pretty much everywhere on unix (e.g. paths) kinda sucks
        data = unicode(data) # read the comment above

        # Try to use '|' style for multiline data,
        #  quoting it with 'literal' if lines are too long anyway,
        #  not sure if Emitter.analyze_scalar can also provide useful info here
        if '\n' in data:
            style = '|'
            data = '\n'.join([line.rstrip() for line in data.splitlines()])
        else:
            style = 'plain'

        return yaml.representer.ScalarNode('tag:yaml.org,2002:str', data, style=style)

for str_type in [bytes, unicode]:
    UnsafePrettyYAMLDumper.add_representer(
        str_type, UnsafePrettyYAMLDumper.represent_stringish )

UnsafePrettyYAMLDumper.add_representer(
    type(None), lambda s,o: s.represent_scalar('tag:yaml.org,2002:null', '') )


def dump_add_vspacing(buff, vspacing):
    'Post-processing to add some nice-ish spacing for deeper map/list levels.'
    if isinstance(vspacing, int):
        vspacing = ['\n']*(vspacing+1)
    buff.seek(0)
    result = list()
    for line in buff:
        level = 0
        line = line.decode('utf-8')
        result.append(line)
        if ':' in line:
            while line.startswith('  '):
                level, line = level + 1, line[2:]
            if len(vspacing) > level and len(result) != 1:
                vspace = vspacing[level]
                result.insert( -1, vspace
                    if not isinstance(vspace, int) else '\n'*vspace )
    buff.seek(0), buff.truncate()
    buff.write(''.join(result).encode('utf-8'))


def dump(data, dst=unicode, safe=False, force_embed=False, vspacing=None):
    buff = io.BytesIO()
    Dumper = PrettyYAMLDumper if safe else UnsafePrettyYAMLDumper
    Dumper = ft.partial(Dumper, force_embed=force_embed)
    yaml.dump_all([data], buff, Dumper=Dumper, default_flow_style=False, encoding='utf-8', allow_unicode=True, indent=4)

    if vspacing is not None:
        dump_add_vspacing(buff, vspacing)

    if dst is bytes:
        return buff.getvalue()
    elif dst is unicode:
        return buff.getvalue().decode('utf-8')
    else:
        dst.write(buff.getvalue())

class Loader(yaml.Loader):
    """ 支持OrderedDict """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(
            'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(
            'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            msg = 'expected a mapping node, but found %s' % node.id
            raise yaml.constructor.ConstructError(None,
                                                  None,
                                                  msg,
                                                  node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as err:
                raise yaml.constructor.ConstructError(
                    'while constructing a mapping', node.start_mark,
                    'found unacceptable key (%s)' % err, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

def load(data):
    return yaml.load(data, Loader=Loader)
