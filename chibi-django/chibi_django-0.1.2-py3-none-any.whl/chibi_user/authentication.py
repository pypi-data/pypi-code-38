from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import (
    get_authorization_header, BaseAuthentication
)

from chibi_user.models import Token


__all__ = [ 'Token_simple_authentication' ]


class Token_simple_authentication( BaseAuthentication ):
    model = Token

    def authenticate( self, request ):
        auth = get_authorization_header( request ).split( b';' )
        if not auth:
            return None
        if len( auth ) == 1 and not auth[0]:
            return None

        auth = self.parse_tokens( auth )

        if len( auth ) == 0:
            msg = _( 'Invalid token header. No credentials provided.' )
            raise exceptions.AuthenticationFailed( msg )

        return self.authenticate_credentials( auth, request )

    def authenticate_credentials( self, tokens, request ):
        try:
            key = tokens.pop( 'Token' )
            token = self.model.objects.select_related( 'user' ).get( key=key )
        except ( KeyError, self.model.DoesNotExist ):
            raise exceptions.AuthenticationFailed( _( 'Invalid token.' ) )

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(
                _( 'User inactive or deleted.' ) )

        return ( token.user, token )

    def authenticate_header( self, request ):
        return 'Token'

    def parse_tokens( self, tokens ):
        result = {}
        for token in tokens:
            if len( token ) == 0:
                msg = _( 'Invalid token header. No credentials provided.' )
                raise exceptions.AuthenticationFailed( msg )
            s_token = token.split()
            len_s_token = len( s_token )
            if len_s_token == 1 or len_s_token > 2:
                msg = _(
                    'Invalid token header. Token string '
                    'should not contain spaces.' )
                raise exceptions.AuthenticationFailed( msg )
            try:
                result[ s_token[0].decode() ] = s_token[1].decode()
            except UnicodeError:
                msg = _(
                    'Invalid token header. Token string '
                    'should not contain invalid characters.' )
                raise exceptions.AuthenticationFailed( msg )
        return result

    def check_prefix( self, prefix ):
        return 'token' if prefix == 'token' else None


'''
import jwt
from rest_framework_jwt.settings import api_settings
#jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
#jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class Base_JWT_authentication( BaseAuthentication ):
    """
    Token based authentication using the JSON Web Token standard.
    """

    def authenticate( self, request ):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        jwt_value, setting = self.get_jwt_value( request )
        if jwt_value is None:
            return None

        try:
            payload = setting.jwt_decode_handler( jwt_value )
        except jwt.ExpiredSignature:
            msg = _( 'Signature has expired.' )
            raise exceptions.AuthenticationFailed( msg )
        except jwt.DecodeError:
            msg = _( 'Error decoding signature.' )
            raise exceptions.AuthenticationFailed( msg )
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user = self.authenticate_credentials( payload )

        return ( user, payload )

    def authenticate_credentials( self, payload, setting ):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()
        username = setting.jwt_get_username_from_payload( payload )

        if not username:
            msg = _( 'Invalid payload.' )
            raise exceptions.AuthenticationFailed( msg )

        try:
            user = User.objects.get_by_natural_key( username )
        except User.DoesNotExist:
            msg = _( 'Invalid signature.' )
            raise exceptions.AuthenticationFailed( msg )

        if not user.is_active:
            msg = _( 'User account is disabled.' )
            raise exceptions.AuthenticationFailed( msg )

        return user


class JSONWebTokenAuthentication( BaseJSONWebTokenAuthentication ):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    www_authenticate_realm = 'api'

    def get_jwt_value( self, request ):
        auth = get_authorization_header( request ).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth:
            if api_settings.JWT_AUTH_COOKIE:
                return request.COOKIES.get( api_settings.JWT_AUTH_COOKIE )
            return None

        auth_settings = self.find_settings( auth )
        if not auth_settings:
            return None

        if len( auth ) == 1:
            msg = _( 'Invalid Authorization header. No credentials provided.' )
            raise exceptions.AuthenticationFailed( msg )
        elif len( auth ) > 2:
            msg = _(
                'Invalid Authorization header. Credentials string '
                'should not contain spaces.' )
            raise exceptions.AuthenticationFailed( msg )

        return auth[1], auth_setting

    def find_settings( self, auth ):
        auth_realm = smart_text( auth[0].lower() )

        for realm, setting in api_settings.jwt_multi_realm.items():
            if auth_realm == realm.lower():
                return setting
        return None

    def authenticate_header( self, request ):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(
            api_settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm )
'''
