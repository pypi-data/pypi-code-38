#! /usr/bin/env python3


"""

"""


import traceback as tb

from ast import *
import sys
import re

from .base import BaseResolver


class ASTIR(BaseResolver):
    def __init__(self):
        super().__init__()
        self._binop_map = {"add": Add(), "sub": Sub(), "mul": Mult(), "div": Div()}
        self._unaryop_map = {"not": Not()}
        self._boolop_map = {"and": And(), "or": Or()}
        self._compare_map = {
            "eq": Eq(),
            "not_eq": NotEq(),
            "lt": Lt(),
            "lt_e": LtE(),
            "gt": Gt(),
            "gt_e": GtE(),
        }
        self._control_flow_map = {
            "if": If,
            "for": For,
            "while": While,
            "try": Try,
            "except": ExceptHandler,
            'async_for': AsyncFor,
        }
        return

    def resolve(self, o_node):
        """Parse an OMP node into AST"""
        if not self.is_astir(o_node):
            return False
        a_node = None
        head = o_node["head"]
        body = o_node.get("body")
        opr = head.split(" ", 1)[0]
        level = o_node.get("level", 0)

        try:
            a_node = getattr(self, opr)(o_node)

        except AttributeError as e:

            if self.is_inline(o_node):
                a_node = self.cast_air(o_node.get("head"))

            else:
                # late catcher
                a_node = False

        except Exception as e:
            tb.print_exc()
            sys.exit(1)
        # if a_node: a_node = self.add_location(a_node, o_node)
        if a_node and level == self._top_level and not type(a_node) in self._stmt_types:
            a_node = Expr(a_node)
        return a_node

    def air_nop(self, *args, **kwds):
        # does nothing; can be use to disable nodes
        # TODO: handle in nested
        return None

    def air_say(self, data):
        # IR for print
        value = None
        p_args = []

        if self.is_inline(data):
            p_args = self._handle_inline_node(data.get("head"), "token")

        else:
            p_args = self._handle_full_node(data.get("body"))
        node = value = Call(func=Name(id="print", ctx=Load()), args=p_args, keywords=[])
        return node

    def air_setv(self, data):
        # assignment (simple for now)
        name = value = None
        targets = []

        if self.is_inline(data):
            data = self._behead(data.get("head"))
            name, value = data.split(" ", 1)
            name = Name(name, Store())
            value = self.cast_air(value)
            targets.append(name)

        elif self.is_full(data):
            anl = self._handle_full_node(data.get("body"))
            name = anl[0]["head"] if isinstance(anl[0], dict) else anl[0]
            name.ctx = Store()
            value = (
                self.cast_air(anl[-1]["head"]) if isinstance(anl[-1], dict) else anl[-1]
            )
            targets.append(name)
        node = Assign(targets=targets, value=value)
        return node

    def air_add(self, data):
        # addition
        return self._binop(data, "add")

    def air_sub(self, data):
        return self._binop(data, "sub")

    def air_mul(self, data):
        return self._binop(data, "mul")

    def air_div(self, data):
        return self._binop(data, "div")

    def _binop(self, data, opn):
        # arithmetic binary operation
        node = None
        bopl = bopr = None
        op = self._binop_map.get(opn.split("_", 1)[-1:][0])
        values = []

        if self.is_inline(data):
            data = self._behead(data.get("head")).split(" ")
            if not all([self.is_num(e) for e in data]):
                raise ValueError(
                    "All operands of a binary operation must be numbers [1]"
                )
            data = [self.cast_air(itm) for itm in data]

        else:
            data = self._handle_full_node(data.get("body"))
            data = [self._resolve(e) if self.is_astir(e) else e for e in data]
        opr_ts = [Num, BinOp]  # valid operand types
        if not all([type(e) in opr_ts for e in data]):
            raise ValueError("All operands of a binary operation must be numbers [2]")
        if len(data) == 1:
            raise ValueError("Only 1 number found during binary arithmetic operation")
        bopl = data[0]

        for itm in data[1:]:
            # recursive binary operations
            bopr = itm
            node = BinOp(left=bopl, op=op, right=bopr)
            bopl = node
        return node

    def is_astir(self, node):
        if not isinstance(node, dict):
            return False
        head = node.get("head")
        return True if head.startswith("air_") or self.cast_air(head, "test") else False

    def air_not(self, data):
        # unary not operation
        return self._unaryop(data, "not")

    def _unaryop(self, data, opn):
        node = None
        op = self._unaryop_map.get(opn.split("_", 1)[-1])

        if self.is_inline(data):
            data = self._behead(data.get("head"))
            data = self.cast_air(data)

        else:
            data = self._handle_full_node(data.get("body"))
            if not len(data) == 1:
                raise ValueError(
                    "A unary operation only takes 1 operand, but {len(data)} found"
                )
            data = data[0]
        node = UnaryOp(op, data)
        return node

    def air_and(self, data):
        # boolean and operation
        return self._boolop(data, "and")

    def air_or(self, data):
        return self._boolop(data, "or")

    def _boolop(self, data, opn):
        node = None
        op = self._boolop_map.get(opn.split("_", 1)[-1])
        values = []

        if self.is_inline(data):
            data = self._behead(data.get("head")).split(" ")
            data = [self.cast_air(v) for v in data]
            values = data

        else:
            data = self._handle_full_node(data.get("body"))
            values = data
        node = BoolOp(op, values)
        return node

    def air_eq(self, data):
        # equality comparison
        return self._compare(data, "eq")

    def air_not_eq(self, data):
        # equality comparison
        return self._compare(data, "not_eq")

    def air_lt(self, data):
        # equality comparison
        return self._compare(data, "lt")

    def air_lt_e(self, data):
        # equality comparison
        return self._compare(data, "lt_e")

    def air_gt(self, data):
        # equality comparison
        return self._compare(data, "gt")

    def air_gt_e(self, data):
        # equality comparison
        return self._compare(data, "gt_e")

    def _compare(self, data, opn):
        node = None
        op = self._compare_map.get(opn.split("_", 1)[-1])
        values = []

        if self.is_inline(data):
            data = self._handle_inline_node(data.get("head"), "split")
            values = data

        else:
            data = self._handle_full_node(data.get("body"))
            values = data
        if len(values) < 2:
            raise ValueError(
                f"Need at least 2 operands to do a comparison, but got {len(values)}"
            )
        left = values.pop(0)
        ops = [op] * len(values)
        node = Compare(left, ops, values)
        return node

    def air_call(self, data):
        # function call
        # TODO: handle eval'uable func name
        func = f_args = None

        if self.is_inline(data):
            data = self._behead(data.get("head"))
            if not " " in data:
                data += " "  # hack to handle no arg
            f_name, f_args = data.split(" ", 1)
            func = Name(id=f_name, ctx=Load())
            f_args = [self.cast_air(a) for a in self._tokenize(f_args)]

        else:
            data = self._handle_full_node(data.get("body"))
            if not data:
                raise ValueError("Need at least the name of a function to call")
            func = data.pop(0)
            f_args = data
        args = []
        kwds = []

        for a in f_args:
            if isinstance(a, keyword):
                kwds.append(a)

            else:
                args.append(a)
        node = Call(func=func, args=args, keywords=kwds)
        return node

    def air_import(self, data):
        # imports
        # TODO: support aliasing, multiple from and combined import methods
        node = None
        from_rx = re.compile(r"(?P<names>[\w\s*]+) from (?P<module>[\w.]+)")
        data = self._node_to_list(data)
        i_aliases = []
        fi_aliases = []

        for im in data:
            if isinstance(im, Name):
                # simple import
                i_aliases.append(alias(name=im.id, asname=None))
                continue
            match = from_rx.match(im.s)
            level = 0

            if match:
                # from import
                if len(data) > 1:
                    raise ImportError(
                        f"Currently only a single module can be imported from; got {len(data)} modules"
                    )
                match = match.groupdict()
                module = match.get("module")

                if re.match(r"^\.+$", module):
                    level = module.count(".")
                    module = None
                names = [
                    alias(name=a, asname=None) for a in match.get("names").split(" ")
                ]
                fi_aliases = {"module": module, "names": names, "level": level}
        if i_aliases and fi_aliases:
            raise ImportError(
                "Cannot currently combine both import methods under the same import node"
            )
        node = (
            Import(i_aliases)
            if i_aliases
            else ImportFrom(**fi_aliases)
            if fi_aliases
            else None
        )
        if not node:
            raise ImportError("Nothing found to import")
        return node

    def air_if(self, data):
        # condition
        return self._control_flow(data, "if")

    def _control_flow(self, data, cft, ignores=None, cl_cnt=None):
        if self.is_inline(data):
            raise Exception("Inline mode is not supported in control nodes")
        node = None
        clauses = []
        if not ignores:
            ignores = ["test", "body", "orelse"]
        if not cl_cnt:
            cl_cnt = [2, 3]  # clause count
        s_types = self._stmt_types
        cf = self._control_flow_map.get(cft)
        data = self._handle_full_node(data.get("body"), ignore_heads=ignores)
        if not len(data) in cl_cnt:
            raise ValueError(
                f"Expected {cl_cnt[0]} to {cl_cnt[1]} items, but got {len(data)}"
            )

        for idx, elt in enumerate(data):
            clause = elt if not isinstance(elt, dict) else elt.get(ignores[idx])

            if cft == "for":
                # for-specific element fixups
                if idx == 0 and isinstance(clause, Name):
                    clause.ctx = Store()

            if cft == "try" and idx == 1:
                # try-specific element fixups
                if not all([isinstance(e, ExceptHandler) for e in clause]):
                    raise ValueError(
                        'All nodes within the handlers clause must be of type "ExceptHandler"'
                    )

            if cft == "except" and idx == 1:
                if not isinstance(clause, Name):
                    raise NameError("Invalid name in except handler")
                clause = clause.id

            if idx + 1 in cl_cnt and not isinstance(clause, list):
                clause = [clause]
            clauses.append(clause)
        while True:
            # fill in remaining missing but required args
            if len(clauses) == cl_cnt[-1]:
                break
            clauses.append([])

        for clause in clauses:
            # wrap expressions to statements
            if not isinstance(clause, list):
                continue

            for idx, a_node in enumerate(clause):
                if not type(a_node) in s_types:
                    clause[idx] = Expr(a_node)
        node = cf(*clauses)
        return node

    def air_for(self, data):
        # loop
        ignores = ["target", "iter", "body", "orelse"]
        cl_cnt = [3, 4]
        return self._control_flow(data, "for", ignores, cl_cnt)

    def air_async_for(self, data):
        # loop
        ignores = ["target", "iter", "body", "orelse"]
        cl_cnt = [3, 4]
        return self._control_flow(data, "async_for", ignores, cl_cnt)

    def air_while(self, data):
        return self._control_flow(data, "while")

    def air_def(self, data):
        return self._function_def(data, FunctionDef)

    def air_async_def(self, data):
        return self._function_def(data, AsyncFunctionDef)

    def _function_def(self, data, nt):
        node = None
        o_clist = data.get("body")  # org clauses list
        f_name = o_clist[0].get("head")
        args = self._arguments(
            o_clist[1].get("body")
            if self.is_full(o_clist[1])
            else o_clist[1].get("head")
        )
        body = self._node_to_list(o_clist[2], ignore_first=["body"])
        body = [Expr(a_n) if not type(a_n) in self._stmt_types else a_n for a_n in body]
        decorators = []
        returns = None
        node = nt(f_name, args, body, decorators, returns)
        return node

    def _arguments(self, data):
        # process args
        node = None
        args_list = []
        vararg = None
        kwonlyargs = []
        kw_defaults = []
        kwarg = None
        defaults = []
        in_keys = False

        if isinstance(data, str):
            if data == "args":
                pass

            else:
                # inline args
                args = data.split(" ")
                if not all([self.is_name(a) for a in args]):
                    raise NameError("One or more invalid names found in arguments [1]")
                args = [arg(a, None) for a in args]
                args_list.append(args)

        elif isinstance(data, list):
            if any([" " in elt.get("head") for elt in data]):
                raise NameError("One or more invalid names found in arguments [2]")
            data = self._handle_full_node(data)

            for elt in data:

                if not in_keys:

                    if isinstance(elt, Name):
                        # pos arg, no def
                        a = arg(elt.id, None)
                        args_list.append(a)
                        continue

                    elif isinstance(elt, keyword):
                        # pos arg w/ def
                        a = arg(elt.arg, None)
                        d = elt.value
                        args_list.append(a)
                        defaults.append(d)
                        continue

                    elif isinstance(elt, Starred):
                        # starred arg (should contain Name node)
                        vararg = arg(elt.value.id, None)
                        in_keys = True
                        continue

                else:
                    if kwarg:
                        raise SyntaxError("Starred keyword must be the final argument")

                    if isinstance(elt, keyword):
                        # keyed arg or map
                        a = arg(elt.arg or "", None)
                        d = elt.value

                        if a.arg:
                            kwonlyargs.append(a)
                            kw_defaults.append(d)

                        else:
                            kwarg = arg(d.id, None) if isinstance(d, Name) else None
                            if not kwarg:
                                raise NameError(f"Expected a name-compatible str")

                    else:
                        raise SyntaxError(
                            "Cannot have a positional argument after a starred or keyword arg"
                        )
        node = arguments(args_list, vararg, kwonlyargs, kw_defaults, kwarg, defaults)
        return node

    def air_class(self, data):
        # class definition
        node = None
        o_clist = data.get("body")
        c_name = o_clist[0].get("head")
        bases = []
        keywords = []
        body = self._node_to_list(o_clist[1])
        body = [Expr(a_n) if not type(a_n) in self._stmt_types else a_n for a_n in body]
        decorators = []
        node = ClassDef(c_name, bases, keywords, body, decorators)
        return node

    def air_raise(self, data):
        # raise exceptions
        # TODO: handle cause clause
        return self._one_line_stmt(data, Raise, 1)

    def air_try(self, data):
        # monitor for and handle exceptions
        ignores = ["body", "handlers", "orelse", "finalbody"]
        cl_cnt = [2, 4]
        return self._control_flow(data, "try", ignores, cl_cnt)

    def air_except_handler(self, data):
        # exception handler (only valid within try handlers)
        ignores = ["type", "name", "body"]
        cl_cnt = [3, 3]
        return self._control_flow(data, "except", ignores, cl_cnt)

    def air_assert(self, data):
        data = self._node_to_list(data)
        if not len(data) == 2:
            raise ValueError(f"Expected 2 arguments but got {len(data)}")
        node = Assert(*data)
        return node

    def air_del(self, data):
        valid_nts = [Name, Attribute, Subscript]

        def fixup(node_list):
            for node in node_list:
                if hasattr(node, "ctx"):
                    node.ctx = Del()
            return node_list

        return self._one_line_stmt(data, Delete, "+", valid_nts, fixup)

    def air_pass(self, data):
        # placeholder
        return Pass()

    def air_break(self, data):
        # break out of a loop
        return Break()

    def air_continue(self, data):
        # continue a loop
        return Continue()

    def air_return(self, data):
        # return a value (at least None; cannot be empty)
        return self._one_line_stmt(data, Return, "1")

    def air_yield(self, data):
        #
        node = None
        return node

    def air_yield_from(self, data):
        #
        node = None
        return node

    def air_global(self, data):
        #
        node = None
        return node

    def air_nonlocal(self, data):
        #
        node = None
        return node

    def air_await(self, data):
        # used within async functions
        node = None
        return self._one_line_stmt(data, Await, '1')

    def _one_line_stmt(self, data, nt, arg_cnt="*", valid_nts=None, fixup=None):
        node = None
        value_list = self._node_to_list(data)
        if valid_nts and not all([type(elt) in valid_nts for elt in value_list]):
            raise ValueError("One or more invalid node types found")
        if str(arg_cnt).isdigit() and not len(value_list) == int(arg_cnt):
            raise ValueError(f"Expected {arg_cnt} nodes but got {len(value_list)}")
        if callable(fixup):
            value_list = fixup(value_list)

        if str(arg_cnt) == "1":
            node = nt(value_list[0])

        elif arg_cnt == "?":
            node = nt(value_list[0] if value_list else None)

        else:
            node = nt(value_list)
        return node

    def air_attr(self, data):
        # attribute access
        data = self._node_to_list(data)
        if not len(data) == 2:
            raise ValueError(f"Expected 2 parameters, but got {len(data)}")
        if not type(data[1]) in [Str, Name]:
            raise ValueError(f"Expected a string that can be used as a name")
        value = data[0]
        attr = data[1].s
        node = Attribute(value, attr, Load())
        return node

    def air_list(self, data):
        # list
        if not " " in data.get("head") and not data.get("body"):
            return List([], Load())
        data = self._node_to_list(data)
        node = List(data, Load())
        return node

    def air_tuple(self, data):
        # tuple
        if not " " in data.get("head") and not data.get("body"):
            return Tuple([], Load())
        data = self._node_to_list(data)
        node = Tuple(data, Load())
        return node

    def air_set(self, data):
        # set
        if not " " in data.get("head") and not data.get("body"):
            return Set([])
        data = self._node_to_list(data)
        node = Set(data)
        return node

    def air_dict(self, data):
        # dict
        keys = []
        values = []

        for pair in data.get("body"):
            key = self.cast_air(pair.get("head"))
            body = pair.get("body")
            value = (
                self._node_to_list(body[0])
                if len(body) == 1
                else self._handle_full_node(body)
                if len(body) > 1
                else None
            )
            if not value:
                raise ValueError("Missing corresponding value for key in dict")
            if isinstance(value, list):
                if not len(value) == 1:
                    raise ValueError(f"Expected a single value but got {len(value)}")
                value = value[0]
            keys.append(key)
            values.append(value)
        node = Dict(keys, values)
        return node

    def air_joined_str(self, data):
        # f-string
        data = self._node_to_list(data)
        values = [
            v if isinstance(v, Str) else FormattedValue(v, -1, None) for v in data
        ]
        node = JoinedStr(values)
        return node

    def air_starred(self, data):
        # variable reference
        node = self._one_line_stmt(data, Starred, "1")
        node.ctx = node.value.ctx
        return node

    def air_kwd(self, data):
        # keyword args
        node = None
        data = self._node_to_list(data)

        if len(data) == 1:
            # mapping ref
            node = keyword(None, data[0])

        elif len(data) == 2:
            if not isinstance(data[0], Name):
                raise NameError(f"Expected a name-compatible str")
            node = keyword(data[0].id, data[1])
        return node

    def _keyword(self, data):
        # Keyword arg in class def?
        arg = data.get("head")
        if not self.is_name(arg):
            raise NameError("Expecting a name-compatible str")
        body = data.get("body")
        value = self._node_to_list(body[0]) if len(body) == 1 else None
        if not value:
            raise ValueError(f"Expected a single valuue but got {len(body)}")
        node = keyword(arg, value)
        return node

    def air_slice(self, data):
        # subscripting simplified
        data = self._node_to_list(data)
        slice_ = None

        if len(data) == 2:
            slice_ = Index(data[1])

        elif len(data) in [3, 4]:
            slice_ = Slice(*(data[1:]))

        else:
            raise IndexError("Invalid number if subscripts found.")
        node = Subscript(data[0], slice_, Load())
        return node

    def air_with(self, data):
        return self._with_stmt(data, With)

    def air_async_with(self, data):
        return self._with_stmt(data, AsyncWith)

    def _with_stmt(self, data, nt):
        node = None
        ignores = ['items', 'body']
        s_types = self._stmt_types
        items = [
            self._withitem(itm)
            for itm in data['body'][0].get('body')
        ]
        body = self._handle_full_node(
            data['body'][1].get('body'),
            ignore_heads=ignores,
        )
        body = [
            Expr(b)
            if not type(b) in s_types else b
            for b in body
        ]
        node = nt(items, body)
        return node

    def _withitem(self, data):
        node = None
        ctx_e = None
        opt_v = self._handle_inline_node(data.get('head'), 'single')[0]

        if isinstance(opt_v, (Name, Tuple, List)):
            ctx_e = self._resolve(data.get('body')[0])
            if ctx_e in self._stmt_types + [Expr]:
                raise TypeError(f'Item context for "with" must be an expression, not a statement')
            if hasattr(opt_v, 'ctx'):
                opt_v.ctx = Store()

        else:
            ctx_e = opt_v
            opt_v = None
        node = withitem(ctx_e, opt_v)
        return node


def generate_neu():
    """Make copy in neucode"""
    am = parse(open(sys.argv[0]).read())
    astir = "#! /usr/bin/env neu\n\n"

    for node in am.body[1:-2]:
        astir += f"* {dump(node)}\n"

    with open(sys.argv[0].replace(".py", ".neu", 1), "w") as af:
        af.write(astir)
    return


THIS_FILE = "astir.py"


if __name__ == "__main__":
    generate_neu()
