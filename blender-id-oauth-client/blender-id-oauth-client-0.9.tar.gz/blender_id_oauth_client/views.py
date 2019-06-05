import collections
import datetime
import functools
import logging
from urllib.parse import urlencode

from oauthlib.oauth2 import InvalidGrantError, MismatchingStateError
from requests_oauthlib import OAuth2Session
import django.contrib.auth
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpRequest, HttpResponseRedirect, HttpResponseServerError
from django.shortcuts import redirect, render
from django.urls import reverse
import django.utils.timezone

from . import models, signals

log = logging.getLogger(__name__)
User = get_user_model()
ClientSettings = collections.namedtuple(
    'ClientSettings',
    'client secret url_base url_authorize url_token url_userinfo url_logout')


@functools.lru_cache(maxsize=1)
def blender_id_oauth_settings() -> ClientSettings:
    """Container for Blender ID OAuth Client settings."""
    from urllib.parse import urljoin

    url_base = settings.BLENDER_ID['BASE_URL']
    return ClientSettings(
        client=settings.BLENDER_ID['OAUTH_CLIENT'],
        secret=settings.BLENDER_ID['OAUTH_SECRET'],
        url_base=url_base,
        url_authorize=urljoin(url_base, 'oauth/authorize'),
        url_token=urljoin(url_base, 'oauth/token'),
        url_userinfo=urljoin(url_base, 'api/me'),
        url_logout=urljoin(url_base, 'logout'),
    )


def login_view(request):
    """Login the user by redirecting to Blender ID.

    If the user was visting a page that required login, its url will be saved in
    the session and made available after login through a redirect.
    """
    blender_id_oauth = blender_id_oauth_settings()
    redirect_uri = request.build_absolute_uri(reverse('oauth:callback'))
    bid = OAuth2Session(blender_id_oauth.client, redirect_uri=redirect_uri)
    authorization_url, state = bid.authorization_url(blender_id_oauth.url_authorize)

    # State is used to prevent CSRF.
    request.session['oauth_state'] = state
    request.session['next_after_login'] = (request.GET.get('next') or
                                           request.META.get('HTTP_REFERER'))
    return redirect(authorization_url)


def redirect_to_login(next_url: str) -> HttpResponseRedirect:
    resp = redirect('oauth:login')
    if next_url:
        query = urlencode({'next': next_url})
        resp['Location'] = resp['Location'] + f'?{query}'
    return resp


@transaction.atomic()
def callback_view(request):
    my_log = log.getChild('callback_view')

    next_after_login = request.session.pop('next_after_login', settings.LOGIN_REDIRECT_URL)
    session_state = request.session.pop('oauth_state', '')
    if not session_state:
        # If there is no session state, we'll have to try again.
        my_log.debug('No session state, redoing the login.')
        return redirect_to_login(next_after_login)

    blender_id_oauth = blender_id_oauth_settings()
    redirect_uri = request.build_absolute_uri(reverse('oauth:callback'))

    bid = OAuth2Session(blender_id_oauth.client,
                        state=session_state,
                        redirect_uri=redirect_uri)

    try:
        token = bid.fetch_token(blender_id_oauth.url_token, client_secret=blender_id_oauth.secret,
                                authorization_response=request.build_absolute_uri())
    except (InvalidGrantError, MismatchingStateError) as ex:
        retry_count = request.session.get('bid_login_retry_count', 0) + 1
        if retry_count > 3:
            request.session['bid_login_retry_count'] = 0
            return redirect('oauth:login_loop_detected')
        request.session['bid_login_retry_count'] = retry_count

        # This happens if the user takes too long to log in; Blender ID has
        # then already discarded the grant, and we should just try again.
        my_log.info('%s error received from Blender ID, retrying the login', type(ex))
        return redirect_to_login(next_after_login)
    else:
        request.session['bid_login_retry_count'] = 0

    bid = OAuth2Session(blender_id_oauth.client, token=token)
    resp = bid.get(blender_id_oauth.url_userinfo)
    if resp.status_code != 200:
        my_log.error('Error %s getting user info URL %s with token %s: %s',
                     resp.status_code,
                     blender_id_oauth.url_userinfo,
                     bid.token,
                     resp.text,
                     )
        # TODO(Sybren): create a proper page for this error, or at least style it nicely.
        return HttpResponseServerError('Error %d getting your user information from Blender ID'
                                       % resp.status_code)

    user_oauth = resp.json()

    # Look up the user by OAuth ID
    oauth_user_id = user_oauth['id']
    oauth_user_email = user_oauth['email']
    oauth_user_nickname = user_oauth['nickname']

    try:
        user_info = models.OAuthUserInfo.objects.get(oauth_user_id=oauth_user_id)
    except models.OAuthUserInfo.DoesNotExist:
        my_log.debug('User not seen before, going to search by email address.')
        # TODO(Sybren): handle nickname conflict
        # TODO(Sybren): handle email conflict
        user, created = User.objects.get_or_create(
            email=oauth_user_email,
            defaults={'username': oauth_user_nickname,
                      'password': User.objects.make_random_password()})
        models.OAuthUserInfo.objects.create(user=user, oauth_user_id=oauth_user_id)
        if created:
            my_log.debug('User also not found by email address, created new one.')
            signals.user_created.send(sender=user, instance=user, oauth_info=user_oauth)
    else:
        # Found user_info by OAuth ID.
        user = user_info.user

    # Update the user with the info we just got from Blender ID.
    # TODO(Sybren): handle nickname conflict
    # TODO(Sybren): handle email conflict
    if user.email != oauth_user_email or user.username != oauth_user_nickname:
        my_log.debug('Updating user pk=%d from OAuth server')
        user.email = oauth_user_email
        user.username = oauth_user_nickname
        user.save(update_fields={'email', 'username'})

    # Convert access_token expiry time into datetime.
    if 'expires_in' in token:
        expires_at = django.utils.timezone.now() + datetime.timedelta(seconds=token['expires_in'])
    else:
        expires_at = None

    # Store the OAuth token, associated with the newly created User
    models.OAuthToken.objects.create(
        user=user,
        oauth_user_id=oauth_user_id,
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        expires_at=expires_at)

    django.contrib.auth.login(request, user)

    if next_after_login:
        log.debug('Redirecting user to %s after login', next_after_login)
        return redirect(next_after_login)

    return redirect(settings.LOGIN_REDIRECT_URL)


def logout_view(request: HttpRequest):
    """Logout from this site, and then from Blender ID.

    This helps perceiving the current site as part of Blender ID.
    """
    from urllib.parse import quote

    blender_id_oauth = blender_id_oauth_settings()
    django.contrib.auth.logout(request)

    redirect_url = blender_id_oauth.url_logout
    if settings.LOGOUT_REDIRECT_URL:
        next_url = request.build_absolute_uri(settings.LOGOUT_REDIRECT_URL)
        quoted_next_url = quote(next_url)
        redirect_url = f'{redirect_url}?next={quoted_next_url}'

    return redirect(redirect_url)


def login_loop_detected(request: HttpRequest):
    return render(request, 'blender_id_oauth_client/login_loop_detected.html')
