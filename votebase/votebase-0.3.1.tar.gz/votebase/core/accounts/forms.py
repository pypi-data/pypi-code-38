import hashlib
import random

from django.contrib.auth import get_user_model
from form_utils.forms import BetterModelForm

from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EMPTY_VALUES
from django.utils.translation import ugettext as _

from votebase.core.accounts.helpers import get_profile_model
from votebase.core.accounts.models import Profile
from votebase.core.utils.common import generate_slug_for_user, generate_token
from votebase.core.utils.mixins import PickadayFormMixin

User = get_user_model()

PASSWORD_MIN_SIZE = 5


class RecoveryForm(forms.Form):
    username = forms.EmailField(
        label=_(u'E-mail'), required=True, max_length=settings.MAX_USERNAME_LENGTH)


class LoginForm(forms.Form):
    username = forms.EmailField(
        label=_(u'E-mail'), max_length=settings.MAX_USERNAME_LENGTH,
        required=True,
        widget=forms.TextInput(attrs={'class': 'span3'}))
    password = forms.CharField(
        label=_(u'Password'), min_length=PASSWORD_MIN_SIZE, max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'span3'}))


class RegisterForm(forms.ModelForm):
    username = forms.EmailField(
        label=_(u'E-mail'), required=True, min_length=PASSWORD_MIN_SIZE,
        max_length=settings.MAX_USERNAME_LENGTH, widget=forms.TextInput(attrs={'class': 'span3'}))
    first_name = forms.CharField(
        label=_(u'First name'), required=False, min_length=2, max_length=30,
        widget=forms.TextInput(attrs={'class': 'span3'}))
    last_name = forms.CharField(
        label=_(u'Surname'), required=False, min_length=2, max_length=30,
        widget=forms.TextInput(attrs={'class': 'span3'}))
    password = forms.CharField(
        label=_(u'Password'), required=True, min_length=PASSWORD_MIN_SIZE, max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'span3'}))
    retype = forms.CharField(
        label=_(u'Confirm password'), required=True, min_length=PASSWORD_MIN_SIZE,
        max_length=128, widget=forms.PasswordInput(attrs={'class': 'span3'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password', 'retype')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_(u'A user with that username \
        already exists.'))

    def clean_retype(self):
        password = self.cleaned_data.get('password', '')
        retype = self.cleaned_data.get('retype', None)
        if password != retype:
            raise forms.ValidationError(_(u'The two password fields \
            didn\'t match.'))
        return password

    def save(self, **kwargs):
        data = self.cleaned_data

        #create user
        user = User.objects.create_user(
            username=data.get('username'),
            email=data.get('username'),
            password=data.get('password'),
        )

        #user = User(
        #    username=data.get('username'), email=data.get('username'),
        #    first_name=data.get('first_name'), last_name=data.get('last_name'))
        #user.set_password(data.get('password'))

        user.save()

        # update profile
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()

        # Create new profile
        profile = user.get_profile()
        profile.first_name = first_name
        profile.last_name = last_name
        profile.token = generate_token()

        if first_name in EMPTY_VALUES and last_name in EMPTY_VALUES:
            first_name = _(u'Unknown user')

        profile.slug = generate_slug_for_user(first_name, last_name)

        # Build an activation hash
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        profile.activation_hash = hashlib.sha1(salt + user.username).hexdigest()
        profile.save()

        return user


class SimpleRegisterForm(forms.ModelForm):
    username = forms.EmailField(
        label='', required=True, min_length=PASSWORD_MIN_SIZE,
        max_length=30, widget=forms.TextInput(attrs={'class': 'span3', 'required': 'required', 'placeholder': _(u'E-mail')}))
    password = forms.CharField(
        label='', required=True, min_length=5, max_length=30,
        widget=forms.PasswordInput(attrs={'class': 'span3', 'required': 'required', 'placeholder': _(u'Password')}))

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(_(u'A user with that username \
        already exists.'))

    class Meta:
        model = User
        fields = ('username', 'password')


class PasswordForm(forms.Form):
    old_password = forms.CharField(
        label=_(u'Old password'), required=True, min_length=PASSWORD_MIN_SIZE,
        widget=forms.PasswordInput(attrs={'class': 'span3'}))
    new_password = forms.CharField(
        label=_(u'New password'), required=True, min_length=PASSWORD_MIN_SIZE,
        widget=forms.PasswordInput(attrs={'class': 'span3'}))
    retype = forms.CharField(
        label=_(u'Retype password'), required=True,
        min_length=PASSWORD_MIN_SIZE,
        widget=forms.PasswordInput(attrs={'class': 'span3'}))

    def __init__(self, user, *args, **kwargs):
        super(PasswordForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        data = self.cleaned_data
        if self.user.check_password(data.get('old_password', None)) is False:
            raise forms.ValidationError(_(u'Old password is not correct'))
        return data.get('old_password')

    def clean_retype(self):
        data = self.cleaned_data

        if data.get('new_password', None) != data.get('retype', None):
            raise forms.ValidationError(_(u'New and retyped password \
            must be same.'))

        return data.get('retype', None)

    def save(self):
        data = self.cleaned_data
        self.user.set_password(data['new_password'])
        self.user.save()


class UserForm(forms.ModelForm):
    first_name = forms.CharField(
        label=_(u'First name'), required=True, min_length=2, max_length=30)
    last_name = forms.CharField(
        label=_(u'Surname'), required=True, min_length=2, max_length=30)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', )


class ProfileForm(PickadayFormMixin, BetterModelForm):
    date_of_birth = forms.DateField(
        required=False,
        label=_(u'Date of birth'),
        input_formats=settings.DATE_INPUT_FORMATS,
        widget=forms.DateInput(format=settings.DATE_FORMAT, attrs={
            'class': 'datepicker span3',
        })
    )

    class Meta:
        model = get_profile_model()
        fieldsets = [
            (_(u'Public options'), {
                'fields': ['slug', ],
            }),
            (_(u'Private information'), {
                'fields': ['first_name', 'last_name', 'gender', 'date_of_birth']
            })
        ]
        widgets = {
            'slug': forms.TextInput(attrs={'class': 'span3'}),
            'first_name': forms.TextInput(attrs={'class': 'span3'}),
            'last_name': forms.TextInput(attrs={'class': 'span3'}),
            'gender': forms.Select(attrs={'class': 'span3'}),
        }

    def __init__(self, request, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        self.user = request.user
        self.request = request
        if 'slug' in self.fields:
            self.fields['slug'].required = False
            self.fields['slug'].help_text = _(
                u'Slug used to customize sharing URL. For example my-segment.'
                u' Keep blank to be autogenerated by your name.')

        if 'gender' in self.fields:
            self.fields['gender'].empty_label = None
            self.fields['gender'].label = _(u'Gender')
            self.fields['gender'].choices = (('m', _(u'Male')), ('f', _(u'Female')))
            self.fields['gender'].help_text = _(
                u'Stay calm, your privacy is safe. '
                u'It will be used for statistical purposes only')

        if 'date_of_birth' in self.fields:
            self.fields['date_of_birth'].help_text = _(
                u'Stay calm, your privacy is safe. '
                u'It will be used for statistical purposes only')
        self.fix_fields(*args, **kwargs)

    def clean_slug(self):
        slug = self.cleaned_data.get('slug', None)

        if slug is not None and slug not in EMPTY_VALUES:
            slug = slug.strip()
        else:
            return None

        try:
            profile = Profile.objects.get(slug=slug)
            if profile.user == self.user:
                return slug
            raise forms.ValidationError(_('URL is already taken.'))
        except ObjectDoesNotExist:
            return slug

    def clean(self):
        cleaned_data = self.cleaned_data

        if cleaned_data.get('slug', None) is None:
            first_name = cleaned_data.get('first_name', '').strip()
            last_name = cleaned_data.get('last_name', '').strip()
            if first_name in EMPTY_VALUES and last_name in EMPTY_VALUES:
                first_name = _(u'Unknown user')
            cleaned_data['slug'] = generate_slug_for_user(first_name, last_name)

        if len(self._errors):
            messages.error(self.request, _(u'Saving failed. Check your inputs.'))

        return cleaned_data
