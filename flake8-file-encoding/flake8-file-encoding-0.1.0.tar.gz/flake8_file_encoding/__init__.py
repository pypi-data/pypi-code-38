import ast
from enum import Enum
import collections

__version__ = "0.1.0"


Argument = collections.namedtuple("Argument", ["state", "value"])


class ArgumentState(Enum):
    POSITIONAL = 1
    KEYWORD = 2
    NOTFOUND = 3


class EncodingChecker:
    name = __name__
    version = __version__

    def __init__(self, tree):
        self.tree = tree

    def run(self):
        for node in ast.walk(self.tree):
            for err in self.rule_FEN001(node):
                yield err

    @staticmethod
    def get_arg(node, position, keyword):
        """
        Gets an argument from a Call node, where the argument can be specified
        with either a position or a keyword.
        """
        args = node.args
        if len(args) >= position + 1:
            return Argument(ArgumentState.POSITIONAL, args[position])
        for kwarg in node.keywords:
            if kwarg.arg == keyword:
                return Argument(ArgumentState.KEYWORD, kwarg)
        return Argument(ArgumentState.NOTFOUND, None)

    def rule_FEN001(self, node):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "open"
        ):
            mode = self.get_arg(node, 1, "mode")
            if mode.state == ArgumentState.NOTFOUND:
                mode = "r"
            elif isinstance(mode.value, ast.Str):
                mode = mode.value.s
            else:
                # TODO: new error code for invalid modes
                return
            if "b" in mode:
                return

            encoding = self.get_arg(node, 3, "encoding")
            if encoding.state == ArgumentState.NOTFOUND:
                yield (
                    node.lineno,
                    node.col_offset,
                    "FEN001 open() call has no encoding argument",
                    type(self),
                )
