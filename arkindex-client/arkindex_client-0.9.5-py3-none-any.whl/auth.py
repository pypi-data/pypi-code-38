from apistar.client.auth import TokenAuthentication, SessionAuthentication


class TokenSessionAuthentication(TokenAuthentication):
    """
    A token authentication that takes care of CSRF tokens.
    """

    def __init__(self, token, scheme='Token', csrf_cookie_name='arkindex.csrf', csrf_header_name='X-CSRFToken'):
        """
        :param str token: The API token to use.
        :param str scheme: The HTTP authentication scheme to use for token authentication.
        :param str csrf_cookie_name: Name of the CSRF token cookie.
        :param str csrf_header_name: Name of the CSRF request header.
        """
        self.session_auth = SessionAuthentication(
            csrf_cookie_name=csrf_cookie_name,
            csrf_header_name=csrf_header_name,
        )
        super().__init__(token, scheme=scheme)

    def __call__(self, request):
        request = self.session_auth(request)
        if self.token is None:
            return request
        return super().__call__(request)
