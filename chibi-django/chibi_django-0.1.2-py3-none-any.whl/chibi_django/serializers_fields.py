from rest_framework import serializers
from rest_framework.reverse import reverse


class Impossible_build_url( Exception ):
    pass


class parametrise_hyperlink_identity_field(
        serializers.HyperlinkedIdentityField ):

    lookup_fields = None
    lookup_obj_fields = None
    lookup_request_path = None

    def __init__( self, *args, **kargs ):
        self.lookup_fields = kargs.pop( 'lookup_fields', self.lookup_fields )
        self.lookup_obj_fields = kargs.pop(
            'lookup_obj_fields', self.lookup_obj_fields)
        self.lookup_request_path = kargs.pop(
            'lookup_request_path', self.lookup_request_path )
        super().__init__( *args, **kargs )

    def get_url( self, obj, view_name, request, format ):
        kargs = {}

        try:
            self._build_kargs_from_model( kargs )
            self._build_kargs_from_obj( obj, kargs )
            self._build_kargs_from_request( request, kargs )
        except Impossible_build_url:
            return None

        url = reverse( view_name, kwargs=kargs, request=request,
                       format=format )
        return url

    def _build_kargs_from_model( self, kargs ):
        if self.lookup_fields is not None:
            raise NotImplementedError(
                "the lookup_fields are for get the parameter of the model"
            )

    def _build_kargs_from_obj( self, obj, kargs ):
        if self.lookup_obj_fields is not None:
            if isinstance( obj, dict ):
                for lookup, field in self.lookup_obj_fields:
                    value = obj[ field ]
                    if value is None:
                        msg = (
                            "cannot find the field `{}` in the object"
                        ).format( field )
                        raise Impossible_build_url( msg )
                    kargs[ lookup ] = value
            else:
                for lookup, field in self.lookup_obj_fields:
                    if '.' in field:
                        value = obj
                        for part_field in field.split( '.' ):
                            value = getattr( value, part_field )
                    else:
                        value = getattr( obj, field )
                    if value is None:
                        msg = (
                            "cannot find the field `{}` in the object"
                        ).format( field )
                        raise Impossible_build_url( msg )
                    kargs[ lookup ] = value

    def _build_kargs_from_request( self, request, kargs, ):
        if self.lookup_request_path is not None:
            path_kargs = request.resolver_match.kwargs
            for lookup, field in self.lookup_request_path:
                value = path_kargs[ lookup ]
                if value is None:
                    msg = (
                        "cannot find the field '{}' in the request path"
                    ).format( field )
                    raise Impossible_build_url( msg )
                kargs[ lookup ] = value

    def to_internal_value( self, *args, **kw ):
        result = super().to_internal_value( *args, **kw )
        return result

    def to_representation( self, *args, **kw ):
        result = super().to_representation( *args, **kw )
        return str( result )
