print("hello!")
print("HIII")
from Computers import Computers




"""
import requests
import logging
import json
import sys
import os
sys.path.append(os.getcwd())
from Computers import Computers

logging.basicConfig(level=logging.DEBUG)
#client_id = input("Client ID: ")
#api_key = input("API Key: ")
client_id = "20a77b2b4743c0431fea"
api_key = "61a05de2-8e27-404b-b419-218f2f6ed0d4"
auth = (client_id, api_key)

class Version:
    def __init__(self):
        r = requests.get("https://api.amp.cisco.com/v1/version", auth=auth)
        if r.status_code == 200:
            print("Authenticated")
            logging.log(logging.DEBUG, "DEBUG Message AUTH good")
        print(r)


class Computer:
    def __init__(self):
        self.foo = "bar"



class Auth:
    def __init__(self, client_id, api_key):
        self.client_id = client_id
        self.api_key = api_key


c = Computers()

v = Version()
print(v)

"""