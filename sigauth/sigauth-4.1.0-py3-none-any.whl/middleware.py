import abc

from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from sigauth.helpers import RequestSignatureChecker


class SignatureCheckMiddlewareBase(MiddlewareMixin, abc.ABC):

    request_checker = None

    @property
    @abc.abstractmethod
    def secret(self):
        pass

    def __init__(self, *args, **kwargs):
        self.request_checker = RequestSignatureChecker(self.secret)
        super().__init__(*args, **kwargs)

    def process_view(self, request, view_func, view_args, view_kwarg):
        if self.should_check(request):
            if not self.request_checker.test_signature(request):
                return HttpResponse('Unauthorized', status=401)

    @staticmethod
    def should_check(request):
        url_name = request.resolver_match.url_name
        return url_name not in settings.SIGAUTH_URL_NAMES_WHITELIST
