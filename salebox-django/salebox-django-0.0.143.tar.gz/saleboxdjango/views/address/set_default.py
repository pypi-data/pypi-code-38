from saleboxdjango.views.address.base import SaleboxAddressView
from saleboxdjango.forms import SaleboxAddressIDForm


class SaleboxAddressSetDefaultView(SaleboxAddressView):
    action = 'address-set-default'
    form = SaleboxAddressIDForm

    def form_valid(self, request):
        try:
            self.sa.set_default(self.form.cleaned_data['id'])
            self.status = 'success'
        except:
            self.status = 'fail'
