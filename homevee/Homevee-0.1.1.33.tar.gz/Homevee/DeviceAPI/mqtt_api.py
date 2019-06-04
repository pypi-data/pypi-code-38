#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import socket
import time
import traceback
from time import sleep

import paho.mqtt.client as mqtt

from Homevee.DeviceAPI.mqtt_sensor import handle_mqtt_sensor
from Homevee.Helper import Logger, smarthome_functions, translations
from Homevee.Item.Gateway import *

MQTT_CLIENT = None

topics_to_subscribe = [
    '/home/#'
]

QUALITY_OF_SERVICE = 0

# https://www.dinotools.de/2015/04/12/mqtt-mit-python-nutzen/

def run_device_action(topic, msg, db: Database = None):
    if db is None:
        db = Database()
    topic_parts = topic.split("/")

    #topic_parts[0] is empty
    #topic_parts[1] is "home"

    result = None

    if(topic_parts[2] == "device"):
        result = db.select_one("SELECT * FROM MQTT_DEVICES WHERE TOPIC = :topic",
                    {'topic': topic})

        key = result['KEY']

        data = json.loads(msg)

        device_types = ["MQTT_SENSORS"]  # , "MQTT_TRIGGERS"]

        for device_type in device_types:
            results = db.select_all("SELECT * FROM " + device_type + " WHERE DEVICE_ID = :dev_id",
                        {'dev_id': result['ID']})

            for device in results:
                for data_item in data:
                    if str(device['VALUE_ID']) == str(data_item['id']):
                        handle_mqtt_sensor(device['ID'], data_item['value'])

        # Run MQTT-Trigger
        '''db.select_all("SELECT * FROM MQTT_TRIGGERS WHERE TOPIC = :topic", {'topic': message.topic})
        for item in cur.fetchall():
            #handle item action
            data = json.loads(msg)
            Logger.log(data)
            Logger.log(item)
            run_trigger_automation("MQTT-Trigger", item['TYPE'], item['ID'], data['action'])
            break'''
    elif(topic_parts[2] == "assistant" and topic_parts[4]=="send"):
        start_time = time.time()
        smart_speaker = db.select_all("SELECT * FROM SMART_SPEAKER WHERE ID = :id",
                    {'id': topic_parts[3]})

        topic = '/' + topic_parts[1] + '/' + topic_parts[2] + '/' + topic_parts[3] + '/receive'

        try:
            data = json.loads(msg)

            data = json.loads(data['msg'])

            username = data['username']
            text = data['text']

            text = text.encode('utf-8')

            result = smarthome_functions.do_voice_command(username, text, None, smart_speaker['LOCATION'], db, translations.LANGUAGE)

            result['time'] = time.time()
        except:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            answer = "Es gab einen Fehler."
            result = {'msg_text': answer, 'msg_speech': answer}

        end_time = time.time()
        result['computing_duration'] = end_time - start_time

        publish(topic, json.dumps(result))

def publish(topic, msg):
    client = mqtt.Client()

    gateway = Item.load_from_db(Gateway, MQTT_BROKER, Database())

    Logger.log("publishing to "+topic+": "+msg)

    client.connect(gateway.ip)
    client.publish(topic, msg, QUALITY_OF_SERVICE, False)

def on_message(client, userdata, message):
    db = Database()

    msg = str(message.payload.decode("utf-8"))
    Logger.log("message received: ", msg)
    Logger.log("message topic: ", message.topic)
    # Logger.log("message qos=",message.qos)
    # Logger.log("message retain flag=",message.retain)

    # decrypt message with saved key of the device in db
    try:
        run_device_action(message.topic, msg)
    except:
        if(Logger.IS_DEBUG):
                traceback.print_exc()

def on_connect(client, userdata, flags, rc):
    for topic in topics_to_subscribe:
        client.subscribe(topic, QUALITY_OF_SERVICE)

    for topic in get_topics():
        client.subscribe(topic, QUALITY_OF_SERVICE)


def init_client():
    while (True):
        gateway = Item.load_from_db(Gateway, MQTT_BROKER, Database())

        if gateway is None:
            sleep(30)

        try:
            broker_address = gateway.ip
        except:
            broker_address = None

        #keep retrying when broker_address is None
        if broker_address is None:
            sleep(15)
            continue

        try:
            client = mqtt.Client()
            client.on_connect = on_connect
            client.on_message = on_message

            client.connect(broker_address)

            Logger.log("Connected to MQTT Broker: " + broker_address)


            while(True):
                #check if client still connected and exit if not
                client.loop(1)

        except socket.error as e:
            continue
        # Logger.log("Cannot reach MQTT Broker: " + broker_address)


def get_topics():
    # load topics from database

    return []
