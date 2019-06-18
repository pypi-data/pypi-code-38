from stackifyapm.conf import constants
from stackifyapm.utils import compat, get_url_data
from stackifyapm.utils.wsgi import get_environ, get_headers


def get_data_from_request(request, capture_body=False):
    result = {
        "env": dict(get_environ(request.environ)),
        "headers": dict(get_headers(request.environ)),
        "method": request.method,
        "socket": {
            "remote_address": request.environ.get("REMOTE_ADDR"),
            "encrypted": request.is_secure
        },
        "cookies": request.cookies,
    }
    if request.method in constants.HTTP_WITH_BODY:
        body = None
        if request.content_type == "application/x-www-form-urlencoded":
            body = compat.multidict_to_dict(request.form)
        elif request.content_type and request.content_type.startswith("multipart/form-data"):
            body = compat.multidict_to_dict(request.form)
        else:
            try:
                body = request.get_data(as_text=True)
            except Exception:
                pass

        if body is not None:
            result["body"] = body if capture_body else "[REDACTED]"

    result["url"] = get_url_data(request.url)
    return result


def get_data_from_response(response):
    result = {}

    if isinstance(getattr(response, "status_code", None), compat.integer_types):
        result["status_code"] = response.status_code
    elif isinstance(getattr(response, "status", None), compat.integer_types):
        result["status_code"] = response.status
    elif isinstance(getattr(response, "code", None), compat.integer_types):
        result["status_code"] = response.code

    if getattr(response, "headers", None):
        headers = response.headers
        result["headers"] = {key: ";".join(headers.getlist(key)) for key in compat.iterkeys(headers)}

    return result


def get_data_from_exception():
    return {
        'status_code': 500,
    }
