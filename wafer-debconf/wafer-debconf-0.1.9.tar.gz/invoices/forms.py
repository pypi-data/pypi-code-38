from django import forms
from django.core.signing import BadSignature

from crispy_forms.helper import FormHelper

from invoices.models import Invoice


class InvoiceForm(forms.Form):
    url = forms.URLField(
        label='URL',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False

    def clean_url(self):
        url = self.cleaned_data['url']
        invalid_url_error = 'Needs to a be a valid URL for a visible invoice'

        # The URL validator should have ensured that we have enough slashes to
        # do things like this
        reference_number = url.rstrip('/').rsplit('/', 1)[1]
        signed_url = ':' in reference_number
        if signed_url:
            try:
                reference_number = Invoice.signer.unsign(reference_number)
            except BadSignature:
                raise forms.ValidationError(invalid_url_error)

        try:
            invoice = Invoice.objects.get(reference_number=reference_number)
        except Invoice.DoesNotExist:
            raise forms.ValidationError(invalid_url_error)

        if self.user != invoice.recipient and not signed_url:
            raise forms.ValidationError(invalid_url_error)

        if invoice.status != 'new':
            raise forms.ValidationError('Invoice is not unpaid')

        if invoice.compound:
            raise forms.ValidationError('This is a combined invoice, itself')

        self.invoice = invoice

        return url


class InvoiceFormset(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        invoices = []
        for form in self.forms:
            if hasattr(form, 'invoice'):
                invoices.append(form.invoice.pk)

        if len(invoices) > len(set(invoices)):
            raise forms.ValidationError('Invoices must be distinct')

        if len(invoices) < 2:
            raise forms.ValidationError(
                'At least 2 URLs need to be provided for any combining to '
                'happen.')


class CombineForm(forms.Form):
    invoiced_entity = forms.CharField(
        label='Invoiced entity',
    )
    billing_address = forms.CharField(
        label='Billing address',
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False
