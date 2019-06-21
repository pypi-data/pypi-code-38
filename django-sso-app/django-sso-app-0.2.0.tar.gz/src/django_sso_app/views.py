from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from . import settings


class SsoAdminAuthUser(TemplateView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        redirect_url = settings.DJANGO_SSO_ADMIN_USER_URL
        return HttpResponseRedirect(redirect_to=redirect_url)

