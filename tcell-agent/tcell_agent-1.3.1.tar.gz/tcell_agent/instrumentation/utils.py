def header_keys_from_request_env(request_env):
    request_headers_keys = []
    for header in request_env:
        if header.startswith('HTTP_'):
            new_key = header[5:]
            request_headers_keys.append(new_key)
    if 'CONTENT_TYPE' in request_env:
        request_headers_keys.append('CONTENT_TYPE')
    if 'CONTENT_LENGTH' in request_env:
        request_headers_keys.append('CONTENT_LENGTH')
    return request_headers_keys
