from django.shortcuts import redirect
from django.views.generic import TemplateView

from saleboxdjango.lib.basket import SaleboxBasket
from saleboxdjango.lib.checkout import SaleboxCheckout


class SaleboxAccountBasketView(TemplateView):
    template_name = 'salebox/account/basket.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        sb = SaleboxBasket(request)
        context['data'] = sb.get_raw_data()

        sc = SaleboxCheckout(request)
        context['checkout'] = {
            'nav': sc.get_checkout_nav()
        }

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        sb = SaleboxBasket(request)
        sc = SaleboxCheckout(request)
        return redirect(sc.set_basket(sb, request))
