import hmac, os, json, getpass
from time import time
from functools import wraps
from hashlib import sha256
from base64 import urlsafe_b64encode, b64decode
from urllib.parse import urlparse
from requests import post
from argus_cli.settings import settings


def csrf_token_for(url: str, key: str) -> str:
    """Generates a CSRF token for an API URL
    
    :param url: URL endpoint
    :param key: User's session key
    :returns: CSRF token
    """
    # Parse the URL into its components
    u = urlparse(url)

    # Create the original path, i.e https://domain.tld/path
    path = "%s://%s%s" % (u.scheme, u.netloc, u.path)

    # Decode the session key
    session_key = b64decode(key)

    jwt_settings = {
        "alg": "HS256",
        "typ": "JWT"
    }

    jwt_contents = {
        "url": path,
        "timestamp": int(round(time()*1000))
    }

    canonical_string = "%s.%s" % (
        urlsafe_b64encode(json.dumps(jwt_settings).encode('utf-8')).decode('utf-8'),
        urlsafe_b64encode(json.dumps(jwt_contents).encode('utf-8')).decode('utf-8')
    )

    # Sign the URL, timestamp,
    signature = hmac.new(session_key, msg=canonical_string.encode("utf-8"), digestmod=sha256).digest()
    token = "%s.%s" % (canonical_string, urlsafe_b64encode(signature).decode('utf-8'))
    return token

def with_api_key(api_key: str) -> dict:
    """Authenticates the user towards the API with an API key

    :param api_key: User's API key
    :return: Authentication headers
    """
    # TODO: Check if the API Key is valid for the user
    return {
        "Argus-API-Key": api_key
    }


def with_credentials(username: str = "", password: str = "", method: str = "ldap", base_url: str = None) -> callable:
    """Authenticates the user with the API via TOTP, Radius or LDAP, and returns a function
    that creates the correct headers with CSRF token for a given URL, using the user's
    sessionKey and cookie.

    :param base_url: API URL
    :param method: Authentication method
    :param username: The user's username
    :param password: The user's password
    :return: Authentication data
    """
    base_url = base_url or settings["api"]["api_url"]
    auth_url = "%s/authentication/v1/%s/authenticate" % (base_url, method)

    parameters = {
        "userName": username,
        "password": password
    }
    if not username:
        parameters["userName"] = input("Username: ")
    if not password:
        parameters["password"] = getpass.getpass("Enter %spassword: " % ("AD3 " if method == "ldap" else ""))
    if method == "totp":
        parameters["tokenCode"] = input("Enter TOTP token code: ")
    elif method == "radius":
        parameters["tokenCode"] = input("Enter Radius token code: ")
        parameters["mode"] = "AUTHENTICATION"
    elif method not in ("ldap", "password"):
        raise ValueError("Invalid authentication method: %s" % method)

    response = post(auth_url, json=parameters)

    # Accept both 200 and 201 response
    if response.status_code in (200, 201):
        authentication_data = response.json()["data"]

        def authenticate(url: str) -> dict:
            """Authenticator function, generates a CSRF token for the given URL
            
            :param str url: URL to create CSRF token for
            :returns: Headers to pass to a request
            """
            return {
                "Cookie": "argus_username=%s; argus_cookie=%s;" % (authentication_data["username"], authentication_data["cookie"]),
                "Argus-CSRF-Token": csrf_token_for(url, authentication_data["sessionKey"])
            }
        return authenticate
    else:
        print("Authentication failed %d" % response.status_code)

        # Return empty headers — failed authentication does not need to raise 
        # any further errors.
        return lambda x: {}

def with_authentication(mode: str = "password", base_url: str = None, username: str = "", api_key: str = "") -> callable:
    """Creates a decorator that can be used by plugins to have authentication handled for them,
    by calling with_credentials or with_api_key and then passing the authentication headers
    to the decorated function as `authentication`. 

    Generated API methods accept `authentication` parameter, so after decorating a function
    with this, the authentication argument can be passed directly to any API method.

    :param str mode: LDAP, Radius, Password or API key
    :returns: decorator function
    """
    base_url = base_url or settings["api"]["api_url"]

    # If an API key is given, automatically switch to API key mode
    if api_key:
        mode = "api_key" 

    if mode.lower() not in ('apikey', 'api_key'):
        authentication_header_factory = with_credentials(method=mode, username=username, base_url=base_url)
    else:
        api_key = api_key or settings["api"]["api_key"] or input("Enter API key: ")
        authentication_header_factory = lambda _: with_api_key(api_key)

    def decorator(function):
        """Returns a callable that can be used to create authentication headers for a URL,
        for LDAP, TOTP, Password or API key authentication. This will be passed in to the function
        as authentication=function, and can be passed to any API call
        """

        # Ensure the docstring and function name is copied over
        @wraps(function)
        def authenticate(*args, **kwargs):
            """[{mode} AUTHENTICATED]{doc}""".format(mode=mode, doc=function.__doc__)
            kwargs.update({
                "authentication": authentication_header_factory
            })
            return function(*args, **kwargs)
        return authenticate
    return decorator
