import requests
import logging
import time

session = requests.Session()
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

log = logging.getLogger()

def fetch_json(url, r):
    respone_data = {}
    if r is None:
        return respone_data
    if r.status_code != 200:
        log.error('http fail: %s %s %s', url, r.status_code, r.text);
        return respone_data
    try:
        respone_data = r.json()
    except ValueError:
        log.error('http json_decode error: %s %s', url, r.text);
    return respone_data

def get(url, **kwargs):
    call = lambda : session.get(url, **kwargs)
    return safe_reqeust(url, call)

def post(url, **kwargs):
    call = lambda : session.post(url, **kwargs)
    return safe_reqeust(url, call)

def safe_reqeust(url, call):
    try:
        r = call()
        return r
    except requests.exceptions.RequestException as e:
        return None
