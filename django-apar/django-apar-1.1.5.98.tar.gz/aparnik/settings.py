from django.conf import settings
from rest_framework.settings import APISettings

USER_SETTINGS = getattr(settings, 'APARNIK', None)

DEFAULTS = {
    'API_PRODUCT_MODE': False,
    'AWS_ACTIVE': True,
    'BANK_ACTIVE': True,
    'ZARINPAL_MERCHENT_CODE': '',
    'USER_LOGIN_WITH_PASSWORD': False,
    'USER_CREATE_SERIALIZER': 'aparnik.contrib.users.api.serializers.UserCreateSerializer',
    'USER_UPDATE_SERIALIZER': 'aparnik.contrib.users.api.serializers.UserUpdateSerializer',
    'USER_DETAIL_SERIALIZER': 'aparnik.contrib.users.api.serializers.UserDetailSerializer',
    'USER_SUMMARY_LIST_SERIALIZER': 'aparnik.contrib.users.api.serializers.UserSummaryListSerializer',
    'USER_LOGIN_API_VIEW': 'aparnik.contrib.users.api.views.UserLoginAPIView',
    'USER_LIST_API_VIEW': 'aparnik.contrib.users.api.views.UserListAPIView',
    'USER_DETAIL_API_VIEW': 'aparnik.contrib.users.api.views.UserDetailAPIView',
    'USER_CREATE_API_VIEW': 'aparnik.contrib.users.api.views.UserCreateAPIView',
    'USER_UPDATE_API_VIEW': 'aparnik.contrib.users.api.views.UserUpdateAPIView',
    'USER_INVITATION_CODE_LENGTH': 6,
    'USER_INVITATION_CODE_INT': False,
    'USER_IS_SHOW_ADMIN_PANEL': True,
    'USER_REGISTER_WITH_LOGIN': False,
    'SMS_EXPIRE_TOKEN': 120,
    'SMS_API_KEY': '',
    'SMS_OTA_NAME': '',
    'SEND_SMS': False,
    'VERIFY_FAKE': False,
    'VERIFY_FAKE_CODE': '',
    'JALALI_FORMAT': '%Y/%m/%d',
    'INVITATION_PERCENT_DISCOUNT': 0,
    'COUPON_CODE_LENGTH': 5,
    'IS_FCM': True,
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = (
    'AWS_ACTIVE',
    'BANK_ACTIVE',
    'USER_LOGIN_WITH_PASSWORD',
    'USER_CREATE_SERIALIZER',
    'USER_UPDATE_SERIALIZER',
    'USER_DETAIL_SERIALIZER',
    'USER_SUMMARY_LIST_SERIALIZER',
    'USER_LOGIN_API_VIEW',
    'USER_LIST_API_VIEW',
    'USER_DETAIL_API_VIEW',
    'USER_CREATE_API_VIEW',
    'USER_UPDATE_API_VIEW',
    'USER_INVITATION_CODE_INT',
    'USER_IS_SHOW_ADMIN_PANEL',
    'USER_REGISTER_WITH_LOGIN',
    'API_PRODUCT_MODE',
    'SEND_SMS',
    'VERIFY_FAKE',
    'IS_FCM',
)

aparnik_settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
from aparnik.contrib.settings.models import Setting
