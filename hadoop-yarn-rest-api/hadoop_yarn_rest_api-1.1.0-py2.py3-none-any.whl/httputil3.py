#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
from urllib.error import HTTPError
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

'''
@author: whitebeard-k
'''

class HttpRequest(object):
    '''
        HTTP 호출 
    '''
    
    def param_encode(self, params):
        return urllib.parse.urlencode(params)
    
    def request(self, request_url, request_type="GET", params=None, headers={}, data=None):
        opener = urllib.request.build_opener(urllib.request.HTTPHandler)
        
        if params:
            request_url = "{0}?{1}".format(request_url, self.param_encode(params))
        
        req = urllib.request.Request(request_url, data, headers)
        req.get_method = lambda: request_type
        
        try:
            response = opener.open(req)
        except HTTPError as hpe:
            # fail
            return HttpResponse(hpe)
        
        return HttpResponse(response)
        
class HttpResponse(object):
    
    __CONTENT__TYPE__ = "Content-Type"
    
    def __init__(self, info):
        
        self.info = info
        self.headers = info.headers
        self.code = info.code
        self.msg = info.msg
        self.body = info.read()
        self.isok = True if not isinstance(info, HTTPError) else False
    
if __name__ == "__main__":
    http = HttpRequest()
    response = http.request("http://localhost:11000/oozie")
    
    print((response.headers["Content-Type"]))