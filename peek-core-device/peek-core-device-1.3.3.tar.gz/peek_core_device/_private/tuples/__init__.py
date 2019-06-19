from txhttputil.util.ModuleUtil import filterModules


def loadPrivateTuples():
    """ Load Private Tuples

    In this method, we load the private tuples.
    This registers them so the Vortex can reconstructed them from
    serialised data.

    """
    for mod in filterModules(__name__, __file__):
        __import__(mod, locals(), globals())
