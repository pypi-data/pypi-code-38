import functools
import json

from addict import Dict
from cached_property import cached_property
from cdiserrors import AuthZError
import flask
from werkzeug.local import LocalProxy

from authutils.errors import AuthError
from authutils.token.validate import set_current_token, validate_request


def set_current_user(**kwargs):
    flask.g.user = CurrentUser(**kwargs)
    set_current_token(flask.g.user._claims)
    return flask.g.user


# Proxy for the current user.
#
# Other modules importing authutils can import ``current_user`` from here,
# which will use ``_get_or_set_current_user`` to look up the user.
current_user = LocalProxy(set_current_user)


class CurrentUser(object):
    """
    Information about the user which issued a request.

    Args:
        _claims (dict): claims from the user's token (if validated already)
        jwt_kwargs (dict): keyword arguments to pass to ``validate_request``

    Attributes:
        _claims (dict): dictionary of claims from user token
        id (str): unique ID for the user
        username (str): user's username, according to token
        projects (Dict[str, List[str]): mapping of project IDs to roles
        is_admin (bool): whether the user has admin privileges
    """

    def __init__(self, claims=None, jwt_kwargs=None):
        jwt_kwargs = jwt_kwargs or {}
        if "aud" not in jwt_kwargs:
            jwt_kwargs["aud"] = {"openid"}
        self._claims = claims or validate_request(**jwt_kwargs)
        self.id = self._claims["sub"]
        self.username = self._get_user_info("name")
        self.projects = self._get_user_info("projects", default={})

    def __str__(self):
        str_out = {"id": self.id, "username": self.username, "is_admin": self.is_admin}
        return json.dumps(str_out)

    def _get_user_info(self, field, default=None):
        return self._claims.get("context", {}).get("user", {}).get(field, default)

    @cached_property
    def is_admin(self):
        """
        Indicate whether the current user has admin privileges.

        Return:
            bool: whether user is admin
        """
        # Try to just use the user context from the claims. If that doesn't
        # have the ``is_admin`` field then use the database lookup.
        return bool(self._get_user_info("is_admin"))

    def require_admin(self):
        """
        Raise an error if this user doesn't have admin privileges.
        """
        if not self.is_admin:
            raise AuthZError("user ({}) does not have admin privileges".format(self.id))

    def get_project_ids(self, role="_member_"):
        """
        Return a list of projects for which the user has this role.
        """
        return [
            project for project, roles in self.projects.iteritems() if role in roles
        ]


def set_global_user(**decorator_kwargs):
    """
    Wrap a Flask blueprint view function to set the global user
    ``flask.g.user`` to an instance of ``CurrentUser``, according to the
    information from the JWT in the request headers. The validation will also
    set the current token.

    This requires a flask application and request context.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            set_current_user(**decorator_kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator
