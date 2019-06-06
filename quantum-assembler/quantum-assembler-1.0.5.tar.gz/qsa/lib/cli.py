import abc
import re
import sys

from qsa.lib.datastructures import DTO



def parseopt(opt):
    k, v = opt.split('=', 1)
    return re.sub('\s+$', '', k), re.sub('^\s+', '', v)


class BaseCommand(abc.ABC):
    """The base class for all CLI commands."""
    command_name = abc.abstractproperty()
    help_text = None
    subcommands = None
    args = None
    usage = None

    @staticmethod
    def parseopt(opt):
        return parseopt(opt)

    def __init__(self, injector, assembler):
        self.parser = None
        self.subcommands = type(self).subcommands or []
        self.subparsers = None
        self.args = type(self).args or []
        self.injector = injector
        self.assembler = assembler

    def add_to_parser(self, parser, parent=None):
        """Adds the command to the argument parser."""
        cls = type(self)
        if self.args and self.subcommands:
            raise ValueError(f"Specify either {cls.__name__}.args or {cls.__name__}.subcommands")
        if self.subcommands:
            self._add_subcommands(parser, parent)
        if self.args:
            self._add_args(parser, parent or parser)

    def _add_subcommands(self, parser, parent):
        assert self.subcommands
        self.parser = parser.add_parser(self.command_name,
            help=self.help_text)
        self.subparsers = self.parser.add_subparsers(title=self.command_name,
            description=self.help_text, prog=self.usage)
        for cls in self.subcommands:
            cls(self.injector, self.assembler)\
                .add_to_parser(self.parser, self.subparsers)

    def _add_args(self, parser, parent):
        assert self.args
        self.parser = parent.add_parser(self.command_name,
            help=self.help_text)
        for arg in self.args:
            arg.add_to_parser(self.parser)
        self.parser.set_defaults(func=self._handle)

    def _handle(self, args):
        return self.handle(args)

    def handle(self, args):
        raise NotImplementedError("Subclasses must override this method.")

    def fail(self, msg):
        print(msg)
        sys.exit(1)

    def message(self, message):
        print(message)


class Command(BaseCommand):

    def _handle(self, args):
        return self.injector.call(self.handle)


class Argument:
    """Wrapper around arguments for :meth:`argparse.ArgumentParser.add_argument()`."""

    @staticmethod
    def parseports(ports):
        return [DTO(port=int(x), protocol=y)
            for x,y in [str.split(x, '/') for x in ports] ]

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def add_to_parser(self, parser):
        parser.add_argument(*self.args, **self.kwargs)


class ArgumentList(Argument):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({
            'action': 'append',
            'default': []
        })


class Enable(Argument):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({'action': 'store_true'})


class Selectors(ArgumentList):

    @staticmethod
    def parse(values):
        return {x: y for x, y in [parseopt(str.join(' ', x))
            for x in values]}

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'action': 'append',
            'nargs': '+',
            'default': []
        })
        super().__init__(*args, **kwargs)


class Annotations(ArgumentList):
    dest = 'annotations'
    help_text = "annotate the resource."

    @staticmethod
    def parse(values):
        return {x: y for x, y in [parseopt(str.join(' ', x))
            for x in values]}

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'action': 'append',
            'nargs': '+',
            'dest': self.dest,
            'help': self.help_text,
            'default': []
        })
        super().__init__(*args, **kwargs)


class Labels(Annotations):
    dest = 'labels'
    help_text = "label the resource."
