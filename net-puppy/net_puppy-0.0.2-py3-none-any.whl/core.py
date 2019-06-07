# Developed by Vishal Keshav
import os
import subprocess
import time

import requests
from websocket import create_connection
from requests.auth import HTTPBasicAuth
import json

def _get_notification(data, token):
    url = "https://api.pushbullet.com/v2/pushes?limit=1"
    headers = {"Accept": "application/json",
               "Content-Type": "application/json",
               "User-Agent": "pyPushBullet"}
    r = requests.request("GET", url, data=None, params=None, headers=headers,
                                    files=None, auth=HTTPBasicAuth(token, ""))
    r.raise_for_status()
    return r.json()

def _run_command(command_str):
    if command_str[0] == 'C':
        os.system(command_str[2:])
    else:
        print("invalid command, " + command_str)


def start(token):
    """
    Starts receving commands from the push bullet server.
    Ctrl+X to exit
    From server, process linux commands only with "C " prepended.

    Args:
        token: token created from push bullet service.
    Returns:
        None
    """
    url = "wss://stream.pushbullet.com/websocket/" + token
    ws = create_connection(url)
    while 1:
        data = ws.recv()
        data = json.loads(data)
        if data["type"] != "nop":
            if data["type"] == "tickle":
                notification = _get_notification(data, token)
                _run_command(notification['pushes'][0]['body'])
