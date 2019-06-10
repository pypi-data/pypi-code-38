from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import EmailModel


""" Start EmailForm. """
# start contact form here.
class EmailForm(ModelForm):

    class Meta:

        model = EmailModel

        fields = ['from_email', 'phone_number', 'full_name',
                  'subject', 'content' ]

        labels = {'from_email': 'Company"s email',
                  'phone_number' : 'Your phone',
                  'full_name' : 'Full Name',
                  'subject' : 'Subject',
                  'content' : 'Message' }

        widgets = {'from_email' :  forms.EmailInput(attrs={"type": "email", "id": "email", "name": "email input", "placeholder": "Email"}),
                   'phone_number': forms.NumberInput(attrs={"type": "number", "id": "phone", "name": "phone input", "placeholder": "Phone number"}),
                   'full_name': forms.TextInput(attrs={"type":"text", "id": "full-name", "name": "full name input", "placeholder": "Fullname"}),
                   'subject': forms.TextInput(attrs={"type":"text", "id": "subject", "name": "subject input", "placeholder": "subject"}),
                   'content': forms.Textarea(attrs={"id": "content", "name": "content input", "placeholder": "message", "rows": "3"}) }

    # django form field level validation.
    def clean_phone_number(self, *args, **kwargs):
        phone_number = self.cleaned_data.get('phone_number')

        if phone_number == 1234567890:
            raise forms.ValidationError("Phone number is invalid.")
        else:
            return phone_number
# End contact form here.
""" End EmailModel here. """