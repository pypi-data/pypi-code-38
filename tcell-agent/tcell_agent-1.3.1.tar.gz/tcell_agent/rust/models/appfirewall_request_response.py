from tcell_agent.rust.models.utils import convert_multidict_params, convert_post_params, \
    convert_single_dict_params
from tcell_agent.utils.strings import ensure_str_or_unicode, stringify

MAX_PATH_PARAM_LENGTH = 200
MAX_COOKIE_LENGTH = 1000


class AppfirewallRequestResponse(dict):
    def __init__(self, appsensor_meta):
        dict.__init__(self)
        # todo: cache these params if/when Patches requests converts them so they're not double converted.  sep. PR
        post_params_list = convert_post_params(appsensor_meta.post_dict, appsensor_meta.files_dict,
                                               appsensor_meta.encoding)

        self["method"] = appsensor_meta.method
        self["status_code"] = appsensor_meta.response_code
        self["route_id"] = appsensor_meta.route_id
        self["path"] = appsensor_meta.path
        # todo: cache these params if/when Patches requests converts them so they're not double converted.  sep. PR
        self["query_params"] = convert_multidict_params(appsensor_meta.get_dict, appsensor_meta.encoding)
        self["post_params"] = post_params_list
        self["content_type"] = appsensor_meta.content_type
        self["request_body"] = ensure_str_or_unicode(appsensor_meta.encoding, appsensor_meta.request_body)
        self["headers"] = convert_multidict_params(appsensor_meta.headers_dict, appsensor_meta.encoding)
        self["cookies"] = convert_single_dict_params(appsensor_meta.cookie_dict, MAX_COOKIE_LENGTH)
        self["path_params"] = convert_single_dict_params(appsensor_meta.path_dict, MAX_PATH_PARAM_LENGTH)
        self["remote_address"] = appsensor_meta.remote_address
        self["full_uri"] = appsensor_meta.location
        self["session_id"] = stringify(appsensor_meta.session_id)
        self["user_id"] = stringify(appsensor_meta.user_id)
        self["user_agent"] = appsensor_meta.user_agent_str
        self["request_bytes_length"] = appsensor_meta.request_content_bytes_len
        self["response_bytes_length"] = appsensor_meta.response_content_bytes_len
        self["sql_exceptions"] = appsensor_meta.sql_exceptions
        self["database_result_sizes"] = appsensor_meta.database_result_sizes

        if appsensor_meta.csrf_reason:
            self["csrf_exception"] = {"exception_payload": stringify(appsensor_meta.csrf_reason)}
