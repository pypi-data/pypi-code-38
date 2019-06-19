# -*- coding: utf-8 -*-
"""Views for authentication

In this views, authentication views are composited with GenericAPIView
(of rest_framework) and mixins, which is implemented for process views.

Because, we didn't know what methods you use for process business logics.
You can construct your own views by extending our mixins.

(rest_framework's generic views used this strategy)
"""

from __future__ import unicode_literals

import functools

from django.conf import settings
from django.contrib.auth import (
    logout as auth_logout,
)
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    SuccessURLAllowedHostsMixin,
)
from django.utils.decorators import method_decorator
from django.utils.module_loading import import_string
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from rest_framework import (
    generics, permissions, response, status, views,
)

from .contrib.rest_framework.decorators import sensitive_post_parameters
from .serializers import (
    PasswordChangeSerializer,
    PasswordResetSerializer,
)


class LoginMixin(SuccessURLAllowedHostsMixin):
    """Mixin for logging-in
    """
    # TODO return 302 if needed.
    # redirect_url = False
    response_includes_data = False
    """Set this to ``True`` if you wanna send user data (or more)
    when authentication is successful. (default: ``False``)
    """

    serializer_class = None
    """You should make your own serializer class if you cusomize
    auth backend and this backend are not satisfied by ``LoginSerializer``.

    (accept other than ``username`` and ``password``.
    (e.g ``RemoteUserBackend``)
    """

    def get_serializer_class(self):
        serializer_class = import_string(
            settings.REST_AUTH_LOGIN_SERIALIZER_CLASS
        )
        return serializer_class

    def login(self, request, *args, **kwargs):
        """Main business logic for loggin in

        :exception ValidationError: auth failed, but it will be handled\
        by rest_frameworks error handler.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(request=request)

        data = self.get_response_data(serializer.data)
        headers = self.get_success_headers(serializer.data)

        return response.Response(
            data, status=status.HTTP_200_OK, headers=headers,
        )

    def get_response_data(self, data):
        """Override this method when you use ``response_includes_data`` and
        You wanna send customized user data (beyond serializer.data)
        """
        empty = settings.REST_AUTH_LOGIN_EMPTY_RESPONSE

        if not empty:
            return data

    def get_success_headers(self, data):
        return {}


class LoginView(LoginMixin, generics.GenericAPIView):
    """LoginView for REST-API.
    """
    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        """Just calls ``LoginMixin.login``
        """
        return self.login(request, *args, **kwargs)


class LogoutView(views.APIView):
    """LogoutView for user logout.
    """
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request, *args, **kwargs):
        """Logout a user. performed by ``django.contrib.auth.logout``

        No data is to sent.
        """
        auth_logout(request)
        return response.Response(None, status=status.HTTP_200_OK)


class PasswordForgotMixin(object):
    """View for sending password-reset-link.
    """
    serializer_class = PasswordResetSerializer

    def forgot(self, request, *args, **kwargs):
        """Sends a password-reset-link to requested email.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email_opts = self.get_email_opts(request=request)
        serializer.save(**email_opts)

        return response.Response(None, status=status.HTTP_200_OK)

    def get_email_opts(self, **opts):
        """Override this method to add more options for sending emails.
        """
        email_opts = {}
        email_opts.update(settings.REST_AUTH_EMAIL_OPTIONS)
        email_opts.update(opts)

        return email_opts


class PasswordForgotView(PasswordForgotMixin, generics.GenericAPIView):
    """sending password-reset email to user.
    """

    def post(self, request, *args, **kwargs):
        """
        """
        return self.forgot(request, *args, **kwargs)


class PasswordForgotConfirmView(PasswordResetConfirmView):
    """django-rest-auth's password reset confirmation just adopts django's one.
    This idea is under assumption, which password reset confirmation
    should be done, by clicking password-reset-url we sent and moving to
    webpage to change password.
    """


class PasswordResetDoneView(PasswordResetCompleteView):
    """adopts django's password reset complete view.
    """


class PasswordChangeMixin(object):
    """Change password for a user.
    """
    serializer_class = PasswordChangeSerializer

    def get_serializer_class(self):
        # HACK `PasswordChangeSerializer` requires `user` as a first param in
        # __init__, so we should bind it to that class for all HTTP methods.
        klass = super(PasswordChangeMixin, self).get_serializer_class()
        return functools.partial(klass, self.request.user)

    def reset(self, request, *args, **kwargs):
        """Reset password.
        No data is to sent.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(None)


class PasswordChangeView(PasswordChangeMixin, generics.GenericAPIView):
    """View for change password.
    """
    permission_classes = (permissions.IsAuthenticated, )

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def post(self, request, *args, **kwargs):
        """
        """
        return self.reset(request, *args, **kwargs)
