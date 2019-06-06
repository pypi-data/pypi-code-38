""" 
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
"""

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.schema import MetaData

metadata = MetaData(schema="core_user")
DeclarativeBase = declarative_base(metadata=metadata)

from txhttputil.util.ModuleUtil import filterModules


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
