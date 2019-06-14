from saleboxdjango.views.rating.base import SaleboxRatingView
from saleboxdjango.forms import SaleboxRatingRemoveForm


class SaleboxRatingRemoveView(SaleboxRatingView):
    action = 'rating-remove'
    form = SaleboxRatingRemoveForm

    def form_valid(self, request):
        try:
            self.sr.set_variant(self.form.cleaned_data['variant_id'])
            self.sr.remove_rating()

            self.status = 'success'
            self.results = self.sr.get_data(self.results_csv)
        except:
            self.status = 'fail'
