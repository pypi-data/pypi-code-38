# -*- coding: utf-8 -*-
from congo.communication.classes import SimpleEmailMessage
from congo.conf import settings
from congo.maintenance import get_current_site
from congo.utils.form import add_widget_css_class
from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm as DjAuthenticationForm, SetPasswordForm as DjSetPasswordForm, PasswordResetForm as DjPasswordResetForm
from django.contrib.auth.models import UserManager as DjUserManager
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
import re

password_widget = forms.PasswordInput(attrs = {'autocomplete':'off'})

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length = 60, required = False, label = _('First name'))
    last_name = forms.CharField(max_length = 80, required = False, label = _('Last name'))
    email = forms.EmailField(widget = forms.TextInput(), label = _(u'Adres e-mail'))
    password1 = forms.CharField(max_length = 255, widget = password_widget, label = _(u"Hasło"), help_text = _(u"Przynajmniej 8 znaków, użyj liczb i liter."))
    password2 = forms.CharField(max_length = 255, widget = password_widget, label = _(u"Potwierdź hasło"))

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        model = get_user_model()

        if model.objects.filter(email = email).exists():
            raise forms.ValidationError(_(u"Użytkownik z podanym adresem e-mail już istnieje"))

        return email

    def clean_password1(self):
        password = self.cleaned_data['password1']

        if len(password) < 8:
            raise forms.ValidationError(_(u"Hasło jest zbyt krótkie. Minimalna długość hasła to 8 znaków."))
        elif not re.compile('^.*(?=.*\d)(?=.*[a-zA-Z]).*$').search(password):
            raise forms.ValidationError(_(u"Hasło musi zawierać co najmniej jedną literę i jedną cyfrę."))

        return password

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()

        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        accept_newsletter = cleaned_data.get('accept_newsletter')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', _(u"Wprowadzone hasła nie pasują do siebie."))

        if accept_newsletter and not (first_name or last_name):
            self.add_error('first_name', _(u"Aby zostać naszym subskrybentem, wpisz swoje imię."))

        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = get_user_model().objects.create_user(DjUserManager.normalize_email(data['email']), data['password1'])
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.is_active = False
        user.save()

        return user

class AuthenticationForm(DjAuthenticationForm):
    def __init__(self, request = None, *args, **kwargs):
        super(AuthenticationForm, self).__init__(request, *args, **kwargs)

        self.fields['username'].label = _(u"Twój e-mail")
        self.error_messages['invalid_login'] = _(u"Wprowadź poprawny adres e-mail oraz hasło. Wielkość liter ma znaczenie.")
        self.error_messages['inactive'] = _(u"Konto nie jest aktywne.")

class SetPasswordForm(DjSetPasswordForm):
    new_password1 = forms.CharField(label = _(u"Nowe hasło"), widget = forms.PasswordInput, help_text = _(u"Przynajmniej 8 znaków, użyj liczb i liter."))
    new_password2 = forms.CharField(label = _(u"Potwierdź nowe hasło"), widget = forms.PasswordInput)

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        password_validation.validate_password(password, self.user)
        return password

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_(u"Wprowadzone hasła nie pasują do siebie."))
        return password2

class PasswordChangeForm(SetPasswordForm):
    old_password = forms.CharField(label = _(u"Aktualne hasło"), widget = forms.PasswordInput)

    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(_(u"Aktualne hasło zostało wprowadzone błędnie. Wprowadź je ponownie."))
        return old_password
PasswordChangeForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']

class PasswordResetForm(DjPasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].label = _(u"Twój e-mail")
#        add_widget_css_class(self, 'form-control')

    def clean_email(self):
        email = self.cleaned_data["email"]
        model = get_user_model()

        self.users_cache = model.objects.filter(email__iexact = email)
        if not len(self.users_cache):
            raise forms.ValidationError(_(u"Ten adres e-mail nie ma skojarzonego konta użytkownika. Czy jesteś pewien, że jesteś zarejestrowany?"))
        if any((not user.has_usable_password()) for user in self.users_cache):
            raise forms.ValidationError(_(u"Użytkownik związany z tym adresem e-mail nie może zresetować hasła."))
        return email

    def save(self, *args, **kwargs):
        for user in self.users_cache:
            if user.first_name or user.last_name:
                recipient_name = ("%s %s" % (user.first_name, user.last_name)).strip()
            else:
                recipient_name = None

            subject = _(u"Resetowania hasła")
            site = get_current_site()

            data_dict = {
                'email': user.email,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'user': user,
                'token': default_token_generator.make_token(user),
                'protocol': 'https' if settings.CONGO_SSL_ENABLED else 'http',
            }

            email_message = SimpleEmailMessage(subject, recipient_email = user.email, recipient_name = recipient_name, data_dict = data_dict, site = site, template = "password_reset")
            email_message.send()

# For the purposes of Django Admin

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label = _(u"Hasło"), widget = forms.PasswordInput)
    password2 = forms.CharField(label = _(u"Powtórz hasło"), widget = forms.PasswordInput, help_text = _(u"Wpisz to samo hasło jak wyżej, w celu weryfikacji."))

    class Meta:
        model = get_user_model()
        fields = ('email',)

    def clean_username(self):
        model = get_user_model()
        email = self.cleaned_data["email"]

        if model.objects.filter(email = email).exists():
            raise forms.ValidationError(_(u"Użytkownik z podanym adresem e-mail już istnieje"))
        else:
            return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        password_validation.validate_password(password)
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_(u"Wprowadzone hasła nie pasują do siebie."))
        return password2

    def save(self, commit = True):
        user = super(UserCreationForm, self).save(commit = False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label = _(u"Hasło"), help_text = _(u"Czyste hasła nie są zapisywane, więc nie ma możliwości aby zobaczyć hasło użytkownika, ale możesz zmienić hasło używając <a href=\"../password/\">tego formularza</a>."))

    class Meta:
        model = get_user_model()
        # @OG "django.core.exceptions.ImproperlyConfigured: Creating a ModelForm without either the 'fields' attribute or the 'exclude' attribute is prohibited; form UserChangeForm needs updating."
        # Zostawiam to dla Ciebie...
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        field = self.fields.get('user_permissions', None)
        if field is not None:
            field.queryset = field.queryset.select_related('content_type')

    def clean_password(self):
        return self.initial["password"]
