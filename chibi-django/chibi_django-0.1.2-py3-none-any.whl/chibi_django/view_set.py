from django.utils.translation import gettext as _
from chibi_django import mixins
from rest_framework import viewsets


class Multi_serializer_viewset( viewsets.GenericViewSet ):
    def get_serializer( self, *args, serializer_name='default', **kw ):
        serializer_class = self.get_serializer_class( serializer_name )
        kw[ 'context' ] = self.get_serializer_context()
        return serializer_class( *args, **kw )

    def get_serializer_class( self, serializer_name='default' ):
        serializers = super().get_serializer_class()
        if not isinstance( serializers, dict ):
            return serializers
        try:
            serializer_class = serializers[ serializer_name ]
        except KeyError:
            try:
                serializer_class = serializers[ 'default' ]
            except KeyError:
                raise KeyError(
                    _( 'The serializer %s is not defined' ) % serializer_name )
        return serializer_class


class Nested_view_set( Multi_serializer_viewset ):
    def create_build_data( self, data ):
        return data

    def update_build_data( self, data ):
        return data


class Model_viewset(
        mixins.Create_model, mixins.Retrieve_model, mixins.Update_model,
        mixins.Destroy_model, mixins.List_model, Nested_view_set ):
    pass


class Read_only_model_viewset(
        mixins.Retrieve_model, mixins.List_model, Nested_view_set ):
    pass
