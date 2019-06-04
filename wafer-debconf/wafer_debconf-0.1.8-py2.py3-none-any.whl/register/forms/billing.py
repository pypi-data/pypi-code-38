from django import forms

from crispy_forms.helper import FormHelper


class BillingForm(forms.Form):
    invoiced_entity = forms.CharField(
        label='Company',
        help_text='If you want your company to be named on the invoice, '
                  'name them here. '
                  'If blank, the invoice will be made out to you.',
        required=False,
    )
    billing_address = forms.CharField(
        label='My billing address',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        attendee = kwargs.pop('attendee')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False

        self.billable = attendee.billable()

    def clean(self):
        cleaned_data = super().clean()
        if self.billable and not cleaned_data.get('billing_address'):
            self.add_error('billing_address',
                           'Paid attendees need to provide a billing address')
