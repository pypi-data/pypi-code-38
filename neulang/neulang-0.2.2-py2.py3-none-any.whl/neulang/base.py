"""
Base resolver and registry.
"""


import traceback as tb

from ast import *
import sys
import re
from shlex import shlex


class ResolverRegistry(type):
    _registry = {}
    _instances = {}

    def __new__(cls, name, bases, attrs):
        # register and instanciate class as soon as it's defined
        new_cls = type.__new__(cls, name, bases, attrs)
        cls._registry[new_cls.__name__] = new_cls
        new_cls()
        return new_cls

    def __call__(cls, *args, **kwds):
        # make registered classes singletons
        if cls not in cls._instances:
            cls._instances[cls] = super(ResolverRegistry, cls).__call__(*args, **kwds)
        return cls._instances[cls]

    @classmethod
    def get_resolvers(cls):
        return cls._instances

    @classmethod
    def add_resolver(cls, resolver):
        # allow usage as non-meta
        cls._instances[resolver.__class__.__name__] = resolver
        return True


class BaseResolver:
    # __metaclass__ = ResolverRegistry

    def __init__(self, ):
        ResolverRegistry.add_resolver(self)
        self._stmt_types = [
            Assign,
            Import,
            ImportFrom,
            If,
            For,
            While,
            FunctionDef,
            ClassDef,
            Delete,
            Pass,
            Break,
            Continue,
            Return,
            Yield,
            YieldFrom,
            Global,
            Nonlocal,
            Await,
            Raise,
            Assert,
            Try,
            ExceptHandler,
            With,
            AsyncFor,
            AsyncWith,
        ]
        self._resolvers = self.get_resolvers()
        self._top_level = 1
        return

    def get_resolvers(self):
        return ResolverRegistry.get_resolvers()

    def _resolve(self, node):
        """Resolve a node by seeking the correct resolver"""
        # TODO: resolver priority list or sort method
        a_node = None
        anl = []
        resolvers = self._resolvers
        r_names = [
            "ASTIR",
            'AdaptResolver',
            #"RegexResolver",
            "PyExprResolver",
        ]
        resolved = False
        is_single = True  # flag to de-list single-node results

        for rsvr in r_names:
            # TODO: make custom return object to handle special cases
            a_node = resolvers[rsvr].resolve(node)
            if a_node is False:
                continue  # node unhandled flag

            if a_node is None:
                # nothing to add (but node already handled)
                resolved = True
                break

            if a_node:
                # make list for processing
                if not isinstance(a_node, list):
                    is_single = False
                    a_node = [a_node]
                assert not any(
                    [isinstance(e, list) for e in a_node]
                ), "Found nested list"
                a_node = [self.add_location(a_n, node) for a_n in a_node]

                if node.get("level") == self._top_level:

                    for a_n in a_node:
                        if (
                            not isinstance(a_n, Expr)
                            and not type(a_n) in self._stmt_types
                        ):
                            a_n = Expr(a_n)
                        a_n.lineno = node.get("lineno", 0)
                        a_n.col_offset = node.get("col_offset", 0)
                        self.pre_test(a_n, node.get("lineno", 0))
                        anl.append(a_n)
                resolved = True
            if not anl:
                anl = a_node
            if anl:
                break
        if not resolved:
            raise ValueError("Unresolved node")
        if not is_single:
            return anl[0]
        return anl

    def add_handler(self, data):
        pass

    def add_location(self, a_node, o_node):
        """Add locations from org to AST node"""
        lineno = o_node.get("lineno", None)
        col_offset = o_node.get("col_offset", None)
        if not (lineno or col_offset):
            return a_node

        def _fix(node, lineno, col_offset):
            if "lineno" in node._attributes:
                if not hasattr(node, "lineno"):
                    node.lineno = lineno
                else:
                    lineno = node.lineno
            if "col_offset" in node._attributes:
                if not hasattr(node, "col_offset"):
                    node.col_offset = col_offset
                else:
                    col_offset = node.col_offset
            for child in iter_child_nodes(node):
                _fix(child, lineno, col_offset)

        _fix(a_node, lineno or 1, col_offset or 0)
        return a_node

    def cast_air(self, value, mode="norm"):
        # cast to type via wrapper
        # TODO: prob delegate to PyExprResolver
        node = None

        if self.is_num(value):
            # number
            node = Num(n=float(value) if "." in value else int(value))

        elif value in ["True", "False", "None"]:
            node = NameConstant(
                True if value == "True" else False if value == False else None
            )

        elif self.is_name(value):
            node = Name(value, Load())

        elif self.is_string(value):
            # quoted string; maybe make fallthrough
            node = Str(s=value[1:-1])

        else:
            # unquoted string (or sth else)
            node = Str(value) if mode == "norm" else None
            # raise TypeError(f'Unable to detect a castable type for `{value}`')
        return node

    def _handle_inline_node(self, data, mode, ignore_first=False):
        # node with args in head
        data = self._behead(data)

        if mode == "split":
            data = data.split(" ")

        elif mode == "token":
            # tokenize to account for quotes
            data = self._tokenize(data)

        elif mode == "single":
            # make a list
            data = [data]

        else:
            raise ValueError(f"Unknown mode {mode}")
        anl = [self.cast_air(v) for v in data]
        return anl

    def _handle_full_node(self, data, ignore_heads=False):
        # args from node with body
        if not isinstance(data, list):
            raise ValueError(f"Expected a list, but got {type(data)}")
        anl = []  # AST node list

        for o_node in data:
            head = o_node.get("head")
            a_node = (
                {head: self._handle_full_node(o_node.get("body"))}
                if isinstance(ignore_heads, list) and head in ignore_heads
                else self._resolve(o_node)
            )
            if (
                a_node is False
                or isinstance(a_node, dict)
                and a_node.get(o_node.get("head")) is False
            ):
                return False  # Wut!!! TODO: watch
            if a_node in [None, []]:
                continue
            anl.append(a_node) if not isinstance(a_node, list) else anl.extend(a_node)
        return anl

    def _handle_combo_node(self, data):
        # node with args in head and body
        return node

    def _behead(self, data):
        # remove prefix if it's there
        if not isinstance(data, str):
            raise ValueError(f"Expected a string but got {type(data)}")
        if re.search(r"air_[A-Za-z_]+(\s.*)?", data):
            data = data.split(" ", 1)[1]
        return data

    def _node_type(self, node):
        nt = ""
        head = node.get("head")
        body = node.get("body")

        if not body:
            nt = "inline"

        elif not " " in head:
            nt = "full"

        elif " " in head and body:
            nt = "combo"

        else:
            nt = "unknown"
        return nt

    def _node_to_list(self, node, mode="token", ignore_first=False):
        # convert a node to a list, and any sub-nodes to AST
        data = None

        if self.is_inline(node):
            data = self._handle_inline_node(node.get("head"), mode)

        else:
            data = self._handle_full_node(node.get("body"), ignore_first)
        return data

    def _tokenize(self, text):
        # tokenize string into args
        if not isinstance(text, str):
            raise TypeError(f"Expected a str but got {type(text)}")
        tokens = []
        sl = shlex(text)

        while True:
            token = sl.read_token()
            if not token:
                break
            tokens.append(token)
        return tokens

    def is_inline(self, node):
        if not isinstance(node, dict):
            raise TypeError("Expected a dict but got {type(node)}")
        return self._node_type(node) == "inline"

    def is_full(self, node):
        if not isinstance(node, dict):
            raise TypeError("Expected a dict but got {type(node)}")
        return self._node_type(node) == "full"

    def is_combo(self, node):
        if not isinstance(node, dict):
            raise TypeError("Expected a dict but got {type(node)}")
        return self._node_type(node) == "combo"

    def is_name(self, text):
        # check if something is a valid Python name
        if not isinstance(text, str):
            raise TypeError("Expected a str but got {type(text)}")
        return not not re.search(r"^[A-Za-z_][A-Za-z0-9_]*$", text)

    def is_string(self, text):
        # check if a quoted string
        if not isinstance(text, str):
            raise TypeError("Expected a str but got {type(text)}")
        return text[:1] in ['"', "'"] and text[:1] == text[-1:]

    def is_num(self, value):
        if not isinstance(value, str):
            raise TypeError("Expected a str but got {type(value)}")

        try:
            float(value)
            return True

        except ValueError:
            return False

    def pre_test(self, node, line):

        try:
            nm = Module([node])
            nc = compile(nm, "<pre_test>", "exec")

        except Exception as e:
            print(f"Compile test failed at line #{line}")
            tb.print_exc()
            sys.exit(1)
        return node
