from saleboxdjango.views.basket.base import SaleboxBasketView
from saleboxdjango.forms import SaleboxBasketBasketForm


class SaleboxBasketBasketView(SaleboxBasketView):
    action = 'basket-basket'
    form = SaleboxBasketBasketForm

    def form_valid(self, request):
        try:
            self.sb.update_basket(
                request,
                self.form.cleaned_data['variant_id'],
                self.form.cleaned_data['quantity'],
                self.form.cleaned_data['relative']
            )
            self.status = 'success'

            self.results = self.sb.get_data(
                request,
                self.results_csv,
                self.form.cleaned_data['variant_id']
            )
        except:
            self.status = 'fail'
