import importlib


def import_( module, cls=None ):
    if cls is None:
        split = module.split( '.' )
        cls = split[-1]
        module = ".".join( split[:-1] )
        return import_( module=module, cls=cls )
    module = importlib.import_module( module )
    return getattr( module, cls )


def export( cls ):
    if isinstance( cls, type ):
        return "{module}.{cls}".format(
            module=cls.__module__, cls=cls.__name__ )
    else:
        return export( cls=cls.__class__ )
