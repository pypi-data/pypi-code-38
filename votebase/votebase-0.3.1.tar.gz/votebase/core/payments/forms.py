from form_utils.forms import BetterModelForm
from django.utils.translation import ugettext_lazy as _
from votebase.core.payments.models import Information


class InformationForm(BetterModelForm):
    class Meta:
        model = Information
        fieldsets = [
            (_(u'Contact information'), {
                'fields': ['first_name', 'last_name', 'phone']
            }),
            (_(u'Company details (if needed)'), {
                'fields': ['company_name',
                           'company_id', 'company_tax_id', 'company_vat']
            }),
            (_(u'Address'), {
                'fields': ['street_and_number', 'city', 'zip', 'country']
            }),
        ]
