from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings


class Location_header:
    def get_success_headers( self, data ):
        try:
            return { 'Location': data[ api_settings.URL_FIELD_NAME ] }
        except ( TypeError, KeyError ):
            return {}


class Create_model( Location_header ):
    def create( self, request, *args, **kw ):
        serializer = self.get_serializer(
            data=self.create_build_data( request.data ),
            serializer_name='create' )
        serializer.is_valid( raise_exception=True )
        self.perform_create( serializer )
        headers = self.get_success_headers( serializer.data )
        return Response( status=status.HTTP_201_CREATED, headers=headers )

    def perform_create( self, serializer ):
        serializer.save()


class List_model:
    def list( self, request, *args, **kw ):
        queryset = self.filter_queryset( self.get_queryset() )

        page = self.paginate_queryset( queryset )
        if page is not None:
            serializer = self.get_serializer( page, many=True,
                                              serializer_name='list' )
            return self.get_paginated_response( serializer.data )

        serializer = self.get_serializer( queryset, many=True,
                                          serializer_name='list' )
        return Response( serializer.data )


class Retrieve_model:
    def retrieve( self, request, *args, **kw ):
        instance = self.get_object()
        serializer = self.get_serializer( instance,
                                          serializer_name='retrieve' )
        return Response( serializer.data )


class Update_model:
    def update( self, request, *args, **kw ):
        partial = kw.pop( 'partial', False )
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=self.update_build_data( request.data ),
            partial=partial, serializer_name='update' )

        serializer.is_valid( raise_exception=True )
        self.perform_update( serializer )
        return Response( status=status.HTTP_204_NO_CONTENT )
        # return Response( serializer.data )

    def perform_update( self, serializer ):
        serializer.save()

    def partial_update( self, request, *args, **kwargs ):
        kwargs['partial'] = True
        return self.update( request, *args, **kwargs )


class Destroy_model:
    def destroy( self, request, *args, **kw ):
        instance = self.get_object()
        self.perform_destroy( instance )
        return Response( status=status.HTTP_204_NO_CONTENT )

    def perform_destroy( self, instance ):
        instance.delete()
