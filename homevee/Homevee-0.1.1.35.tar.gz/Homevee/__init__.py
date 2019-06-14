#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import socket
import sys
import time
import traceback
from _thread import start_new_thread

from Homevee import RestAPI
from Homevee.API import API
from Homevee.CloudConnection import CloudConnection
from Homevee.Cronjob.CalendarReminderCronjob import CalendarReminderCronjob
from Homevee.Cronjob.CheckUpdateCronjob import CheckUpdateCronjob
from Homevee.Cronjob.HeatingSchemeCronjob import HeatingSchemeCronjob
from Homevee.Cronjob.OverviewNotificationCronjob import OverviewNotificationCronjob
from Homevee.Cronjob.PhilipsHueValueLoaderCronjob import PhilipsHueValueLoaderCronjob
from Homevee.Cronjob.SaveEnergyDataCronjob import SaveEnergyDataCronjob
from Homevee.Cronjob.SaveSensorDataCronjob import SaveSensorDataCronjob
from Homevee.Cronjob.TimedAutomationsCronjob import TimedAutomationsCronjob
from Homevee.Cronjob.UserPingCronjob import UserPingCronjob
from Homevee.Cronjob.WeatherUpdaterCronjob import WeatherUpdaterCronjob
from Homevee.Cronjob.ZWaveValueLoaderCronjob import ZWaveValueLoaderCronjob
from Homevee.Helper import Logger, translations
from Homevee.Helper.translations import translate, translate_print
from Homevee.Item.User import User
from Homevee.SmartSpeakerConnection import SmartSpeakerConnection
from Homevee.Updater import Updater
from Homevee.Utils.Constants import END_OF_MESSAGE
from Homevee.Utils.Database import Database
from . import Cronjob
from . import VoiceAssistant
from .DeviceAPI import mqtt_api
# from Functions import ar_control, people_classifier
# from Helper import compression
from .Helper.helper_functions import save_request_to_db, send_to_client, \
    update_ip_thread, update_cert_thread, check_cert


class Homevee():
    #add flags
    def __init__(self, cloud_connection=True, websocket_server=True, http_server=True):
        self.cloud_connection = cloud_connection
        self.websocket_server = websocket_server
        self.http_server = http_server

        db = Database()
        db.upgrade()

        translate_print('homevee_server_started')

        homevee_update = Updater().get_homevee_update_version()

        if(homevee_update is not None):
            print(translate('update_available').format(homevee_update))

        self.init_cronjobs()

    def add_user(self, username, password, is_admin=False, db: Database = None):
        if db is None:
            db = Database()

        hashed_pw, salt = User.hash_password(password)

        permissions = ''
        if is_admin:
            permissions = '{"permissions":["admin"]}'

        param_array = {'username': username, 'ip': '', 'permissions': permissions, 'password': hashed_pw, 'salt': salt}
        db.insert("INSERT OR IGNORE INTO 'userdata' (USERNAME, PASSWORD, PW_SALT, IP, PERMISSIONS) VALUES (:username, :password, :salt, :ip, :permissions);",
            param_array)

    def init_cronjobs(self):
        CalendarReminderCronjob()
        HeatingSchemeCronjob()
        TimedAutomationsCronjob()

        SaveEnergyDataCronjob()
        SaveSensorDataCronjob()
        OverviewNotificationCronjob()
        PhilipsHueValueLoaderCronjob()
        ZWaveValueLoaderCronjob()

        WeatherUpdaterCronjob()
        CheckUpdateCronjob()

        #UserPingCronjob()

    def start_api_socket(self):
        HOST = ''  # Symbolic name meaning all available interfaces
        PORT = 7777  # Arbitrary non-privileged port

        # Zeitzone anpassen
        os.environ['TZ'] = 'Europe/Berlin'

        '''while True:
            data = raw_input("Data: ")
            key = raw_input("Key: ")

            aes = AESCipher.AESCipher(key)
            new_aes = AESCipher.AESCipher(key)
            Logger.log("Data: "+data)
            cipher = aes.encrypt(data)
            Logger.log("Cipher: "+cipher)
            plain = new_aes.decrypt(cipher)
            Logger.log("Plain: "+plain)'''

        # aes = AESCipher.AESCipher('3s6v9y$B&E)H@McQfTjWmZq4t7w!z%C*')
        # Logger.log("Plain: "+aes.decrypt('qYqXviw/9yowSeMeJqkRhC6QUtQdPjFhyUdlzb0Cyz4xddOQbLMpNUjs8hMbk8al'))

        # Cronjob.save_energy_data.init_thread()

        test_speech = False
        if test_speech:
            while (True):
                voice_input = input("Gib einen Sprachbefehl ein: ")
                print(VoiceAssistant.voice_command("sascha", voice_input, None, None, Database(), translations.LANGUAGE))

        # Smart Speaker Communication
        #smart_speaker_connection = SmartSpeakerConnection()
        #smart_speaker_connection.start_loop()

        # Connect to MQTT-Broker
        start_new_thread(mqtt_api.init_client, ())

        # Start Websocket-Server
        if self.websocket_server:
            pass
            # start_new_thread(start_websocket_server, ())

        # Start HTTP-Server
        if self.http_server:
            pass
            # start_new_thread(webinterface.start_http_server, ())

        # Communicate with cloud
        if self.cloud_connection:
            #start_new_thread(cloud_connection_loop, ())

            #cloud_connection = CloudConnection()
            #cloud_connection.start_connection_loop()

            start_new_thread(CloudConnection.cloud_connection_loop, ())

        # Lokale IP und Zertifikat regelmäßig aktualisieren
        start_new_thread(update_ip_thread, ())
        start_new_thread(update_cert_thread, ())

        # Reset Image-Classifier flags
        # db = Database()
        # db.set_server_data(ar_control.IS_TRAINING_TAG, "false", db)
        # db.set_server_data(people_classifier.IS_TRAINING_TAG, "false", db)

        #RestAPI.start_rest_api()

        # check if certs exist
        check_cert(db=Database())

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Logger.log('Socket created')

        # Bind socket to local host and port
        try:
            s.bind((HOST, PORT))
        except socket.error as msg:
            if(Logger.IS_DEBUG):
                traceback.print_exc()
            Logger.log('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

        Logger.log('Socket bind complete')

        # Start listening on socket
        s.listen(10)
        Logger.log('Socket now listening')

        while True:
            try:
                self.listen_for_requests(s)
            except KeyboardInterrupt:
                break
            except:
                if(Logger.IS_DEBUG):
                    traceback.print_exc()

        s.close()

    def start(self):
        # Zeitzone anpassen
        os.environ['TZ'] = 'Europe/Berlin'

        # Smart Speaker Communication
        # smart_speaker_connection = SmartSpeakerConnection()
        # smart_speaker_connection.start_loop()

        # Connect to MQTT-Broker
        start_new_thread(mqtt_api.init_client, ())

        # Create Function mappings for incoming api calls
        API().create_function_mappings()
        print(API().get_function_mappings())

        # Communicate with cloud
        if self.cloud_connection:
            start_new_thread(CloudConnection.cloud_connection_loop, ())

        # Lokale IP und Zertifikat regelmäßig aktualisieren
        start_new_thread(update_ip_thread, ())
        start_new_thread(update_cert_thread, ())

        RestAPI.start_rest_api()

    # Function for handling connections. This will be used to create threads
    def clientthread(self, conn):
        # infinite loop so that function do not terminate and thread do not end.
        db = Database()

        is_http = False

        sent_data = None

        while True:
            try:
                # Receiving from client
                method_start_time = time.time()

                data = ""

                while (True):
                    new_data = conn.recv(8192).decode('utf-8')

                    # Logger.log(new_data)

                    # data = data + compression.decompress_string(new_data)

                    data = data + new_data

                    if (data.endswith(END_OF_MESSAGE)):
                        break

                if data == "":
                    db.close()
                    conn.close()
                    return

                data = data[:len(END_OF_MESSAGE) * -1]

                Logger.log("Received: " + str(data))

                is_http = False
                is_resend = False

                error = False

                try:
                    data = json.loads(data)
                    data = json.loads(data['msg'])
                    Logger.log("Request is not in HTTP-Format")
                except:
                    Logger.log("Data could not be parsed")
                    send_to_client(json.dumps({'status': 'error'}), conn, is_http)
                    error = True

                if 'resend' in data and data['resend'] is True:
                    # Daten erneut senden
                    Logger.log("Resend!")
                    is_resend = True
                    Logger.log(str(len(sent_data)) + " | " + sent_data)

                    send_to_client(sent_data[data['resendstart']:], conn, is_http)

                if not error and not is_resend:
                    if not is_resend:
                        message = API().process_data(data, db)

                        # print "compressing: "+message

                        # start_time = time.time()
                        # compressed_message = compression.compress_string(message)
                        # end_time = time.time()

                        # print "uncompressed: "+str(len(message))
                        # print "compressed: "+str(len(compressed_message))+", time: "+str(end_time-start_time)

                        # compressed_message = compressed_message.decode('iso-8859-1').encode('utf8')

                        msg = json.dumps({'msg': message, 'computing_time': (time.time() - method_start_time) * 1000})

                    if (msg is not None):
                        send_to_client(msg, conn, is_http)

                        sent_data = msg

                        save_request_to_db(data, msg, db)
                    else:
                        Logger.log("Error in reply")
                        send_to_client(json.dumps({'status': 'error'}), conn, is_http)

                    if not data:
                        break
            # except socket.error:
            #    break
            except Exception as e:
                if(Logger.IS_DEBUG):
                    traceback.print_exc()
                Logger.log("Fehler: " + str(e))
                send_to_client(json.dumps({'status': 'error'}), conn, is_http)

            # Stop endless loop
            break

        # came out of loop
        conn.close()
        db.commit()
        db.close()
        Logger.log("Verbindung beendet")

    def listen_for_requests(self, s):
        # s = ssl.wrap_socket(s, keyfile=constants.LOCAL_SSL_PRIVKEY, certfile=constants.LOCAL_SSL_CERT, server_side=True)

        # wait to accept a connection - blocking call
        conn, addr = s.accept()
        Logger.log('Connected with ' + addr[0] + ':' + str(addr[1]))

        # start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(self.clientthread, (conn,))