import requests
import dong

def post(api, **kwargs):
    url = "{}/{}".format(dong.SERVER_IP, api)
    r = requests.post(url, **kwargs)
    return r

def get(api, **kwargs):
    url = "{}/{}".format(dong.SERVER_IP, api)
    r = requests.get(url, **kwargs)
    return r
