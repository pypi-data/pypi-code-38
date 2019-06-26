from django.views import View
from django.http import HttpResponseBadRequest
from django.conf import settings
from ..lib.giosg_trigger_in_django import GiosgTriggerInDjango


class ApplicationTriggerView(View):
    """
    This module expects to find "GIOSG_APP_SECRET" variable in Django settings.
    This is intended to be subclassed, and used via "on_<trigger-type>" methods.
    """
    http_method_names = ['get']

    def get(self, request):
        # Leave validation to GiosgTriggerInDjango object
        try:
            trigger = GiosgTriggerInDjango(request, settings.GIOSG_APP_SECRET)
            handler = getattr(self, 'on_'+trigger.type, self.__unsupported_trigger_type)
            return handler(request, trigger)
        # Handle any giosg-auth-token validation errors
        except ValueError as e:
            return HttpResponseBadRequest(e)

    def __unsupported_trigger_type(self, *args, **kwargs):
        return HttpResponseBadRequest('Unsupported trigger type')

    def on_install(self, request, trigger):
        raise NotImplementedError

    def on_setup(self, request, trigger):
        raise NotImplementedError

    def on_uninstall(self, request, trigger):
        raise NotImplementedError

    def on_chat_start(self, request, trigger):
        raise NotImplementedError

    def on_chat_end(self, request, trigger):
        raise NotImplementedError

    def on_console_load(self, request, trigger):
        raise NotImplementedError

    def on_manual_dialog(self, request, trigger):
        raise NotImplementedError

    def on_manual_nav(self, request, trigger):
        raise NotImplementedError

    def on_chat_open(self, request, trigger):
        raise NotImplementedError

    def on_chat_close(self, request, trigger):
        raise NotImplementedError

    def on_chat_focus(self, request, trigger):
        raise NotImplementedError
