from django import forms

from saleboxdjango.lib.basket import SaleboxBasket
from .base import SaleboxCheckoutBaseView


class SaleboxCheckoutGatewayForm(forms.Form):
    pass


class SaleboxCheckoutGatewayView(SaleboxCheckoutBaseView):
    http_method_names = ['get', 'post']

    checkout_step = 'gateway'
    form_class = SaleboxCheckoutGatewayForm
    template_name = 'salebox/checkout/gateway.html'

    def gateway(self, request, *args, **kwargs):
        context = self.get_context_data()
        store = self.sc.save_to_store(request.user)

        # override this middle section relevant to your needs
        #
        #
        #
        context['html'] = '<form><!-- PUT YOUR CODE HERE --></form>'

        # reset the shopping basket
        basket = SaleboxBasket(request)
        basket.reset_basket(request)

        # render the gateway redirect
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        return self.gateway(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.gateway(request, *args, **kwargs)
