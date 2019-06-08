"""
    This is a wrapper from invoke
"""
from invoke import Program, Collection
import logging
from . import database
from . import project
from .run import server, worker, services, stop

logging.basicConfig(level=logging.INFO)

ns = Collection()
ns.add_collection(Collection.from_module(database))
ns.add_collection(Collection.from_module(project))
ns.add_task(server)
ns.add_task(services)
ns.add_task(worker)
ns.add_task(stop)

program = Program(version="0.0.49", namespace=ns)
