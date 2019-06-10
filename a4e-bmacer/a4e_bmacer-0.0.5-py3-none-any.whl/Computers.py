import requests
import logging
from Auth import auth

class Computers:
    def __init__(self):
        url = "https://api.amp.cisco.com/v1/computers"
        r = requests.get(url, auth=auth)
        if r.status_code != 200:
            raise Exception(f"Non-200 Status Code: {r.status_code}")
        self.status_code = r.status_code
        logging.log(logging.DEBUG, f"Computers: {r}")