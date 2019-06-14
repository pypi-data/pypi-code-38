"""Test helpers for the API"""
from base64 import b64encode
from collections import OrderedDict
import requests_mock
from faker import Faker

from argus_cli.settings import settings

RANDOMIZE = Faker()


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
    
class Mocker(requests_mock.Mocker, metaclass=Singleton):
    """We're using a Singleton class here to use instead of requests_mock.mocker,
    because requests_mock.mocker prevents us from nesting mocks as it replaces its
    own instances in context managers. By ensuring that there can only be one instance
    of the Mocker class, we can be sure that nesting will be allowed
    """
    def __enter__(self):
        if not self._last_send:
            self.start()
        return self

def response(url: str, status_code: int = 200, method: str = 'GET', json=None) -> callable:
    """Creates a decorator that can be used to mock the given URL
    and intercept calls to it with a response of the given status code
    and JSON.

    :param str url: URL to intercept
    :param int status_code: HTTP status to respond with
    :param dict json: JSON body to respond with (optional)
    """
    def decorator(function):
        """Mock {url}, respond with HTTP {status_code}""".format(url=url, status_code=status_code)
        def mock_response(*args, **kwargs):
            with Mocker(real_http=True) as mock:
                mock.register_uri(method.upper(), url, status_code=status_code, json=json)
                return function(*args, **kwargs)
        return mock_response
    return decorator

def mock_authentication(mode: str):
    return response(
        url="%s/authentication/v1/%s/authenticate" % (settings["api"]["api_url"], mode),
        status_code=201,
        method="POST",
        json={ "data": { "sessionKey": str(b64encode(b"mockSessionKey12345")), "cookie": "dqjweioqjoijwef", "username": "mock"} }
    )

def fake_response(response_definition, key=None):
    """Recursive method that traverses a dict response and generates
    fake data for each key, faking a successful response
    """
    def is_leaf(response_definition):
        # If it ONLY  has a type key, and nothing else,
        # this is a leaf and we should generate fake data for it
        if isinstance(response_definition, (dict, OrderedDict)):
            if ("type",) == tuple(response_definition.keys()):
                return True
            # If it has several keys, but no children that have a "type"
            # key of their own, this is also a leaf
            if not any(
                    filter(lambda x: "type" in x, [
                        value for key, value in response_definition.items()
                        if isinstance(value, dict)
                    ])):
                return True
            # Lists count as leaves as well
            if "type" in response_definition and response_definition["type"] == "list":
                return True
        return not response_definition

    # If the definition only contains type, we can replace this
    # object with fake data of that type
    if is_leaf(response_definition) and response_definition:
        if response_definition["type"] == 'str' and "enum" in response_definition:
            # Always pick the first enum so the generated files dont change
            # when example responses are created
            return response_definition["enum"][0]
        elif response_definition["type"] == "list" and "items" in response_definition:
            return [fake_response(response_definition["items"])]
        elif response_definition["type"] == "dict":
            if "items" in response_definition:
                return fake_response(response_definition["items"])
            return {}
        else:
            if key and \
            (key.lower() in ("username", "email", "link", "url", "name", "responsecode") \
              or "timestamp" in key.lower()):
                return fake_data_for(key)
            else:
                return fake_data_for(response_definition["type"])

    elif isinstance(response_definition, (dict, OrderedDict)):
        return OrderedDict({
            key: fake_response(value, key)
            for key, value in sorted(response_definition.items())
            if isinstance(value, dict) and "type" in value
        })
    else:
        return response_definition

def fake_data_for(python_type: str):
    """Generates fake data for a given type, where type can be any basic python type,
    such as int, str, float, bool; but it also supports more specific types, such as
    url, username, and email

    :param str python_type: String representation of python type
    :returns: Generated fake value
    """
    python_type = python_type.lower()

    if python_type == 'int':
        return 8
    elif python_type == 'bool':
        return False
    elif python_type == 'float':
        return 3.14
    elif python_type == 'None':
        return None
    elif python_type == "responsecode":
        # Always return successful response since otherwise
        # we wouldnt get a response anyway
        return 200
    elif python_type == 'username':
        return "Dr.Username"
    elif "timestamp" in python_type:
        return 957484801
    elif python_type == 'email':
        return 'dr.username@space.com'
    elif python_type in ('name', 'firstname'):
        return 'johnny'
    elif python_type in ('surname', 'lastname'):
        return 'mnemonic'
    else:
        if hasattr(RANDOMIZE, python_type):
            return getattr(RANDOMIZE, python_type)()
        else:
            return "This field may contain text"