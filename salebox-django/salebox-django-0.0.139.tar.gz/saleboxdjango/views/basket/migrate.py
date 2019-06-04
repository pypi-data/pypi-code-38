from saleboxdjango.views.basket.base import SaleboxBasketView
from saleboxdjango.forms import SaleboxBasketMigrateForm


class SaleboxBasketMigrateView(SaleboxBasketView):
    action = 'basket-migrate'
    form = SaleboxBasketMigrateForm

    def form_valid(self, request):
        try:
            self.sb.migrate_basket_wishlist(
                request,
                self.form.cleaned_data['variant_id'],
                self.form.cleaned_data['to_basket']
            )
            self.status = 'success'

            self.results = self.sb.get_data(
                request,
                self.results_csv
            )
        except:
            self.status = 'fail'
