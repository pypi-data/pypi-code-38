# -*- coding: utf-8 -*-
"""Serializer implementations for authentication.
"""

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer for rest_framework & AUTH_USER_MODEL.

    Fields & methods are built on a django's defualt ``User`` model.
    Extend this serializer if you need your custom user model.

    (Even if ``AUTH_USER_MODEL`` is can be customized, this is recommended
    that You don't change & use customized user model.
    using custom user model is very complex.)

    :param username: ``USERNAME_FIELD`` of ``AUTH_USER_MODEL``
    :param email: ``User.get_email_field_name()``
    :param password1: password of a user (write_only, used only when created)
    :param password2: password confirmation (write_only)

    :TODO: Serializer Only implements creating. list/get are need to be implmtd
    """
    password1 = serializers.CharField(
        label=_('Password'),
        validators=[password_validation.validate_password],
        help_text=password_validation.password_validators_help_text_html(),
        write_only=True,
        style={'input_type': 'password'},
    )
    password2 = serializers.CharField(
        label=_('Password Confirmation'),
        help_text=_('Enter the same password as before, for verification.'),
        write_only=True,
        style={'input_type': 'password'},
    )

    default_error_messages = {
        'password_mismatch': _('2 passwords should be equal'),
    }

    class Meta:
        model = UserModel
        fields = (
            UserModel.USERNAME_FIELD, UserModel.get_email_field_name(),
            'password1', 'password2',
        )

        extra_kwargs = {
            UserModel.get_email_field_name(): {
                'required': True,
                'allow_blank': False,
            },
        }

    def validate(self, data):
        """Vaildates if two passwords are equal.

        :exception ValidationError: when 2 passwds are different
        """
        password1 = data.get('password1')
        password2 = data.get('password2')

        data['password2'] = self._validate_password2(password1, password2)

        return data

    def _validate_password2(self, password1, password2):
        if password1 != password2:
            raise serializers.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        return password2

    def create(self, validated_data):
        """Creates user instance

        CAVEAT:

        A clear difference between django's ``ModelForm`` and rest_framework's
        ``ModelSerializer`` is that, model serializer's ``save`` method doesn't
        respect form's ``commit=True``.

        Inside ``super().create``, a query is fired to create user,
        and inside this, additional query is fired to save hashed password.
        It's because ``ModelSerializer``'s ``create`` method uses
        default manager's create function, ``Model._default_manager.create()``

        (User model creation is recommended by calling ``UserManager``'s
        ``create_user`` method)

        :param validated_data: validated data created after ``self.vaildate``
        """
        password = validated_data.pop('password1')
        validated_data.pop('password2')

        # NOTE We should set user's password manually because
        # ModelSerializer.create calls model._default_manager.save().
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(password)

        # TODO: user activation through email confirmation.
        require_email_confirmation = getattr(
            settings, 'REST_AUTH_SIGNUP_REQUIRE_EMAIL_CONFIRMATION', False
        )

        if require_email_confirmation:
            user.is_active = False

        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for loggin in.
    It checks username and password are correct for settings.AUTH_USER_MODEL.

    After validating it, ``user`` instance created for authenticated user.
    View methods should persist this user.
    (through ``django.contrib.auth.login``)

    :param username: ``USERNAME_FIELD`` for AUTH_USER_MODEL
    :param password: user's password

    :TODO: It fits only ModelBackend of django. need to take\
    other authentication backends.
    """
    username = serializers.CharField(
        label=_('Username'), max_length=254,
    )

    password = serializers.CharField(
        label=_('Password'), write_only=True,
        style={'input_type': 'password'},
    )

    default_error_messages = {
        'invalid_login': _(
            'Please enter a correct username and password. '
            'Note that both fields may be case-sensitive.'
        ),
        'inactive': _('This account is inactive.'),
    }

    def validate(self, data):
        """Checks username & password.
        uses ``django.contrib.auth.authenticate``

        :param data: validated data from ``Serializer.validate``
        :return: validated_data
        :exception VaildationError: if username or password are incorrect
        """
        username = data['username']
        password = data['password']

        self.user = auth.authenticate(username=username, password=password)
        if self.user is None:
            raise serializers.ValidationError(
                self.error_messages['invalid_login'], code='invalid_login',
            )

        self.confirm_login_allowed(self.user)

        return data

    def confirm_login_allowed(self, user):
        """Checks if validated user is allowed for website.

        Override this method if you use custom authentication method
        and have additional methods for allowing login.

        :exception VaildationError: if user are not allowed
        """

        # XXX NOTE This condition doesn't have any effects
        # if you use `django.contrib.auth.backends.ModelBackend`
        # It's useful just for custom backends
        if not user.is_active:
            raise serializers.ValidationError(
                self.error_messages['inactive'], code='inactive',
            )

    def get_user(self):
        """
        :return: ``user`` instance created after ``self.validate``
        """
        return self.user


class PasswordResetSerializer(serializers.Serializer):
    """Sends a website link for resetting password.
    It uses django's ``PasswordResetForm`` directly because
    there is just one required field, `email`, and form implemented
    its business logic nicely.

    :param email: email address to receive password-reset-link.
    """
    email = serializers.EmailField(
        label=_('Email'), max_length=254,
    )

    password_reset_form_class = PasswordResetForm

    def validate_email(self, value):
        """
        :exception VaildationError: ``rest_framework``'s field validation
        :exception VaildationError: ``django``'s field vaildation
        """
        self.form = self.password_reset_form_class(data=self.initial_data)
        if not self.form.is_valid():
            if 'email' in self.form.errors:
                raise serializers.ValidationError(self.form.errors['email'])
            # XXX non email errors should be catched & re-raised
            # (if django's PasswordResetForm add new fields)

        return value

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=True, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):
        """sends a email, which contains link for resetting password
        """

        return self.form.save(
            domain_override=domain_override,
            subject_template_name=subject_template_name,
            email_template_name=email_template_name, use_https=use_https,
            token_generator=token_generator, from_email=from_email,
            request=request, html_email_template_name=html_email_template_name,
            extra_email_context=extra_email_context,
        )


class SetPasswordSerializer(serializers.Serializer):
    """This serializer resets password of a given user.
    Please be VERY CAREFUL for using this any given user's password
    can be changed.

    Setting permission IsAdminUser is recommended.

    :param new_password1: new password
    :param new_password2: new password confirmation.
    """
    new_password1 = serializers.CharField(
        label=_('New password'),
        validators=[password_validation.validate_password],
        help_text=password_validation.password_validators_help_text_html(),
        write_only=True,
        style={'input_type': 'password'},
    )

    new_password2 = serializers.CharField(
        label=_('New password confirmation'),
        help_text=_('Enter the same password as before, for verification.'),
        write_only=True,
        style={'input_type': 'password'},
    )

    default_error_messages = {
        'password_mismatch': _('2 passwords should be equal'),
    }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordSerializer, self).__init__(*args, **kwargs)

    def validate(self, data):
        """
        :exception VaildationError: if two given passwords are different.
        """
        password1 = data.get('new_password1')
        password2 = data.get('new_password2')

        data['new_password2'] =\
            self._validate_new_password2(password1, password2)

        return data

    def _validate_new_password2(self, password1, password2):
        if password1 != password2:
            raise serializers.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        return password2

    def create(self, validated_data):
        """resets password
        """
        password = validated_data['new_password1']
        self.user.set_password(password)
        self.user.save()

        return self.user


class PasswordChangeSerializer(SetPasswordSerializer):
    """resets password of user.
    Resetting password is done if old_password is correct and
    two new passwords are equals.

    :param old_password: old_password
    :param new_password1: new password
    :param new_password2: new password confirmation.
    """
    old_password = serializers.CharField(
        label=_('Old password'),
        write_only=True,
        style={'input_type': 'password'},
    )

    default_error_messages = {
        'password_incorrect': _('Your old password was entered incorrectly. '
                                'Please enter it again.'),
    }

    def validate_old_password(self, old_password):
        """
        :exception ValidationError: if old_password is not correct
        """
        if not self.user.check_password(old_password):
            raise serializers.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect'
            )

        return old_password
