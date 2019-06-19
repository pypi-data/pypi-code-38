"""CAS authentication middleware"""


from django.conf import settings
from django.contrib.auth import logout as do_logout
from django.http import HttpResponseRedirect
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

from .exceptions import CasTicketException
from .utils import single_sign_out
from .domain import Domain


__all__ = ['CASMiddleware']


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class CASMiddleware(MiddlewareMixin):

    def process_request(self, request):
        """Checks that the authentication middleware is installed"""
        request.domain = Domain.pop(request.get_host())

        error = ("The Django CAS middleware requires authentication "
                 "middleware to be installed. Edit your MIDDLEWARE_CLASSES "
                 "setting to insert 'django.contrib.auth.middleware."
                 "AuthenticationMiddleware'.")
        assert hasattr(request, 'user'), error

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Forwards unauthenticated requests to the admin page to the CAS
        login URL, as well as calls to django.contrib.auth.views.login and
        logout.
        """
        logoutRequest = request.POST.get('logoutRequest', '')
        if logoutRequest:
            return single_sign_out(request)
        return None

    def process_exception(self, request, exception):
        """When we get a CasTicketException, that is probably caused by the ticket timing out.
        So logout/login and get the same page again."""
        if isinstance(exception, CasTicketException):
            do_logout(request)
            # This assumes that request.path requires authentication.
            return HttpResponseRedirect(request.path)
        else:
            return None
