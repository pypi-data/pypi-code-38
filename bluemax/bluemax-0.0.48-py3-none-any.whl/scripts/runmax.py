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

sys.path.insert(0, os.getcwd())

logger = logging.getLogger(__name__)


def write_pid(path):
    pid = os.getpid()
    with open(path, "w") as f:
        f.write(f"{pid}")


def import_module(name):
    "Íts ok not to have the module but not ok to not have dependants."
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError as ex:
        if name not in str(ex):
            raise


def get_module(name):
    if name is None:
        print("module expected")
    else:
        md = importlib.import_module(name)
        procs = importlib.import_module(f"{name}.procedures")
        if procs:
            if not getattr(procs, "__all__"):
                print(f"expected __all__ in procedures module")
            else:
                options["procedures"] = f"{name}.procedures"
                ext_settings = import_module(f"{name}.settings")
                if ext_settings:
                    options["settings_extend"] = f"{name}.settings:extend"
                ext_urls = import_module(f"{name}.urls")
                if ext_urls:
                    options["urls_extend"] = f"{name}.urls:extend"
                return True
        else:
            print(f"expected procedures in {name}")


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
        write_pid(pid)
        m_server.main()
        os.remove(pid)


@cli.command()
@click.option("-p", "--pid", default=None, help="/path/to/pid/file")
@click.option("-m", "--module", required=True, help="module to remote")
def worker(pid, module):
    from bluemax.work import worker as m_worker

    if pid is None:
        pid = "worker.pid"
    if get_module(module):
        load_config(".env")
        logger.info(
            "hello from worker! mode: %s", "debug" if options.debug else "prod"
        )
        write_pid(pid)
        m_worker.main()
        os.remove(pid)


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
    print(f"gen {name}")
    if os.path.exists(name) and force is False:
        print("that module already exists: ", name)
    else:
        if not os.path.isdir(name):
            os.makedirs(name)
        with open(os.path.join(name, "__init__.py"), "w") as file:
            file.write("")
        with open(os.path.join(name, "settings.py"), "w") as file:
            file.write(
                """''' add your settings here '''
import logging

def extend(settings):
    logging.info('extending settings')
    return settings
"""
            )
        with open(os.path.join(name, "urls.py"), "w") as file:
            file.write(
                """''' add your tornado routes here '''
import logging

def extend(urls):
    logging.info('extending urls')
    return urls
"""
            )
        with open(os.path.join(name, "procedures.py"), "w") as file:
            file.write(
                """''' an example function and exposing it through __all__ '''

__all__=['add']

def add(a:int, b:int)->int:
    return a+b
"""
            )
        with open(os.path.join(name, "services.py"), "w") as file:
            file.write(
                """''' an example service '''
import asyncio
import time
from bluemax import context

async def clock():
    ''' Will broadcast every 5 seconds '''
    while True:
        context.broadcast('time', {'now': time.time()})
        await asyncio.sleep(5)
"""
            )
