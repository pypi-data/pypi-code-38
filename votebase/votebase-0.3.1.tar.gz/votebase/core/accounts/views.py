from smtplib import SMTPRecipientsRefused
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic.base import TemplateResponseMixin, View, TemplateView
from django.views.generic.edit import FormView

from votebase.core.accounts.forms import LoginForm, \
    PasswordForm, ProfileForm, RecoveryForm, SimpleRegisterForm
from votebase.core.accounts.helpers import get_profile_model
from votebase.core.utils import mail
from votebase.core.utils.common import generate_token
from votebase.core.utils.helpers import get_class


AFTER_LOGIN = 'surveys_index'
AFTER_REGISTRATION = 'surveys_index'


Profile = get_profile_model()
User = get_user_model()


class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return redirect(AFTER_LOGIN)

        request.breadcrumbs([
            (_(u'Login'), reverse('accounts_login')),
        ])
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(AFTER_LOGIN)

    def form_valid(self, form):
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'])

        if user is None:
            messages.error(
                self.request, _(u'Your username or password was incorrect.'))
            return_url = reverse('accounts_login')

            if 'next' in self.request.GET:
                return_url += '?next=' + self.request.GET['next']
            return redirect(return_url)

        elif user.is_active is True:
            self.request.session['ppc_google'] = 'login'
            login(self.request, user)

            if 'next' in self.request.GET:
                return redirect(self.request.GET['next'])
        else:
            messages.error(self.request, _(u'Your account is not active!'))
            messages.info(self.request, _(u'Please, check your email and activate your account.'))

        return super(LoginView, self).form_valid(form)


class LoginAsDemoView(View):
    def get(self, request):
        try:
            user = User.objects.get(username='demo')
            user = authenticate(username='demo', password='demo')
            login(self.request, user)
            return redirect('surveys_index')
        except ObjectDoesNotExist:
            return redirect('home')


class RegisterView(FormView):
    template_name = 'accounts/register.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(AFTER_LOGIN)

        request.breadcrumbs([
            (_(u'Registration'), reverse('accounts_register')),
        ])

        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        if self.request.GET.get('type') == 'quick':
            return SimpleRegisterForm

        register_form_class_name = getattr(settings, 'VOTEBASE_REGISTER_FORM', 'votebase.core.accounts.forms.RegisterForm')
        return get_class(register_form_class_name)

    def get_success_url(self):
        if 'next' in self.request.GET:
            return self.request.GET['next']

        return reverse(AFTER_REGISTRATION)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, _(u'You have been successfully registered.'))

        # Send activation email
        if settings.REQUIRED_ACTIVATION:
            user.is_active = False
            user.save()
            mail.registration(self.request, user)

            messages.info(self.request, _(u'Please, check your email and activate your account.'))
        else:
            user = authenticate(username=user.username, password=form.data.get('password'))
            login(self.request, user)

        return super(RegisterView, self).form_valid(form)


class ActivateView(View, TemplateResponseMixin):
    def get(self, request, activation_hash):
        if activation_hash is None:
            messages.add_message(
                request, messages.ERROR,
                _(u'Activation key is missing!'))
            return redirect('accounts_login')

        try:
            # Grab user profile
            profile = Profile.objects.get(activation_hash=activation_hash)

            # Get user
            user = User.objects.get(pk=profile.user_id)

            if not user.is_active:
                # Activate the user account
                user.is_active = True
                user.save()

                messages.add_message(
                    request, messages.SUCCESS,
                    _(u'Your account was successfully activated.'))
            else:
                messages.add_message(
                    request, messages.ERROR,
                    _(u'You have already activated your account!'))

            # Authenticate
            #user = authenticate(username =
            # user.username, password = user.password)
            user.backend = 'django.contrib.auth.backends.ModelBackend'

            # Login user
            login(request, user)

            # redirect to user main screen
            return redirect(AFTER_LOGIN)

        except ObjectDoesNotExist:
            messages.add_message(
                request, messages.ERROR,
                _(u'Your activation key is incorrect!'))
        return redirect('accounts_login')


class ProfileView(FormView):
    template_name = 'accounts/profile.html'
    form_class = ProfileForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self._set_profile(request)

        request.breadcrumbs([
            (_(u'Account'), reverse('accounts')),
            (_(u'Profile'), reverse('accounts_profile')),
        ])
        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def _set_profile(self, request):
        try:
            self.profile = request.user.get_profile()
        except ObjectDoesNotExist:
            self.profile = Profile.objects.create(user=request.user)
            self.profile.token = generate_token()
            self.profile.save()

    def form_valid(self, form):
        form.save()

        messages.success(self.request, _(u'Profile successfully saved.'))
        return super(ProfileView, self).form_valid(form)

    def get_form_kwargs(self):
        form_kwargs = super(ProfileView, self).get_form_kwargs()
        form_kwargs.update({
            'request': self.request,
            'instance': self.profile
        })
        return form_kwargs

    def get_success_url(self):
        return reverse('accounts_profile')


class PackageView(TemplateView):
    template_name = 'accounts/package.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        request.breadcrumbs([
            (_(u'Account'), reverse('accounts')),
            (_(u'Profile'), reverse('accounts_profile')),
        ])
        return super(PackageView, self).dispatch(request, *args, **kwargs)


class LogoutView(TemplateResponseMixin, View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LogoutView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        logout(request)
#        messages.add_message(
#            request, messages.SUCCESS,
#            _(u'You have been successfully signed out.'))
        return redirect('home')


class LogoutAndRegisterView(TemplateResponseMixin, View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LogoutAndRegisterView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        logout(request)
        return redirect('accounts_register')


class PasswordView(FormView):
    template_name = 'accounts/password.html'
    form_class = PasswordForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        request.breadcrumbs([
            (_(u'Account'), reverse('accounts')),
            (_(u'Profile'), reverse('accounts_profile')),
        ])
        return super(PasswordView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('accounts_password')

    def get_form_kwargs(self):
        form_kwargs = super(PasswordView, self).get_form_kwargs()
        form_kwargs['user'] = self.request.user
        return form_kwargs

    def form_valid(self, form):
        form.save()
        messages.add_message(self.request, messages.SUCCESS, _(u'Your password was changed.'))
        return super(PasswordView, self).form_valid(form)


class APIKeysView(TemplateView):
    template_name = 'accounts/api_keys.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        request.breadcrumbs([
            (_(u'Account'), reverse('accounts')),
            (_(u'Profile'), reverse('accounts_profile')),
        ])
        return super(APIKeysView, self).dispatch(request, *args, **kwargs)


class RecoveryView(TemplateResponseMixin, View):
    template_name = 'accounts/recovery.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user != AnonymousUser():
            return redirect(AFTER_LOGIN)
        request.breadcrumbs([
            (_(u'Account'), reverse('accounts')),
            (_(u'Forgotten password'), reverse('accounts_recovery')),
        ])
        return super(RecoveryView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return self.render_to_response({'form': RecoveryForm()})

    def post(self, request):
        recovery_form = RecoveryForm(request.POST)
        if recovery_form.is_valid():
            data = recovery_form.cleaned_data
            try:
                user = User.objects.get(username=data['username'])
                password = User.objects.make_random_password()

                try:
                    mail.password_recovery(user.email, password)

                    # update password only if email was delivered
                    user.set_password(password)
                    user.save()

                    messages.add_message(
                        request, messages.SUCCESS,
                        _(u'E-mail with new password was sent.'))
                except SMTPRecipientsRefused:
                    messages.add_message(
                        request, messages.ERROR,
                        _(u'Could not send e-mail with new password. \
                        Check if your e-mail address is correct or try again later, please '))

                return self.render_to_response({
                    'form': RecoveryForm()})
            except ObjectDoesNotExist:
                messages.add_message(
                    request, messages.ERROR,
                    _(u'User does not exists!'))
        return self.render_to_response({'form': recovery_form})
