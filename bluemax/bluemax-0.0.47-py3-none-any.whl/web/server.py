from tornado.options import options
from tornado.ioloop import IOLoop
from tornado.web import Application
from ..work.service_manager import ServiceManager
from ..work.manager import Manager
from ..utils.config import extend
from .settings import settings
from .urls import urls
import importlib
import logging

LOGGER = logging.getLogger(__name__)

"""
    Simple Tornado Server
"""


def make_app():
    values = settings()

    if options.settings_extend:
        values = extend(options.settings_extend, values)

    pcs = importlib.import_module(options.procedures)

    if options.redis_url:
        from ..work.redis_manger import RedisManager

        values["manager"] = RedisManager(pcs, options.workers)
    else:
        logging.info("local manager")
        values["manager"] = Manager(pcs, options.workers)

    if options.services:
        services = importlib.import_module(options.services)
        services = ServiceManager(services)
        logging.info("services: %s", services.available_services)
        values["manager"].add_targets(services)
        values["services"] = services

    paths = urls()

    if options.urls_extend:
        paths = extend(options.urls_extend, paths)

    return Application(paths, **values)


def main():
    app = make_app()
    app.listen(options.port)
    LOGGER.info("listening on port %s", options.port)

    ioloop = IOLoop.current()
    try:
        ioloop.start()
    except KeyboardInterrupt:
        logging.info("stopping")
        ioloop.stop()
