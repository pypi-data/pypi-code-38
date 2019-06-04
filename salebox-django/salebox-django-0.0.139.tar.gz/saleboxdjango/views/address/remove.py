from saleboxdjango.views.address.base import SaleboxAddressView
from saleboxdjango.forms import SaleboxAddressIDForm


class SaleboxAddressRemoveView(SaleboxAddressView):
    action = 'address-remove'
    form = SaleboxAddressIDForm

    def form_valid(self, request):
        try:
            self.sa.set_inactive(self.form.cleaned_data['id'])
            self.status = 'success'
        except:
            self.status = 'fail'
