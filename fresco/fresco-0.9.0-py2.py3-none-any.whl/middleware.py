# Copyright 2015 Oliver Cope
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
__all__ = 'XForwarded'


class XForwarded(object):
    """\
    Modify the WSGI environment so that the X_FORWARDED_* headers are observed
    and generated URIs are correct in a proxied environment.

    Use this whenever the WSGI application server is sitting behind
    Apache or another proxy server.

    It is easy for clients to spoof the X-Forwarded-For header. You can largely
    protect against this by listing all trusted proxy server addresses in
    ``trusted``. See http://en.wikipedia.org/wiki/X-Forwarded-For for more
    details.

    HTTP_X_FORWARDED_FOR is substituted for REMOTE_ADDR and
    HTTP_X_FORWARDED_HOST for SERVER_NAME. If HTTP_X_FORWARDED_SSL is set, then
    the wsgi.url_scheme is modified to ``https`` and ``HTTPS`` is set to
    ``on``.

    Example::

        >>> from fresco import FrescoApp, context, GET, Response
        >>> from flea import Agent
        >>> app = FrescoApp()
        >>> @app.route('/', GET)
        ... def view():
        ...     return Response(["URL is ", context.request.url,
        ...                      "; REMOTE_ADDR is ",
        ...                      context.request.remote_addr])
        ...
        >>> r = Agent(XForwarded(app))
        >>> response = r.get('/',
        ...     SERVER_NAME='wsgiserver-name',
        ...     SERVER_PORT='8080',
        ...     HTTP_HOST='wsgiserver-name:8080',
        ...     REMOTE_ADDR='127.0.0.1',
        ...     HTTP_X_FORWARDED_HOST='real-name:81',
        ...     HTTP_X_FORWARDED_FOR='1.2.3.4'
        ... )
        >>> response.body
        u'URL is http://real-name:81/; REMOTE_ADDR is 1.2.3.4'
        >>> response = r.get('/',
        ...     SERVER_NAME='wsgiserver-name',
        ...     SERVER_PORT='8080',
        ...     HTTP_HOST='wsgiserver-name:8080',
        ...     REMOTE_ADDR='127.0.0.1',
        ...     HTTP_X_FORWARDED_HOST='real-name:443',
        ...     HTTP_X_FORWARDED_FOR='1.2.3.4',
        ...     HTTP_X_FORWARDED_SSL='on'
        ... )
        >>> response.body
        u'URL is https://real-name/; REMOTE_ADDR is 1.2.3.4'
    """

    def __init__(self, app, trusted=None):
        self.app = app
        if trusted:
            self.trusted = set(trusted)
        else:
            self.trusted = set()

    def __call__(self, environ, start_response):
        """\
        Call the WSGI app, passing it a modified environ
        """
        env = environ.get
        is_ssl = (env('HTTP_X_FORWARDED_PROTO') == 'https'
                  or env('HTTP_X_FORWARDED_SSL') == 'on')

        host = env('HTTP_X_FORWARDED_HOST')
        if host is not None:
            if ':' in host:
                port = host.split(':')[1]
            else:
                port = is_ssl and '443' or '80'

            environ['HTTP_HOST'] = host
            environ['SERVER_PORT'] = port

        if is_ssl:
            environ['wsgi.url_scheme'] = 'https'
            environ['HTTPS'] = 'on'

        try:

            forwards = (environ['HTTP_X_FORWARDED_FOR'].split(', ')
                        + [env('REMOTE_ADDR', '')])
        except KeyError:
            # No X-Forwarded-For header?
            return self.app(environ, start_response)

        if self.trusted:
            for ip in forwards[::-1]:
                # Find the first non-trusted ip; this is our remote address
                if ip not in self.trusted:
                    environ['REMOTE_ADDR'] = ip
                    break
        else:
            environ['REMOTE_ADDR'] = forwards[0]

        return self.app(environ, start_response)
