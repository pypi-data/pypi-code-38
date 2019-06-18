from django.http import HttpResponse
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.features.headers import add_headers


@catches_generic_exception(__name__, "Error inserting headers")
def django_add_headers(request, response):
    if isinstance(response, HttpResponse) and response.has_header("Content-Type"):
        if response["Content-Type"] and response["Content-Type"].startswith("text/html"):
            add_headers(response, request._tcell_context)
