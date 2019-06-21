# -*- coding: utf-8 -*-
# Python version: 3
#
# Bash format Code loader
# Simon Fraser University
# Ruoyi Wang
#
#
from bashlex.ast import node as BashNode
import sys
import os
import copy
import pickle
import json

from natlang.format.astTree import AstNode as BaseNode

# migrated
import itertools

pattern_argument_types = {
    'Regex',
    'File',
    'Directory',
    'Path',
    'Format',
    'Option',
    'ReservedWord',
    'Program',
    'Bandwidth'
}

quantity_argument_types = {
    'Number',
    '+Number',
    '-Number',
    'Quantity',
    '+Quantity',
    '-Quantity',
    'Size',
    '+Size',
    '-Size',
    'Timespan',
    '+Timespan',
    '-Timespan',
    'DateTime',
    '+DateTime',
    '-DateTime',
    'Permission',
    '+Permission',
    '-Permission'
}

argument_types = pattern_argument_types | quantity_argument_types | \
                 {'Type', 'Unknown'}


def get_normalize_tokens(ast, p=None, sketch=False):
    if ast is None:
        return []
    if ast == []:
        return []
    if ast.kind.isupper():
        if sketch:
            return ['<SKETCH_{}>'.format(p.kind.upper())]
        # leaf node
        if ast.kind == 'VAR':
            # var node
            # append $
            return ['$'] + [ast.value[1:]]
        else:
            # return the lexeme as-is
            return [ast.value]
    elif ast.kind == 'pipeline':
        if ast.prev is None:
            prev_tokens = []
        else:
            prev_tokens = get_normalize_tokens(ast.prev, ast, sketch)
            prev_tokens.append('|')
        return prev_tokens + get_normalize_tokens(ast.last_cmd, ast, sketch)
    elif ast.kind == 'cmd':
        assign_list_tokens = get_sstl(ast.assign_list, get_normalize_tokens, sketch)
        prog_tokens = get_normalize_tokens(ast.prog, ast, sketch)
        args_tokens = get_sstl(ast.args, get_normalize_tokens, sketch)
        redir_tokens = get_sstl(ast.redir, get_normalize_tokens, sketch)
        if assign_list_tokens:
            assign_list_tokens.append(' ')
        if args_tokens:
            args_tokens.insert(0, ' ')
        if redir_tokens:
            redir_tokens.insert(0, ' ')
        tokens = assign_list_tokens + prog_tokens + args_tokens + redir_tokens
        return tokens
    elif ast.kind == 'assign':
        lhs = [ast.lhs]
        op = [ast.op]
        rhs = get_normalize_tokens(ast.rhs, ast, sketch)
        return lhs + op + rhs
    elif ast.kind == 'assign_rhs':
        return list(itertools.chain.from_iterable(
            get_normalize_tokens(x, ast, sketch) for x in ast.parts))
    elif ast.kind == 'redir':
        lhs = []
        if ast.lhs:
            lhs.append(ast.lhs)
        rhs = get_normalize_tokens(ast.rhs, ast, sketch)
        return lhs + [ast.type] + rhs
    elif ast.kind == 'prog':
        return list(itertools.chain.from_iterable(
            get_normalize_tokens(x, ast, sketch) for x in ast.parts))
    elif ast.kind in ['arg', 'binarylogicop', 'unarylogicop', 'operator']:
        return list(itertools.chain.from_iterable(
            get_normalize_tokens(x, ast, sketch) for x in ast.parts))
    elif ast.kind in argument_types:
        return list(itertools.chain.from_iterable(
            get_normalize_tokens(x, ast, sketch) for x in ast.parts))
    elif ast.kind == 'flag':
        tokens = [ast.name]
        if ast.value is not None:
            tokens.append(' ')
            tokens.extend(itertools.chain.from_iterable(
                get_normalize_tokens(x, ast, sketch) for x in ast.value))
        return tokens
    elif ast.kind == 'cst':
        return ['$('] + get_normalize_tokens(ast.pipeline, ast, sketch) + [')']
    elif ast.kind == 'lpst':
        return ['<('] + get_normalize_tokens(ast.pipeline, ast, sketch) + [')']
    elif ast.kind == 'rpst':
        return ['>('] + get_normalize_tokens(ast.pipeline, ast, sketch) + [')']
    elif ast.kind == 'arith_subst':
        return ['$(('] + get_normalize_tokens(ast.pipeline, ast, sketch) + ['))']
    elif ast.kind == 'param_exp':
        return ['${'] + list(itertools.chain.from_iterable(
            get_normalize_tokens(x, ast, sketch) for x in ast.parts)) + ['}']
    elif ast.kind == 'dquote_str':
        return ['"'] + list(itertools.chain.from_iterable(
            get_normalize_tokens(x, ast, sketch) for x in ast.parts)) + ['"']
    elif ast.kind == 'squote_str':
        return ["'"] + list(itertools.chain.from_iterable(
            get_normalize_tokens(x, ast, sketch) for x in ast.parts)) + ["'"]
    elif ast.kind == 'paren_grp':
        return ['('] + get_normalize_tokens(ast.pipeline, ast, sketch) + [')']
    elif ast.kind == 'curly_grp':
        return ['{', ' '] + get_normalize_tokens(ast.pipeline, ast, sketch) + ['}']


def get_sstl(l, f, sketch):
    """space-separated token list"""
    token_list = []
    for node in l:
        if token_list:
            token_list.append(' ')
        token = f(node, sketch=sketch)
        token_list.extend(token)
    return token_list


# migration END

class AstNode(BaseNode):
    def find_literal_nodes(self):
        if self.value[0] == 'LITERAL':
            return [self]
        else:
            nodes = []
            node = self.child
            while node is not None:
                nodes.extend(node.find_literal_nodes())
                node = node.sibling
            return nodes

    def export(self):
        pass


class _TmpNode:
    def __init__(self, tag, value):
        self.tag = tag
        self.value = value
        self.children = []

    def __repr__(self):
        return 'TmpNode({}, {})'.format(repr(self.tag), repr(self.value))


def tree2ast(root):
    if root is None:
        return None, None
    elif root.value[0] == 'LITERAL':
        return 'LITERAL', root.value[1]
    elif root.value[0] == 'DUMMY':
        return None, None
    elif root.value[0] == 'ROOT':
        return tree2ast(root.child)
    elif root.value[0].endswith('_vec'):
        children = []
        n = root.child
        while n is not None:
            kind, ast_node = tree2ast(n)
            n = n.sibling
            if kind == 'LITERAL':
                kind = 'value'
            if kind is None:
                continue
            children.append(ast_node)
        return root.value[0][:-4], children
    elif root.value[0].endswith('_optional'):
        return root.value[0][:-len('_optional')], tree2ast(root.child)[1]
    else:
        children = {}
        n = root.child
        while n is not None:
            kind, ast_node = tree2ast(n)
            n = n.sibling
            if kind == 'LITERAL':
                kind = 'value'
            if kind is None:
                continue
            children[kind] = ast_node
            # children.append(ast_node)
        kind = root.value[0]
        if kind == 'pipeline':
            children['last_cmd'] = children['cmd']
            del children['cmd']
        root_ast_node = BashNode(kind=root.value[0], **children)
        return root.value[0], root_ast_node


def iter_fields(bash_ast):
    return [(k, v) for k, v in bash_ast.__dict__.items() if k != 'kind']


def _translate(bash_ast):
    """translate bash ast into custom class TmpNode"""

    if isinstance(bash_ast, _TmpNode):
        for i, child in enumerate(bash_ast.children):
            bash_ast.children[i] = _translate(child)
        return bash_ast
    elif not isinstance(bash_ast, BashNode):
        # literal
        return _TmpNode('LITERAL', bash_ast)
    else:
        node = _TmpNode(bash_ast.kind, None)
        for field, value in iter_fields(bash_ast):
            if isinstance(value, list):
                # star-production
                # this child is a list
                # transform into a standalone node
                vec_child = _TmpNode(field + '_vec', None)
                vec_child.children = list(value)
                node.children.append(vec_child)
            elif value is None:
                # optional-production
                vec_child = _TmpNode(field + '_optional', None)
                node.children.append(vec_child)
            else:
                node.children.append(value)

        for i, child in enumerate(node.children):
            node.children[i] = _translate(child)

        return node


def _restructure_rec(node, orig_children):
    """
    `node` is the already transformed node (type=tree.Node)
    `orig_children` is a list of the children corresponds to `node`
        (type=[TmpNode])
    """
    # edge case
    tag = node.value[0]
    if (tag.endswith('_vec') or tag.endswith('_optional')) and \
            not orig_children:
        # transformed grammar with no children
        dummy = AstNode()
        dummy.value = ('DUMMY', None)
        node.child = dummy
        dummy.parent = node

    # transform each child node
    child_nodes = []
    for orig_child in orig_children:
        child_node = AstNode()
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


def _restructure(tmp_node, node_cls=AstNode):
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


def bashAst2astTree(bash_ast, node_cls=AstNode):
    if bash_ast is None:
        return None
    root = _translate(bash_ast)
    res_root = _restructure(root, node_cls)
    res_root.refresh()
    return res_root


class BashAst(AstNode):
    def __init__(self, parent=None):
        AstNode.__init__(self, parent=parent)

    def getSketch(self):
        root = copy.deepcopy(self)
        leaves = root.find_literal_nodes()
        for leaf in leaves:
            leaf.value = leaf.value[0], '<SKETCH_{}>'.format(leaf.parent.value[0].upper())

        return root


class Code:
    def __init__(self, tokens, sketch, ast, createSketch=True):
        self.value = tokens
        self.astTree = ast
        if sketch is not None:
            self.sketch = Code(sketch, None, None, False)

        self.astTree = bashAst2astTree(ast, BashAst)
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
        sketch = self.sketch
        if self.astTree is not None:
            sketch.astTree = self.astTree.getSketch()
        return sketch

    def export(self):
        ast = tree2ast(self.astTree)[1]
        tokens = get_normalize_tokens(ast)
        return ''.join(tokens)


def load(fileName, linesToLoad=sys.maxsize, verbose=True, option=None,
         no_process=False):
    with open(fileName, 'rb') as f:
        trees = pickle.load(f)

    loaded = []
    with open(option, 'r') as f:
        for i, line in enumerate(f):
            entry = json.loads(line)
            loaded.append(
                Code(entry['token'], entry['sketch'], trees[i]))

    return loaded


def draw_tmp_tree(root, name='tmp'):
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

    fringe = [root]
    while fringe:
        node = fringe.pop()
        g.node(str(id(node)), repr(node))
        for child in node.children:
            fringe.append(child)
            g.node(str(id(child)), repr(node))
            g.edge(str(id(node)), str(id(child)))

    return g.render()


def repr_n(node):
    return 'Node{}'.format(repr(node.value))


def draw_res_tree(root, name='res'):
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
    g.attr(rankdir='BT')

    fringe = [root]
    while fringe:
        node = fringe.pop()
        g.node(str(id(node)), repr_n(node))
        if node.child is not None:
            child = node.child
            fringe.append(child)
            g.node(str(id(child)), repr_n(node))
            # g.edge(str(id(node)), str(id(child)), color='red')

        if node.sibling is not None:
            sibling = node.sibling
            fringe.append(sibling)
            # g.node(str(id(sibling)), repr_n(node))
            # g.edge(str(id(node)), str(id(sibling)), color='blue')

        if node.parent is not None:
            g.edge(str(id(node)), str(id(node.parent)), color='green')

    return g.render()


if __name__ == '__main__':
    loaded = load('/Users/ruoyi/Projects/PycharmProjects/data_fixer/bash/train.cm.filtered.ast.pkl',
                  option='/Users/ruoyi/Projects/PycharmProjects/data_fixer/bash/train.cm.filtered.seq2seq')
