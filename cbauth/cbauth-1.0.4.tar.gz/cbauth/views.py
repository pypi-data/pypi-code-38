import logging

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.edit import FormMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import (
    PasswordResetForm
)
from django.contrib.auth.views import (
    PasswordResetConfirmView
)


from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters


logger = logging.getLogger('simple')


# RESTfull API Views
# ---------------------------------------------------------
class AuthMixin(object):
    def get(self, request, *args, **kwargs):
        response = {
            'message': _(u'Only POST method is allowed')
        }
        return Response(response, status=405)


class APIMeView(generics.GenericAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        """
        Returns user information
        """

        user = request.user
        if not user.is_anonymous:
            refresh = RefreshToken.for_user(user)
            data = {
                'username': user.username,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'no user'}, status=403)


class APILoginView(AuthMixin, generics.GenericAPIView):
    """
    Async Login API endpoint
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request, data=request.data)
        if form.is_valid():

            user = form.get_user()

            if getattr(settings, 'CB_GENERATE_COOKIE', False):
                login(request, user)

            refresh = RefreshToken.for_user(user)

            response = {
                'username': user.username,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }

            return Response(response)
        else:
            response = {
                'errors': form.errors
            }
            return Response(response, status=400)


class APILogoutView(AuthMixin, generics.GenericAPIView):
    """
    Async Logout API endpoint
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        header = request.META.get('HTTP_AUTHORIZATION')

        if header is not None:
            try:
                token = RefreshToken(header)
                token.blacklist()
            except Exception as e:
                logger.error(e)

        logger.info(request.COOKIES)
        logout(request)

        return Response({"detail": _("Successfully logged out.")},
                        status=status.HTTP_200_OK)


class APIPasswordResetView(generics.GenericAPIView, FormMixin):
    permission_classes = (permissions.AllowAny,)
    from_email = None
    form_class = PasswordResetForm
    token_generator = default_token_generator
    email_template_name = 'auth.password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    html_email_template_name = None

    def get_initial(self):
        return {}

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            response = {
                'errors': form.errors
            }
            return Response(response, status=400)

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': None,
        }
        form.save(**opts)

        return Response({
            "detail": _(
                "We've emailed you instructions for setting your "
                "password, if an account exists with the email you entered. "
                "You should receive them shortly."
            )
        })


class APIPasswordResetConfirmView(generics.GenericAPIView,
                                  PasswordResetConfirmView):
    permission_classes = (permissions.AllowAny,)

    def get_initial(self):
        return {}

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        logger.info(">>> dispatching")
        self.args = args
        self.kwargs = kwargs
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if self.token_generator.check_token(self.user, token):
                self.validlink = True
                return super().dispatch(request, *args, **kwargs)

        logger.info(">>> dispatching END")
        self.response = Response({
            "detail": _(
                "The password reset link was invalid, possibly because it has "
                "already been used.  Please request a new password reset."
            )
        }, status=403)
        request = self.initialize_request(request, *args, **kwargs)
        self.response = self.finalize_response(request, self.response, *args,
                                               **kwargs)
        return self.response

    def get(self, request, *args, **kwargs):
        return Response({
            "detail": _("The password reset link is valid.")
        }, status=200)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            response = {
                'errors': form.errors
            }
            return Response(response, status=400)

    def form_valid(self, form):
        form.save()
        return Response({
            'detail': _("Password changed successfully")
        }, status=200)
