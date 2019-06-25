from tornado.web import RequestHandler, HTTPError
from tornado.options import options
from ...utils import json_utils
import asyncio
import logging

"""
    Support for Tornado Authentication.
"""


class UserMixin:
    """
        Should be mixed in with WebsocketHandlers
        or RequestHandlers. Make sure it is the
        first class in the declaration as it
        overrides methods in both handlers.
    """

    @property
    def cookie_name(self):
        """ return the cookie_name declared in options"""
        if self.settings.get("cookie_name"):
            return self.settings["cookie_name"]
        return options.cookie_name

    def get_current_user(self):
        """ return the current user from the cookie """
        result = self.get_secure_cookie(self.cookie_name)
        logging.debug("%s:%s", self.cookie_name, result)
        if result:
            result = json_utils.loads(result.decode("utf-8"))
        return result

    def set_current_user(self, value):
        """ put the current user in the cookie """
        if value:
            self.current_user = value
            self.set_secure_cookie(self.cookie_name, json_utils.dumps(value))
        else:
            self.clear_cookie(self.cookie_name)

    def set_transfer_user(self, value):
        return self.create_signed_value(
            "transfer-user", value=json_utils.dumps(value).encode("utf-8")
        )

    def get_transfer_user(self, value):
        user = self.get_secure_cookie("transfer-user", value)
        if user:
            self.current_user = user
            logging.info("current_user set: %s", user)
            return json_utils.loads(user.decode("utf-8"))


class LoginHandler(UserMixin, RequestHandler):
    """
        Can be called as ajax from the
        websocket client to get the auth cookie
        into the headers.
    """

    def login(self, username, password):
        raise Exception("subclass responsibility")

    async def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")

        user = self.login(username, password)
        if asyncio.iscoroutine(user):
            user = await user
        if user:
            self.set_current_user(user)
            self.write(self.set_transfer_user(user))
        else:
            self.set_status(403)
            self.finish("<html><body>Username or password incorrect</body></html>")


class LogoutHandler(UserMixin, RequestHandler):
    def get(self):
        """ removes cookie and redirects to optional next argument """
        self.set_current_user(None)
        self.redirect(self.get_argument("next", "/"))
