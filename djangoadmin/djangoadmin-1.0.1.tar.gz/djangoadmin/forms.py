from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserChangeForm
from .models import UserModel


""" start your custom form here. """
#Registration form
class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model  = User

        fields = [
            'username', 'email',
            'password1', 'password2'
        ]

        labels = {
            'username' : 'Username',
            'email' : 'Email',
            'password1': 'Password',
            'password2': 'Password confirmation',
        }
# end form here.
""" end your custom form here. """


""" start your custom form here. """
#AuthenticationForm form
class SigninForm(AuthenticationForm):

    class Meta:
        model  = User

        fields = [
            'username', 'password',
        ]

        labels = {
            'username' : 'Username',
            'password': 'Password',
        }
# end form here.
""" end your custom form here. """


""" start your custom form here. """
#EditProfileForm form
class EditProfileForm(UserChangeForm):

    class Meta:
        model  = User

        fields = [
            'username', 'first_name', 'last_name',
            'email', 'password'
        ]

        labels = {
            'username': 'Username',
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'Email',
            'password': 'Password'
        }

        widgets = { 
            'username': forms.TextInput(attrs={'type': 'text', 'placeholder':'Username'}),
            'first_name': forms.TextInput(attrs={'type': 'text', 'placeholder':'First name'}),
            'last_name': forms.TextInput(attrs={'type': 'text', 'placeholder':'Last name'}),
            'email': forms.EmailInput(attrs={'type': 'email', 'placeholder': 'Email'})
        }
# end form here.
""" end your custom form here. """


""" start userform here. """
# start here.
class UserForm(ModelForm):
    
    class Meta:
        model = UserModel

        fields = ['image', 'address', 'phone', 'website']

        labels = {
            'image': 'Image',
            'address': 'Address',
            'phone': 'Phone',
            'website': 'Website',
        }

        widgets = { 
            'image': forms.ClearableFileInput(attrs={'type': 'file'}),
            'address': forms.TextInput(attrs={'type': 'text', 'placeholder':'Address'}),
            'phone': forms.NumberInput(attrs={'type': 'number', 'placeholder':'Phone number'}),
            'website': forms.URLInput(attrs={'type': 'url', 'placeholder': 'Website url'})
        }
# end here.
""" end userform here. """
