import json
import datetime

from django.conf import settings
from django.contrib.auth import logout, get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES, validate_email
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext
from django.views.decorators.csrf import csrf_exempt

from votebase.api.views import APIView, BasicAuthMixin
from votebase.core.accounts.forms import PASSWORD_MIN_SIZE
from votebase.core.accounts.models import Profile
from votebase.core.utils import mail
from votebase.core.utils.common import generate_token, generate_slug_for_user


User = get_user_model()


class UserProfileMixin(object):
    def get_profile_data(self, profile, use_display_values=False):
        if isinstance(profile, Profile):
            return {
                'id': profile.pk,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'slug': profile.slug,
                'gender': profile.gender,
                'activation_hash': profile.activation_hash,
                'last_seen_surveys': profile.last_seen_surveys.strftime(APIView.DATETIME_FORMAT),
                'created': profile.created.strftime(APIView.DATETIME_FORMAT),
                'modified': profile.modified.strftime(APIView.DATETIME_FORMAT)
            }

        result = {}

        for key in profile._meta.get_all_field_names():
            if key.startswith('_') or key in ('api_key', 'user', 'package_valid_to'):
                continue
            value = getattr(profile, key, None)

            if isinstance(value, datetime.datetime):
                result[key] = value.strftime(APIView.DATETIME_FORMAT) if value else None
            elif isinstance(value, basestring) or isinstance(value, tuple) \
                or isinstance(value, list) or isinstance(value, bool)\
                or value is None or isinstance(value, int):

                if use_display_values:
                    try:
                        result[key] = getattr(profile, 'get_%s_display' % key, None)()
                    except (AttributeError, TypeError):
                        result[key] = value
                else:
                    result[key] = value

            else:
                try:
                    if isinstance(value, dict):
                        try:
                            json.dumps(value)
                            result[key] = unicode(value)
                        except TypeError:
                            #print key, type(value)
                            result[key] = unicode(value)
                    else:
                        #print key, type(value)
                        result[key] = unicode(value)
                except Exception as e:
                    result[key] = unicode(e)
        return result


class RegisterView(UserProfileMixin, APIView):
    @method_decorator(csrf_exempt)
    def post(self, request, **kwargs):
        try:
            data = json.loads(request.body)
        except ValueError as e:
            return self.return_error_response(HttpResponseBadRequest, message='Request POST data is in incorrect format.')

        username = data.get('username', None)
        if username is None:
            return self.return_error_response(HttpResponseBadRequest, message='username is missing.')

        try:
            validate_email(username)
        except ValidationError:
            return self.return_error_response(HttpResponseBadRequest, message='Enter valid email as username.')

        password = data.get('password', None)
        if password is None:
            return self.return_error_response(HttpResponseBadRequest, message='password is missing.')

        if len(password.strip()) < PASSWORD_MIN_SIZE:
            return self.return_error_response(HttpResponseBadRequest, message='Password has to have at least %s characters.' % PASSWORD_MIN_SIZE)

        first_name = data.get('first_name', None)
        if first_name is None:
            return self.return_error_response(HttpResponseBadRequest, message='first_name is missing.')

        last_name = data.get('last_name', None)
        if last_name is None:
            return self.return_error_response(HttpResponseBadRequest, message='last_name is missing.')

        if User.objects.filter(username=data.get('username')).exists():
            return self.return_error_response(HttpResponseBadRequest, message='User with that username already exists.')

        # Create user
        user = User.objects.create_user(
            username=data.get('username'),
            email=data.get('username'),
            password=data.get('password')
        )
        user.save()

        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()

        # Create new profile
        profile = user.get_profile()
        profile.first_name = first_name
        profile.last_name = last_name
        profile.token = generate_token()

        if first_name in EMPTY_VALUES and\
           last_name in EMPTY_VALUES:
            first_name = ugettext(u'Unknown user')

        profile.slug = generate_slug_for_user(first_name, last_name)
        profile.save()

        ## Send activation email
        #if settings.REQUIRED_ACTIVATION:
        #    user.is_active = False
        #    user.save()
        #    mail.registration(self.request, user)
        #    message = ugettext(u'Please, check your email and activate your account.')
        #else:
        #    message = ugettext(u'You have been successfully registered.')

        user.is_active = True
        user.save()
        message = 'User was successfully registered.'

        return self.return_response({
            #'code': 200,
            'message': message,
            'user': {
                'id': user.pk,
                'email': user.username,
                'is_active': user.is_active,
                #'profile': self.get_profile_data(user.profile)
            }
        })


class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return self.return_response({
            'status': 'success',
            'message': 'Logged out'
        })


class LoginView(BasicAuthMixin, UserProfileMixin, APIView):
    @method_decorator(csrf_exempt)
    def post(self, request):
        # Check basic auth in BasicAuthMixin
        if not self.is_authenticated(request):
            return self.challenge()

        if not self.request.user.is_active:
            return self.return_error_response(HttpResponseForbidden, message='User is inactive.')

        user = request.user
        result = {
            'id': user.pk,
            'email': user.username,
            #'profile': self.get_profile_data(user.profile)
        }

        return self.return_response({'user': result})


class ProfileView(BasicAuthMixin, UserProfileMixin, APIView):
    profile_fields = ('first_name', 'last_name', 'slug', 'gender')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        self.request = request

        # Check basic auth in BasicAuthMixin
        if not self.is_authenticated(request):
            return self.challenge()

        if not self.request.user.is_active:
            return self.return_error_response(HttpResponseForbidden, message='User is inactive.')

        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        user = self.request.user
        profile = self.get_profile_data(user.profile)
        return self.return_response(profile)

    @method_decorator(csrf_exempt)
    def post(self, request):
        user = self.request.user

        if not request.body:
            return self.return_error_response(HttpResponseBadRequest, message='POST data are missing.')

        try:
            data = json.loads(request.body)
        except ValueError as e:
            return self.return_error_response(HttpResponseBadRequest, message='Request POST data is in incorrect format.')

        try:
            is_profile_changed = self.update_profile(user.profile, data)
            message = 'Profile successfully updated.' if is_profile_changed else 'Nothing changed.'
            return self.return_response({
                #'code': 200,
                'message': message,
                'profile': self.get_profile_data(user.profile)
            })
        except (Exception, ValueError, TypeError) as e:
                return self.return_error_response(HttpResponseBadRequest, message=e.message)

    def update_profile(self, profile, data):
        is_profile_changed = False
        for field in self.profile_fields:
            if field in data and hasattr(profile, field):
                old_value = getattr(profile, field, None)
                new_value = data.get(field)
                if old_value != new_value:
                    is_profile_changed = True
                    setattr(profile, field, new_value)
                    profile.save()
        return is_profile_changed
