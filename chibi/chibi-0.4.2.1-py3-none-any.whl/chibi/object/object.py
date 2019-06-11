from collections import OrderedDict

from .descriptor import Descriptor


class Chibi_object_meta_base():
    _fields = {}


class Chibi_object_meta( type ):
    @classmethod
    def __prepare__( cls, name, bases ):
        return OrderedDict()

    def __new__( cls, clsname, bases, clsdict ):

        fields = [
            k for k, v in clsdict.items() if isinstance( v, Descriptor ) ]
        for name in fields:
            clsdict[name].name = name

        attr_meta = clsdict.pop( 'Meta', None )
        clsobj = super().__new__( cls, clsname, bases, clsdict )

        if attr_meta is None:
            if hasattr( clsobj, '_meta' ):
                attr_meta = clsobj._meta
            else:
                attr_meta = Chibi_object_meta_base()
            clsobj.Meta = attr_meta
        else:
            clsobj.Meta = attr_meta
        meta_base = getattr( clsobj, 'Meta', None )
        clsobj._meta = Chibi_object_meta_base()
        clsobj._meta.__dict__.update( meta_base.__dict__.copy() )
        attr_meta = clsobj._meta

        if hasattr( attr_meta, '_fields' ):
            attr_meta._fields = {}
        attr_meta._fields.update( meta_base._fields )
        attr_meta._fields.update(
            { name: clsdict[ name ] for name in fields } )
        return clsobj


class Chibi_object( metaclass=Chibi_object_meta ):
    """
    Notes
    -----
    la clase de Meta se guarda como una clase interna llamada _meta en la
        instancia
    atributos de la clase _meta
    ---------------------------
        _fields: este dicionario guarda el nombre y la instancia del campo
    """
    class Meta( Chibi_object_meta_base ):
        pass

    def __init__( self, *args, **kargs ):
        for name, field in self._meta._fields.items():
            setattr( self, name, kargs.get( name, field.default ) )


class Chibi_object_iterate_field( Chibi_object ):
    class Meta( Chibi_object.Meta ):
        iterate_field = None

    def __init__( self, *args, **kargs ):
        if not hasattr( self, self.Meta.iterate_field ):
            AttributeError(
                "No found attribute found %s" % self.Meta.iterate_field )
        super().__init__(*args, **kargs )

    def __iter__( self ):
        return iter( getattr( self, self.Meta.iterate_field ) )


__all__ = [Chibi_object, Chibi_object_iterate_field]
