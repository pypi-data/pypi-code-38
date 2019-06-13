from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from saleboxdjango.lib.address import SaleboxAddress


class SaleboxAccountHomeView(TemplateView):
    template_name = 'salebox/account/home.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        sa = SaleboxAddress(request.user)
        context['delivery_address_count'] = sa.get_count()

        return self.render_to_response(context)
