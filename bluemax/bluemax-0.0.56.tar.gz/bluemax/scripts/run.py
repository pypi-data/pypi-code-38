""" Task for the running of bluemax """
import os
import logging
import signal
from invoke import task
from tornado.options import options
from bluemax.web.settings import load_config
from bluemax.web import server as m_server
from bluemax.work import worker as m_worker
from bluemax.work.service_manager import ServiceManager
from .utils import get_module, pid_file

LOGGER = logging.getLogger(__name__)


@task(
    default=True,
    help={
        "pid": "/path/to/pid/file",
        "module": "module to remote",
        "services": "services module",
    },
)
def server(_, module, pid="server.pid", services=None):
    """ runs a bluemax server with optional services """
    if get_module(module):
        load_config(".env")
        if services:
            options.services = services
        LOGGER.info("mode: %s", "debug" if options.debug else "prod")
        with pid_file(pid):
            m_server.main()


@task(
    help={
        "pid": "/path/to/pid/file",
        "module": "module to remote",
        "workers": "number of workers",
    }
)
def worker(_, module, pid="worker.pid", workers=None):
    """ runs bluemax worker """
    if get_module(module):
        load_config(".env")
        if workers:
            options.workers = int(workers)
        LOGGER.info(
            "hello from worker! mode: %s", "debug" if options.debug else "prod"
        )
        with pid_file(pid):
            m_worker.main()


@task(help={"pid": "/path/to/pid/file", "module": "module to remote"})
def services(_, pid="services.pid", services=None):
    """ runs bluemax services """
    load_config(".env")
    if services:
        options.services = services
    LOGGER.info("hello from services!")
    with pid_file(pid):
        ServiceManager.run(options.services)


@task(help={"pid": "/path/to/pid/file"})
def stop(_, pid):
    """ kills process in pid file and removes file """
    try:
        with open(pid, "r") as f:
            contents = f.read()
        pid = int(contents)
        os.kill(pid, signal.SIGINT)
        if os.path.isfile(pid):
            os.remove(pid)
    except:
        raise Exception("could not find %s", pid)
