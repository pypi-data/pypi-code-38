from django import forms

from saleboxdjango.views.checkout.base import SaleboxCheckoutBaseView


class SaleboxCheckoutPaymentMethodForm(forms.Form):
    payment_method = forms.ChoiceField(choices=(
        (1, 'Credit or Debit Card'),
        (2, 'E-Wallet'),
    ))


class SaleboxCheckoutPaymentMethodView(SaleboxCheckoutBaseView):
    checkout_step = 'payment_method'
    form_class = SaleboxCheckoutPaymentMethodForm
    template_name = 'salebox/checkout/payment_method.html'

    def form_valid_pre_redirect(self, form):
        id = form.cleaned_data['payment_method']
        self.sc.set_payment_method(id, None, self.request)
        return True
