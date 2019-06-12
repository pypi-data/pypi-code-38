from django.contrib.auth import authenticate, login
from base64 import b64decode


class AuthenticatorBase(object):
    """
    Abstract class for authentication.
    """

    def authenticate(self, request):  # pragma: no cover
        """
        Override this method to perform authentication on an HTTP request.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        """

        raise NotImplementedError('Method not implemented')


class DjangoSessionAuthenticator(AuthenticatorBase):
    """
    An authenticator using Django sessions. Useful for testing read operations
    via the browser. It is not suitable for use with write operations, as CSRF
    protection is bypassed.
    """

    def authenticate(self, request):
        """
        Returns True if the current user is authenticated.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        """

        if request.method in ('PATCH', 'POST', 'PUT', 'DELETE'):
            if getattr(request, '_dont_enforce_csrf_checks', False):
                return True

        a = request.user.is_authenticated
        return a if not callable(a) else a()


class HTTPBasicAuthenticator(AuthenticatorBase):
    """
    An authenticator using HTTP Basic authentication.
    """

    def authenticate(self, request):
        """
        Returns True if a Django user can be found matching the username and
        password supplied in Base64 format.

        :param request: The HTTP request
        :type request: ``django.http.request.HttpRequest``
        """

        auth = request.META.get('HTTP_AUTHORIZATION', '')

        if auth.startswith('Basic '):
            try:
                auth = b64decode(auth[6:]).decode('utf-8')
            except Exception:  # pragma: no cover
                return False

            try:
                username, password = auth.split(':', 1)
            except Exception:  # pragma: no cover
                return False

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:
                login(request, user)
                return True
