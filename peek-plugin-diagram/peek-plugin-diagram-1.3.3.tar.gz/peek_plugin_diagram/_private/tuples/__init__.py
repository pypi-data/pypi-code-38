from txhttputil.util.ModuleUtil import filterModules


def loadPrivateTuples():
    """ Load Private Tuples

    In this method, we load the private tuples.
    This registers them so the Vortex can reconstructed them from
    serialised data.

    """
    for mod in filterModules(__name__, __file__):
        __import__(mod, locals(), globals())

    from peek_plugin_diagram._private.tuples import grid
    for mod in filterModules(grid.__name__, grid.__file__):
        __import__(mod, locals(), globals())

    from peek_plugin_diagram._private.tuples import branch
    for mod in filterModules(branch.__name__, branch.__file__):
        __import__(mod, locals(), globals())

    from peek_plugin_diagram._private.tuples import location_index
    for mod in filterModules(location_index.__name__, location_index.__file__):
        __import__(mod, locals(), globals())
