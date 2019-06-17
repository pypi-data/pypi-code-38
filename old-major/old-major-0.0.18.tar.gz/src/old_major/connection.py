import websocket
import requests
import json
import inotify.adapters
import threading

from time import sleep
from getmac import get_mac_address

from .led_debugger import LedDebugger
from .parser import parse

DEBUG = LedDebugger()

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
    watch_thread = threading.Thread(target=watch_for_collects, args=(directory, mac_addr))    
    token_thread = threading.Thread(target=get_token, args=(url, mac_addr))
    
    watch_thread.start()
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

                station_id, timestamp = fname[:-4].split('_')
                headers = {"content-type": "application/json"}
                partial_msg = dict(parse(fpath + fname))
                partial_msg['auth_token'] = token
                partial_msg['central'] = mac_addr
                partial_msg['name'] = station_id
                partial_msg['timestamp'] = timestamp 

                msg = json.dumps(partial_msg)
                while requests.post(url, data=msg, headers=headers, timeout=20) != 200:
                    sleep(600)


"""
Constantly makes get requests to get token
"""
def get_token(url: str, mac_addr: str):
    formated_mac = mac_addr.replace(':', '-')
    payload = {'mac': formated_mac}
    response = requests.get(url, params=payload, timeout=20)

    while response.status_code != 200:
        print('Trying to acquire token')
        sleep(10)
        response = requests.get(url, params=payload, timeout=20)
    
    DEBUG.neutral()
    sleep(1)
    f = open('/home/pi/ricc/token', 'w')
    f.write(response.text)
    f.close()
    DEBUG.success()


"""
Let the server know the central is online
"""
def signup(url: str, mac_addr: str):
    headers = {"content-type": "application/json"}
    msg = json.dumps({'mac_address': mac_addr})
    response = requests.post(url, data=msg, headers=headers, timeout=20)
    
    if response.status_code == 201:
        DEBUG.neutral()
        sleep(1)
        DEBUG.success()

    return response
