from txhttputil.util.ModuleUtil import filterModules


def loadPublicTuples():
    for mod in filterModules(__name__, __file__):
        __import__(mod, locals(), globals())

    from . import login
    from . import import_

    login.loadTuples()
    import_.loadTuples()
