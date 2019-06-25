
import base64
import logging
import urllib
import  tornado.web
import tornado.escape
import tornado.auth
from tornado import escape
from .authentication import UserMixin

LOGGER = logging.getLogger(__name__)


class CognitoHandler(UserMixin, tornado.web.RequestHandler, tornado.auth.OAuth2Mixin):
    """ 
        This plays safe with AWS Congnito
        Settings should have:

        "cookie_name": "tornado-user",
        "cookie_secret": "it_was_a_dark_and_stormy_night_cognito",
        "login_url": "https://<provided by ngrok>.ngrok.io/login",
        "cognito_oauth": {
            "key": "<client_id provided by cognito>",
            "secret": "<secret provided by cognito>",
            "redirect_url": "https://<provided by ngrok>.ngrok.io/login",
            "endpoint": "https://<provided by cognito>.amazoncognito.com",
        }

    """
    def initialize(self):
        self._OAUTH_SETTINGS_KEY = "cognito_oauth"
        cognito_domain = self.settings[self._OAUTH_SETTINGS_KEY]["endpoint"]
        self._OAUTH_AUTHORIZE_URL = f"{cognito_domain}/oauth2/authorize"
        self._OAUTH_ACCESS_TOKEN_URL = f"{cognito_domain}/oauth2/token"
        self._OAUTH_USER_INFO_URL = f"{cognito_domain}/oauth2/userInfo"
        self._OAUTH_LOGIN_URL = f"{cognito_domain}/oauth2/login"
        self._REDIRECT_URL = self.settings[self._OAUTH_SETTINGS_KEY]["redirect_url"]

    async def get(self):
        if self.get_argument("code", False):
            LOGGER.debug("have code")
            http = self.get_auth_http_client()
            access = await self.get_authenticated_user(
                redirect_uri=self._REDIRECT_URL, code=self.get_argument("code")
            )
            LOGGER.debug("have access %r", access)
            response = await http.fetch(
                self._OAUTH_USER_INFO_URL,
                headers={"Authorization": f"Bearer {access['access_token']}"},
                raise_error=False,
            )
            if response.code != 200:
                LOGGER.debug("failed: %s %r", response.code, response.body)
                raise tornado.web.HTTPError(response.code)
            user = escape.json_decode(response.body)
            LOGGER.debug("have user: %r", user)
            # Save the user and access token with
            # e.g. set_secure_cookie.
            self.set_current_user(user)
            self.redirect("/")
        else:
            try:
                LOGGER.debug("redirecting")
                await self.authorize_redirect(
                    redirect_uri=self._REDIRECT_URL,
                    client_id=self.settings["cognito_oauth"]["key"],
                    scope=["profile", "email", "openid"],
                    response_type="code",
                    extra_params={},
                )
                LOGGER.debug("redirected")
            except Exception as ex:
                LOGGER.exception(ex)
                raise

    async def get_authenticated_user(self, redirect_uri: str, code: str):

        client_id = self.settings["cognito_oauth"]["key"]
        client_secret = self.settings["cognito_oauth"]["secret"]
        http = self.get_auth_http_client()
        body = urllib.parse.urlencode(
            {
                "redirect_uri": redirect_uri,
                "code": code,
                "client_id": client_id,
                "grant_type": "authorization_code",
            }
        )
        authorized = base64.b64encode(
            f"{client_id}:{client_secret}".encode("utf-8")
        ).decode("ascii")
        LOGGER.debug("basic %s", authorized)
        response = await http.fetch(
            self._OAUTH_ACCESS_TOKEN_URL,
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {authorized}",
            },
            body=body,
        )
        return escape.json_decode(response.body)
