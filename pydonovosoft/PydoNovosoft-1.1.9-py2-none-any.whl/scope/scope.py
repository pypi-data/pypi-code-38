import requests
import PeriodicPositionProto_pb2
from google.protobuf.json_format import MessageToJson
import requests
from datetime import datetime, timedelta
import json
import base64


class MProfiler(object):

    def __init__(self, url, user="", passw=""):
        self.profiler = url
        self.username = user
        self.password = passw

    def get_messages(self):
        url = self.profiler+"/v1/MessageBatch"
        obj = requests.get(url, auth=(self.username, self.password))
        batch = {}
        if obj is not None and obj.status_code == 200:
            res = obj.json()
            events = []
            for message in res["messages"]:
                event = PeriodicPositionProto_pb2.PeriodicPosition()
                binary = base64.b64decode(message["body"])
                event.ParseFromString(str(binary))
                parsed = json.loads(MessageToJson(event, False, False, 0))
                events.append(parsed)
            batch["events"] = events
            batch["batchId"] = res["batchId"]
            batch["date"] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        return batch

    def acknowledge(self, batch):
        url = self.profiler + "/v1/MessageBatch/Ack/"+batch
        obj = requests.post(url, auth=(self.username, self.password))
        if obj.status_code == 200:
            return True
        else:
            return False


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