from collections import defaultdict


class Chibi_atlas( dict ):
    """
    Clase para crear dicionarios para que sus keys sean leibles como
    atributos de classes
    """

    def __init__( self, *args, **kw ):
        for arg in args:
            if isinstance( arg, dict ):
                for k, v in arg.items():
                    self[ k ] = v
        for k, v in kw.items():
            self[ k ] = v

        # super().__init__( *args, **kw )

    def __getattr__( self, name ):
        try:
            return self[ name ]
        except KeyError as e:
            try:
                return super().__getattribute__( name )
            except AttributeError as e:
                raise

    def __setattr__( self, name, value ):
        self[ name ] = _wrap( value )

    def __setitem__( self, name, value ):
        super().__setitem__( name, _wrap( value ) )


class Chibi_atlas_ignore_case( Chibi_atlas ):
    """
    clase que crea chibi atlas que son case insensitive
    """
    def __init__( self, *args, **kw ):
        args_clean = []
        for a in args:
            if isinstance( a, dict ) or hasattr( a, 'items' ):
                args_clean.append( { k.lower(): v for k, v in a.items() } )
        kw = { k.lower(): v for k, v in kw.items() }
        super().__init__( *args_clean, **kw )

    def __getattr__( self, name ):
        name = name.lower()
        return super().__getattr__( name )

    def __getitem__( self, key ):
        key = key.lower()
        return super().__getitem__( key )

    def __setattr__( self, name, value ):
        name = name.lower()
        return super().__setattr__( name, value )

    def __setitem__( self, key, value ):
        key = key.lower()
        return super().__setitem__( key, value )


class Chibi_atlas_default( defaultdict, Chibi_atlas ):
    """
    chibi atlas que emula `py:class:collections.defaultdict`
    """
    pass


def _wrap( val, klass=None ):
    if type( val ) == dict:
        if klass is None:
            return Chibi_atlas( val )
        else:
            return klass( val )
    return val
