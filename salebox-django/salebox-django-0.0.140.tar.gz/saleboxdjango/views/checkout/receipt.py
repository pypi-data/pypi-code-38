from django import forms
from .base import SaleboxCheckoutBaseView


class SaleboxCheckoutReceiptForm(forms.Form):
    pass


class SaleboxCheckoutReceiptView(SaleboxCheckoutBaseView):
    checkout_step = 'receipt'
    form_class = SaleboxCheckoutReceiptForm
    template_name = 'salebox/checkout/receipt.html'
