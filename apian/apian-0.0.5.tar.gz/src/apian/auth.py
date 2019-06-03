from functools import wraps
import re
import flask
import jwt


AUTH_CONFIG_KEY = "authentication"


def authentication_enabled(auth_config):
    """Predicate on the auth configuration dictionary that returns whether
    authentication should be enabled for the application.

    :param auth_config: The authentication config dictionary.
    """
    if auth_config is None:
        return False
    return auth_config.get("enabled", True)


def authenticated(route):
    """Decorator for Flask routes that checks if the authentication header
    exists and is valid, and if it is, passes the user id as a named parameter
    `user_id` to the route.

    :param route: The route to wrap.
    """

    @wraps(route)
    def wrapper(*args, **kwargs):
        auth_config = flask.current_app.config[AUTH_CONFIG_KEY]
        if not authentication_enabled(auth_config):
            return route(*args, user_id=auth_config["user_id"], **kwargs)

        header = flask.request.headers.get("Authorization")
        if header is None:
            flask.abort(401, "Missing authorization header")

        try:
            claims = _extract_claims(auth_config, header)
        except ValueError as exc:
            flask.abort(401, str(exc))
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            flask.abort(401, "Invalid or expired authentication token")

        user_id = claims.get("sub")
        if user_id is None:
            flask.abort(401, "Missing user id")
        return route(*args, user_id=user_id, **kwargs)

    return wrapper


_TOKEN_PATTERN = re.compile(r"Bearer (.*)")


def _extract_claims(auth_config, header):
    """Return a dictionary of claims extracted from the Authorization header.

    :param auth_config: The authentication config dictionary.
    :param header: The contents of the authorization header.
    """
    m = _TOKEN_PATTERN.match(header)
    if not m:
        raise ValueError("Invalid authorization header")

    token = m.group(1)
    return jwt.decode(
        token, auth_config.get("secret"), algorithms=["HS256"]
    )
