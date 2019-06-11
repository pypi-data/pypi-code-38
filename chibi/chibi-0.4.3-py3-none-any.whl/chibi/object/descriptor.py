import datetime

from chibi.atlas import Chibi_atlas_default
from chibi.atlas.tree import Chibi_tree


class Descriptor:
    """
    describe a parameter of class
    """
    default = None

    def __init__( self, name=None, required=False, default=None ):
        self.name = name
        self.required = required
        self.default = default if default is not None else self.default

    def __get__( self, instance, cls ):
        return instance.__dict__.get( self.name, self.default )

    def __set__( self, instance, value ):
        try:
            instance.__dict__[self.name] = value
        except Exception as e:
            import pdb
            pdb.set_trace()
            pass

    def __repr__( self ):
        return "descriptor.{}".format( type( self ).__name__ )


class Any( Descriptor ):
    def __repr__( self ):
        return "any.{}".format( type( self ).__name__ )


class Kind( Descriptor ):
    """
    descriptor with assert of type
    """
    kind = object

    def __set__( self, instance, value ):
        if not isinstance( value, self.kind ):
            raise TypeError( "Expected {}".format(self.kind ) )
        super().__set__( instance, value )


class Integer( Kind ):
    kind = int
    default = 0


class Float( Kind ):
    kind = float
    default = 0.0


class String( Kind ):
    kind = str
    default = ''


class DateTime( Kind ):
    kind = datetime.datetime
    default = datetime.datetime.now()


class Date( Kind ):
    kind = datetime.date
    default = datetime.datetime.now().date()


class List( list, Descriptor ):
    def __set__( self, instance, value ):
        if value is None:
            value = list()
        super().__set__( instance, list( value ))


class Set( set, Descriptor ):
    def __set__( self, instance, value ):
        if value is None:
            value = set()
        super().__set__( instance, set( value ))


class List_kind_strict( List ):
    def __init__( self, *args, kind=None, **kw ):
        super().__init__( *args, **kw )
        self._kind = kind

    def __set__( self, instance, value ):
        for pos, elem in enumerate( value ):
            if not isinstance( elem, self._kind ):
                raise TypeError(
                    "in the position {}, expected {}".format(
                        pos, self._kind ) )

        super().__set__( instance, value )

    def append( self, item ):
        if self._kind and not isinstance( item, self._kind ):
            raise TypeError("Expected {}".format( self.kind ) )
        super().append( item )


class Dict( dict, Descriptor ):
    def __set__( self, instance, value ):
        if value is None:
            super().__set__( instance, value )
        else:
            super().__set__( instance, dict( value ))


class Dict_defaults( Chibi_atlas_default, Descriptor ):
    default = None

    def __init__( self, *args, default=None, **kw ):
        super().__init__( *args, **kw )
        if default is None:
            default = self.default
        if not callable( default ):
            default_item = default

            def default_factory():
                return default_item
        else:
            default_factory = default
        self._default_factory = default_factory

    def __set__( self, instance, value ):
        """
        si es None el valor se vuelve a inicializar el dicionario con su
        fabrica por default
        """
        if value is None:
            new_dict = Chibi_atlas_default( self._default_factory )
            super().__set__( instance, new_dict )
        elif not isinstance( value, Chibi_atlas_default ):
            raise TypeError(
                "Expected type of {}".format( Chibi_atlas_default ) )
        else:
            super().__set__( instance, value )


class Tree_simple( Chibi_tree, Descriptor ):
    default = None

    def __init__( self, *args, default_factory=None, **kw ):
        super().__init__( *args, **kw )
        self._default_factory = default_factory

    def __set__( self, instance, value ):
        if value is None:
            new_tree = Chibi_tree( self._default_factory )
            super().__set__( instance, new_tree )
        elif not isinstance( value, Chibi_tree ):
            raise TypeError("Expected type of {}".format( Chibi_tree ) )
        else:
            super().__set__( instance, value )


class Choice( Descriptor ):
    choice = None

    def __init__( self, *args, choice, **kargs ):
        super().__init__( *args, **kargs )
        self.choice = choice

    def __set__( self, instance, value ):
        if value in self.choice:
            super().__set__( instance, value )
        else:
            raise TypeError( (
                "Expected value of ( {} ) but received {}"
            ).format( self.choice, value ) )


class String_choice( Choice, String ):
    pass
