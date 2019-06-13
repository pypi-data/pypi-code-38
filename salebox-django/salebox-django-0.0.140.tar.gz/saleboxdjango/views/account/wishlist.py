from django.shortcuts import redirect
from django.views.generic import TemplateView

from saleboxdjango.lib.basket import SaleboxBasket


class SaleboxAccountWishlistView(TemplateView):
    template_name = 'salebox/account/wishlist.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        sb = SaleboxBasket(request)
        context['data'] = sb.get_raw_data()

        return self.render_to_response(context)
