import websocket
import requests
import json
import inotify.adapters
import threading
import os

from time import sleep
from getmac import get_mac_address

from .led_debugger import LedDebugger
from .parser import parse

DEBUG = LedDebugger()
ACTUATOR_FILE = '/home/pi/ricc/actuator'


class WSConnection:

    SWITCH_SUCCESS = json.dumps({'message': 200})

    def __init__(self, url, interface="eth0"):
        self.url = url
        self.interface = interface
        self.actuator_on = False
        self.token = None
        self.socket = websocket.WebSocketApp(self.url,
                                            on_open = self._on_open,
                                            on_message = self._on_message,
                                            on_error = self._on_error,
                                            on_close = self._on_close)

        self.socket_thread = threading.Thread(target=self._run_forever)
        self.socket_thread.daemon = True

    def start_connection(self):
        if not self.socket_thread.is_alive():
            self.socket_thread.start()
            
    def _run_forever(self):
        while True:
            sleep(2)
            print('Trying to connect')
            self.socket.run_forever()

    def _switch_actuator(self):
        # send message to mesh network
        self.actuator_on = not self.actuator_on
        with open(ACTUATOR_FILE, 'w') as actuator_file:
            if self.actuator_on:
                actuator_file.write('1')
            else:
                actuator_file.write('0')

    def _on_open(self):
        print('Connected')
        DEBUG.success()

    def _on_message(self, message):
        print('Switching actuator')
        DEBUG.neutral()
        sleep(1)
        self._switch_actuator()
        self.socket.send(self.SWITCH_SUCCESS)
        DEBUG.success()

    def _on_error(self, error):
        print('Error "' + error + '"')
        DEBUG.failed()
        sleep(5)
        print('Retrying')
        self.start_connection()

    def _on_close(self):
        print("Connection lost")
        DEBUG.failed()
        sleep(5)
        print('Trying to stabilish connection')
        self.start_connection()


"""
Send data to the API.
"""
def send_http_data(url: str, token: str, data: dict):
    payload = {'Authorization': token}
    msg = json.dumps(data)
    response = requests.post(url, data=payload, json=msg)
    
    return response.status


def monitor(directory, url, mac_addr):
    watch_data_thread = threading.Thread(target=watch_for_collects, args=(directory, mac_addr))    
    watch_register_thread = threading.Thread(target=watch_for_register, args=('/home/pi/ricc/dev', mac_addr)) 
    token_thread = threading.Thread(target=get_token, args=(url, mac_addr))
    
    watch_data_thread.start()
    watch_register_thread.start()
    token_thread.start()


"""
Watch for new collects and send to the API.
"""
def watch_for_collects(directory: str, mac_addr: str):
    url = 'http://164.41.98.14/send_data/'

    token_file = open('/home/pi/ricc/token', 'r')
    token = token_file.readline()
    token_file.close()

    i = inotify.adapters.Inotify()
    i.add_watch(directory)

    for event in i.event_gen():
        if event:
            event_type = event[1]
            if event_type[0] == 'IN_CLOSE_WRITE':
                fpath = event[2]
                fname = event[3]
                full_path = (fpath + '/' + fname)
                if os.path.getsize(full_path):
                    station_id, timestamp = fname[:-4].split('_')
                    headers = {"content-type": "application/json"}
                    partial_msg = {
                        'data': parse(full_path),
                        'auth_token': token,
                        'central': mac_addr,
                        'name': station_id,
                        'timestamp': timestamp
                    }

                    msg = json.dumps(partial_msg)
                    r = requests.post(url, data=msg, headers=headers, timeout=20)

                    if(r.status_code == 200 or r.status_code == 201):
                        print('Data was sended successfully!\n')
                        os.remove(full_path)
                        DEBUG.neutral()
                        sleep(1)
                        DEBUG.success()
                    else:
                        t = threading.Thread(target=resend_data, args=(url, msg, headers))
                        t.start()


"""
Try to send a msg with sensor data 5 times.
"""
def resend_data(url, msg, headers):
    for i in range(10):
        print('Resending data\n')
        try:
            r = requests.post(url, data=msg, headers=headers, timeout=20)
            if(r.status_code == 200 or r.status_code == 201):
                break
            sleep(1800)
        except requests.exceptions.RequestException as e:
            sleep(1800)


"""
Constantly makes get requests to get token
"""
def get_token(url: str, mac_addr: str):
    formated_mac = mac_addr.replace(':', '-')
    payload = {'mac': formated_mac}
    while True:
        try:
            response = requests.get(url, params=payload, timeout=20)
            while response.status_code != 200:
                print('Trying to acquire token')
                sleep(10)
                response = requests.get(url, params=payload, timeout=20)
    
            sleep(1)
            f = open('/home/pi/ricc/token', 'w')
            json_data = json.loads(response.text)
            f.write(json_data['auth_token'])
            f.close()
            break
        except requests.exceptions.RequestException as e:
            print('Failed to get token, device without internet conection, retraying!\n')
            sleep(30)


"""
Let the server know the central is online
"""
def signup(url: str, mac_addr: str):
    headers = {"content-type": "application/json"}
    msg = json.dumps({'mac_address': mac_addr})
    
    while True:
        try:
            response = requests.post(url, data=msg, headers=headers, timeout=20)
            if response.status_code == 201:
                sleep(1)

            return response
        except requests.exceptions.RequestException as e:
            ('Failed to signup, device without internet conection, retraying!\n')
            sleep(30)


def watch_for_register(directory: str, mac_addr: str):
    url = 'http://164.41.98.14/create_station/'
    headers = {"content-type": "application/json"}

    i = inotify.adapters.Inotify()
    i.add_watch(directory)

    for event in i.event_gen():
        if event:
            event_type = event[1]
            if event_type[0] == 'IN_CLOSE_WRITE':
                fpath = event[2]
                fname = event[3]
                station_name = fname.split('_')[1]
                full_path = (fpath + '/' + fname)
                msg = json.dumps(
                    {
                        'auth_token': auth_token(),
                        'central': mac_addr,
                        'name': station_name
                    }
                )
                response = requests.post(url, data=msg, headers=headers, timeout=20)
                if response.status_code == 201:
                    print('Registered ' + station_name)
                    os.remove(full_path)
                else:
                    print('Error ' + str(response.status_code))


def auth_token():
    with open('/home/pi/ricc/token', 'r') as f:
        return f.readline()
