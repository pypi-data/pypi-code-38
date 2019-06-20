import environ

from django.conf import settings

env = environ.Env()

DJANGO_SSO_COOKIE_DOMAIN = env('DJANGO_COOKIE_DOMAIN', default='example.com')
DJANGO_SSO_USER_PROFILE_MODEL = getattr(settings,
                                        'DJANGO_SSO_USER_PROFILE_MODEL', None)
DJANGO_SSO_HAS_EXTERNAL_USER_PROFILE_MODEL = DJANGO_SSO_USER_PROFILE_MODEL is \
                                             not None
DJANGO_SSO_DEACTIVATE_USER_ON_UNSUBSCRIPTION = env.bool(
    'DJANGO_SSO_DEACTIVATE_USER_ON_UNSUBSCRIPTION', False)
DJANGO_SSO_SERVICE_SUBSCRIPTION_IS_MANDATORY = env.bool(
    'DJANGO_SSO_SERVICE_SUBSCRIPTION_IS_MANDATORY', False)
DJANGO_SSO_STAFF_JWT = env('DJANGO_SSO_STAFF_JWT', default=None)

DJANGO_SSO_URL = env('DJANGO_SSO_URL', default='https://accounts.example.com')
DJANGO_SSO_BACKEND_URL = env('DJANGO_SSO_BACKEND_URL', default=DJANGO_SSO_URL)
DJANGO_SSO_SERVICE_URL = env('DJANGO_SSO_SERVICE_URL',
                             default='https://protectedservice.example.com')

DJANGO_SSO_LOGIN_URL = DJANGO_SSO_URL + '/login/'
DJANGO_SSO_REGISTER_URL = DJANGO_SSO_URL + '/signup/'
DJANGO_SSO_PASSWORD_RESET_URL = DJANGO_SSO_URL + '/send-password-reset/'

DJANGO_SSO_API_URL = DJANGO_SSO_URL + '/api/v1'
DJANGO_SSO_BACKEND_API_URL = DJANGO_SSO_BACKEND_URL + '/api/v1'

DJANGO_SSO_LOGOUT_URL = DJANGO_SSO_API_URL + '/auth/logout/'

DJANGO_SSO_USERS_URL = DJANGO_SSO_API_URL + '/profiles/users/'
DJANGO_SSO_BACKEND_USERS_URL = DJANGO_SSO_BACKEND_API_URL + '/profiles/users/'

DJANGO_SSO_USER_URL = DJANGO_SSO_USERS_URL + '{user_id}/'
DJANGO_SSO_BACKEND_USER_URL = DJANGO_SSO_BACKEND_USERS_URL + '{user_id}/'

DJANGO_SSO_USERS_CHECK_URL = DJANGO_SSO_USERS_URL + 'check/'
DJANGO_SSO_BACKEND_USERS_CHECK_URL = DJANGO_SSO_BACKEND_USERS_URL + 'check/'

DJANGO_SSO_USER_SUBSCRIPTIONS_URL = DJANGO_SSO_API_URL + '/profiles/users/{' \
                                                         'user_id}/subscriptions/'
DJANGO_SSO_BACKEND_USER_SUBSCRIPTIONS_URL = DJANGO_SSO_BACKEND_API_URL + \
                                            '/profiles/users/{' \
                                            'user_id}/subscriptions/'

DJANGO_SSO_USER_SUBSCRIPTIONS_CREATE_URL = DJANGO_SSO_USER_SUBSCRIPTIONS_URL \
                                           + 'create/{service_id}/'
DJANGO_SSO_BACKEND_USER_SUBSCRIPTIONS_CREATE_URL = \
    DJANGO_SSO_BACKEND_USER_SUBSCRIPTIONS_URL + 'create/{service_id}/'

DJANGO_SSO_USER_SUBSCRIPTION_UNSUBSCRIBE_URL = \
    DJANGO_SSO_USER_SUBSCRIPTIONS_URL + '{subscription_id}/unsubscribe/'
DJANGO_SSO_BACKEND_USER_SUBSCRIPTION_UNSUBSCRIBE_URL = \
    DJANGO_SSO_BACKEND_USER_SUBSCRIPTIONS_URL + '{subscription_id}/unsubscribe/'

DJANGO_SSO_SERVICES_URL = DJANGO_SSO_API_URL + '/services/'
DJANGO_SSO_BACKEND_SERVICES_URL = DJANGO_SSO_BACKEND_API_URL + '/services/'

DJANGO_SSO_SERVICE_SUBSCRIBE_URL = DJANGO_SSO_SERVICES_URL + '{service_id}/subscribe/'
DJANGO_SSO_BACKEND_SERVICE_SUBSCRIBE_URL = DJANGO_SSO_BACKEND_SERVICES_URL + \
                                           '{service_id}/subscribe/'

DJANGO_SSO_ADMIN_USER_URL = DJANGO_SSO_URL + '/admin/profiles/user/'

DJANGO_SSO_REQUIRED_PROFILE_FIELDS = ['sso_id', 'sso_rev',
                                      "latitude", "longitude",
                                      "first_name", "last_name",
                                      "description",
                                      "picture",
                                      "birthdate",
                                      "address", "country",
                                      "language",
                                      "is_unsubscribed"]

DJANGO_SSO_CONSUMER_USERNAME_HEADER = env('DJANGO_SSO_CONSUMER_USERNAME_HEADER',
                                          default='HTTP_X_CONSUMER_USERNAME')
DJANGO_SSO_CONSUMER_GROUPS_HEADER = env('DJANGO_SSO_CONSUMER_GROUPS_HEADER',
                                        default='HTTP_X_CONSUMER_GROUPS')

DJANGO_SSO_REPLICATE_PROFILE = env.bool('DJANGO_SSO_REPLICATE_PROFILE', False)
DJANGO_SSO_MANAGE_USER_GROUPS = env.bool('DJANGO_SSO_MANAGE_USER_GROUPS', True)

DJANGO_SSO_JWT_HEADER = env('DJANGO_SSO_JWT_HEADER', default='jwt')

DJANGO_SSO_ANONYMOUS_CONSUMER_USERNAME = env(
    'DJANGO_SSO_ANONYMOUS_CONSUMER_USERNAME', default="anonymous")
