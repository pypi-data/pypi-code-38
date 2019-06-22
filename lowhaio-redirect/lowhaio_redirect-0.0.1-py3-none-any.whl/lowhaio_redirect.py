import urllib.parse


class HttpTooManyRedirects(Exception):
    pass


async def empty_async_iterator():
    while False:
        yield


async def buffered(data):
    return b''.join([chunk async for chunk in data])


def get(_, __, ___, ____, headers):
    next_request_headers = tuple(
        (key, value)
        for key, value in headers if key.lower() not in (b'content-length', b'transfer-encoding')
    )

    return (b'GET', empty_async_iterator, (), (), next_request_headers)


def unchanged(method, body, body_args, body_kwargs, headers):
    return (method, body, body_args, body_kwargs, headers)


default_redirects = (
    (b'301', lambda method: unchanged if method != b'POST' else get),
    (b'302', lambda method: unchanged if method != b'POST' else get),
    (b'303', lambda method: unchanged if method in (b'GET', b'HEAD') else get),
    (b'307', lambda method: unchanged),
    (b'308', lambda method: unchanged),
)


def strip_authorization_if_different_host(request_headers, request_host, redirect_host):
    forbidden = \
        (b'authorization',) if request_host != redirect_host else \
        ()
    return tuple(
        (key, value)
        for key, value in request_headers if key.lower() not in forbidden
    )


def redirectable(request, redirects=default_redirects, max_redirects=20,
                 transform_headers=strip_authorization_if_different_host):

    redirects_dict = dict(redirects)

    async def _redirectable(method, url, params=(), headers=(),
                            body=empty_async_iterator, body_args=(), body_kwargs=()):

        for _ in range(0, max_redirects):
            status, response_headers, response_body = await request(
                method, url, params=params, headers=headers,
                body=body, body_args=body_args, body_kwargs=body_kwargs,
            )

            try:
                transform_request = redirects_dict[status](method)
            except KeyError:
                return status, response_headers, response_body

            # Ensure the connection is closed/returned to the pool
            await buffered(response_body)

            location = dict(
                (key.lower(), value)
                for key, value in response_headers
            )[b'location'].decode('ascii')

            parsed_request_url = urllib.parse.urlsplit(url)
            location = urllib.parse.urlsplit(location)
            parsed_redirect_url = location._replace(
                scheme=location.scheme if location.scheme != '' else parsed_request_url.scheme,
                netloc=location.netloc if location.netloc != '' else parsed_request_url.netloc,
            )

            url = urllib.parse.urlunsplit(parsed_redirect_url)
            headers = transform_headers(
                headers, parsed_request_url.hostname, parsed_redirect_url.hostname)

            method, body, body_args, body_kwargs, headers = transform_request(
                method, body, body_args, body_kwargs, headers,
            )

        raise HttpTooManyRedirects()

    return _redirectable
