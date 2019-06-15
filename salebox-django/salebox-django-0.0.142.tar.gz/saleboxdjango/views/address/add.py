from saleboxdjango.views.address.base import SaleboxAddressView
from saleboxdjango.forms import SaleboxAddressAddForm

from saleboxdjango.models import Country, CountryState, UserAddress


class SaleboxAddressAddView(SaleboxAddressView):
    action = 'address-add'
    form = SaleboxAddressAddForm

    def form_valid(self, request):
        try:
            country = None
            if self.form.cleaned_data['country'] is not None:
                country = Country \
                            .objects \
                            .filter(id=self.form.cleaned_data['country']) \
                            .first()

            state = None
            if self.form.cleaned_data['country_state'] is not None:
                state = CountryState \
                            .objects \
                            .filter(id=self.form.cleaned_data['country_state']) \
                            .first()

            ua = UserAddress(
                user=request.user,
                default=self.form.cleaned_data['set_default'],
                address_group=self.form.cleaned_data['address_group'] or 'default',
                full_name=self.form.cleaned_data['full_name'],
                address_1=self.form.cleaned_data['address_1'],
                address_2=self.form.cleaned_data['address_2'],
                address_3=self.form.cleaned_data['address_3'],
                address_4=self.form.cleaned_data['address_4'],
                address_5=self.form.cleaned_data['address_5'],
                country_state=state,
                country=country,
                postcode=self.form.cleaned_data['postcode']
            )
            ua.save()
            self.status = 'success'
        except:
            self.status = 'fail'
