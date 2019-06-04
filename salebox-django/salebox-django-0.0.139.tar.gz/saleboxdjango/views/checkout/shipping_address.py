from django import forms
from django.shortcuts import redirect

from saleboxdjango.forms import SaleboxAddressAddForm
from saleboxdjango.lib.address import SaleboxAddress
from saleboxdjango.models import UserAddress
from saleboxdjango.views.checkout.base import SaleboxCheckoutBaseView


class SaleboxCheckoutShippingAddressForm(forms.Form):
    shipping_address_id = forms.IntegerField()


class SaleboxFormNameForm(forms.Form):
    salebox_form_name = forms.ChoiceField(choices=(
        ('select_address', 'select_address'),
        ('add_shipping', 'add_shipping'),
    ))

class SaleboxCheckoutShippingAddressView(SaleboxCheckoutBaseView):
    initial = {}
    checkout_step = 'shipping_address'
    form_class = SaleboxCheckoutShippingAddressForm
    template_name = 'salebox/checkout/shipping_address.html'

    def get(self, request, *args, **kwargs):
        self.shipping_form = SaleboxAddressAddForm(initial=self.initial)
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

        # form control
        context['shipping_address_id'] = self.sc.data['shipping_address']['id']
        return context

    def post(self, request, *args, **kwargs):
        self.shipping_form = SaleboxAddressAddForm(initial=self.initial)

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

        # if we've reached this point, some input was invalid...
        # just re-show the page
        return self.form_invalid(form)
