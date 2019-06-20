# -*- coding: utf-8 -*-
from congo.conf import settings
from django import http
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import get_resolver, LocaleRegexURLResolver, resolve, reverse, Resolver404, NoReverseMatch
from django.http.response import HttpResponseRedirect
from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.utils.http import is_safe_url, unquote
from django.utils.translation import check_for_language
from urlparse import urlparse
import six

class LanguageMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self._is_language_prefix_patterns_used = False
        for url_pattern in get_resolver(None).url_patterns:
            if isinstance(url_pattern, LocaleRegexURLResolver):
                self._is_language_prefix_patterns_used = True
                break

    def process_request(self, request):
        is_admin_backend = getattr(request, 'is_admin_backend', False)

        if is_admin_backend:
            language = settings.CONGO_ADMIN_LANGUAGE_CODE
        else:
            check_path = self.is_language_prefix_patterns_used()
            language = translation.get_language_from_request(request, check_path = check_path)

        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        if request.method == 'POST':
            language = request.POST.get('language')
            action = request.POST.get('action')

            content_type_id = request.POST.get('content_type_id')
            object_id = request.POST.get('object_id')

            if action == 'set_language' and check_for_language(language):
                host = request.get_host()
                next_url = request.GET.get('next', None)
                referer = request.META.get('HTTP_REFERER', None)

                if content_type_id and object_id:
                    try:
                        with translation.override(language):
                            content_type = ContentType.objects.get_for_id(content_type_id)
                            obj = content_type.get_object_for_this_type(id = object_id)
                            if hasattr(obj, 'get_absolute_url'):
                                response = HttpResponseRedirect(obj.get_absolute_url())
                    except ObjectDoesNotExist:
                        pass
                elif next_url:
                    if is_safe_url(url = next_url, host = host):
                        response = HttpResponseRedirect(next_url)
                elif referer:
                    if is_safe_url(url = referer, host = host):
                        referer_url = urlparse(referer)[2]
                        try:
                            # http://wenda.soso.io/questions/275666/django-templates-get-current-url-in-another-language
                            view = resolve(referer_url)
                            with translation.override(language):
                                next_url = reverse(view.view_name, args = view.args, kwargs = view.kwargs)
                                response = HttpResponseRedirect(next_url)
                        except (Resolver404, NoReverseMatch):
                            pass

                if hasattr(request, 'session'):
                    request.session[translation.LANGUAGE_SESSION_KEY] = language
                else:
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language, max_age = settings.LANGUAGE_COOKIE_AGE, path = settings.LANGUAGE_COOKIE_PATH, domain = settings.LANGUAGE_COOKIE_DOMAIN)
        else:
            if self.is_language_prefix_patterns_used() and hasattr(request, 'LANGUAGE_CODE'):
                if hasattr(request, 'session'):
                    request.session[translation.LANGUAGE_SESSION_KEY] = request.LANGUAGE_CODE
                else:
                    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, request.LANGUAGE_CODE, max_age = settings.LANGUAGE_COOKIE_AGE, path = settings.LANGUAGE_COOKIE_PATH, domain = settings.LANGUAGE_COOKIE_DOMAIN)

        return response

    def is_language_prefix_patterns_used(self):
        """
        Returns `True` if the `LocaleRegexURLResolver` is used
        at root level of the urlpatterns, else it returns `False`.
        """
        return self._is_language_prefix_patterns_used

class AngularUrlMiddleware(MiddlewareMixin):
    """
    Based on: https://github.com/jrief/django-angular/blob/master/djng/middleware.py
    If the request path is <ANGULAR_REVERSE> it should be resolved to actual view, otherwise return "None" and continue as usual.
    This must be the first middleware in the MIDDLEWARE_CLASSES tuple!
    """
    ANGULAR_REVERSE = '/reverse/'
    ANGULAR_URL_NAME = 'dj_url'
    ANGULAR_URL_ARGS = 'dj_args'
    ANGULAR_URL_KWARGS = 'dj_kwarg'

    def process_request(self, request):
        """
        Reads url name, args, kwargs from GET parameters, reverses the url and resolves view function
        Returns the result of resolved view function, called with provided args and kwargs
        Since the view function is called directly, it isn't ran through middlewares, so the middlewares must
        be added manually
        The final result is exactly the same as if the request was for the resolved view.

        Parametrized urls:
        djangoUrl.reverse can be used with parametrized urls of $resource
        In that case the reverse url is something like: /reverse/?dj_url=orders&dj_kwarg_id=:id
        $resource can either replace the ':id' part with say 2 and we can proceed as usual,
        reverse with reverse('orders', kwargs={'id': 2}).

        If it's not replaced we want to reverse to url we get a request to url
        '/reverse/?dj_url=orders&dj_kwarg_id=' which
        gives a request.GET QueryDict {u'dj_url': [u'orders'], u'dj_kwarg_id': [u'']}

        In that case we want to ignore the id param and only reverse to url with name 'orders' and no params.
        So we ignore args and kwargs that are empty strings.
        """
        if request.path == self.ANGULAR_REVERSE:
            url_name = request.GET.get(self.ANGULAR_URL_NAME)
            url_args = request.GET.getlist(self.ANGULAR_URL_ARGS, [])
            url_kwargs = {}

            # Remove falsy values (empty strings)
            url_args = filter(lambda x: x, url_args)

            # Read kwargs
            for param in request.GET:
                prefix = '%s_' % self.ANGULAR_URL_KWARGS
                if param.startswith(prefix):
                    # Ignore kwargs that are empty strings
                    if request.GET[param]:
                        url_kwargs[param[len(prefix):]] = request.GET[param] # to remove kwarg prefix

            url = unquote(reverse(url_name, args = url_args, kwargs = url_kwargs))
            assert not url.startswith(self.ANGULAR_REVERSE), "Prevent recursive requests"

            # rebuild the request object with a different environ
            request.path = request.path_info = url
            request.environ['PATH_INFO'] = url
            query = request.GET.copy()
            for key in request.GET:
                if key in (self.ANGULAR_URL_NAME, self.ANGULAR_URL_ARGS) or key.startswith(self.ANGULAR_URL_KWARGS):
                    query.pop(key, None)
            if six.PY3:
                request.environ['QUERY_STRING'] = query.urlencode()
            else:
                request.environ['QUERY_STRING'] = query.urlencode().encode('utf-8')

            # Reconstruct GET QueryList in the same way WSGIRequest.GET function works
            request.GET = http.QueryDict(request.environ['QUERY_STRING'])
