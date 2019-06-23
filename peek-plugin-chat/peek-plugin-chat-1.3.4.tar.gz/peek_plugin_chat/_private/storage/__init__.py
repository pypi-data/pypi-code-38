from txhttputil.util.ModuleUtil import filterModules


def loadStorageTuples():
    """ Load Storage Tables

    This method should be called from the "load()" method of the agent, server, worker
    and client entry hook classes.

    This will register the ORM classes as tuples, allowing them to be serialised and
    deserialized by the vortex.

    """

    for mod in filterModules(__package__, __file__):
        __import__(mod, locals(), globals())
