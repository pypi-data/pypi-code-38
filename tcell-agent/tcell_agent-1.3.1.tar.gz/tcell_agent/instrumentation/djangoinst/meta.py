from tcell_agent.global_state import get_default_charset
from tcell_agent.instrumentation.better_ip_address import better_ip_address, tcell_get_host
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.djangoinst.models import \
    TCellDjangoRequest

MAXIMUM_BODY_SIZE = 20000


@catches_generic_exception(__name__, "Error setting request context information")
def initialize_tcell_context(request):
    request._tcell_context = TCellInstrumentationContext()
    request._tcell_context.referrer = request.META.get("HTTP_REFERER")
    request._tcell_context.user_agent = request.META.get("HTTP_USER_AGENT")
    request._tcell_context.remote_address = better_ip_address(request.META)
    request._tcell_context.method = request.method
    request._tcell_context.path = request.path
    request._tcell_context.fullpath = tcell_get_full_path(request)
    request._tcell_context.uri = tcell_build_absolute_uri(request, request._tcell_context.fullpath)
    request._tcell_context.route_id = None


def get_appsensor_meta(request):
    appsensor_meta = request._tcell_context.appsensor_meta
    appsensor_meta.remote_address = request._tcell_context.remote_address
    appsensor_meta.method = request._tcell_context.method
    appsensor_meta.user_agent_str = request._tcell_context.user_agent
    appsensor_meta.location = request._tcell_context.uri
    appsensor_meta.path = request._tcell_context.path
    appsensor_meta.route_id = request._tcell_context.route_id
    appsensor_meta.session_id = request._tcell_context.session_id
    appsensor_meta.user_id = request._tcell_context.user_id
    appsensor_meta.encoding = request.encoding or get_default_charset()

    return appsensor_meta


def set_response(meta, django_response_class, response):
    if meta.response_processed:
        return
    meta.response_processed = True

    response_content_len = 0
    try:
        if isinstance(response, django_response_class):
            response_content_len = len(response.content)
    except Exception:
        pass

    meta.response_content_bytes_len = response_content_len
    meta.response_code = response.status_code


def parse_body(tcell_request):
    if (not tcell_request.content_length) or tcell_request.content_length >= MAXIMUM_BODY_SIZE:
        return [tcell_request.request.POST, None]

    request_body = tcell_request.request.body
    if tcell_request.is_json():
        return [{}, request_body]
    return [tcell_request.request.POST, request_body]


def set_request(meta, request):
    if meta.request_processed:
        return
    meta.request_processed = True

    django_request = TCellDjangoRequest(request)
    post_dict, raw_body = parse_body(django_request)
    meta.get_dict = request.GET
    meta.cookie_dict = request.COOKIES
    meta.headers_dict = django_request.normalized_headers
    meta.request_body = raw_body
    meta.content_type = django_request.content_type
    meta.request_content_bytes_len = django_request.content_length
    meta.files_dict = django_request.filenames_dict
    meta.post_dict = post_dict


def tcell_build_absolute_uri(request, full_path=None):
    if not full_path:
        full_path = tcell_get_full_path(request)
    return request.scheme + '://' + tcell_get_host(request) + full_path


# see: https://tcellio.atlassian.net/wiki/spaces/EN/pages/642023425/Microbenchmarking+results+for+django
def tcell_get_full_path(request):
    query_string = request.META.get('QUERY_STRING', '')
    if query_string == '':
        return request.path
    return request.path + '?' + query_string
