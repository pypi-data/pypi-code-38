import requests
import hashlib

def get_token(hostname, username, password):
    url = "http://{}:7681/access_token".format(hostname)
    headers = { "Content-Type": "application/x-www-form-urlencoded"}

    form = {
        "device_name": "Home Assistant",
        "device_hardware_id": "homeassistant",
        "device_os": 5,
        "device_type": 3,
        "device_app": 1
    }
    auth = ( username, hashlib.sha512(password).hexdigest())
    r = requests.post(url, auth=auth, data=form)
    return r.text.split("&")[0].split("=")[1]
