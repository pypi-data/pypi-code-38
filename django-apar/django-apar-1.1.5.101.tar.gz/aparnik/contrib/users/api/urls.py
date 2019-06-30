from django.conf.urls import url, include
from rest_framework_jwt.views import verify_jwt_token

from aparnik.settings import aparnik_settings
from aparnik.contrib.users.api.views import UserSendSMSAPI, UserVerifySMSAPI, FCMAddTokenAPIView, UserLogoutAPIView, \
    UserTokenAPIView, UserForgetPasswordAPI, UserSubsetListAPIView
UserLoginAPI = aparnik_settings.USER_LOGIN_API_VIEW
UserListAPIView = aparnik_settings.USER_LIST_API_VIEW
UserDetailAPIView = aparnik_settings.USER_DETAIL_API_VIEW
UserCreateAPIView = aparnik_settings.USER_CREATE_API_VIEW
UserUpdateAPIView = aparnik_settings.USER_UPDATE_API_VIEW

app_name = 'aparnik_users'

urlpatterns = [
    url(r'^$', UserListAPIView.as_view(), name='list'),
    url(r'^admin/', include('aparnik.contrib.users.api.admin.urls', namespace='admin')),
    url(r'^subset/$', UserSubsetListAPIView.as_view(), name='subset'),
    url(r'^login$', UserLoginAPI.as_view(), name='login'),
    url(r'^forget-password/', UserForgetPasswordAPI.as_view(), name='forget-password'),
    url(r'^logout/', UserLogoutAPIView.as_view(), name='logout'),
    url(r'^send-sms/', UserSendSMSAPI.as_view(), name='send-sms'),
    url(r'^verify-sms/', UserVerifySMSAPI.as_view(), name='verify-sms'),
    url(r'^notification-add-token/', FCMAddTokenAPIView.as_view(), name='FCM-add-token'),
    url(r'^create', UserCreateAPIView.as_view(), name='create'),
    url(r'^token/verify', verify_jwt_token, name='verify'),
    url(r'^token', UserTokenAPIView.as_view(), name='token'),
    url(r'^(?P<username>[\w-]+)/$', UserDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<username>[\w-]+)/update$', UserUpdateAPIView.as_view(), name='update'),

]