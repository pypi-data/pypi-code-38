from saleboxdjango.views.basket.base import SaleboxBasketView
from saleboxdjango.forms import SaleboxBasketWishlistForm


class SaleboxBasketWishlistView(SaleboxBasketView):
    action = 'basket-wishlist'
    form = SaleboxBasketWishlistForm

    def form_valid(self, request):
        try:
            self.sb.update_wishlist(
                request,
                self.form.cleaned_data['variant_id'],
                self.form.cleaned_data['add'],
            )
            self.status = 'success'

            self.results = self.sb.get_data(
                request,
                self.results_csv,
                self.form.cleaned_data['variant_id']
            )
        except:
            self.status = 'fail'
