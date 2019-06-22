# -*- coding: utf-8 -*-


from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework.generics import RetrieveAPIView, CreateAPIView, UpdateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework import filters
from rest_framework.serializers import as_serializer_error
from rest_framework.validators import ValidationError

from fcm_django.models import FCMDevice

from aparnik.settings import aparnik_settings
from aparnik.utils.utils import convert_iran_phone_number_to_world_number
from aparnik.contrib.users.models import DeviceType


UserDetailSerializer = aparnik_settings.USER_DETAIL_SERIALIZER
UserCreateSerializer = aparnik_settings.USER_CREATE_SERIALIZER
UserUpdateSerializer = aparnik_settings.USER_UPDATE_SERIALIZER
UserSummeryListSerializer = aparnik_settings.USER_SUMMARY_LIST_SERIALIZER
# from slider.api.serializers import SliderDetailsSerializer, Slider
# from notification.models import Notification

User = get_user_model()


def get_user_name(username):
    username = convert_iran_phone_number_to_world_number(username)
    try:
        user = User._default_manager.get_by_natural_key(username)
    except:
        if aparnik_settings.USER_REGISTER_WITH_LOGIN and not aparnik_settings.USER_LOGIN_WITH_PASSWORD:
            user = User(username=username)
            user.save()
        else:
            user = None

    return user


class UserTokenAPIView(APIView):
    permission_classes = [AllowAny]

    """
    A view that returns the count of active users in JSON.
    """
    def post(self, request, format=None):

        status = HTTP_400_BAD_REQUEST
        content = {}

        try:
            from aparnik.contrib.users.models import DeviceLogin
            from rest_framework_jwt.views import obtain_jwt_token

            username = request.data.get('username').strip()
            version_number = request.data.get('version_number', None)
            device_id = request.data.get('device_id', None)
            device_type = DeviceType.find(request.data.get('device_type', None))
            os_version = request.data.get('os_version', None)
            device_model = request.data.get('device_model', None)

            user = get_user_name(username=username)

            responce = obtain_jwt_token(request=request._request, format=format)
            if responce.status_code == 200:

                if user.is_can_login(device_id=device_id):
                    device = DeviceLogin.objects.create(user=user, version_number=version_number, device_id=device_id,
                                                        os_version=os_version, device_model=device_model,
                                                        device_type=device_type)
                    device.save()

                    if aparnik_settings.IS_FCM:
                        device_fcm = FCMDevice.objects.filter(device_id=device.device_id).order_by('-id').first()
                        if not device_fcm:
                            raise ValidationError({
                                'login': _("We can't login. Please Contact with support team.")
                            })
                        device_fcm.user = user
                        device_fcm.save()
            return responce

        except Exception as e:
            raise ValidationError(as_serializer_error(e))
           

class UserForgetPasswordAPI(APIView):
    permission_classes = [AllowAny]

    """
    A view that returns the count of active users in JSON.
    """
    def post(self, request, format=None):

        status = HTTP_400_BAD_REQUEST
        content = {}

        try:
            username = request.data.get('username').strip()
            version_number = request.data.get('version_number', None)
            device_id = request.data.get('device_id', None)
            device_type = DeviceType.find(request.data.get('device_type', None))
            os_version = request.data.get('os_version', None)
            device_model = request.data.get('device_model', None)

            user = get_user_name(username=username)
            user.reset_password()

            content['success'] = True
            content['msg'] = ""
            status = HTTP_200_OK
            return Response(content, status=status)
        except Exception:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            raise ValidationError({
                'reset_password': _("We can't reset password. Please Contact with support team.")
            })


class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    """
    A view that returns the count of active users in JSON.
    """
    def post(self, request, format=None):

        status = HTTP_400_BAD_REQUEST
        content = {}

        try:
            user = request.user
            from aparnik.contrib.users.models import DeviceLogin
            version_number = request.data.get('version_number', None)
            device_id = request.data.get('device_id', None)
            device_type = DeviceType.find(request.data.get('device_type', None))
            os_version = request.data.get('os_version', None)
            device_model = request.data.get('device_model', None)
            device_login = DeviceLogin.objects.active().filter(device_id=device_id, user=user).first()
            if device_login:
                device_login.is_active = False
                device_login.save()
                if aparnik_settings.IS_FCM:
                    device = FCMDevice.objects.filter(user=user, device_id=device_login.device_id).first()
                    device.user = None
                    device.save()
            content['success'] = True
            content['msg'] = ""
            status = HTTP_200_OK
            return Response(content, status=status)
        except Exception:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            raise ValidationError({
                'logout': _("We can't logout. Please Contact with support team.")
            })


class UserLoginAPIView(APIView):
    """
    A view that returns the count of active users in JSON.
    """
    def post(self, request, format=None):

        status = HTTP_400_BAD_REQUEST
        content = {}


        try:
            username = request.data.get('username').strip()
            # user = User._default_manager.get_by_natural_key(username)
            user = get_user_name(username=username)
            version_number = request.data.get('version_number', None)
            device_id = request.data.get('device_id', None)
            device_type = DeviceType.find(request.data.get('device_type', None))
            os_version = request.data.get('os_version', None)
            device_model = request.data.get('device_model', None)
            app_signature = request.data.get('app_signature', None)
        except Exception:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            raise ValidationError({
                'login': _("We can't find this number.")
            })

        try:

            user.OTARequest(app_signature=app_signature)
            # serializer = UserDetailSerializer(user, context={'request': self.request})
            content['data'] = {}
            # content['data']['user'] = serializer.data
            # content['data']['ota'] = user.token
            content['success'] = True
            content['msg'] = ""
            status = HTTP_200_OK
            return Response(content, status=status)
        except Exception as e:
            raise ValidationError(as_serializer_error(e))


class UserSendSMSAPI(APIView):
    """
    A view that returns the count of active users in JSON.
    """
    def post(self, request, format=None):

        status = HTTP_400_BAD_REQUEST
        content = {}

        try:
            username = request.data.get('username').strip()
            # user = User._default_manager.get_by_natural_key(username)
            user = get_user_name(username=username)
            version_number = request.data.get('version_number', None)
            device_id = request.data.get('device_id', None)
            os_version = request.data.get('os_version', None)
            device_model = request.data.get('device_model', None)
            app_signature = request.data.get('app_signature', None)
        except Exception:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            raise ValidationError({
                'login': _("We can't find this number.")
            })

        try:

            user.OTARequest(app_signature=app_signature)
            # serializer = UserDetailSerializer(user, context={'request': self.request})
            content['data'] = {}
            # content['data']['user'] = serializer.data
            # content['data']['ota'] = user.token
            content['success'] = True
            content['msg'] = ""
            status = HTTP_200_OK
            return Response(content, status=status)
        except Exception:
            raise ValidationError({
                'login': _("We can't login. Please Contact with support team.")
            })


class UserVerifySMSAPI(APIView):
    """
    A view that returns the count of active users in JSON.
    """
    def post(self, request, format=None):

        status = HTTP_400_BAD_REQUEST
        content = {}

        try:
            username = request.data.get('username').strip()
            # user = User._default_manager.get_by_natural_key(username)
            user = get_user_name(username=username)
            version_number = request.data.get('version_number', None)
            password = request.data.get('password', None)
            device_id = request.data.get('device_id', None)
            os_version = request.data.get('os_version', None)
            device_model = request.data.get('device_model', None)

        except:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            raise ValidationError({
                'login': _("We can't find this number.")
            })

        try:

            if user.OTAVerify(password):
                user.verify_mobile = True
                user.save()
            else:
                raise ValidationError
            # serializer = UserDetailSerializer(user, context={'request': self.request})
            content['data'] = {}
            # content['data']['user'] = serializer.data
            # content['data']['ota'] = user.token
            content['success'] = True
            content['msg'] = ""
            status = HTTP_200_OK

        except Exception:
            raise ValidationError({
                'login': _("کد وارد شده اشتباه است.")
            })

        return Response(content, status=status)


class UserListAPIView(ListAPIView):
    serializer_class = UserSummeryListSerializer
    permission_classes = [IsAuthenticated]
    # queryset = User.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'username_mention', 'last_name', 'first_name']

    def get_queryset(self):

        return User.objects.active()


class UserSubsetListAPIView(ListAPIView):
    serializer_class = UserSummeryListSerializer
    permission_classes = [IsAuthenticated]
    # queryset = User.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'last_name', 'first_name']

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(pk__in=user.invite_by.get_invited_by().values_list('invite'))


class UserDetailAPIView(RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'username'
    lookup_field = 'username'

    def get_queryset(self):
        user = self.request.user

        return User.objects.filter(username=user.username)


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()
    permission_classes = [AllowAny]


#
class UserUpdateAPIView(UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'username'
    lookup_field = 'username'

    def get_object(self, *args, **kwargs):

        user = self.request.user
        return user


class FCMAddTokenAPIView(APIView):
    permission_classes = (AllowAny,)
    """
    A view that returns the count of active users in JSON.
    """
    def post(self, request, format=None):

        status = HTTP_400_BAD_REQUEST
        content = {}

        try:
            device_type = DeviceType.find(request.data.get('device_type', None))
            device_id = request.data.get('device_id', None)
            device_model = request.data.get('device_model', None)
            fcm_token = request.data.get('fcm_token', None)
            if fcm_token is None:
                raise Exception
            fcm = FCMDevice.objects.create(registration_id=fcm_token, device_id=device_id, type=DeviceType.value(device_type))
            fcm.save()
            content['success'] = True
            content['msg'] = ""
            status = HTTP_200_OK
            return Response(content, status=status)
        except Exception:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            raise ValidationError({
                'fcm': _("We can't add fcm token.")
            })


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user': UserDetailSerializer(user, context={'request': request}).data
    }
