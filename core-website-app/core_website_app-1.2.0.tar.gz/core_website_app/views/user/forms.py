""" Form needed for the user part of everything
"""
from django import forms
from core_main_app.commons.fields import CustomPasswordPoliciesField


class RequestAccountForm(forms.Form):
    """
    Form to request an account
    """
    def clean_password_confirm(self):
        """
        Validates that the two new passwords match.
        """
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_confirm')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
        return password2

    username = forms.CharField(label='Username', max_length=100, required=True)
    password = CustomPasswordPoliciesField(label='Password', required=True)
    password_confirm = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=True)
    firstname = forms.CharField(label='First Name', max_length=100, required=True)
    lastname = forms.CharField(label='Last Name', max_length=100, required=True)
    email = forms.EmailField(label='Email Address', max_length=100, required=True)


class ContactForm(forms.Form):
    """
    Form to contact the administrator
    """
    name = forms.CharField(label='Name', max_length=100, required=True)
    email = forms.EmailField(label='Email Address', max_length=100, required=True)
    message = forms.CharField(label='Message', widget=forms.Textarea(attrs={'class': 'textarea_lock_h'}),
                              required=True)
