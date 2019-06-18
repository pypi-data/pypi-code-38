# pylint: disable=protected-access
"""
Define functions for validating a JWT and tracking the current token and claims
from a request.
"""

import functools

from cdislogging import get_logger
import flask
import jwt
from werkzeug.local import LocalProxy

from authutils.errors import (
    JWTError,
    JWTAudienceError,
    JWTExpiredError,
    JWTPurposeError,
)
from authutils.token.keys import get_public_key_for_token


#: Proxy for the current token, which gets assigned to in
#: ``require_auth_header``, so any function using that as a decorator can then
#: use ``current_token`` to get the claims for the token.
#:
#: (Note that this should really be called `set_current_claims`, since we're
#: using the claims here and not the raw token, which *is* what gets used for
#: `store_session_token`/`get_session_token`.)
#:
#: Anything that needs to check a JWT should try to use this, and set it if it
#: wasn't already, to avoid redundant validation.
current_token = LocalProxy(lambda: getattr(flask.g, "_current_token", None))


def set_current_token(token):
    flask.g._current_token = token


def store_session_token(token):
    flask.session["_authutils_access_token"] = token


def get_jwt_token():
    """
    Get the current JWT (in encoded form), from a bearer auth header.

    Requires flask request context.

    Return:
        str: encoded token
    """
    auth_header = flask.request.headers.get("Authorization")
    token = None
    if auth_header:
        items = auth_header.split(" ")
        if len(items) == 2 and items[0].lower() == "bearer":
            token = items[1]
    return token


def get_session_token():
    """
    Get the current JWT (in encoded form), from either a bearer auth header or
    the `_authutils_access_token` in the flask session.

    Requires flask request context and a matching Session interface.

    Return:
        str: encoded token
    """
    return get_jwt_token() or flask.session.get("_authutils_access_token")


def _validate_purpose(claims, pur):
    """
    Check that the claims from a JWT have the expected purpose claim ``pur``.

    Args:
        claims (dict): claims from token
        pur (str): expected purpose

    Return:
        None

    Raises:
        JWTPurposeError:
            if the claims do not contain a purpose claim or if it doesn't match
            the expected value
    """
    if "pur" not in claims:
        raise JWTPurposeError("claims missing `pur` claim")
    if claims["pur"] != pur:
        raise JWTPurposeError(
            "claims have incorrect purpose: expected {}, got {}".format(
                pur, claims["pur"]
            )
        )


def _validate_jwt(encoded_token, public_key, aud, issuers):
    """
    Validate the encoded JWT ``encoded_token``, which must satisfy the
    audiences ``aud``.

    This is just a slightly lower-level function to decode the token and
    perform the most basic checks on the token.

    - Decode JWT using public key; PyJWT will fail if iat or exp fields are
      invalid
    - Check audiences: token audiences must be a superset of required audiences
      (the ``aud`` argument); fail if not satisfied

    Args:
        encoded_token (str): encoded JWT
        public_key (str): public key to validate the JWT signature
        aud (set): non-empty set of audiences the JWT must satisfy

    Return:
        dict: the decoded and validated JWT

    Raises:
        ValueError: if receiving an incorrectly-typed argument
        JWTValidationError: if any step of the validation fails
    """
    # Typecheck arguments.
    if not isinstance(aud, set) and not isinstance(aud, list):
        raise ValueError("aud must be set or list")
    if not isinstance(issuers, set) and not isinstance(issuers, list):
        raise ValueError("issuers must be set or list")

    # To satisfy PyJWT, since the token will contain an aud field, decode has
    # to be passed one of the audiences to check here (so PyJWT doesn't raise
    # an InvalidAudienceError). Per the JWT specification, if the token
    # contains an aud field, the validator MUST identify with one of the
    # audiences listed in that field. This implementation is more strict, and
    # allows the validator to demand multiple audiences which must all be
    # satisfied by the token (see below).
    aud = set(aud)
    random_aud = list(aud)[0]
    try:
        token = jwt.decode(
            encoded_token, key=public_key, algorithms=["RS256"], audience=random_aud
        )
    except jwt.InvalidAudienceError as e:
        raise JWTAudienceError(e)
    except jwt.ExpiredSignatureError as e:
        raise JWTExpiredError(e)
    except jwt.InvalidTokenError as e:
        raise JWTError(e)

    # PyJWT validates iat and exp fields (and aud...sort of); everything else
    # must happen here.

    # iss
    # Check that the issuer of the token has the expected hostname.
    if token["iss"] not in issuers:
        msg = "invalid issuer {}; expected: {}".format(token["iss"], issuers)
        raise JWTError(msg)

    # aud
    # The audiences listed in the token must completely satisfy all the
    # required audiences provided. Note that this is stricter than the
    # specification suggested in RFC 7519.
    missing = aud - set(token["aud"])
    if missing:
        raise JWTAudienceError("missing audiences: " + str(missing))

    return token


def validate_jwt(
    encoded_token,
    aud,
    purpose="access",
    issuers=None,
    public_key=None,
    attempt_refresh=True,
    logger=None,
):
    """
    Validate a JWT and return the claims.

    Args:
        encoded_token (str): the base64 encoding of the token
        aud (Optional[Iterable[str]]):
            list of audiences that the token must satisfy; defaults to
            ``{'openid'}`` (minimum expected by OpenID provider)
        purpose (Optional[str]):
            which purpose the token is supposed to be used for (access,
            refresh, or id)
        issuers (Iterable[str]): list of allowed token issuers
        public_key (Optional[str]): public key to vaidate JWT with

    Return:
        dict: dictionary of claims from the validated JWT

    Raises:
        ValueError: if ``aud`` is empty
        JWTError:
            if auth header is missing, decoding fails, or the JWT fails to
            satisfy any expectation
    """
    logger = logger or get_logger(__name__, log_level="info")
    if not issuers:
        issuers = []
        for config_var in ["OIDC_ISSUER", "USER_API", "BASE_URL"]:
            value = flask.current_app.config.get(config_var)
            if value:
                issuers.append(value)
    if public_key is None:
        public_key = get_public_key_for_token(
            encoded_token, attempt_refresh=attempt_refresh, logger=logger,
        )
    if not aud:
        raise ValueError("must provide at least one audience")
    aud = set(aud)
    claims = _validate_jwt(encoded_token, public_key, aud, issuers)
    if purpose:
        _validate_purpose(claims, purpose)
    return claims


def validate_request(aud, purpose="access", logger=None):
    """
    Validate a ``flask.request`` by checking the JWT contained in the request
    headers.
    """
    logger = logger or get_logger(__name__, log_level="info")
    # Get token from the headers.
    try:
        encoded_token = flask.request.headers["Authorization"].split(" ")[1]
    except IndexError:
        raise JWTError("could not parse authorization header")
    except KeyError:
        raise JWTError("no authorization header provided")

    # Pass token to ``validate_jwt``.
    return validate_jwt(encoded_token, aud, purpose, logger=logger)


def require_auth_header(aud, purpose=None, logger=None):
    """
    Return a decorator which adds request validation to check the given
    audiences and (optionally) purpose.
    """
    logger = logger or get_logger(__name__, log_level="info")

    def decorator(f):
        """
        Decorate the given function to check for a valid JWT header.
        """

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            """
            Wrap a function to first validate the request header token.

            Assign the claims from the token to ``flask.g._current_token`` so
            the code inside the function can use the ``LocalProxy`` for the
            token (see top of this file).
            """
            set_current_token(validate_request(aud=aud, purpose=purpose, logger=logger))
            return f(*args, **kwargs)

        return wrapper

    return decorator
