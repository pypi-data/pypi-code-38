import requests
import dong
import logging

def post(api, **kwargs):
    url = "{}/{}".format(dong.SERVER_IP, api)
    logging.info("post:{}".format(url))
    r = requests.post(url, **kwargs)
    return r

def get(api, **kwargs):
    url = "{}/{}".format(dong.SERVER_IP, api)
    logging.info("get:{}".format(url))
    r = requests.get(url, **kwargs)
    return r
