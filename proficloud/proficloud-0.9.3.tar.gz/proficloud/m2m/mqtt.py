import requests
import json
import paho.mqtt.client as mqtt
from urllib.parse import urlparse
import ssl
import datetime

class ProficloudAppliance():

    def __init__(self, uuid, regtoken, useStaging=False):
        self.session = requests.Session()
        """The requests-session for communication through REST"""
        self.baseurl = "https://www.proficloud.net/"
        if useStaging:
            self.baseurl = "https://www.proficloud-staging.net/"

        self.uuid = uuid
        self.regtoken = regtoken

        self.publishtopic = "/appliance/out/"+uuid

        if not self.getComToken():
            raise Exception("Unable to get a communication token for appliance")

        self.connected = False

        print("Trying to connect to mqtt...")
        self.mqttConnect()

    def getRegistrationToken(uuid,useStaging=False):
        headers = { "Content-Type" : "application/json"}
        payload = {"uuid": uuid}

        session = requests.Session()
        """The requests-session for communication through REST"""
        baseurl = "https://www.proficloud.net/"
        if useStaging:
            baseurl = "https://www.proficloud-staging.net/"

        response = session.post(
            url=baseurl+"register/appliance",
            headers=headers,
            data=json.dumps(payload))
        
        if response.status_code == 200:
            return response.content.decode()
        else:
            return None

    def getComToken(self):

        headers = { 
            "Content-Type" : "application/json",
            "X-PROFICLOUD-API-TOKEN": self.regtoken
        }

        response = self.session.get(
            url = self.baseurl + "api/appliances/"+self.uuid+"/credentials?protocol=mqtt",
            headers = headers
        )

        if response.status_code == 200:
            content = json.loads(response.content.decode())
            self.endpoint = content["endpoint"]
            self.comtoken = content["comtoken"]
            return True
        else:
            return False

    def mqttConnect(self):
        self.client = mqtt.Client()
        url = urlparse(self.endpoint)

        def on_connect(client, userdata, flags, rc):
            print("Connected!")
            self.connected = True
        self.client.on_connect = on_connect

        def on_disconnect(client, userdata, rc):
            print("Disconnected!")
            self.connected = False
        self.client.on_disconnect = on_disconnect

        def on_message(client, userdata, message):
                print("message received " ,str(message.payload.decode("utf-8")))
                print("message topic=",message.topic)
                print("message qos=",message.qos)
                print("message retain flag=",message.retain)
        self.client.on_message=on_message 

        self.client.username_pw_set(self.uuid, password=self.comtoken)

        #self.client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED,
        #tls_version=ssl.PROTOCOL_TLS, ciphers=None)
        self.client.tls_set_context()

        self.client.connect(url.netloc.split(":")[0], url.port, 30)

    def loop(self):
        self.client.loop()

    def mqttDisconnect(self):
        self.client.disconnect()

    def publishSimple(self, metric, value, date=None):

        if date is None:
            date = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")#"%Y-%m-%dT%H:%M:%S.%f"

        data = [{
            "metric": metric,
            "value": str(value),
            "date": str(date)
            }]

        jsonData = json.dumps(data)

        jsonDataEscape = jsonData.translate(str.maketrans({
            #"-":  r"\-",
            #"]":  r"\]",
            "\\": r"\\",
            #"^":  r"\^",
            #"$":  r"\$",
            #"*":  r"\*",
            #".":  r"\."
        }
        ))

        payload = {
            "from": self.uuid,
            "data": jsonDataEscape
        }

        print(self.publishtopic)
        
        jsonpl = json.dumps(payload)
        print(jsonpl)

        self.client.publish(
            self.publishtopic, 
            jsonpl
            )
