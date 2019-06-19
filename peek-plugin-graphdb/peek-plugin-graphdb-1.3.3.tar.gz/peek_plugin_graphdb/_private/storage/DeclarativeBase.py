from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.schema import MetaData
from txhttputil.util.ModuleUtil import filterModules

metadata = MetaData(schema="pl_graphdb")
DeclarativeBase = declarative_base(metadata=metadata)


def loadStorageTuples():

    """ Load Storage Tables

    This method should be called from the "load()" method of the agent, server, worker
    and client entry hook classes.

    This will register the ORM classes as tuples, allowing them to be serialised and
    deserialized by the vortex.

    """
    for mod in filterModules(__package__, __file__):
        if mod.startswith("Declarative"):
            continue
        __import__(mod, locals(), globals())
