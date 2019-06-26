import jwt
import requests


class CodeGrantFlowTokenResponse:
    """
    Container/"DTO"-of-sorts for (persistent) token response properties, helps with IDEs.
    """
    def __init__(self, access_token, token_type, user_id, organization_id, app_id):
        self.access_token = access_token  # "Persistent" access token / "API KEY"
        self.token_type = token_type  # Keyword to use in "Authorization" Header as a prefix for the token
        self.user_id = user_id  # ID of the user to which the token grants an access
        self.organization_id = organization_id  # ID of the organization in which context the token allows API requests
        self.app_id = app_id  # ID of (your) app that requested for persistent access token


class GiosgappTriggerContext:
    """
    Abstraction for views in Django Framework, to conveniently validate and parse Giosg Trigger Requests.
     - Validates query parameters of the trigger request
     - Validates the signature of data-JWT using app secret
     - Validates expiration times of both data-JWT and token-JWT
     - Validates existence of redirect_uri if type is "install"
     - Raises ValueError with an error message if any check fails.

     tldr: Validates everything for you and raises ValueError in case of errors. Provides helper methods.

    Additionally provides methods

        get_auth_header_content():
            constructs a string for Authorization header content, using trigger's token and app secret
            returns string to insert in "Authorization" Header, to query Giosg HTTP API while valid (.access_token_exp)
            https://developers.giosg.com/giosg_apps.html#using-http-api-from-app-triggers

        exchange_persistent_token(): ONLY VIABLE WITH BOT USER -- ELSE RAISES A VALUE ERROR
            requests (via Code Grant Flow) for a persistent access token
            returns CodeGrantFlowTokenResponse, or raises ValueError with an error message
            https://developers.giosg.com/authentication.html#token-request-with-authorization-code-grant-flow

     Properties:

        .type -- string : Trigger type
        .user_id -- string : UUID of the current user or null if not applicable
        .org_id -- string : UUID of the organization/company where the user_id belongs to
        .chat_id -- string : UUID of the related chat, if any, otherwise null
        .visitor_id -- string : ID of the related visitor, if available, otherwise null
        .inst_id -- string : UUID of the app instance/installation.
        .app_id -- string : UUID of the app
        .app_user_id -- string : UUID of any related bot user, or null if no such user was created on app installation
        .access_token -- string : Non-persistent JWT (JSON Web Token) to use when using giosg HTTP API endpoints
        .access_token_exp -- string : Non-persistent
    """
    def __init__(self, django_request, giosg_app_secret):
        """
        :param django_request: https://docs.djangoproject.com/en/2.1/ref/request-response/#httprequest-objects
        :param giosg_app_secret: https://developers.giosg.com/giosg_apps.html#trigger-requests
        """

        # Check type of the trigger condition exists
        trigger_type = django_request.GET.get('type')
        if not trigger_type:
            raise ValueError('Missing URI query parameter "type"')

        # Check data JWT (signed with the app secret) exists
        app_data = django_request.GET.get('data')
        if not app_data:
            raise ValueError('Missing URI query parameter "data"')

        # Check request is coming from Giosg (via signed data-JWT), and check both JWTs for expiration
        try:
            app_data = jwt.decode(app_data, giosg_app_secret, algorithm='HS256')
        except jwt.InvalidSignatureError:
            raise ValueError('Data-JWT has an invalid signature, your connection may be tampered.')
        except jwt.ExpiredSignatureError:
            raise ValueError('Data-JWT is expired, request may be replayed from browser history (or tampered).')

        # Additionally check redirect URI exists if type is "install", and assign it to properties if so
        self.redirect_uri = None
        if trigger_type == 'install':
            self.redirect_uri = django_request.GET.get('redirect_uri')
            if not self.redirect_uri:
                raise ValueError('Missing URI query parameter "redirect_uri"')

        # Additionally check access token if type is ANYTHING BUT uninstall, and assign it to properties if so
        self.access_token = None
        self.access_token_exp = None
        if trigger_type != 'uninstall':
            access_token = django_request.GET.get('token')
            if not access_token:
                raise ValueError('Missing URI query parameter "token"')
            access_token_data = jwt.decode(access_token, verify=False)
            self.access_token = access_token
            self.access_token_exp = access_token_data['exp']

        # Assign ever-present properties
        self.type = trigger_type
        self.user_id = app_data['user_id']
        self.org_id = app_data['org_id']
        self.chat_id = app_data['chat_id']
        self.visitor_id = app_data['visitor_id']
        self.inst_id = app_data['inst_id']
        self.app_id = app_data['app_id']
        self.app_user_id = app_data['app_user_id']

        # Set these "private" for methods
        self.__app_secret = giosg_app_secret
        self.__app_user_code = app_data['app_user_code']

    def get_auth_header_content(self):
        """
        :return: String for "Authorization" HTTP header's content
        """
        # Check the app trigger for access token, it is NOT present if type is 'uninstall'
        if not self.access_token:
            raise ValueError('An access token is required to form an Authorization header.')
        return 'GIOSGAPP {} {}'.format(self.access_token, self.__app_secret)

    def exchange_persistent_access_token(self):
        """
        :return: CodeGrantFlowTokenResponse with persistent access token
        """
        # Check the app trigger for an existing bot user, else it is impossible to request for persistent token
        if not self.app_user_id:
            raise ValueError('A bot user is required to request a persistent access token.')

        # Default Content-Type is application/x-www-form-urlencoded as required by Giosg API
        r = requests.post(
            'https://service.giosg.com/identity/token',
            data={
                'grant_type': 'authorization_code',
                'code': self.__app_user_code,
                'client_id': self.app_id,
                'client_secret': self.__app_secret
            }
        )

        # Unpack response content
        r_data = r.json()

        # Process any (known) errors
        if r.status_code == 400:
            raise ValueError('{} {}'.format(r_data['error'], r_data['error_description']))

        return CodeGrantFlowTokenResponse(
            r_data['access_token'],
            r_data['token_type'],
            r_data['user_id'],
            r_data['organization_id'],
            r_data['app_id']
        )
