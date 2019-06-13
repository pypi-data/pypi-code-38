from saleboxdjango.views.base import SaleboxBaseView
from saleboxdjango.lib.basket import SaleboxBasket


class SaleboxBasketView(SaleboxBaseView):
    user_must_be_authenticated = False

    def init_class(self, request):
        self.sb = SaleboxBasket(request)
