from saleboxdjango.forms import SaleboxRatingAddForm
from saleboxdjango.views.rating.base import SaleboxRatingView


class SaleboxRatingAddView(SaleboxRatingView):
    action = 'rating-add'
    form = SaleboxRatingAddForm

    def form_valid(self, request):
        try:
            self.sr.set_variant(self.form.cleaned_data['variant_id'])
            self.sr.add_rating(self.form.cleaned_data['rating'])

            self.status = 'success'
            self.results = self.sr.get_data(self.results_csv)
        except:
            self.status = 'fail'
