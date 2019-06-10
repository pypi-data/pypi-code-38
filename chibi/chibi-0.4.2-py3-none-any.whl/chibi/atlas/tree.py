from . import Chibi_atlas_default
import copy


def _default_factory_tree_attr():
    return Chibi_tree()


def flat( tree, result=None ):
    if result is None:
        result = {}
    for k, v in tree.items():
        result[ k ] = v
        flat( v, result=result )
    return result


class Chibi_tree( Chibi_atlas_default ):
    def __init__( self, default_factory=None ):
        if default_factory is None:
            default_factory = _default_factory_tree_attr
        super().__init__( default_factory )

    def __repr__( self ):
        return repr( dict( self ) )

    def to_dict( self ):
        result = {}
        for k, v in self.items():
            result[k] = v.to_dict()
        return result

    def find( self, obj, recursive=True ):
        if obj in self:
            return self[ obj ]
        if recursive:
            result = None
            for v in self.values():
                result = v.find( obj, recursive=recursive )
                if result is not None:
                    return result

    def remove( self, obj, recursive=True ):
        if obj in self:
            del self[ obj ]
        if recursive:
            for v in self.values():
                v.remove( obj, recursive=recursive )

    def flat( self ):
        return flat( self )

    def dependencies_batches( self ):
        results = []
        flat_tree = flat( copy.copy( self ) )
        while flat_tree:
            current_batch = [ k for k, v in flat_tree.items() if not v ]
            if not current_batch:
                raise NotImplementedError
            for dep in current_batch:
                del flat_tree[ dep ]
                for t in flat_tree.values():
                    t.remove( dep )
            results.append( current_batch )
        return results

    def __copy__( self ):
        result = type( self )()
        for k, v in self.items():
            result[k] = copy.copy( v )
        return result


def build_tree( *objs, key=None, children=None, results=None ):
    if not key or not callable( key ):
        raise NotImplementedError
    if not children or not callable( children ):
        raise NotImplementedError

    if not results:
        results = Chibi_tree()

    for obj in objs:
        key_value = key( obj )
        children_value = children( obj )
        position_key = results.find( key_value )
        if position_key is None:
            position_key = results[ key_value ]
        for child in children_value:
            position_key[ key( child ) ]
        build_tree(
            *children_value, key=key, children=children,
            results=position_key )
    return results
