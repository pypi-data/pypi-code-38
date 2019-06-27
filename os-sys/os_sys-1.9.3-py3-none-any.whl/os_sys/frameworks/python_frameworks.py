import sys, os, string, abc, __future__
class str(str):
    def r(self):
        print(self)
class list(list):
    def r(self):
        print(self)
import http as _http, html as _html_
class html():
    
    http = _http
    html = _html_
    def __init__(self, port=9752):
        self.init = True
        self.html_version = "html5"
        self.http = True
        self.port = port
        self.html = _html_
        self.http = _http
        self.localhost = "http://127.0.0.1:"
        self.host = self.localhost + str(self.port)
from http.server import ThreadingHTTPServer as base, BaseHTTPRequestHandler as ha
class HTTPServer(base):
    pass
class handler(ha):
    pass


    



