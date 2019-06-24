from django.views.generic import TemplateView
from django.urls import reverse_lazy
from issuestracker.conf import settings as app_settings
from issuestracker.utils.auth import secure


@secure
class Base(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["API_TOKEN"] = app_settings.SECRET_KEY

        context["API_ROOT"] = reverse_lazy("issuestracker:api-root")

        return context
