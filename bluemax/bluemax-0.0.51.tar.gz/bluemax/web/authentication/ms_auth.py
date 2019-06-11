import tornado.web
import tornado.auth
from tornado import escape
from tornado.options import options
from .authentication import LoginHandler, UserMixin
from urllib.parse import urlencode
from ...utils import json_utils
import logging


class ProfileHandler(UserMixin, tornado.web.RequestHandler):
    @tornado.web.authenticated
    async def get(self):
        self.finish(json_utils.dumps(self.current_user, indent=4))


class MSLoginHandler(LoginHandler, tornado.auth.OAuth2Mixin):

    _USER_URL = "https://graph.microsoft.com/v1.0/me"
    _OAUTH_AUTHORIZE_URL = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
    )
    _OAUTH_ACCESS_TOKEN_URL = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    )

    async def get(self):
        if self.get_argument("code", False):
            access = await self.get_authenticated_user(
                redirect_uri=self.settings["login_url"],
                client_id=self.settings["ms_oauth"]["key"],
                client_secret=self.settings["ms_oauth"]["secret"],
                code=self.get_argument("code"),
                extra_params={"scope": "User.Read profile openid email"},
            )
            user = await self.get_user_profile(
                self._USER_URL, access_token=access["access_token"]
            )
            logging.info(user)
            self.set_current_user(user)
            self.redirect(self.get_argument("state"))
        else:
            await self.authorize_redirect(
                redirect_uri=self.settings["login_url"],
                client_id=self.settings["ms_oauth"]["key"],
                client_secret=self.settings["ms_oauth"]["secret"],
                scope=["User.Read"],
                response_type="code",
                extra_params={
                    "approval_prompt": "auto",
                    "state": self.get_argument("next"),
                },
            )

    async def get_user_profile(self, url, access_token):
        http = self.get_auth_http_client()
        try:
            response = await http.fetch(url, headers={"Authorization": access_token})
        except Exception as ex:
            logging.exception(ex)
            raise
        logging.debug(response.body)
        return escape.json_decode(response.body)

    async def get_authenticated_user(
        self, redirect_uri, client_id, client_secret, code, extra_params=None
    ):
        http = self.get_auth_http_client()
        args = {
            "redirect_uri": redirect_uri,
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
        }
        if extra_params:
            args.update(extra_params)
        body = urlencode(args)
        try:
            response = await http.fetch(
                self._OAUTH_ACCESS_TOKEN_URL,
                method="POST",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                body=body,
            )
        except Exception as ex:
            logging.info(body)
            logging.exception(ex)
            raise
        logging.debug(response.body)
        args = escape.json_decode(response.body)
        session = {
            "access_token": args.get("access_token"),
            "expires_in": args.get("expires_in"),
        }
        return session
