from django import forms
from .base import SaleboxCheckoutBaseView


class SaleboxCheckoutConfirmationForm(forms.Form):
    pass


class SaleboxCheckoutConfirmationView(SaleboxCheckoutBaseView):
    checkout_step = 'confirmation'
    form_class = SaleboxCheckoutConfirmationForm
    template_name = 'salebox/checkout/confirmation.html'