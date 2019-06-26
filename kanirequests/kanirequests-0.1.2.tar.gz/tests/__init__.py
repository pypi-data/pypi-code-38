import os
import requests
import requests.packages.urllib3
from requests.utils import add_dict_to_cookiejar, dict_from_cookiejar
requests.packages.urllib3.disable_warnings()

class Pyhttp(object):
    def __init__(self, headers={}, proxy={}):
        self.session = HTMLSession()
        self.session.headers.update(headers)
        
        self.proxy = proxy
        if proxy != {}:
            self.session.proxies = proxy
        self.adapters = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount("http://", self.adapters)
        self.session.mount("https://", self.adapters)
    
    def get(self, url, *args, **kwargs):
        return self.session.get(url, cookies=self.session.cookies, *args, **kwargs)
        
    def post(self, url, *args, **kwargs):
        return self.session.post(url, cookies=self.session.cookies, *args, **kwargs)
        
    def put(self, url, *args, **kwargs):
        return self.session.put(url, cookies=self.session.cookies, *args, **kwargs)
        
    def delete(self, url, *args, **kwargs):
        return self.session.delete(url, cookies=self.session.cookies, *args, **kwargs)
    
    def close(self):
        self.session.close()
    
    def cookies_to_dict(self):
        return dict_from_cookiejar(self.session.cookies)
    
    def add_cookies(self, cookies):
        add_dict_to_cookiejar(self.session.cookies, cookies)
