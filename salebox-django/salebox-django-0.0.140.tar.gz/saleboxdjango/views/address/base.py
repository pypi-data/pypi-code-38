from saleboxdjango.views.base import SaleboxBaseView
from saleboxdjango.lib.address import SaleboxAddress


class SaleboxAddressView(SaleboxBaseView):
    def init_class(self, request):
        self.sa = SaleboxAddress(request.user)
