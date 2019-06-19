import asyncio
import functools
import importlib
import inspect
import operator
import typing

import click
from IPython import embed
from sanic.server import trigger_events
from sanic import Sanic

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.5.3"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"
__all__ = ['common_cli', 'CommandEnv', 'sanic_triggers', 'async_server_trigger']


class CommandEnv:

    app: Sanic
    shell_imports: typing.List[typing.Tuple[str, str]] = []
    shell_producers: typing.List[typing.Callable[[Sanic], typing.Dict[str, typing.Any]]] = []
    shell_cleanups: typing.List[typing.Callable[[typing.Dict], None]] = []
    default_port: str = '8080'
    default_host: str = '127.0.0.1'

    @classmethod
    def run_cli(cls):
        sources = [common_cli]
        try:
            command_module = importlib.import_module(cls.app.name + '.commands')
            sources.extend(
                map(
                    operator.itemgetter(1),
                    inspect.getmembers(command_module, lambda x: isinstance(x, click.Group))
                )
            )
        except ModuleNotFoundError:
            pass
        click.CommandCollection(sources=sources)()


def sanic_triggers(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        server_settings = CommandEnv.app._helper()  # pylint: disable=protected-access
        CommandEnv.app.config['MANUAL_TRIGGERS'] = True
        trigger_events(server_settings['before_start'], loop)
        trigger_events(server_settings['after_start'], loop)
        result = func(*args, **kwargs)
        trigger_events(server_settings['before_stop'], loop)
        trigger_events(server_settings['after_stop'], loop)
        return result

    return wrapper


def async_server_trigger(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if not hasattr(CommandEnv, 'app') or not CommandEnv.app.config.get('MANUAL_TRIGGERS', False):
            return await func(*args, **kwargs)
    return wrapper


def async_command(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if hasattr(CommandEnv, 'app'):
            CommandEnv.app.config['MANUAL_TRIGGERS'] = True
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(func(*args, **kwargs))
        return result
    return wrapper


@click.group()
def common_cli():
    pass


@common_cli.command()
@click.option('--host', default=lambda: CommandEnv.default_host)
@click.option('--port', default=lambda: CommandEnv.default_port, type=int)
@click.option('--workers', default=1, type=int)
@click.option('--debug/--no-debug', default=True)
@click.option('--auto-reload/--no-auto-reload', default=False)
def run(host, port, workers, debug, auto_reload):
    CommandEnv.app.run(host=host, port=port, debug=debug, auto_reload=auto_reload, workers=workers)


@common_cli.command()
@sanic_triggers
def shell():
    user_ns = {}
    for module, elements in CommandEnv.shell_imports:
        module = importlib.import_module(module)
        if elements == '*':
            if hasattr(module, '__all__'):
                for element_name in module.__all__:
                    user_ns[element_name] = getattr(module, element_name)
            else:
                user_ns.update({
                    x[0]: x[1] for x in
                    inspect.getmembers(module, lambda x: not inspect.ismodule(x))
                    if not (x[0].startswith('__') and x[0].endswith('__'))
                })
    for shell_producer in CommandEnv.shell_producers:
        user_ns.update(shell_producer(CommandEnv.app))
    embed(
        header=f'Welcome to {CommandEnv.app.name} shell',
        autoawait=True,
        loop_runner='asyncio',
        user_ns=user_ns
    )
    for shell_cleanup in CommandEnv.shell_cleanups:
        shell_cleanup(user_ns)
    print('Good luck!')
