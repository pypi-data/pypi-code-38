"""
Define functions for updating the public keys associated with certain token
issuers and retrieving the public key which can be used to verify a given JWT.

The public keys should be stored on the flask app in a `jwt_public_keys`
attribute, which will be a dictionary mapping issuer URLs (`iss` in a JWT) to
ordered dictionaries mapping key IDs to public key strings.

For example:

.. code-block:: python

    flask.current_app.jwt_public_keys == {
        'http://some-gen3-stack.net/user': OrderedDict([
            'key-01': '-----BEGIN PUBLIC KEY-----...',
            'key-02': '-----BEGIN PUBLIC KEY-----...',
        ]),
        'http://different-gen3-site.org/user': OrderedDict([
            'key-01': '-----BEGIN PUBLIC KEY-----...',
        ]),
    }
"""

from collections import OrderedDict
import json

from cdislogging import get_logger
import flask
import jwt
import requests


from authutils.errors import JWTError


def refresh_jwt_public_keys(user_api=None, logger=None):
    """
    Update the public keys that the Flask app is currently using to validate
    JWTs.

    Response from ``/jwt/keys`` should look like this:

    .. code-block:: javascript

    {
        "keys": [
            [
                "key-id-01",
                "-----BEGIN PUBLIC KEY---- ... -----END PUBLIC KEY-----\n"
            ],
            [
                "key-id-02",
                "-----BEGIN PUBLIC KEY---- ... -----END PUBLIC KEY-----\n"
            ]
        ]
    }

    Take out the array of keys, put it in an ordered dictionary, and assign
    that to ``flask.current_app.jwt_public_keys``.

    Args:
        user_api (Optional[str]):
            the URL of the user API to get the keys from; default to whatever
            the flask app is configured to use

    Return:
        None

    Side Effects:
        - Reassign ``flask.current_app.jwt_public_keys`` to the keys obtained
          from ``get_jwt_public_keys``, as an OrderedDict.

    Raises:
        ValueError: if user_api is not provided or set in app config
    """
    logger = logger or get_logger(__name__, log_level="info")
    # First, make sure the app has a ``jwt_public_keys`` attribute set up.
    missing_public_keys = (
        not hasattr(flask.current_app, "jwt_public_keys")
        or not flask.current_app.jwt_public_keys
    )
    if missing_public_keys:
        flask.current_app.jwt_public_keys = {}
    user_api = user_api or flask.current_app.config.get("USER_API")
    if not user_api:
        raise ValueError("no URL(s) provided for user API")
    path = "/".join(path.strip("/") for path in [user_api, "jwt", "keys"])
    jwt_public_keys = requests.get(path).json()["keys"]
    logger.info(
        "refreshing public keys; updated to:\n" + json.dumps(jwt_public_keys, indent=4)
    )
    flask.current_app.jwt_public_keys.update({user_api: OrderedDict(jwt_public_keys)})


def get_public_key(kid, iss=None, attempt_refresh=True, logger=None):
    """
    Given a key id ``kid``, get the public key from the flask app belonging to
    this key id. The key id is allowed to be None, in which case, use the the
    first key in the OrderedDict.

    - If current flask app is not holding public keys (ordered dictionary) or
      key id is in token headers and the key id does not appear in those public
      keys, refresh the public keys by calling ``refresh_jwt_public_keys()``
    - If key id is provided in the token headers:
      - If key id does not appear in public keys, fail
      - Use public key with this key id
    - If key id is not provided:
      - Use first public key in the ordered dictionary

    Args:
        kid (str): the key id
        attempt_refresh (bool):
            whether to try to refresh the public keys of the flask app if
            encountering a key id that does not exist in those keys; for fence
            itself this should be ``False``, and for other services it should
            be ``True``

    Return:
        str: the public key

    Side Effects:
        - From ``refresh_jwt_public_keys``: reassign
          ``flask.current_app.jwt_public_keys`` to the keys obtained from
          ``get_jwt_public_keys``.

    Raises:
        JWTValidationError:
            if the key id is provided and public key with that key id is found
    """
    iss = (
        iss
        or flask.current_app.config.get("OIDC_ISSUER")
        or flask.current_app.config["USER_API"]
    )
    logger = logger or get_logger(__name__, log_level="info")
    need_refresh = not hasattr(flask.current_app, "jwt_public_keys") or (
        kid and kid not in flask.current_app.jwt_public_keys.get(iss, {})
    )
    if need_refresh and attempt_refresh:
        refresh_jwt_public_keys(iss, logger=logger)
    if iss not in flask.current_app.jwt_public_keys:
        raise JWTError("issuer not found: {}".format(iss))
    iss_public_keys = flask.current_app.jwt_public_keys[iss]
    try:
        return iss_public_keys[kid]
    except KeyError:
        raise JWTError("no key exists with given key id: {}".format(kid))


def get_public_key_for_token(encoded_token, attempt_refresh=True, logger=None):
    """
    Attempt to look up the public key which should be used to verify the token.

    Really just a thin wrapper around ``get_public_key`` which grabs the
    ``kid`` from the token headers and the ``iss`` from the token claims.

    Args:
        encoded_token (str): encoded JWT
        attempt_refresh (bool): whether to refresh public keys

    Return:
        str: public RSA key for token verification
    """
    logger = logger or get_logger(__name__, log_level="info")
    try:
        kid = jwt.get_unverified_header(encoded_token).get("kid")
    except jwt.InvalidTokenError as e:
        raise JWTError(e)

    force_issuer = flask.current_app.config.get("FORCE_ISSUER")
    if force_issuer:
        iss = flask.current_app.config["USER_API"]
    else:
        try:
            iss = jwt.decode(encoded_token, verify=False).get("iss")
        except jwt.InvalidTokenError as e:
            raise JWTError(e)
    return get_public_key(kid, iss=iss, attempt_refresh=attempt_refresh, logger=logger)
