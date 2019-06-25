from django import forms

from crispy_forms.helper import FormHelper


class MiscForm(forms.Form):
    notes = forms.CharField(
        label='Special Needs and Notes for the registration team',
        help_text='Anything else you need to describe. '
                  'The registration team will see this. '
                  'The bursaries team will not.',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False
