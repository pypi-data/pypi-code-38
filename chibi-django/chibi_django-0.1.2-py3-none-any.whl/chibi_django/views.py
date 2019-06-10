from django import http
from django.utils.translation import ugettext as _
from chibi_django.exceptions import Http_not_found, Http_internal_server_error
from rest_framework.renderers import JSONRenderer


def page_not_found(request, exception, template_name='404.html'):
    """
    404 error handler.
    Templates: :template:`404.html`
    Context: None
    """
    # format = request.META.get( 'CONTENT_TYPE', 'application/json' )
    base_exception = Http_not_found( _( "The resource does not exist." ) )
    result = base_exception.context
    result = JSONRenderer().render( result )

    return http.HttpResponseNotFound( result )


def server_error(request, template_name='500.html'):
    """
    500 error handler.
    Templates: :template:`500.html`
    Context: None
    """
    # format = request.META.get( 'CONTENT_TYPE', 'application/json' )
    base_exception = Http_internal_server_error()
    result = base_exception.context
    result = JSONRenderer().render( result )

    return http.HttpResponseServerError( result )
