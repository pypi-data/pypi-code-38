import logging

from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.utils.deprecation import \
    MiddlewareMixin  # https://stackoverflow.com/questions/42232606/django
# -exception-middleware-typeerror-object-takes-no-parameters
from django.utils.encoding import smart_str
from django.utils.http import urlencode
from jwt import decode
from jwt.exceptions import DecodeError

from . import settings
from .utils import (get_sso_id, get_profile_from_sso,
                    update_local_profile_from_sso,
                    get_profile_model)

logger = logging.getLogger("django_sso_app")
UserProfileModel = get_profile_model()


class SsoMiddleware(MiddlewareMixin):
    """
    See django.contrib.auth.middleware.RemoteUserMiddleware.
    """

    # Name of request header to grab username from.  This will be the key as
    # used in the request.META dictionary, i.e. the normalization of headers to
    # all uppercase and the addition of "HTTP_" prefix apply.
    header = settings.DJANGO_SSO_CONSUMER_USERNAME_HEADER
    # Username for anonymous user
    anonymous_username = settings.DJANGO_SSO_ANONYMOUS_CONSUMER_USERNAME

    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, "user"):
            raise ImproperlyConfigured(
                "SSO middleware requires the authentication middleware to be"
                " installed.  Edit your MIDDLEWARE setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the SsoMiddleware class.")

        if request.user.is_authenticated and request.user.is_staff:  # django
            #  >= 1.10 has is_authenticated as parameter
            # If a staff user is already authenticated, we don't need to
            # continue
            return

        try:
            consumer_username = request.META[self.header]

            if consumer_username == self.anonymous_username:
                if request.user.is_authenticated:
                    self._remove_invalid_user(request)
                return

            encoded_jwt = request.COOKIES.get(settings.DJANGO_SSO_JWT_HEADER,
                                              None)

        except KeyError as e:
            # If specified header or jwt doesn't exist then remove any existing
            # authenticated user, or return (leaving request.user set to
            # AnonymousUser by the AuthenticationMiddleware).
            if request.user.is_authenticated:
                self._remove_invalid_user(request)
            return

        if settings.DJANGO_SSO_REPLICATE_PROFILE:
            try:
                decoded_jwt = decode(jwt=encoded_jwt, verify=False)
            except DecodeError:
                logger.exception("Error decoding JWT!")

                if request.user.is_authenticated():
                    self._remove_invalid_user(request)
                return
        else:
            decoded_jwt = None

        # If the user is already authenticated and that user is active and the
        # one we are getting passed in the headers, then the correct user is
        # already persisted in the session and we don't need to continue.
        if request.user.is_authenticated:
            sso_id = get_sso_id(consumer_username)
            user_profile = request.user

            if settings.DJANGO_SSO_HAS_EXTERNAL_USER_PROFILE_MODEL:
                user_profile = UserProfileModel.objects.get(user=request.user)

            if user_profile.sso_id == sso_id:
                if request.user.is_active:
                    if settings.DJANGO_SSO_REPLICATE_PROFILE:
                        # Check if sso_rev changed and, if so, fetch profile
                        # from
                        # SSO and update the local one
                        rev_changed = user_profile.sso_rev != decoded_jwt["rev"]
                        if rev_changed:
                            logger.info("Rev changed from {} to {} for {},"
                                        " updating ..."
                                        .format(user_profile.sso_rev,
                                                decoded_jwt["rev"],
                                                consumer_username))

                            sso_profile = get_profile_from_sso(
                                sso_id=sso_id, encoded_jwt=encoded_jwt)
                            update_local_profile_from_sso(
                                sso_profile=sso_profile,
                                profile=user_profile)

                            logger.info("{} updated with latest data from SSO"
                                        .format(consumer_username))

                        return
                    else:
                        logger.info("{} logged in"
                                    .format(consumer_username))
                        return

                # The user is not active.
                self._remove_invalid_user(request)
            else:
                # An authenticated user is associated with the request, but
                # it does not match the authorized user in the header.
                self._remove_invalid_user(request)

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        user = auth.authenticate(request=request,
                                 consumer_username=consumer_username,
                                 encoded_jwt=encoded_jwt,
                                 decoded_jwt=decoded_jwt)

        # Redirect user to Term Of Service.
        is_to_subscribe = getattr(user, "is_to_subscribe", False)
        _username = smart_str(user.username)
        logger.info('IS {} TO SUBSCRIBE? {}'
                    .format(_username, is_to_subscribe))
        if user and is_to_subscribe:
            _qs = urlencode({"next": settings.DJANGO_SSO_SERVICE_URL})
            _url = "{sso}?{qs}".format(sso=settings.DJANGO_SSO_LOGIN_URL,
                                       qs=_qs)
            logger.info("User {username} must agree to the Terms of Service,"
                        " redirecting to {url} ..."
                        .format(username=_username, url=_url))
            response = HttpResponseRedirect(redirect_to=_url)
            return response

        if user and user.is_active:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            auth.login(request, user)
            logger.info("User {username} was authenticated successfully!"
                        .format(username=_username))

    @staticmethod
    def _remove_invalid_user(request):
        """
        Removes the current authenticated user in the request which is invalid.
        """
        auth.logout(request)
