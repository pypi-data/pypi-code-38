from tcell_agent.features.headers import add_headers
from tcell_agent.instrumentation.decorators import catches_generic_exception


@catches_generic_exception(__name__, "Error inserting headers")
def flask_add_headers(request, response):
    if response.headers.get("Content-Type", None) and \
       response.headers["Content-Type"].startswith("text/html"):
        add_headers(response.headers, request._tcell_context)
