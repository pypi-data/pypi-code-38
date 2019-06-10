import copy
import functools
import logging
import operator
import os
import tempfile

import ioc
import jinja2

import qsa.lib.cli
from qsa.cli.exc import CommandError
####################MOVE
import os

import yaml

LF = '\n'
WS = ' '


def format_environment_variable(value, inline=True):
    symbol = value if os.getenv('QSA_PREFIX_ENVIRONMENT') != '1'\
        else '{QSA_PKG_NAME}_{value}'.format(value=value, **os.environ).upper()
    return f'${symbol}' if inline else symbol


def envdefault(key, value):
    key = format_environment_variable(key, inline=False)
    return f'${{{key}-{value}}}'


def dictsort(d):
    return sorted(d.items(), key=lambda x: x[0])


def limit(value, max_length, indent, prefix=''):
    """Limits the length of each line in the output to
    `length`, indented by `indent`, broken up on word
    boundaries.
    """
    INDENT = WS * indent
    NEWLINE = LF + INDENT
    words = value.split(WS)
    stmt = ''
    if prefix:
        stmt = f'{prefix} '
    result = ''
    for word in words:
        if not word: # Value container consecutive spaces.
            continue
        length = len(stmt[stmt.rfind('\n'):])\
            if stmt.rfind('\n') != -1\
            else len(stmt)
        if (length + len(word) > max_length):
            stmt = str.strip(stmt, WS)
            stmt += NEWLINE + ('' if not prefix else f'{prefix} ')
        stmt += f'{word} '
    return str.strip(stmt)

def render_yaml(value):
    if hasattr(value, 'as_dict'):
        value = value.as_dict()
    return yaml.safe_dump(value, default_flow_style=False, indent=2)\
        .strip().rstrip('.').strip()


def safe_variable(value):
    return str.replace(value, '.', '_')

####################MOVE


class BaseExtension:
    logger = logging.getLogger('qsa')

    #: The name of the extension. This attribute is required.
    name = None

    #: Specifies the command name. If this attribute is ``None``, the
    #: extension is assumed not to implement a subcommand.
    command_name = None

    #: Configures subcommands for the parser.
    subcommands = []

    #: Help text to be displayed when ``qsa <command_name> --help`` is invoked.
    help_text = None

    #: Specifies the schema class to load and dump the configuration.
    #: If :attr:`BaseExtension.schema_class` is ``None``, it is
    #: assumed that the extension does not have a configuration.
    schema_class = None

    #: Defines the order of extension execution.
    weight = 0.0

    # Specifies arguments for the template environment.
    template_params = {
        'lstrip_blocks': False,
        'trim_blocks': False
    }

    # The extension will inject itself in the dependency injector
    # using this key.
    inject = None

    def __init__(self, config, assembler, injector):
        self.config = config
        self.assembler = assembler
        self.injector = injector
        self.spec = None
        self.quantum = None
        self.loader = jinja2.PackageLoader(self.__module__, 'templates')
        self.template = jinja2.Environment(
            loader=jinja2.ChoiceLoader([
                jinja2.PackageLoader(self.__module__, 'templates'),
                jinja2.PackageLoader('qsa', 'templates')
            ]),
            **self.template_params
        )
        self.template.globals.update(envname=format_environment_variable)
        self.template.globals.update(envdefault=envdefault)
        self.template.filters.update({
            'yaml': render_yaml,
            'dictsort': dictsort,
            'limit': limit,
            'safe_variable': safe_variable
        })
        if self.schema_class:
            schema = self.schema_class.getfordump()
            self.spec = schema.defaults()

    def on_spec_loading(self, data, quantum):
        """Invoked when the content of :attr:`~qsa.const.QUANTUMFILE` is
        deserialized into a dictionary.

        Args:
            data: the data as loaded from the Quantum specification.
            quantum: the parsed and cleaned data. Note that this is the
                full specification, not only for this extension.
        """
        #assert not self.spec
        if not self.schema_class:
            self.logger.debug("Extension %s does not implement configuration.",
                self.name)
            return
        schema = self.schema_class.getforload()
        try:
            self.spec = schema.dump(copy.deepcopy(data))
        except Exception as e:
            self.spec = {}
        quantum.update(copy.deepcopy(self.spec))

    def on_spec_loaded(self, quantum):
        """Invoked when the full Quantum specification is loaded."""
        assert not self.quantum
        self.quantum = quantum

    def on_spec_updated(self, quantum):
        """Invoked when the Quantum specification is updated."""
        if not self.schema_class:
            return
        schema = self.schema_class.getforload()
        self.spec = schema.load(quantum.spec)

    def on_spec_render(self, qf):
        """Invoked when the Quantumfile is being rendered to string."""
        if not self.schema_class or not self.spec:
            return
        if not self.isenabled():
            return
        qf.addsection(self.name, self.render('Quantumfile.j2'),
            self.weight)

    def on_spec_section_render(self, qf, section, subsections):
        """Invoked when a specific section is rendered."""
        pass

    def isenabled(self):
        return True

    def _createcommand(self, subcommands):
        if self.command_name is None:
            return
        parser = self.createcommand(subcommands)
        self._add_parser_defaults(parser)
        if self.subcommands:
            parent = parser.add_subparsers(dest='command')
        for subcommand in self.subcommands:
            if isinstance(subcommand, (dict, tuple)):
                self._createsubcommand(parent, **subcommand)
            elif issubclass(subcommand, qsa.lib.cli.BaseCommand):
                subcommand(self.injector, self.assembler).add_to_parser(parent)

    def _createsubcommand(self, parent, name, args):
        parser = parent.add_parser(name)
        for arg in args:
            if isinstance(arg, dict):
                parser.add_argument(**arg)
            elif isinstance(arg, tuple):
                name, arg = arg
                parser.add_argument(name, **arg)
            else:
                raise NotImplementedError
        parser.set_defaults(func=self.run_subcommand)

    def _add_parser_defaults(self, parser):
        parser.set_defaults(workdir=os.getenv('QSA_WORKDIR'))
        parser.set_defaults(func=self.handle)

    def createcommand(self, parent):
        """Exposes a subcommand to the ``qsa`` command-line
        interface.
        """
        parser = parent.add_parser(self.command_name,
            help=self.help_text)
        return parser

    def run_subcommand(self, args):
        f = getattr(self, f'handle_{args.command.replace("-", "_")}')
        self.injector.call(f)

    def handle(self):
        self.logger.debug('%s.Extension.handle() is not implemented',
            self.__module__)

    def render(self, template_name, ctx=None):
        """Renders the Jinja2 template `template_name` using the given
        context `ctx`.
        """
        ctx = ctx or {}
        ctx.update({
            'IS_QUANTUM_INIT': os.getenv('QSA_INIT') == '1'
        })
        t = self.template.get_template(template_name)
        spec = {}
        if self.schema_class:
            schema = self.schema_class.getfordump()
            spec = schema.dump(ctx.pop('spec', None) or copy.deepcopy(self.spec))
        return t.render(spec=spec, quantum=dict(self.quantum), **ctx)

    def render_to_file(self, fs, template_name, dst, *args, **kwargs):
        """Render the content of `template_name` and writes it to the specified
        destination `dst`.
        """
        ctx = kwargs.setdefault('ctx', {})
        ctx['FILENAME'] = dst
        fs.write(dst, self.render(template_name, **kwargs))

    def fail(self, msg):
        raise CommandError(msg)

    def setup_injector(self, injector):
        """Hook to allow extensions to setup the dependency
        injector.
        """
        if self.inject is not None:
            injector.provide(self.inject, self)

    def setup(self):
        """Hook that is invoked prior to the handler function(s)."""
        pass

    def can_handle(self, *args, **kwargs):
        """Hook returning a boolean if the extension can handle events."""
        return True

    def edit(self, codebase, new=False, template_name='Quantumfile.j2'):
        """Launch an editor to modify the Quantumfile section for this
        extension.
        """
        src = tempfile.mktemp()
        if new:
            defaults = self.get_default_config()
            schema = self.schema_class.getfordump()
            ctx = {'spec': schema.dump(defaults)}
        else:
            raise NotImplementedError
        with open(src, 'w') as f:
            f.write(self.render(template_name, ctx=ctx))
        args = ['vim', '-c', "'set syntax=yaml ts=2 sw=2 expandtab'", src]
        os.system(' '.join(args))
        schema = self.schema_class.getforload()
        self.spec = schema.load(yaml.safe_load(open(src)))
        self.quantum.update(self.spec)
        self.quantum.persist(codebase)

    def get_default_config(self):
        """Returns the default configuration for this extension."""
        return {}

    def initialize(self):
        """Initializes the extension if it has not been configured
        yet.
        """
        if not self.schema_class:
            return
        schema = self.schema_class.getfordump()
        self.spec = schema.dump(schema.defaults())
        print(self.spec, schema.defaults())
        self.quantum.update(self.spec)

    @staticmethod
    def project_type(typname, inject=False):
        def decorator_factory(func):
            @functools.wraps(func)
            def decorator(self, *args, **kwargs):
                p = self.quantum.get('project.type', None)
                if p != typname:
                    raise CommandError(
                        f"This operation is not available for project type {p}")
                return func(self, *args, **kwargs)\
                    if not inject else self.injector.call(func)
            return decorator
        return decorator_factory

    @staticmethod
    def inject(func):
        """Use the injector of a :class;`BaseExtension` to inject
        dependencies into the decorated function `func`.
        """
        @functools.wraps(func)
        def decorator(self, *args, **kwargs):
            return self.injector.call(func)
        return decorator

    def require(self, key, value, op=None):
        """Requires that the configuration `key` returns ``True``
        with `value` using `op`.
        """
        op = op or operator.eq
        cfg = self.quantum.get(key, None)
        if not op(cfg, value):
            raise CommandError(
                f"This operation is not available when {key}=={cfg}")
        return True

    def provide_class(self, dep):
        name = type(dep).__name__
        ioc.provide(f'{self.name}:{name}', dep)
