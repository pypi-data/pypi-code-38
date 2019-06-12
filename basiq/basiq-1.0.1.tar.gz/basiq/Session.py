import requests
import time
from .API import API
from .services import UserService


class Session:
    def __init__(self, api, api_key, version="1.0"):
        self.__api_key = api_key
        self.validity = None
        self.refreshed = None
        self.__token = None
        self.headers = None
        self.api = api
        self.version = version

        self.getToken()

    def getToken(self):
        if self.validity != None and time.gmtime() - self.refreshed < self.validity:
            return self.__token

        if self.version != "1.0" and self.version != "2.0":
            print('Provided version not available')

        r = self.api.set_header("Authorization", "Basic " + self.__api_key) \
                .set_header("basiq-version", self.version) \
                .post("token", {})

        if "access_token" in r:
            self.refreshed = time.gmtime()
            self.validity = r["expires_in"]
            self.__token = r["access_token"]
            self.api.headers = {
                "Authorization": "Bearer " + r["access_token"]
            }
            return r["access_token"]
        else:
            print("No access token:", r)

    def getInstitutions(self):
        return self.api.get("institutions")

    def getInstitution(self, id):
        return self.api.get("institutions/" + id)

    def getUser(self, id):
        return UserService(self).get(id)

    def forUser(self, id):
        return UserService(self).forUser(id)
