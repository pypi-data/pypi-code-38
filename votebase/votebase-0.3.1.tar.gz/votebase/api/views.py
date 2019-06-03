import json
import binascii
import pytz
import logging

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View


User = get_user_model()

logger = logging.getLogger('votebase')


class APIView(View):
    #DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    DATE_FORMAT = '%Y-%m-%d'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        logger.info('Method called (%s)', request.method)

        api_key = request.GET.get('api_key', None)

        if api_key is None:
            return self.return_error_response(HttpResponseBadRequest, message='API key is missing.')

        try:
            self.api_user = User.objects.get(profile__api_key=api_key)
        except ObjectDoesNotExist:
            return self.return_error_response(HttpResponseForbidden, message='Incorrect API key.')

        return super(APIView, self).dispatch(request, *args, **kwargs)

    def return_error_response(self, response_class, message=None, status_code=None):
        obj = {
            'code': status_code if status_code else response_class.status_code,
            'message': message
        }
        return self.return_response(obj=obj, response_class=response_class)

    def return_response(self, obj, response_class=HttpResponse):
        response = response_class(
            json.dumps(obj, indent=4, separators=(',', ': ')),
            content_type='application/json'
        )
        response["Date"] = now().astimezone(pytz.timezone(settings.TIME_ZONE)).strftime(APIView.DATETIME_FORMAT)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Credentials"] = True
        #response["Access-Control-Credentials"] = True
        response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "Authorization, Origin"
        response["Access-Control-Expose-Headers"] = "Date"
        return response

    def options(self, request, **kwargs):
        return self.return_response({
            'status': 'SUCCESS'
        })


class BasicAuthMixin(object):
    realm = 'API'

    def is_auth_string_present(self, request):
        return request.META.get('HTTP_AUTHORIZATION', None) is not None

    def is_authenticated(self, request):
        if not self.is_auth_string_present(request):
            return False

        auth_string = request.META.get('HTTP_AUTHORIZATION', None)

        try:
            (authmeth, auth) = auth_string.split(" ", 1)

            if not authmeth.lower() == 'basic':
                return False

            auth = auth.strip().decode('base64')
            (username, password) = auth.split(':', 1)
            #print '(username, password) = %s' % str((username, password))
        except (ValueError, binascii.Error):
            return False

        #        request.user = self.auth_func(username=username, password=password)\
        #        or AnonymousUser()
        #
        #        return not request.user in (False, None, AnonymousUser())

        return self.valid_credentials(username, password)

    def valid_credentials(self, username, password):
        try:
            user = User.objects.get(username=username)
            user = authenticate(username=username, password=password)
            #login(self.request, user)
            self.request.user = user
            return user is not None
        except ObjectDoesNotExist:
            return False

    def challenge(self):
        response = HttpResponse("Authorization Required (missing or invalid credentials)")
        response['WWW-Authenticate'] = 'Basic realm="%s"' % self.realm
        response.status_code = 401
        return response
