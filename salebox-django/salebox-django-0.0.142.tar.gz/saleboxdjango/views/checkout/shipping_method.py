from django import forms

from saleboxdjango.lib.shipping_options import SaleboxShippingOptions
from saleboxdjango.views.checkout.base import SaleboxCheckoutBaseView


class SaleboxCheckoutShippingMethodForm(forms.Form):
    shipping_method = forms.IntegerField()

class SaleboxCheckoutShippingMethodView(SaleboxCheckoutBaseView):
    shipping_options_class = SaleboxShippingOptions
    checkout_step = 'shipping_method'
    form_class = SaleboxCheckoutShippingMethodForm
    template_name = 'salebox/checkout/shipping_method.html'

    def get_additional_context_data(self, context):
        context = self._get_shipping_options(context)

        combined_price = None

        # use selected option if exists
        if self.sc.get_raw_data()['shipping_method']['id'] is not None:
            for o in context['shipping_options']:
                if o['id'] == self.sc.get_raw_data()['shipping_method']['id']:
                    combined_price = o['combined_price']
                    break

        # no option selected, choice the default
        if combined_price is None:
            for o in context['shipping_options']:
                if o['available'] and o['selected']:
                    combined_price = o['combined_price']
                    break

        # no option selected, no default, fallback to first available
        if combined_price is None:
            for o in context['shipping_options']:
                if o['available']:
                    combined_price = o['combined_price']
                    break

        context['combined_shipping_price'] = combined_price
        return context

    def form_valid_pre_redirect(self, form):
        # retrieve selected option
        id = form.cleaned_data['shipping_method']
        options = self._get_shipping_options()['shipping_options']
        selected = next(o for o in options if o['id'] == id)

        # store in checkout
        self.sc.set_shipping_method(
            selected['id'],
            selected['label'],
            selected['price'],
            selected['meta'],
            self.request
        )

        return True

    def _get_shipping_options(self, context={}):
        smc = self.shipping_options_class()
        return smc.go(
            self.request,
            self.sc.get_raw_data(),
            context
        )
