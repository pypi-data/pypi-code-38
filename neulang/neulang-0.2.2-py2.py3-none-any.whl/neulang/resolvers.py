"""

"""


import traceback as tb

import sys
import re
from ast import *

from .base import BaseResolver
from .astir import ASTIR
from .adapt_resolver import AdaptResolver


class Resolver(BaseResolver):

    def __init__(self, parent=None):
        self._parent = parent
        super().__init__()
        del self._resolvers["Resolver"]
        PyExprResolver()
        ASTIR()
        #RegexResolver()
        AdaptResolver()
        return

    def resolve(self, tree):
        """Top level delegating resolver"""
        if not tree:
            raise ValueError("Unable to find any parseable content. Missing *'s?")
        nodes = []
        self._top_level = tree[0].get("level")

        for node in tree:

            try:
                a_node = self._resolve(node)
                if a_node:
                    nodes.append(a_node) if not isinstance(
                        a_node, list
                    ) else nodes.extend(a_node)

            except Exception as e:
                tb.print_exc()
                return None
        assert not any([isinstance(n, list) for n in nodes])
        module = Module(nodes)
        return module

    def get_pif(self, key):
        resolvers = list(self._resolvers.values())
        pif = None

        for r in resolvers:
            pif = getattr(r, "_pifs", {}).get(key)
            if pif:
                break
        if not pif:
            raise AttributeError(f'Unable to resolve PIF "{key}"')
        return pif

    def add_handler(self, data):
        return None


class RegexResolver(BaseResolver):
    def __init__(self):
        super().__init__()
        self._rx_test = re.compile(r"(^add_regex_handler(\s.+)?)")
        self._rx_hashes = {}
        self._pifs = {}

    def resolve(self, o_node):
        if not self.is_regex(o_node):
            return False
        a_node = None
        head = o_node.get("head")
        h_match = re.match(r"add_(?P<type>\w+)_handler(\s.+)?", head)

        if h_match:
            # TODO: handler type detection in 'self.add_handler'
            h_type = h_match.groupdict().get("type")
            a_node = self.add_handler(o_node)
            if a_node is not None:
                raise ValueError(f"None expected but got {type(a_node)}")

        else:
            a_node = self.nl_call(o_node)
        return a_node

    def add_handler(self, data):
        ignores = ["match", "body"]
        data = self._node_to_list(data, ignore_first=ignores)
        if not len(data) == 2:
            raise ValueError(f"Expected 2")
        match = data[0].get("match")[0]
        if not isinstance(match, Str):
            raise ValueError(f"Expected string")
        match = match.s
        body = data[1].get("body")
        body = [Expr(a_n) if not type(a_n) in self._stmt_types else a_n for a_n in body]
        rx_h = f"rx_{abs(hash(match))}"
        self._rx_hashes[match] = rx_h
        pif = body  # pif as a snippet
        self._pifs[rx_h] = pif
        return None

    def nl_call(self, data):
        head = data.get("head")
        body = data.get("body", [])
        rx_h = context = p_body = None

        if body:
            # preprocess body (allows for late handler definitions)
            p_body = self._node_to_list(data)

        for rx in self._rx_hashes:
            # find an appropriate handler
            # TODO: make abstract for any handler type
            match = re.match(rf"{rx}", head)
            if not match:
                continue
            rx_h = self._rx_hashes.get(rx)
            context = match.groupdict()
            context = parse(f"context={context}").body[0]  # get dict node
            break
        if not rx_h:
            return False  # late detection of handlability
        pif = self._pifs[rx_h]
        assert isinstance(pif, list), f"Expected a list but got (type(pif))"
        node = [context] + pif
        node.extend(p_body or [])
        return node

    def is_regex(self, node):
        # TODO: better way to detect handlable nodes
        if not isinstance(node, dict):
            return False
        head = node.get("head", "")
        return (
            True
        )  # if self._rx_test.match(head) or not self.cast_air(head, 'test') else False


class PyExprResolver(BaseResolver):
    # TODO: maybe move to own module

    def __init__(self):
        super().__init__()
        return

    def resolve(self, data):
        """Convert an expression to a node"""
        if not self.is_expr(data):
            return False
        # TODO: ensure inline? method to incl body node in call?
        head = data.get("head")
        if compilable(head):
            node = parse(head).body[0].value

        else:
            # assumes this is the last to be resolved
            node = Str(head)
        return node

    def add_handler(self, data):
        # actually shouldn't be necessary in this class
        return None

    def is_expr(self, node):
        """Return True if a node is a Python expression."""
        if not isinstance(node, dict):
            return False
        text = node.get("head")

        try:
            # if re.match(r'[\w.]+\(.*\)', text): return True
            if " " in text:
                return True
            compile(text, "<expr_test>", "eval")
            return True

        except SyntaxError:
            pass
        return False


def compilable(text, mode="exec"):
    """Return True if a string can be compiled"""
    # TODO: move to utils
    if not mode in ["eval", "exec"]:
        raise ValueError(f'"{mode}" is an invalid compile mode')

    try:
        compile(text, "", mode)
        return True

    except:
        pass
    return False
