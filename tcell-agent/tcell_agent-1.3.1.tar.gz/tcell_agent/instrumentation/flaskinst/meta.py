from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.instrumentation.better_ip_address import better_ip_address
from tcell_agent.instrumentation.context import TCellInstrumentationContext
from tcell_agent.instrumentation.decorators import catches_generic_exception
from tcell_agent.instrumentation.headers_cleaner import headers_from_environ
from tcell_agent.features.request_timing import start_timer
from tcell_agent.utils.multi_value_dict import MultiValueDict

MAXIMUM_BODY_SIZE = 2000000


@catches_generic_exception(__name__, "Error initializing Flask context")
def initialize_tcell_context(request):
    from tcell_agent.instrumentation.flaskinst.routes import calculate_route_id

    request._tcell_context = TCellInstrumentationContext()

    request._tcell_context.method = request.environ.get("REQUEST_METHOD")
    if request.url_rule is not None:
        request._tcell_context.route_id = calculate_route_id(request._tcell_context.method,
                                                             request.url_rule.rule)
    request._tcell_context.user_agent = request.environ.get("HTTP_USER_AGENT")
    request._tcell_context.remote_address = better_ip_address(request.environ)
    request._tcell_context.uri = request.url
    request._tcell_context.path = request.path
    request._tcell_context.fullpath = request.full_path

    start_timer(request)

    # run this here to ensure variables required by process_response are set
    # before calling letting the request processing continue in case
    # an exception is raised
    request._appsensor_meta = AppSensorMeta()
    request._ip_blocking_triggered = False


def parse_body(request):
    if (not request.content_length) or request.content_length >= MAXIMUM_BODY_SIZE:
        return [request.form, None]

    request_body = request.get_data()
    if request.mimetype and request.mimetype.startswith('application/json'):
        return [{}, request_body]
    return [request.form, request_body]


@catches_generic_exception(__name__, "Error initializing Flask meta")
def create_meta(request):
    appsensor_meta = AppSensorMeta()
    request._appsensor_meta = appsensor_meta
    appsensor_meta.remote_address = request._tcell_context.remote_address
    appsensor_meta.method = request.environ.get("REQUEST_METHOD")
    appsensor_meta.user_agent_str = request._tcell_context.user_agent
    appsensor_meta.location = request.url
    appsensor_meta.path = request.path
    appsensor_meta.route_id = request._tcell_context.route_id

    appsensor_meta.get_dict = request.args
    appsensor_meta.cookie_dict = request.cookies
    appsensor_meta.headers_dict = headers_from_environ(request.environ)
    appsensor_meta.request_content_bytes_len = request.content_length or 0

    post_dict, raw_body = parse_body(request)
    appsensor_meta.post_dict = post_dict
    appsensor_meta.content_type = request.mimetype
    appsensor_meta.request_body = raw_body
    appsensor_meta.path_dict = request.view_args

    if request.files:
        appsensor_meta.files_dict = MultiValueDict()
        for param_name in request.files.keys():
            file_obj_list = request.files.getlist(param_name)
            for file_obj in file_obj_list:
                appsensor_meta.files_dict.add(param_name, file_obj.filename)


def update_meta_with_response(appsensor_meta, response, response_code):
    appsensor_meta.response_code = response_code
    if response is not None:
        appsensor_meta.response_content_bytes_len = response.content_length or 0
