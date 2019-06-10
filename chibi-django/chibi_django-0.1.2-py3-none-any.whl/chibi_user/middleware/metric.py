from datetime import datetime
from django.urls import resolve
from rest_framework import status
import logging


logger = logging.getLogger( 'chibi_user.middleware' )


class User_for_api( object ):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request( request )
        response = self.get_response(request)
        return response

    def process_request( self, request ):
        request._start_time = datetime.utcnow()

    def process_template_response( self, request, response ):
        request._end_time = datetime.utcnow()
        request._total_time = request._start_time - request._end_time

        metrics = {
            'start_time': request._start_time,
            'end_time': request._end_time,
            'total_time': request._total_time,
        }
        self.set_user_to_metrics( request, metrics )
        self.is_an_error_from_user( request, response, metrics )

        logger.info( "metric for user", extra=metrics )

        return response

    def set_user_to_metrics( self, request, metrics ):
        if hasattr( request, 'user' ):
            metrics[ 'user_pk' ] = request.user.pk
        metrics[ 'is_anonymous' ] = 'user_pk' not in metrics

    def is_an_error_from_user( self, request, response, metrics ):
        url_name = self.get_url_name_from_response( request )
        if ( url_name and 'detail' in url_name ):
            metrics[ 'user_error' ] = \
                response.status_code == status.HTTP_404_NOT_FOUND
        else:
            metrics[ 'user_error' ] = False

    def get_url_name_from_response( self, request ):
        url_resolve = resolve( request.get_full_path() )
        return url_resolve.url_name
