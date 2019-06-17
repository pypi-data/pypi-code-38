import json as js
import os
import re
import requests
import configparser
from getpass import getpass
from pathlib import Path
import hashlib
import sys

# Note: If MANTA_URL and/or BLACKFIN_URL are specified as environment
# variables, they will always override the regional settings below.
DEFAULT_SYSTEM_SETTINGS = {
    'us': {
        'prod': {
            'MANTA_URL': 'https://console.demystdata.com/',
            'BLACKFIN_URL': 'https://blackfin.us.mt.p.demystdata.com:443/'
        },
        'stg': {
            'MANTA_URL': 'https://console-stg.demystdata.com/',
            'BLACKFIN_URL': 'https://blackfin-stg.us.mt.n.demystdata.com:443/'
        }
    },
    'local':{
        'dev': {
            'MANTA_URL': 'https://manta.local.mt.d.demystdata.com:8443/',
            'BLACKFIN_URL': 'https://blackfin.local.mt.d.demystdata.com:8443/'
        },
        'sandbox': {
            'MANTA_URL': 'https://console-dev.demystdata.com/',
            'BLACKFIN_URL': 'https://blackfin-dev.us.mt.d.demystdata.com:443/'
        }
    }
}

def wants_debug():
    return os.getenv("DEBUG", False)

def wants_stack_trace():
    return os.getenv("STACK_TRACE", False)

def debug(*strs):
    if wants_debug():
        print(*strs)

def running_in_ipython():
    try:
        __IPYTHON__
        return True
    except NameError:
        return False

# Custom exception handler, used unless DEBUG is on.  Doesn't print
# stack trace, just message.
def handle_exception(exc_type, exc_value, exc_traceback):
    # Ignore KeyboardInterrupt so a console program can exit with Ctrl + C
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print(str(exc_value), file=sys.stderr)

# The configuration is split into two parts, user settings and system
# settings.  User settings (e.g. username and password) are taken
# either from a config file or from named parameters, with parameters
# taking precedence.  System settings are hardcoded in the
# DEFAULT_SYSTEM_SETTINGS dictionary above.  The environment and
# region can be specified either via parameters or in the user config
# file, and default to us/prod otherwise.
class Config(object):

    def __init__(self, config_file=None, region=None, env=None, key=None, username=None, password=None, jwt=None):

        user_settings = {}
        if config_file:
            self.config_file = config_file
        else:
            debug("Looking in ", os.getcwd(), " for config file")
            self.config_file = try_to_find_config_file(os.getcwd())
            debug("Tried to find config file and found", self.config_file)
        if self.config_file:
            user_settings = parse_config(Path(self.config_file).read_text())
        if (key != None):
            user_settings["API_KEY"] = key
        if (username != None):
            user_settings["USERNAME"] = username
        else:
            if "DEMYST_USERNAME" in os.environ:
                user_settings["USERNAME"] = os.environ["DEMYST_USERNAME"]
        if (password != None):
            user_settings["PASSWORD"] = password
        effective_region = region or user_settings.get("REGION") or "us"
        effective_env = env or user_settings.get("ENV") or "prod"
        system_settings = DEFAULT_SYSTEM_SETTINGS[effective_region][effective_env]
        debug("System settings", system_settings)
        debug("user settings", user_settings)
        self.settings = { **system_settings, **user_settings }
        # Use environment variables instead of regional settings if specified.
        if (os.environ.get("BLACKFIN_URL")):
            self.settings["BLACKFIN_URL"] = os.environ.get("BLACKFIN_URL")
        if (os.environ.get("MANTA_URL")):
            self.settings["MANTA_URL"] = os.environ.get("MANTA_URL")
        self.settings["REGION"] = effective_region
        self.settings["ENV"] = effective_env
        # Organization name, fetched lazily when required by get_organization()
        self.organization = None
        # Console userid and fullname, fetched lazily when required by track
        self.console_userid = None
        self.console_fullname = None
        # Provider data cache: maps provider name to full JSON data from Manta
        self.provider_cache = None
        # Remove any JWT token if its name or env don't match what we have
        if self.has_jwt_token():
            json = self.get_jwt_token_json()
            if self.get("USERNAME") and self.get("ENV"):
                if (json["username"] != self.get("USERNAME")) or (json["env"] != self.get("ENV")):
                    self.remove_jwt_token()
        # JWT/SSO: JWT token passed in as argument.
        if jwt:
            self.put_jwt_token(jwt)
        # Custom exception handler
        if not wants_stack_trace():
            sys.excepthook = handle_exception
            if running_in_ipython():
                ipython = get_ipython()
                ipython._showtraceback = handle_exception

    def get(self, name):
        return self.settings.get(name)

    def put(self, name, value):
        self.settings[name] = value

    def has(self, name):
        return name in self.settings

    def all(self):
        return self.settings

    def remove(self, name):
        if name in self.settings:
            del self.settings[name]

    # auth_get() and auth_post() raise an exception if response is non-200.

    def auth_get(self, url, params=None, headers=None):
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        debug("In auth_get url", url)
        debug("self.settings.region", self.settings["REGION"])
        debug("headers in auth_get", headers)
        def make_request():
            if self.settings["REGION"] == 'local':
                return requests.get(url, params=params, headers=headers, verify=False)
            else:
                return requests.get(url, params=params, headers=headers)
        return self.make_auth_call(make_request, params, headers)

    def auth_post(self, url, data=None, json=None, params=None, headers=None, flags=None):
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        if flags is None:
            flags = {}
        debug("In auth_post url", url)
        debug("IN auth_post settings", self.settings)
        debug("self.settings.region", self.settings["REGION"])
        def make_request():
            if self.settings["REGION"] == 'local':
                return requests.post(url, data=data, json=json, params=params, headers=headers, verify=False)
            else:
                return requests.post(url, data=data, json=json, params=params, headers=headers)
        return self.make_auth_call(make_request, params, headers, json, flags)

    def auth_put(self, url, data=None, json=None, params=None, headers=None):
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        def make_request():
            if self.settings["REGION"] == 'local':
                return requests.put(url, data=data, json=json, params=params, headers=headers, verify=False)
            else:   
                return requests.put(url, data=data, json=json, params=params, headers=headers)
        return self.make_auth_call(make_request, params, headers)

    # The lambda function should return a HTTP response.  Prior to
    # calling it, the params and/or headers are augmented with
    # credentials, depending on the authorization scheme (API key or
    # JWT token).
    def make_auth_call(self, function, params=None, headers=None, json=None, flags=None):
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        if flags is None:
            flags = {}
        if json is None:
            json = {}
        # Use API key if configured:
        if self.has("API_KEY") and (len(self.get("API_KEY")) > 0):
            debug("HAS API KEY (should be between arrows)-->", self.get("API_KEY"), "<--")
            params["api_key"] = self.get("API_KEY")
            if("for_blackfin" in flags):
                json["api_key"] = self.get("API_KEY")
            resp = function()
            if (resp.status_code == 200):
                return resp
            else:
                raise RuntimeError("Error while making HTTP request: {} {}".format(resp.status_code, resp.text))
        # Use JWT token if cached:
        elif self.has_jwt_token():
            debug("HAS JWT TOKEN")
            headers["AUTHORIZATION"] = "Bearer " + self.get_jwt_token()
            if("for_blackfin" in flags):
                json["api_key"] = self.get_jwt_token()

            resp = function()
            if (resp.status_code == 200):
                return resp
            elif (resp.status_code == 401):
                # Clear JWT token and redo call, prompting for username and password,
                # in case token is expired.
                self.remove_jwt_token()
                return self.make_auth_call(function, params, headers)
            else:
                raise RuntimeError("Error while making HTTP request: {} {}".format(resp.status_code, resp.text))
        # Otherwise prompt for JWT token and cache it:
        else:
            debug("Hit the else in make_auth_call")
            token = self.prompt_for_jwt_token_and_cache_it()
            headers["AUTHORIZATION"] = "Bearer " + token
            if("for_blackfin" in flags):
                json["api_key"] = token
            resp = function()
            if (resp.status_code == 200):
                return resp
            else:
                debug("resp.text in make_auth_call", resp.text)
                raise RuntimeError("Error while making HTTP request: {} {}".format(resp.status_code, resp.text))

    def prompt_for_jwt_token_and_cache_it(self):
        debug("I Need a token")
        token = self.prompt_for_jwt_token()
        self.put_jwt_token(token)
        return token

    # Fetch JWT token.  If username and password were not in the
    # configuration file, and were not supplied as parameters,
    # prompt the user for them.
    def prompt_for_jwt_token(self):
        jwt_url = self.get("MANTA_URL") + "jwt/create"
        jwt_params = {
            'email_address': self.prompt_for_username(),
            'password': self.prompt_for_password()
        }
        debug("JWT_PARAMS", jwt_params)
        if self.settings["REGION"] == 'local':
            r = requests.post(jwt_url, json=jwt_params, verify=False)
        else:
            r = requests.post(jwt_url, json=jwt_params)
        if (r.status_code == 200):
            token = r.text
            return token
        elif (r.status_code == 401):
            raise RuntimeError(r.json()["error"] + ". Go to https://console.demystdata.com/users/sign_up to create an account if you don't have one.")
        elif (r.status_code == 403):
            sso_url = r.json()["sso_url"]
            raise RuntimeError("Please log in at " + sso_url)
        else:
            raise RuntimeError("Couldn't get an API token. {} {}".format(r.status_code, r.text))

    # Main way to get username:
    #
    # - If it's in the settings return that.
    #
    # - If we have a token, check that it's valid, get the username, and
    #   add it to the settings.
    #
    # - Otherwise prompt the user, and add the username to the settings.
    def get_username(self):
        if self.has("USERNAME"):
            return self.get("USERNAME")
        elif self.has_jwt_token() and self.jwt_token_is_valid():
            json = self.get_jwt_token_json()
            if json["username"]:
                username = json["username"]
                self.put("USERNAME", username)
                return username
            else:
                raise RuntimeError("Token file broken")
        else:
            return self.prompt_for_username()

    # If we have a username configured just return that, otherwise
    # prompt user and save it in config file.
    def prompt_for_username(self):
        debug("Prompting for username")
        if self.has("USERNAME"):
            return self.get("USERNAME")
        else:
            print("Don't have an account? Sign up at https://console.demystdata.com/users/sign_up")
            username = input("Please enter your username: ")
            if username:
                self.put("USERNAME", username)
                return username
            else:
                return None

    def prompt_for_password(self):
        debug("Prompting for password")
        return self.get("PASSWORD") or getpass("Please enter your password: ")

    def get_organization(self):
        if not self.organization:
            # https://github.com/DemystData/demyst-python/issues/215
            headers = { "Content-type": "application/json", "Accept": 'application/json' }
            org_json = self.auth_get(self.get("MANTA_URL") + "organization.json", headers=headers)
            debug(org_json.text)
            org_json = org_json.json()
            self.organization = str(org_json["id"]) if "id" in org_json else "Unknown organization"
        return self.organization

    def get_console_userid(self):
        if not self.console_userid:
            self.fetch_console_userdata()
        return self.console_userid

    def get_console_fullname(self):
        if not self.console_fullname:
            self.fetch_console_userdata()
        return self.console_fullname

    def fetch_console_userdata(self):
        email = self.get_username()
        # Sanity check, usually won't be called unless username is set.
        if not email:
            raise RuntimeError("Can't fetch user data if username not set.")
        headers = { "Content-type": "application/json", "Accept": 'application/json' }
        users_json = self.auth_get(self.get("MANTA_URL") + "manageable_users.json", headers=headers).json()
        users_list = users_json["response"]
        user = next((u for u in users_list if u["email"] == email), False)
        if user:
            self.console_userid = str(user["id"])
            self.console_fullname = user["name"]
        else:
            self.console_userid = "Unknown"
            self.console_fullname = "Anonymous"

    def get_demyst_dir_path(self):
        return Path.home() / ".demyst"

    def get_token_file_path(self):
        return self.get_demyst_dir_path() / "jwt-cache.json"

    def has_jwt_token(self):
        return self.get_token_file_path().is_file()

    def get_jwt_token_json(self):
        text = self.get_token_file_path().read_text()
        return js.loads(text)

    def get_jwt_token(self):
        json = self.get_jwt_token_json()
        if json["jwt"]:
            return json["jwt"]
        else:
            raise RuntimeError("Token file broken: " + text)

    def put_jwt_token(self, token):
        demyst_dir = self.get_demyst_dir_path()
        demyst_dir.mkdir(parents=True, exist_ok=True)
        username = self.get_username()
        env = self.get("ENV")
        if not username:
            raise RuntimeError("Username not set")
        if not env:
            raise RuntimeError("Environment not set")
        json = {
            "jwt": token,
            "username": username,
            "env": env
            }
        text = js.dumps(json)
        self.get_token_file_path().write_text(text)

    def remove_jwt_token(self):
        if (self.has_jwt_token()):
            self.get_token_file_path().unlink()

    # Check we can successfully make an authenticated call
    def jwt_token_is_valid(self):
        if not self.has_jwt_token():
            return False
        try:
            self.auth_get(self.get("MANTA_URL") + "organization.json")
            return True
        except RuntimeError:
            self.remove_jwt_token()
            return False

    # Provider data cache

    def lookup_provider(self, provider_name):
        self.init_provider_cache()
        return self.provider_cache.get(provider_name)

    def all_providers(self):
        self.init_provider_cache()
        return list(self.provider_cache.values())

    def provider_name_to_version_id(self, provider_name):
        self.init_provider_cache()
        p = self.provider_cache[provider_name]
        return p["version"]["id"] if type(p["version"]) is dict else None

    def provider_name_to_id(self, provider_name):
        self.init_provider_cache()
        p = self.provider_cache[provider_name]
        return p["id"]

    def provider_cost(self, provider_name):
        self.init_provider_cache()
        return self.provider_cache[provider_name]["cost"]

    def init_provider_cache(self):
        if self.provider_cache == None:
            providers_json = self.auth_get(self.get("MANTA_URL") + "table_providers/latest").json()
            self.init_provider_cache_from_json(providers_json)

    def init_provider_cache_from_json(self, providers):
        self.provider_cache = {}
        for p in providers:
            self.provider_cache[p["name"]] = p

def load_config(**kwargs):
    return Config(**kwargs)

def try_to_find_config_file(dir):
    if (os.path.isfile(dir + "/df.config")):
        return dir + "/df.config"
    elif (os.path.isfile(dir + "/function/df.config")):
        return dir + "/function/df.config"
    elif os.getenv("DEMYST_DF_CONFIG"):
        return os.getenv("DEMYST_DF_CONFIG")
    else:
        return None

def parse_config(str):
    foo = str.splitlines()
    result = {}
    for x in foo:
        k, v = x.split('=')
        result[k] = v
    return result
