from .exceptions import InvalidCredentialsException, InvalidServiceException
import requests
import logging
from requests.auth import HTTPBasicAuth

REGISTRY_URL = (
    "https://access.auth.theplatform.{tld}/web/Registry/resolveDomain"
)
SIGN_IN_URL = (
    "https://identity.auth.theplatform.{tld}/idm/web/Authentication/signIn"
)
SIGN_OUT_URL = (
    "https://identity.auth.theplatform.{tld}/idm/web/Authentication/signOut"
)


class MPXApi:
    def __init__(
        self, username, password, account, tld, token=None, clientId=None
    ):
        self.username = username
        self.password = password
        self.account = account
        self.tld = tld
        self.token = None
        self.user_id = None
        self.user_name = None
        self.registry = None

        # Used mainly for notification polling
        self.clientId = clientId

        # Allow reuse of cached tokens
        if token is None:
            self.sign_in()
        else:
            self.token = token
        self.get_registry()

    def sign_in(self):
        # Ask for a default timeout of 1 hour, and 10 minutes of idle timeout
        params = {
            "schema": "1.1",
            "_duration": "3600000",
            "_idleTimeout": "600000",
            "httpError": "true",
        }
        headers = {"Content-Type": "application/json"}
        auth = HTTPBasicAuth(username=self.username, password=self.password)
        r = requests.get(
            SIGN_IN_URL.format(tld=self.tld),
            params=params,
            headers=headers,
            auth=auth,
        )

        if r.status_code == 200:
            auth_data = r.json()["signInResponse"]
            self.token = auth_data["token"]
            self.user_id = "/".join(auth_data["userId"].split("/")[-2:])
            self.user_name = auth_data["userName"]
        else:
            raise InvalidCredentialsException(
                "Unable to auth for user: " + self.username
            )

    def sign_out(self):
        params = {"schema": "1.1", "_token": self.token}
        headers = {"Content-Type": "application/json"}
        requests.get(
            SIGN_OUT_URL.format(tld=self.tld), params=params, headers=headers
        )

    def get_registry(self):
        logging.debug(
            "Fetching service registry from %s"
            % REGISTRY_URL.format(tld=self.tld)
        )
        params = {
            "schema": "1.1",
            "form": "json",
            "_accountId": "http://access.auth.theplatform.com/data/Account/"
            + self.account,
        }
        registry_request = self.raw_command(
            method="GET", url=REGISTRY_URL.format(tld=self.tld), params=params
        )
        self.registry = registry_request.json()["resolveDomainResponse"]

    def get_token(self):
        return self.token

    def raw_command(self, method, url, params, data=None):
        params.update({"account": self.account})
        params.update({"token": self.token})
        params.update({"httpError": "true"})
        if "form" not in params:
            params.update({"form": "cjson"})
            params.update({"pretty": "true"})

        req = requests.request(method, url, params=params, data=data)

        # check if we maybe have an expired token
        if req.status_code == 401:
            logging.debug("We encountered an 401 exception, re-signing in")
            self.sign_in()
            return self.raw_command(method, url, params, data)

        return req

    def command(self, service, path, method, params, data=None):
        url = self.get_service_url(service) + path
        return self.raw_command(
            method=method, url=url, params=params, data=data
        )

    def get_service_url(self, service):
        try:
            return self.registry[service]
        except KeyError:
            raise InvalidServiceException(
                "Service " + service + " could not be found"
            )

    def get_account(self):
        return self.account

    def get_user_id(self):
        return self.user_id
