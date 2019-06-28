import requests


class MZone4(object):

    def __init__(self, user, password, url="https://us.mzoneweb.net/api/v2"):
        self._user = user
        self._password = password
        self._url = url

    def _generate_auth(self):
        auth = "Basic "
        return auth

    def get_places(self):
        places = requests.get(self._url+"/places.json?pg=0", auth=(self._user, self._password))
        return places

    def create_place(self, place):
        url = self._url+"/places+/place.json"
        data = place
        requests.post(url, data=data, json=True, auth=(self._user, self._password))


