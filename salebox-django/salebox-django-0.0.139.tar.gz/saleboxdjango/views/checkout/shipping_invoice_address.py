from django import forms
from django.shortcuts import redirect

from saleboxdjango.forms import SaleboxAddressAddForm
from saleboxdjango.lib.address import SaleboxAddress
from saleboxdjango.models import UserAddress
from saleboxdjango.views.checkout.base import SaleboxCheckoutBaseView


class SaleboxCheckoutShippingInvoiceAddressForm(forms.Form):
    shipping_address_id = forms.IntegerField()
    invoice_required = forms.BooleanField(required=False)
    invoice_address_id = forms.IntegerField(required=False)


class SaleboxFormNameForm(forms.Form):
    salebox_form_name = forms.ChoiceField(choices=(
        ('select_address', 'select_address'),
        ('add_shipping', 'add_shipping'),
        ('add_invoice', 'add_invoice'),
    ))

class SaleboxCheckoutShippingInvoiceAddressView(SaleboxCheckoutBaseView):
    initial = {}
    checkout_step = 'shipping_invoice_address'
    form_class = SaleboxCheckoutShippingInvoiceAddressForm
    template_name = 'salebox/checkout/shipping_invoice_address.html'

    def get(self, request, *args, **kwargs):
        self.shipping_form = SaleboxAddressAddForm(initial=self.initial)
        self.invoice_form = SaleboxAddressAddForm(initial=self.initial)
        return super().get(self, request, *args, **kwargs)

    def get_additional_context_data(self, context):
        sa = SaleboxAddress(self.request.user)

        # shipping form
        context['shipping_form'] = self.shipping_form
        context['shipping_addresses'] = sa.get(
            selected_id=self.sc.data['shipping_address']['id'],
            force_selected=True
        )
        context['shipping_address_extras'] = sa.form_extras(
            country_id=self.shipping_form['country'].value()
        )

        # invoice form
        context['invoice_form'] = self.invoice_form
        context['invoice_addresses'] = sa.get(
            selected_id=self.sc.data['invoice_address']['id'],
            non_null_fields=['tax_id'],
            force_selected=True
        )
        context['invoice_address_extras'] = sa.form_extras(
            country_id=self.invoice_form['country'].value()
        )

        # form control
        context['shipping_address_id'] = self.sc.data['shipping_address']['id']
        context['invoice_address_id'] = self.sc.data['invoice_address']['id']
        context['invoice_required'] = self.sc.data['invoice_address']['required']
        return context

    def post(self, request, *args, **kwargs):
        self.shipping_form = SaleboxAddressAddForm(initial=self.initial)
        self.invoice_form = SaleboxAddressAddForm(initial=self.initial)

        # which action is being performed?
        form = SaleboxFormNameForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['salebox_form_name']
        else:
            return self.get(request, *args, **kwargs)

        # action: user has selected an option
        if action == 'select_address':
            form = self.form_class(request.POST)
            if form.is_valid():
                self.sc.set_shipping_address(
                    True,
                    form.cleaned_data['shipping_address_id'],
                    None,
                    request
                )
                self.sc.set_invoice_address(
                    form.cleaned_data['invoice_required'],
                    form.cleaned_data['invoice_address_id'],
                    None,
                    request
                )

                r = self.sc.set_completed(self.checkout_step, request)
                if r is None:
                    raise Exception('There is no next checkout step to redirect to...')
                else:
                    return redirect(r)

        # action: user is adding a shipping address
        if action == 'add_shipping':
            self.shipping_form = SaleboxAddressAddForm(
                request.POST,
                initial=self.initial
            )
            if self.shipping_form.is_valid():
                # add address to db
                sa = SaleboxAddress(request.user)
                address = sa.add(self.shipping_form.cleaned_data)
                self.sc.set_shipping_address(True, address.id, None, request)

                # redirect to self to prevent refresh
                return redirect(request.get_full_path())

        # action: user is adding an invoice address
        if action == 'add_invoice':
            self.invoice_form = SaleboxAddressAddForm(
                request.POST,
                initial=self.initial
            )
            if self.invoice_form.is_valid():
                tax_id = self.invoice_form.cleaned_data['tax_id']
                if tax_id is not None and len(tax_id.strip()) > 4:
                    # add address to db
                    sa = SaleboxAddress(request.user)
                    address = sa.add(self.invoice_form.cleaned_data)
                    self.sc.set_invoice_address(True, address.id, None, request)

                    # redirect to self to prevent refresh
                    return redirect(request.get_full_path())

        # if we've reached this point, some input was invalid...
        # just re-show the page
        return self.form_invalid(form)
