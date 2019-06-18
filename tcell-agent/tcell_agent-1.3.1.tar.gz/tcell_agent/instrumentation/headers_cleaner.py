from future.utils import iteritems

from tcell_agent.utils.multi_value_dict import MultiValueDict


def headers_from_environ(environ):
    request_headers = MultiValueDict()
    for header in environ:
        if header.startswith('HTTP_'):
            new_key = header[5:].lower().replace("_", "-")
            request_headers[new_key] = environ[header]
    if 'cookie' in request_headers:
        del request_headers['cookie']
    if 'CONTENT_TYPE' in environ:
        request_headers['content-type'] = environ['CONTENT_TYPE']
    if 'CONTENT_LENGTH' in environ:
        request_headers['content-length'] = environ['CONTENT_LENGTH']
    return request_headers


def deprecated_headers_from_environ(environ):
    include = ("content-length", "content-type")
    exclude = ("http-cookie")

    env = environ or {}

    env_low_hyphen = {header_name.lower().replace("_", "-"): header_value
                      for header_name, header_value in iteritems(env)}

    env_filtered = {header_name: header_value
                    for header_name, header_value in iteritems(env_low_hyphen)
                    if header_name.startswith("http-") or header_name in include
                    if header_name not in exclude}

    env_deprefixed = {
        header_name[5:] if header_name.startswith("http-") else header_name:
        header_value
        for header_name, header_value in iteritems(env_filtered)
    }

    return env_deprefixed
