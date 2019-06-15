from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from saleboxdjango.forms import SaleboxAddressAddForm
from saleboxdjango.lib.address import SaleboxAddress


class SaleboxAccountAddressView(TemplateView):
    initial = {}
    template_name = 'salebox/account/address.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.sa = SaleboxAddress(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.form = SaleboxAddressAddForm(initial=self.initial)
        return self.output(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = SaleboxAddressAddForm(
            request.POST,
            initial=self.initial
        )
        if self.form.is_valid():
            address = self.sa.add(self.form.cleaned_data)

            # redirect to self to prevent refresh
            return redirect(request.get_full_path())

        return self.output(request, *args, **kwargs)

    def output(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['addresses'] = self.sa.get()
        context['address_form'] = self.form
        context['address_extras'] = self.sa.form_extras(
            country_id=self.form['country'].value()
        )

        return self.render_to_response(context)
