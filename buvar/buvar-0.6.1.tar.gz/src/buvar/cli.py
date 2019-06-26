import collections
import inspect
import sys
import typing

import toml

from buvar import components, config


class CliArgs(list):
    def __init__(self, args=sys.argv[1:]):
        self.args = list(args)

    def take(self, i):
        try:
            return self.args[:i]
        finally:
            self.args = self.args[i:]


class Parse:
    def __init__(self):
        # holds all
        self.stack: typing.Dict[
            typing.Callable,
            typing.List[Argument]
        ] = collections.OrderedDict()

    def argument(self, *args, **kwargs):
        argument = (
            args[0](self, *args[1:], **kwargs)
            if inspect.isclass(args[0])
            else Argument(self, *args, **kwargs)
        )
        return argument

    def stream(self, args=None, context=None):
        if args is None:
            args = CliArgs()
        elif isinstance(args, (tuple, list)):
            args = CliArgs(args)

        if context is None:
            context = {}

        # copy stack
        stack = list(self.stack.values())
        while stack:
            # try the first decorated function
            match = stack.pop(0)
            yield from match.stream(args)

        for arg in args:
            print(arg)


class GroupMismatch(Exception):
    pass


class ArgumentGroup:
    def __init__(self, fun, *arguments):
        self.fun = fun
        self.arguments = list(arguments)

    def add(self, argument):
        self.arguments.append(argument)

    def _consume(self, args):
        # test condiates
        arguments = list(self.arguments)
        while arguments:
            candidate = arguments.pop(0)
            match = candidate.matches(args)
            __import__('pdb').set_trace()      # XXX BREAKPOINT
            if match:
                yield match
            else:
                arg

        # restore args if failed

    def stream(self, args):
        yield from self._consume(args)


class Match:
    def __init__(self, argument, consumed_args, values):
        self.argument = argument
        self.consumed_args = consumed_args
        self.values = values


class Argument:
    def __init__(self, parse, *args, **kwargs):
        self.parse = parse
        self.args = args
        self.kwargs = kwargs

    def __call__(self, fun):
        try:
            self.parse.stack[fun].add(self)
        except KeyError:
            self.parse.stack[fun] = ArgumentGroup(fun, self)
        return fun

    def matches(self, args, context=None):
        if context is None:
            context = {}
        return None


class Option(Argument):
    def __init__(self, parse, name, *flags):
        super().__init__(parse)
        self.name = name
        self.flags = flags

    def matches(self, args, context=None):
        __import__('pdb').set_trace()      # XXX BREAKPOINT
        if len(args) > 1 and args[0] in self.flags:
            match = Match(self, args[:2], {self.name: args[1]})
            args = args[2:]
            return match
        return None





parse = Parse()


@parse.argument(Option, 'config', '-c', '--config')
def foo(config):
    print("foo")



def main():
    list(parse.stream())
