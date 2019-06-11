import copy


__all__ = [ 'Pipeline' ]


class Pipeline_manager:
    def __init__( self, *args, **kw ):
        self.children = []

    def __repr__( self ):
        result = "<class {}( children={} )>".format(
            self.__class__, self.children )
        return result

    def __copy__( self ):
        new_node = self.__class__()
        for child in self.children:
            new_node.append( child )
        return new_node

    def append( self, other ):
        self.children.append( other )

    def __add__( self, other ):
        result = copy.copy( self )
        result.children += other.children
        return result

    def __or__( self, other ):
        me = copy.deepcopy(self)
        if isinstance( other, Pipeline_manager ):
            return me + other

        me.append(other)
        return me

    def to_dict( self ):
        result = {
            'children': [ child for child in self.children ]
        }
        return result

    def run( self, obj ):
        result = obj
        for node in self.children:
            if isinstance( node, type ):
                node = node()
            result = node.process( result )
        return result


class Pipeline_meta( type ):
    def __or__( cls, other ):
        return Pipeline_manager() | cls | other


class Pipeline( metaclass=Pipeline_meta ):
    FUN = None

    def __init__( self, *args, fun=None, **kw ):
        if fun is None:
            self._fun = self.FUN
        else:
            self._fun = fun

    def run( self, obj, *arg, **kw ):
        if not self._fun:
            raise NotImplementedError
        else:
            return self._fun( obj )

    def __or__( self, other ):
        return Pipeline_manager() | self | other
