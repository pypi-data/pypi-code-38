from saleboxdjango.views.base import SaleboxBaseView
from saleboxdjango.lib.rating import SaleboxRating


class SaleboxRatingView(SaleboxBaseView):
    def init_class(self, request):
        self.sr = SaleboxRating(request.user)
