from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.crypto import constant_time_compare
from django.views import View
from django.views.decorators.cache import never_cache

import health_check.views


class HealthcheckView(health_check.views.MainView):
    template_name = 'directory_healthcheck/healthcheck.html'

    def has_permission(self):
        return constant_time_compare(
            self.request.GET.get('token'),
            settings.DIRECTORY_HEALTHCHECK_TOKEN
        )

    @never_cache
    def get(self, *args, **kwargs):
        if not self.has_permission():
            return HttpResponseForbidden()
        return super().get(*args, **kwargs)

    def render_to_response(self, context, status):
        context['errored_plugins'] = [
            plugin for plugin in context['plugins'] if plugin.errors
        ]
        return super().render_to_response(context=context, status=status)


class PingView(View):
    @never_cache
    def get(self, request, *args, **kwargs):
        return HttpResponse('OK')
