from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout


class ChildCareForm(forms.Form):
    child_care = forms.BooleanField(
        label='I need child-care for my kid(s)',
        required=False,
    )
    needs = forms.CharField(
        label='The child care services I need are',
        help_text='How many hours a day? All the conference or only part of '
                  'it? etc.',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
    details = forms.CharField(
        label='Important informations about my kid(s)',
        help_text='Number, ages, languages spoken, special needs, etc.',
        widget=forms.Textarea(attrs={'rows': 5}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False

        self.helper.layout = Layout(
            Field('child_care', id='child_care'),
            Fieldset(
                'Childcare Details',
                'needs',
                'details',
                css_id='details',
            ),
        )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('child_care'):
            if not cleaned_data.get('needs'):
                self.add_error('needs', 'Please provide us with your needs.')
            if not cleaned_data.get('details'):
                self.add_error(
                    'details',
                    "Please provide us with your children's details.")

        return cleaned_data
