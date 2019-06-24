from bluemax.web.settings import load_config
from tornado.options import options
from ..web import settings
from ..web import urls
import click
import signal
import os
import sys
import importlib
import logging
from .utils import import_module, pid_file, get_module

sys.path.insert(0, os.getcwd())

logger = logging.getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
@click.option("-p", "--pid", default=None, help="/path/to/pid/file")
@click.option("-m", "--module", required=True, help="module to remote")
@click.option("-s", "--services", required=False, help="services module")
def server(pid, module, services):
    from bluemax.web import server as m_server

    if pid is None:
        pid = "server.pid"
    if get_module(module):
        if services:
            options.services = services
        load_config(".env")
        logger.info("mode: %s", "debug" if options.debug else "prod")
        with pid_file(pid):
            m_server.main()


@cli.command()
@click.option("-p", "--pid", default=None, help="/path/to/pid/file")
@click.option("-m", "--module", required=True, help="module to remote")
def worker(pid, module):
    from bluemax.work import worker as m_worker

    if pid is None:
        pid = "worker.pid"
    if get_module(module):
        load_config(".env")
        logger.info("hello from worker! mode: %s", "debug" if options.debug else "prod")
        with pid_file(pid):
            m_worker.main()


@cli.command()
@click.argument("pid_path", type=click.Path(exists=True))
def stop(pid_path):
    try:
        with open(pid_path, "r") as f:
            contents = f.read()
        pid = int(contents)
        os.kill(pid, signal.SIGINT)
        os.remove(pid_path)
    except:
        raise Exception("could not find %s", pid_path)


@cli.command()
@click.argument("name")
@click.option("-f", "--force", is_flag=True, default=False, help="force new project")
def startproject(name, force):
    print(f"depricated. use bluemax project.create {name}")
