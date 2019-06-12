import socket
import json
import os
import string
import random
import time
import sys

import paho.mqtt.client
import yaml

projectPath = ""
config = {"uninitialized": True}
data = {}
mqtt = paho.mqtt.client.Client()

def _getIP():
	ip = getConfig("ip")
	if ip: return ip

	discoverSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	discoverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	discoverSocket.settimeout(1)
	
	msg = None

	while not msg:
		discoverSocket.sendto(b"discover", ("255.255.255.255", 27369))
		
		try:
			msg = discoverSocket.recv(1024)
		except socket.timeout:
			pass
	
	return json.loads(msg.decode("utf-8"))["ip"]

def _getID():
	return getConfig("id")

def getConfig(key):
	if key in config:
		return config[key]

	if key in data:
		return data[key]
	
	return None

def connect(**kwargs):
	# MQTT
	onMessage = kwargs.get("on_message")
	if onMessage is not None:
		mqtt.on_message = onMessage
	
	onConnect = kwargs.get("on_connect")
	if onConnect is not None:
		mqtt.on_connect = onConnect
	
	mqtt.username_pw_set("iot-" + _getID(), "iot")
	mqtt.connect(_getIP(), 27370, 60)

	if kwargs.get("block", False):
		mqtt.loop_forever()
	else:
		mqtt.loop_start()

def setup(path = None):
	"Path to a config file"
	
	global mqtt, config, data, projectPath

	if path == None:
		projectPath = os.path.abspath(sys.argv[0])
		fileName = "config.yaml"
	else:
		projectPath = os.path.dirname(path)
		fileName = os.path.basename(path)
		
	# Read files
	try:
		with open(projectPath + "/" + fileName) as f:
			config = yaml.safe_load(f)
	except Exception as e:
		config = {}

	try:
		with open(projectPath + "/data.json") as f:
			data = json.load(f)
	except:
		data = {}

	clientId = getConfig("id")
	
	if not clientId:
		clientId = "".join(random.choices(string.ascii_letters + string.digits, k=16))
		data["id"] = clientId

		with open(projectPath + "/data.json", "w") as f:
			json.dump(data, f)

	# MQTT
	mqtt._client_id = _getID()
