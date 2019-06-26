import requests
from datetime import datetime, timedelta


class MZone(object):

    def __init__(self, user, password):
        self.token = ""
        self._user = user
        self._password = password

    def gettoken(self):
        url = "https://live.mzoneweb.net/mzone6.api/token"
        data = {'grant_type': 'password', 'username': self._user,
                'password': self._password, 'client_id': 'mz-dev',
                'client_secret': 'P9biSi9t1LFSqEGjhL8THfaF',
                'scope': 'openid mz6-api.all mz_username'}
        resp = requests.post(url, data=data)
        if resp.status_code == 200:
            token = resp.json()
            valid = datetime.now() + timedelta(seconds=int(token["expires_in"]))
            token["valid_until"] = valid.__str__()
            self.token = token
        else:
            print(resp.content)

    def check_token(self):
        if not self.token:
            return False
        else:
            valid_until = datetime.strptime(self.token["valid_until"], '%Y-%m-%d %H:%M:%S.%f')
            now = datetime.now()
            if now > valid_until:
                return False
            else:
                return True

    def get_alerts(self):
        url = "https://live.mzoneweb.net/mzone6.api/Alerts?$select=eventType_Description,vehicle_Id," \
              "locationDescription&$expand=vehicle($select=description)"
        if not self.check_token():
            self.gettoken()
        auth = "Bearer "+self.token["access_token"]
        headers = {"Authorization": auth}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()

    def get_vehicles(self):
        url = "https://live.mzoneweb.net/mzone6.api/Vehicles"
        if not self.check_token():
            self.gettoken()
        auth = "Bearer " + self.token["access_token"]
        headers = {"Authorization": auth}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            return resp.json()["value"]
