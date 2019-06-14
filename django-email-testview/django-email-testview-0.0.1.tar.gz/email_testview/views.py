import importlib

from django.conf import settings
from django.http import HttpResponseForbidden
from django.views.generic import TemplateView

from .registry import autodiscover_emails, registry

autodiscover_emails()


class EmailsView(TemplateView):
    template_name = 'emails/emails_view.html'

    def dispatch(self, request, *args, **kwargs):
        if getattr(settings, 'ENVIRONMENT', 'prod').upper() == 'PROD':
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'emails': registry.get_identifiers()})
        return ctx


class EmailTestView(TemplateView):

    def dispatch(self, request, *args, **kwargs):
        if getattr(settings, 'ENVIRONMENT', 'prod').upper() == 'PROD':
            return HttpResponseForbidden()

        identifier = kwargs.get('identifier')

        email_func = registry.get_email_func(identifier)
        fixtures_func = registry.get_fixtures_func(identifier)

        f_args, f_kwargs = fixtures_func()
        self.email_context = email_func(*f_args, **f_kwargs)

        app_name, email_name = registry.get_app_and_email_name(identifier)
        self.template_name = f'{app_name}/email/body/{email_name}.html'
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(self.email_context['context'])
        return ctx
