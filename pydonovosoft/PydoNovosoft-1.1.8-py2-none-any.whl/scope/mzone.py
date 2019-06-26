import requests
from datetime import datetime, timedelta


class MZone(object):

    def __init__(self, user, password, secret, client="mz_dev", url="https://live.mzoneweb.net/mzone61.api/"):
        self._token = ""
        self._user = user
        self._password = password
        self._secret = secret
        self._client = client
        self._url = url

    def gettoken(self):
        url = "https://login.mzoneweb.net/connect/token"
        data = {'grant_type': 'password', 'username': self._user,
                'password': self._password, 'client_id': self._client,
                'client_secret': self._secret,
                'scope': 'openid mz6-api.all mz_username'}
        resp = requests.post(url, data=data, verify=False)
        if resp.status_code == 200:
            token = resp.json()
            valid = datetime.now() + timedelta(seconds=int(token["expires_in"]))
            token["valid_until"] = valid.__str__()
            self._token = token
        else:
            print(resp.content)

    def check_token(self):
        if not self._token:
            return False
        else:
            valid_until = datetime.strptime(self._token["valid_until"], '%Y-%m-%d %H:%M:%S.%f')
            now = datetime.now()
            if now > valid_until:
                return False
            else:
                return True

    def get_alerts(self):
        url = self._url+"Alerts?$select=eventType_Description,vehicle_Id,locationDescription&" \
                "$expand=vehicle($select=description)"
        if not self.check_token():
            self.gettoken()
        auth = "Bearer "+self._token["access_token"]
        headers = {"Authorization": auth}
        resp = requests.get(url, headers=headers, verify=False)
        if resp.status_code == 200:
            return resp.json()
        else:
            return resp.text

    def get_notifications(self, extra=""):
        url = self._url+"Notifications?$format=json"
        if extra:
            url = url+"&$filter="+extra
        if not self.check_token():
            self.gettoken()
        auth = "Bearer " + self._token["access_token"]
        headers = {"Authorization": auth}
        resp = requests.get(url, headers=headers, verify=False)
        if resp.status_code == 200:
            return resp.json()
        else:
            return resp.text

    def set_notifications_read(self, notifications):
        url = self._url + "Notifications/_.markAsRead"
        if not self.check_token():
            self.gettoken()
        auth = "Bearer " + self._token["access_token"]
        headers = {"Authorization": auth}
        data = dict()
        data["notificationIds"] = notifications
        resp = requests.post(url, json=data, headers=headers, verify=False)
        return resp

    def get_subscriptions(self, extra=""):
        url = self._url+"NotificationTemplates/_.getForAllUsers?$format=json&$expand=subscriber"
        if extra:
            url = url+"&$filter="+extra
        if not self.check_token():
            self.gettoken()
        auth = "Bearer " + self._token["access_token"]
        headers = {"Authorization": auth}
        resp = requests.get(url, headers=headers, verify=False)
        if resp.status_code == 200:
            return resp.json()
        else:
            return resp

    def get_vehicles(self):
        url = self._url+"Vehicles"
        if not self.check_token():
            self.gettoken()
        auth = "Bearer " + self._token["access_token"]
        headers = {"Authorization": auth}
        resp = requests.get(url, headers=headers, verify=False)
        if resp.status_code == 200:
            return resp.json()["value"]
        else:
            return resp.text

    def get_last_position(self, gid):
        url = self._url+"LastKnownPositions?$format=json&$expand=vehicle&$filter=vehicle/id eq "+gid
        if not self.check_token():
            self.gettoken()
        auth = "Bearer " + self._token["access_token"]
        headers = {"Authorization": auth}
        resp = requests.get(url, headers=headers, verify=False)
        if resp.status_code == 200:
            return resp.json()["value"]
        else:
            return resp.text


class MZone4(object):

    def __init__(self, user, password, url="https://us.mzoneweb.net/api/v2"):
        self._user = user
        self._password = password
        self._url = url

    def _generate_auth(self):
        auth = "Basic "
        return auth

    def get_places(self, filter=None, ps=0):
        req = self._url+"/places.json?pg=0"
        if filter is not None:
            req = self._url + "/places.json?de="+filter+"&pg=0"
        if ps > 0:
            req = req+"&ps="+str(ps)
        places = requests.get(req, auth=(self._user, self._password))
        return places

    def create_place(self, place):
        url = self._url+"/place/place.json"
        data = place
        resp = requests.post(url, json=data, auth=(self._user, self._password))
        return resp

    def get_events(self, vehicle, startdate, endate, size=0):
        url = self._url+"/vehicles/"+vehicle+"/events/"+startdate+"/"+endate+".json?pg=0"
        if size > 0:
            url = url + "&ps="+size
        resp = requests.get(url, auth=(self._user, self._password))
        return resp

    def get_vehicles(self, size=0):
        url = self._url + "/vehicles.json?pg=0"
        if size > 0:
            url = url + "&ps=" + size
        resp = requests.get(url, auth=(self._user, self._password))
        return resp

    def get_vehicle_groups(self, size=0):
        url = self._url + "/vehiclegroups.json?pg=0"
        if size > 0:
            url = url + "&ps=" + size
        resp = requests.get(url, auth=(self._user, self._password))
        return resp

    def get_vehicle_by_group(self, group, size=0):
        url = self._url + "/vehiclegroups/"+group+"/vehicles.json?pg=0"
        if size > 0:
            url = url + "&ps=" + size
        resp = requests.get(url, auth=(self._user, self._password))
        return resp

    def get_places_by_group(self, group):
        places = requests.get(self._url + "/placegroups/"+group+"/places.json?pg=0", auth=(self._user, self._password))
        return places

    def delete_place(self, place):
        url = self._url + "/places/"+place+".json"
        resp = requests.delete(url, auth=(self._user, self._password))
        return resp

    def create_placegroup(self, name):
        url = self._url+"/placegroups/placegroup.json"
        data = {"Description": name}
        resp = requests.post(url, json=data, auth=(self._user, self._password))
        return resp

    def get_placegroups(self):
        url = self._url+"/placegroups.json?pg=0"
        resp = requests.get(url, auth=(self._user, self._password))
        return resp

    def get_poll_vehicles(self, vehicles):
        url = self._url + "/vehicles/poll.json"
        resp = requests.post(url, json=vehicles, auth=(self._user, self._password))
        return resp





