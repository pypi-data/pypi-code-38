import html
import json
import urllib.parse
from functools import partial

from .validations import expect_in, expect_type, expect_len, expect_len_range, expect_only_one_of, set_dict_data_only_once
from .shared_exceptions import StatusMessageException


class EndpointRouterBadDefinition(StatusMessageException):
    def __init__(self, message, status_code=None, additional_information=None):
        StatusMessageException.__init__(self, message, status_code, additional_information)


class EndpointRouterBadInput(StatusMessageException):
    def __init__(self, message, status_code=None, additional_information=None):
        StatusMessageException.__init__(self, message, status_code, additional_information)


_default_html_error_page = """<!DOCTYPE html>
<html>
<head>
<title>{error_title}</title>
</head>
<body>
{error_message}
</body>
</html>
"""


def html_template_replace_safe(template, identifiers, values):
    for i, v in zip(identifiers, values):
        template = template.replace(i, html.escape(v))

    return template


def default_render_html_error(error_title, error_message=None):
    if not error_message:
        error_message = error_title

    return html_template_replace_safe(_default_html_error_page,
                                      ('{error_title}', '{error_message}'),
                                      (error_title, error_message))


def _method_not_allowed_endpoint(out_format, allowed):
    return {
        'in_format': 'plain',
        'out_format': out_format,
        'status': 405,
        'allowed': allowed,
    }


def run_endpoint(func, request, out_format):
    response = func(request)

    response_data = response
    status_code = 200
    headers = []

    if isinstance(response, tuple):
        expect_len_range(response, 1, 3, 'response return values')

        response_data = response[0]

        if len(response) > 1:
            status_code = response[1]
            expect_type(status_code, int, 'response status code')

        if len(response) > 2:
            headers = response[2]
            expect_type(headers, (dict, list), 'response headers')

            if isinstance(headers, dict):
                headers = [(k, v) for k, v in headers.items()]

            for header_pair in headers:
                expect_type(header_pair, tuple, 'header key/value pair')
                expect_len(header_pair, 2, 'header key/value pair')
                expect_type(header_pair[0], str, 'header key')

    headers = add_content_type_header(headers, out_format)

    if out_format == 'json':
        response_data = json.dumps(response_data)
    else:
        # raw, plain, html, js
        expect_type(response_data, str, 'response data')

    return response_data, status_code, headers


def add_content_type_header(headers, format):
    for key, value in headers:
        if key == 'Content-Type':
            return headers

    if format == 'html':
        headers.append(('Content-Type', 'text/html; charset=utf-8'))
    elif format == 'js':
        headers.append(('Content-Type', 'application/javascript; charset=utf-8'))
    elif format == 'json':
        headers.append(('Content-Type', 'application/json; charset=utf-8'))
    else:
        # raw / plain
        headers.append(('Content-Type', 'text/plain; charset=utf-8'))

    return headers


def add_content_length_header(headers, length):
    for key, value in headers:
        if key == 'Content-Length':
            return headers

    headers.append(('Content-Length', str(length)))

    return headers


_code_status_lookup = {
    # TODO: Redirects
    200: '200 OK',
    201: '201 Created',
    301: '301 Moved Permanently',
    302: '302 Found',
    400: '400 Bad Request',
    401: '401 Unauthorized',
    404: '404 Not Found',
    405: '405 Method Not Allowed',
    500: '500 Internal Server Error',
}


def code_to_status(code):
    return _code_status_lookup.get(code, '500 Internal Server Error')


def parse_request_body(environ, in_format):
    try:
        body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (TypeError, ValueError):
        body_size = 0

    if body_size <= 0:
        return None

    body = environ['wsgi.input'].read(body_size)

    if in_format == 'json':
        try:
            return json.loads(body)
        except (TypeError, ValueError) as e:
            raise EndpointRouterBadInput(f'Failed to parse JSON input: {e}')

    if in_format == 'form':
        try:
            return urllib.parse.parse_qs(body)
        except (TypeError, ValueError) as e:
            raise EndpointRouterBadInput(f'Failed to parse form data input: {e}')

    # raw and plain
    return body


def serve_static_file(filename, request):
    with open(filename) as f:
        return f.read()


def serve_static_data(data, request):
    return data


class EndpointRouter():
    """WSGI router to send requests to the appropriate registered endpoint"""
    def __init__(self, default_in_format='plain', default_out_format='plain', default_html_error=default_render_html_error):
        # First check for any exact matches, then prefix matches
        self._endpoints_exact = {}

        # Only needed if exact matches overlap with prefix matches,
        # and all exact matches should be disallowed for non-declared methods,
        # but the prefix methods are allowed.
        self._endpoints_exact_disallow = {}

        # Any URI that startswith the entries here will be matched
        # Use '/' for catch-all
        self._endpoints_prefix = {}

        self.server_default_in_format = default_in_format
        self.server_default_out_format = default_out_format
        self.server_render_html_error = default_html_error

    def _register_endpoint_internal(self, type_str, type_dict, location, method, endpoint_def):
        expect_type(location, str, f'{type_str} uri')
        set_dict_data_only_once(type_dict, [location, method], endpoint_def,
                                f'{type_str} uri definition for {location} for method {method}')

    def register_endpoint(self, func=None, static_file=None, static_data=None,
                          in_format=None, out_format=None, exact=None, prefix=None, method=None, disallow_other_methods=None):
        if not func and not static_file and not static_data:
            raise EndpointRouterBadDefinition('Must define func for register_endpoint')

        expect_only_one_of([func, static_file, static_data], ('func', 'static_file', 'static_data'))

        if static_file:
            func = partial(serve_static_file, static_file)

        if static_data:
            func = partial(serve_static_data, static_data)

        method = method.upper().strip()
        expect_in(method, ('GET', 'POST', 'PUT', 'PATCH', 'DELETE'), 'method')

        expect_only_one_of([prefix, exact], ['prefix', 'exact'])

        if not in_format:
            in_format = self.server_default_in_format
        if not out_format:
            out_format = self.server_default_out_format

        in_format = in_format.lower().strip()
        out_format = out_format.lower().strip()

        expect_in(in_format, ('raw', 'plain', 'form', 'json'), 'in_format')
        expect_in(out_format, ('raw', 'plain', 'html', 'js', 'json'), 'out_format')

        endpoint_def = {
            'in_format': in_format,
            'out_format': out_format,
            'func': func,
        }

        if exact:
            location = exact
            type_str = 'exact'
            type_dict = self._endpoints_exact

        if prefix:
            location = prefix
            type_str = 'prefix'
            type_dict = self._endpoints_prefix

        if not isinstance(location, (list, tuple)):
            location = [location]

        for loc in location:
            self._register_endpoint_internal(type_str, type_dict, loc, method, endpoint_def)

        if disallow_other_methods:
            if not exact:
                raise EndpointRouterBadDefinition('Can only use disallow_other_methods with exact match endpoints, '
                                                  'as prefix matches are auto-disallowed')
            # The last format specified is the format returned for 405s (if inconsistent for the same endpoint - not recommended!)
            for loc in location:
                self._endpoints_exact_disallow[loc] = out_format

    # TODO: Convenience register_class function (auto-detects get/post/etc. class methods)

    def generate_error_response(self, format, error_title, error_message=None):
        # Always escape HTML to prevent XSS attacks, as all types can be rendered under some circumstances
        if format in ('html', 'js'):
            return self.server_render_html_error(error_title, error_message), [('Content-Type', 'text/html; charset=utf-8')]
        if format == 'json':
            return json.dumps({'message': html.escape(error_message or error_title)}), [('Content-Type', 'application/json; charset=utf-8')]
        # raw / plain
        return html.escape(error_message or error_title), [('Content-Type', 'text/plain; charset=utf-8')]

    def find_endpoint(self, uri_path, method):
        allowed = ['GET']
        other_method_matched = False
        other_out_format = self.server_default_out_format

        if uri_path in self._endpoints_exact:
            test_exact = self._endpoints_exact[uri_path]
            if method in test_exact:
                return test_exact[method]
            allowed = list(test_exact.keys())
            other_method_matched = True
            other_out_format = list(test_exact.values())[0].get('out_format', other_out_format)

        if uri_path in self._endpoints_exact_disallow:
            return _method_not_allowed_endpoint(self._endpoints_exact_disallow[uri_path], allowed)

        for prefix, test_prefix in self._endpoints_prefix.items():
            if uri_path.startswith(prefix):
                if method in test_prefix:
                    return test_prefix[method]
                if not other_method_matched:
                    # If multiple match, then the first match determines the allowed methods
                    allowed = list(test_prefix.keys())
                    other_method_matched = True
                    other_out_format = list(test_prefix.values())[0].get('out_format', other_out_format)

        if other_method_matched:
            return _method_not_allowed_endpoint(other_out_format, allowed)

        return {'status': 404}

    # WSGI Entrypoint
    def application(self, environ, start_response):
        # Default in case of unexpected errors
        status_code = 500
        error = True
        error_message = None
        additional_headers = []

        parsed_uri = urllib.parse.urlparse(environ['REQUEST_URI'])
        uri_path = urllib.parse.unquote(parsed_uri[2])

        method = environ['REQUEST_METHOD'].upper()

        endpoint = self.find_endpoint(uri_path, method)

        in_format = self.server_default_in_format
        if endpoint and endpoint.get('in_format'):
            in_format = endpoint['in_format']

        out_format = self.server_default_out_format
        if endpoint and endpoint.get('out_format'):
            out_format = endpoint['out_format']

        try:
            if not endpoint or endpoint.get('status') == 404:
                status_code = 404
            elif endpoint.get('status') == 401:
                status_code = 401
            elif endpoint.get('status') == 405:
                status_code = 405
                if endpoint.get('allowed'):
                    additional_headers.append(('Allow', ', '.join(endpoint['allowed'])))
            else:
                if not endpoint.get('func'):
                    raise RuntimeError('Internal Error: No func defined for non-error/redirect endpoint')

                func = endpoint['func']

                if in_format == 'raw':
                    return func(environ, start_response)

                request = {
                    'uri': {
                        'path': uri_path,
                        'params': urllib.parse.unquote(parsed_uri[3]),
                        'query': urllib.parse.unquote(parsed_uri[4]),
                        'fragment': urllib.parse.unquote(parsed_uri[5]),
                    },
                    'environ': environ,
                    'body': None,
                }

                if method not in ('GET', 'HEAD'):
                    request['body'] = parse_request_body(environ, in_format)

                response_data, status_code, headers = run_endpoint(func, request, out_format)

                error = False

        except Exception as e:
            if hasattr(e, 'status_code'):
                status_code = e.status_code
            else:
                status_code = 500

            if hasattr(e, 'message'):
                error_message = f'{e.message}'
            else:
                error_message = f'{type(e).__name__}: {e}'

        status = code_to_status(status_code)

        if error:
            response_data, headers = self.generate_error_response(out_format, status, error_message)

        expect_type(response_data, str, 'internal response_data')

        headers.extend(additional_headers)
        encoded_response = response_data.encode('utf-8')
        add_content_length_header(headers, len(encoded_response))

        start_response(status, headers)
        return [encoded_response]
