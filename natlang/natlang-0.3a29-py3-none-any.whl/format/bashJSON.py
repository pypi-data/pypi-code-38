from __future__ import print_function

import json
import os
import sys
import bashlex
import copy
import re
import string
from operator import itemgetter
from natlang.format.astTree import AstNode as BaseNode


class Code:
    placeHolders = ['WORD', 'FLAG', 'NUM', 'SBTK']
    keywords = ('find', 'xargs', 'grep', 'rm', 'echo', 'ls', 'sort',
                'chmod', 'wc', 'cat', 'cut', 'head', 'mv', 'chown', 'cp',
                'mkdir', 'tr', 'tail', 'dirname', 'rsync', 'tar', 'uniq',
                'ln', 'split', 'read', 'basename', 'which', 'readlink',
                'tee', 'date', 'pwd', 'ssh', 'diff', 'cd')

    def __init__(self, tokens, valueTypes, canoCode=None, createSketch=True):
        self.value = tokens
        self.valueTypes = valueTypes
        assert len(self.value) == len(self.valueTypes)
        self.canoCode = canoCode
        self.astTree = None
        self.sketch = None
        if self.canoCode is not None:
            self.astTree = bash2astTree(canoCode)
        if createSketch is True:
            self.sketch = self.getSketch()

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "<BashCode: " + str(self.value) + ">"

    def __getitem__(self, key):
        return self.value[key]

    def getSketch(self):
        sketchTokens = []
        for tk, ty in zip(self.value, self.valueTypes):
            if ty in type(self).placeHolders:
                sketchTokens.append(ty)
            else:
                sketchTokens.append(tk)
        sketch = Code(sketchTokens,
                      self.valueTypes,
                      canoCode=None,
                      createSketch=False)
        if self.astTree is not None:
            sketch.astTree = self.astTree.getSketch()
        return sketch

    def export(self):
        return " ".join(self.value)


def load(file, linesToLoad=sys.maxsize):
    with open(os.path.expanduser(file)) as f:
        content = [line.strip() for line in f][:linesToLoad]
    result = []
    for i, line in enumerate(content):
        entry = json.loads(line)
        entry = Code(entry['token'], entry['type'], entry['cano_code'])
        if entry.astTree is None:
            print("WARNING: skipping invalid entry #" + str(i),
                  file=sys.stderr)
            continue
        result.append(entry)
    return result


class _TmpNode:
    def __init__(self, tag, value):
        self.tag = tag
        self.value = value
        self.children = []

    def __repr__(self):
        return 'TmpNode({}, {})'.format(repr(self.tag), repr(self.value))

    def draw(self, name='tmp'):
        from graphviz import Graph
        import os
        import errno

        try:
            os.makedirs('figures')
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

        fname = 'figures/{}'.format(name + '.gv')
        g = Graph(format='png', filename=fname)

        fringe = [self]
        while fringe:
            node = fringe.pop()
            g.node(str(id(node)), repr(node))
            for child in node.children:
                fringe.append(child)
                g.node(str(id(child)), repr(node))
                g.edge(str(id(node)), str(id(child)))

        return g.render()


class BashAst(BaseNode):
    placeHolders = ['WORD', 'FLAG', 'NUM', 'SBTK']
    keywords = ('find', 'xargs', 'grep', 'rm', 'echo', 'ls', 'sort',
                'chmod', 'wc', 'cat', 'cut', 'head', 'mv', 'chown', 'cp',
                'mkdir', 'tr', 'tail', 'dirname', 'rsync', 'tar', 'uniq',
                'ln', 'split', 'read', 'basename', 'which', 'readlink',
                'tee', 'date', 'pwd', 'ssh', 'diff', 'cd')

    def find_literal_nodes(self):
        if self.value[0] == 'subtoken':
            return [self]
        else:
            nodes = []
            node = self.child
            while node is not None:
                nodes.extend(node.find_literal_nodes())
                node = node.sibling
            return nodes

    def children(self):
        n = self.child
        while n is not None:
            yield n
            n = n.sibling

    def export(self):
        ty = self.value[0]
        if ty == 'subtoken':
            return self.value[1]
        elif ty == 'word':
            return ''.join(x.export() for x in self.children())
        elif ty == 'pipeline':
            return ' | '.join(x.export() for x in self.children())
        elif ty == 'CST':
            command = ' '.join((x.export() for x in self.children()))
            return '$({})'.format(command)
        elif ty == 'PST_left':
            command = ' '.join((x.export() for x in self.children()))
            return '<({})'.format(command)
        elif ty == 'PST_right':
            command = ' '.join((x.export() for x in self.children()))
            return '>({})'.format(command)
        else:
            return ' '.join(x.export() for x in self.children())

    def getSketch(self):
        """
        return the root of a new tree with sketches the sketch tree cannot be
        converted back to python unless all sketch holes are filled
        """
        root = copy.deepcopy(self)
        leaves = root.find_literal_nodes()
        for leaf in leaves:
            if leaf.value[1].isnumeric():
                leaf.value = leaf.value[0], 'NUM'
            elif leaf.value[1] in type(self).keywords \
                    or leaf.value[1] in string.punctuation \
                    or leaf.value[1] == ' ':
                # preserve keywords, puncs, and spaces
                continue
            else:
                # mask other subtokens
                leaf.value = leaf.value[0], 'SBTK'

        return root

    def draw(self, name='ast'):
        from graphviz import Graph
        import os
        import errno

        def repr_n(node):
            return 'Node{}'.format(repr(node.value))

        try:
            os.makedirs('figures')
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

        fname = 'figures/{}'.format(name + '.gv')
        g = Graph(format='png', filename=fname)
        g.attr(rankdir='BT')

        fringe = [self]
        while fringe:
            node = fringe.pop()
            g.node(str(id(node)), repr_n(node))
            if node.child is not None:
                child = node.child
                fringe.append(child)
                g.node(str(id(child)), repr_n(node))

            if node.sibling is not None:
                sibling = node.sibling
                fringe.append(sibling)
                g.node(str(id(sibling)), repr_n(node))

            if node.parent is not None:
                g.edge(str(id(node)), str(id(node.parent)))

        return g.render()


def proc_line(line):
    parts = bashlex.parse(line)
    assert len(parts) == 1
    ast = parts[0]
    return ast


def determine_pst_type(pst_str):
    if pst_str.startswith('<(') and pst_str.endswith(')'):
        pst_type = 'PST_left'
    elif pst_str.startswith('>(') and pst_str.endswith(')'):
        pst_type = 'PST_right'
    else:
        pst_type = 'unknown'
    return pst_type


def remap_pos(node, cst_node, line):
    """
    remap the pos of a command substitution node `cst_node` to its parent node
    `node`
    """
    cst_str = line[slice(*cst_node.pos)]
    remapped_start = node.word.find(cst_str)
    remapped_end = remapped_start + len(cst_str)
    return remapped_start, remapped_end


def split_segments(node, pos_list):
    """
    :param node: Node of type word
    :param pos_list: [((start:int, end:int), type_name:str, node)] pos of
                     special parts
    :return: [(type_name: str, {text_segment: str | node})]
    """
    pos_list.sort(key=itemgetter(0))
    segments = []
    last_end = 0
    for t in pos_list:
        pos, type_name, part = t
        text_segment = node.word[last_end:pos[0]]
        last_end = pos[1]
        if text_segment:
            segments.append(('text', text_segment))
        # node_text = node.word[slice(*pos)]
        segments.append((type_name, part))
    text_segment = node.word[last_end:]
    if text_segment:
        segments.append(('text', text_segment))
    return segments


sbtk_engine = re.compile(r'''
[a-zA-Z]+ | # words
[0-9]+ |    # numbers
.   # everything else
''', re.VERBOSE)


def split_subtoken(text):
    """
    :param text: str
    :return: [str]
    """
    return sbtk_engine.findall(text)


CST_KIND = 'commandsubstitution'
PST_KIND = 'processsubstitution'


def process_node(node, line):
    if node.kind == 'word':
        pos_list = []
        for part in node.parts:
            if part.kind in ('parameter', 'tilde'):
                pass
            else:
                remapped_pos = remap_pos(node, part, line)
                if part.kind == CST_KIND:
                    # cst_type = determine_cst_type(part_str)
                    type_name = 'CST'
                elif part.kind == PST_KIND:
                    part_str = node.word[slice(*remapped_pos)]
                    pst_type = determine_pst_type(part_str)
                    type_name = pst_type
                else:
                    raise RuntimeError('unknown kind {}'.format(part.kinds))
                assert type_name != 'unknown'
                pos_list.append((remapped_pos, type_name, part))

        segments = split_segments(node, pos_list)

        children = []
        for segment in segments:
            ty, data = segment
            if ty == 'text':
                subtokens = split_subtoken(data)
                for subtoken in subtokens:
                    children.append(_TmpNode('subtoken', subtoken))
            else:
                child = process_node(data, line)
                child.tag = ty
                children.append(child)
        ret_node = _TmpNode('word', None)
        ret_node.children = [child for child in children if child is not None]
        return ret_node
    elif node.kind == CST_KIND:
        return process_node(node.command, line)
    elif node.kind == PST_KIND:
        return process_node(node.command, line)
    elif node.kind == 'pipe':
        return None
    else:
        ret_node = _TmpNode(node.kind, None)
        if hasattr(node, 'parts'):
            children = [process_node(part, line) for part in node.parts]
            ret_node.children =\
                [child for child in children if child is not None]
        return ret_node


def _restructure_rec(node, orig_children):
    """
    `node` is the already transformed node (type=tree.Node)
    `orig_children` is a list of the children corresponds to `node`
        (type=[TmpNode])
    """
    # edge case
    tag = node.value[0]
    if node.value is None and not orig_children:
        # transformed grammar with no children
        dummy = BashAst()
        dummy.value = ('DUMMY', None)
        node.child = dummy
        dummy.parent = node

    # transform each child node
    child_nodes = []
    for orig_child in orig_children:
        child_node = BashAst()
        if orig_child.value is None:
            # internal node
            child_node.value = (orig_child.tag,)
        else:
            # leaf node
            child_node.value = (orig_child.tag, orig_child.value)
        child_nodes.append(child_node)

    # link child nodes
    for i, child_node in enumerate(child_nodes):
        child_node.parent = node
        if i == 0:
            node.child = child_node
        if i + 1 < len(child_nodes):
            # not last node
            child_node.sibling = child_nodes[i + 1]

    # recurse
    for child_node, orig_child in zip(child_nodes, orig_children):
        _restructure_rec(child_node, orig_child.children)


def _restructure(tmp_node, node_cls=BashAst):
    """transform the structure of TmpNode into Custom node class
    node_cls should be a subclass of AstNode"""
    node = node_cls()
    if tmp_node.value is None:
        node.value = (tmp_node.tag,)
    else:
        node.value = (tmp_node.tag, tmp_node.value)

    _restructure_rec(node, tmp_node.children)

    # append topmost root node
    root = node_cls()
    root.value = ('ROOT',)
    root.child = node
    node.parent = root
    return root


def bash2astTree(line):
    node = proc_line(line)
    tmp_node = process_node(node, line)
    ast_node = _restructure(tmp_node, BashAst)
    ast_node.refresh()
    return ast_node


if __name__ == '__main__':
    train = load('/Users/ruoyi/Projects/PycharmProjects/data_fixer/' +
                 'bash_exported/train.jsonl')
    dev = load('/Users/ruoyi/Projects/PycharmProjects/data_fixer/' +
               'bash_exported/dev.jsonl')
    test = load('/Users/ruoyi/Projects/PycharmProjects/data_fixer/' +
                'bash_exported/test.jsonl')
