import threading
import time
import argparse
import imp
import os

import AlfonsIoT as iot

log = False

def thread(options):
	function = options["function"]
	topic = options["topic"]
	retain = options["retain"] if "retain" in options else False
	timeout = options["timeout"] if "timeout" in options else 5
	lastValue = None

	while True:
		data = getattr(script, function)()
		if data is None:
			if log: print("Didn't publish to %s because data was None" % topic)
		elif data == lastValue:
			if log: print("Didn't publish %s to %s because there had been no update" % (data, topic))
		else:
			lastValue = data
			iot.mqtt.publish(topic, payload=data, qos=1, retain=retain)
			if log: print("Published %s to %s" % (data, topic))
		
		time.sleep(timeout)

def onConnect(*args):
	print("Connected")

	for t in iot.getConfig("topics"):
		if not "function" in t or not "topic" in t:
			print("A sensor is missing a necessary field")
			continue
		
		threading.Thread(target=thread, args=(t, )).start()

def run():
	global config, script, log

	parser = argparse.ArgumentParser()
	parser.add_argument("config_file", help="Path for the config file")
	parser.add_argument("-p", action="store_true", help="Print every publish. Good for testing", dest="print")
	args = parser.parse_args()
	
	log = args.print

	configPath = os.path.abspath(args.config_file)

	iot.setup(configPath)

	scriptPath = os.path.abspath(os.path.dirname(configPath) + "/" + iot.getConfig("script"))
	script = imp.load_source("Alfons Sensor", scriptPath)

	iot.connect(on_connect=onConnect, block=True)