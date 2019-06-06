from spell.api import base_client
from spell.api.utils import url_path_join


USER_RESOURCE_URL = "users"


class UserClient(base_client.BaseClient):

    def create(self, user_name, email, password, recaptcha_token, full_name=None,
               organization=None, admin_override=None, terms_accepted=False):
        """Create a new user at the server

        Keyword arguments:
        user_name -- user_name of the new user (must be at least 4 characters)
        email -- email of the new user
        password -- password of the new user (must be at least 8 characters)
        full_name -- optional, full name of new user
        organization -- optional, company or group new user is associated with

        Returns:
        a User object for the new user

        """
        payload = {
            "user": {
                "user_name": user_name, "password": password, "email": email,
                "full_name": full_name,
                "organization": organization,
                "terms_accepted": terms_accepted},
            "admin_override": admin_override,
            "recaptcha_token": recaptcha_token}
        r = self.request("post", USER_RESOURCE_URL, payload=payload)
        self.check_and_raise(r)

        # Workaround tests that do not take cookies into account
        # TODO(jay): Fix the tests!
        self.session.cookies.clear()

        return self.get_json(r)["user"]

    def _login(self, user_name, email, password):
        """Log in a user to the server

        Keyword arguments:
        user_name -- user_name of the user
        email -- email of the user
        password -- password of the user

        Returns:
        a User object and an authentication token for the user

        """
        payload = {"user": {"user_name": user_name, "password": password,
                   "email": email}}
        r = self.request("post", "{}/{}".format(USER_RESOURCE_URL, "login"),
                         payload=payload)
        self.check_and_raise(r)
        resp = self.get_json(r)
        self.token = resp["token"]
        return resp["user"], self.token

    def login_with_email(self, email, password):
        """Log in a user by email to the server

        Keyword arguments:
        email -- email of the user
        password -- password of the user

        Returns:
        an authentication token for the user

        """
        return self._login("", email, password)

    def login_with_username(self, user_name, password):
        """Log in a user by user_name to the server

        Keyword arguments:
        user_name -- user_name of the user
        password -- password of the user

        Returns:
        an authentication token for the user

        """
        return self._login(user_name, "", password)

    def logout(self):
        """Log out a user from the server"""
        r = self.request("post", "{}/{}".format(USER_RESOURCE_URL, "logout"))
        self.check_and_raise(r)

    def check_password(self, password):
        """Checks password for a logged-in user

        Keyword arguments:
        password -- password of the user

        Returns:
        nothing if successful
        """
        payload = {"password": password}
        r = self.request("post", "{}/{}".format(USER_RESOURCE_URL, "me/check_password"),
                         payload=payload)
        self.check_and_raise(r)

    def change_password(self, old_password, new_password):
        """Change password for a logged-in user, require password before changing

        Keyword arguments:
        old_password -- current password for the user
        new_password -- new password for the user

        Returns:
        nothing if successful

        """
        payload = {
            "new_password": new_password,
            "old_password": old_password,
        }
        r = self.request("put", "{}/{}".format(USER_RESOURCE_URL, "me/change_password"),
                         payload=payload)
        self.check_and_raise(r)

    def get_user_info(self):
        """Get user information from the server

        Returns:
        a User object for the user

        """
        r = self.request("get", "{}/{}".format(USER_RESOURCE_URL, "me"))
        self.check_and_raise(r)
        return self.get_json(r)["user"]

    def get_billing_info(self):
        """Get user billing information from the server

        Returns:
        a Billing object for the user

        """
        r = self.request("get", url_path_join("billing", self.owner, "status"))
        self.check_and_raise(r)
        return self.get_json(r)["billing_status"]
