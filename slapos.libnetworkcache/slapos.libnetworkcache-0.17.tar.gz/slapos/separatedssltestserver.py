# Note: Some day this test code shall be integrated with libnetworkcachetests
# Unfortunatly it had not worked while running tests, possibly thread issues
# with test + ssl library?
import os
import time
import hashlib
import BaseHTTPServer
import json
import SocketServer
import ssl
import socket
import tempfile
import threading

class NCHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  def __init__(self, request, address, server):
    self.__server = server
    self.tree = server.tree
    BaseHTTPServer.BaseHTTPRequestHandler.__init__(
      self, request, address, server)

  def do_KILL(self):
    raise SystemExit

  def do_GET(self):
    path = os.path.abspath(os.path.join(self.tree, *self.path.split('/')))
    if not (
      ((path == self.tree) or path.startswith(self.tree + os.path.sep))
      and
      os.path.exists(path)
      ):
      self.send_response(404, 'Not Found')
      return
    self.send_response(200)
    out = open(path, 'rb').read()
    self.send_header('Content-Length', len(out))
    self.end_headers()
    self.wfile.write(out)

  def do_PUT(self):
    path = os.path.abspath(os.path.join(self.tree, *self.path.split('/')))
    if not os.path.exists(os.path.dirname(path)):
      os.makedirs(os.path.dirname(path))
    data = self.rfile.read(int(self.headers.getheader('content-length')))
    cksum = hashlib.sha512(data).hexdigest()
    if 'shadir' in path:
      d = json.loads(data)
      data = json.dumps([d])
      if os.path.exists(path):
        f = open(path, 'r')
        try:
          file_data = f.read()
        finally:
          f.close()
        file_data = file_data.strip()
        json_data_list = json.loads(file_data)
        json_data_list.append(d)
        data = json.dumps(json_data_list)
    else:
      raise ValueError('shacache shall use POST')

    open(path, 'wb').write(data)
    self.send_response(201)
    self.send_header('Content-Length', str(len(cksum)))
    self.send_header('Content-Type', 'text/html')
    self.end_headers()
    self.wfile.write(cksum)
    return

  def do_POST(self):
    path = os.path.abspath(os.path.join(self.tree, *self.path.split('/')))
    if not os.path.exists(path):
      os.makedirs(path)
    data = self.rfile.read(int(self.headers.getheader('content-length')))
    cksum = hashlib.sha512(data).hexdigest()
    if 'shadir' in path:
      raise ValueError('shadir shall use PUT')
    else:
      path = os.path.join(path, cksum)

    open(path, 'wb').write(data)
    self.send_response(201)
    self.send_header('Content-Length', str(len(cksum)))
    self.send_header('Content-Type', 'text/html')
    self.end_headers()
    self.wfile.write(cksum)
    return

class Server(BaseHTTPServer.HTTPServer):
  def __init__(self, tree, *args):
    BaseHTTPServer.HTTPServer.__init__(self, *args)
    self.tree = os.path.abspath(tree)

  __run = True

  def serve_forever(self):
    while self.__run:
      self.handle_request()

  def handle_error(self, *_):
    self.__run = False

class SSLServer(Server):
  def __init__(self, tree, certfile, keyfile, cacerts, server_address,
      HandlerClass, *args):
    self.tree = os.path.abspath(tree)
    SocketServer.BaseServer.__init__(self, server_address, HandlerClass)
    #Server.__init__(self, tree, server_address, HandlerClass, *args)
    self.socket = ssl.wrap_socket(socket.socket(self.address_family,
       self.socket_type), server_side=True, certfile=certfile,
       keyfile=keyfile, ssl_version=ssl.PROTOCOL_TLSv1,
       cert_reqs=ssl.CERT_REQUIRED, ca_certs=cacerts)
    self.server_bind()
    self.server_activate()

class SSLNCHandler(NCHandler):
  def setup(self):
    self.connection = self.request
    self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
    self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)

def _run_nc_SSL(tree, host, port, certfile, keyfile, cacerts):
  server_address = (host, port)
  httpd = SSLServer(tree, certfile, keyfile, cacerts, server_address, SSLNCHandler)
  httpd.serve_forever()

ca_cert = """-----BEGIN CERTIFICATE-----
MIID3zCCAsegAwIBAgIJAK6xwAnLgupDMA0GCSqGSIb3DQEBBQUAMIGFMQswCQYD
VQQGEwJQTDENMAsGA1UECAwETGFrYTELMAkGA1UEBwwCVWwxEDAOBgNVBAoMB1Bh
c2lla2ExKDAmBgNVBAMMH0F1dG9tYXRpYyBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkx
HjAcBgkqhkiG9w0BCQEWD2x1a2VAbmV4ZWRpLmNvbTAeFw0xMTA4MzAwOTEwNDda
Fw00MTA4MjIwOTEwNDdaMIGFMQswCQYDVQQGEwJQTDENMAsGA1UECAwETGFrYTEL
MAkGA1UEBwwCVWwxEDAOBgNVBAoMB1Bhc2lla2ExKDAmBgNVBAMMH0F1dG9tYXRp
YyBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkxHjAcBgkqhkiG9w0BCQEWD2x1a2VAbmV4
ZWRpLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMc1jUTwrPAC
mLUL8hwTcOpu3UxZFsAiz/XDNdNpwfEN5RzZrNeW4rJpyqCgPpXtnuQRv2Ru3c2w
oOJbL+JvGicpjleHrpU+DKw3njic7GkBYCYL+UdI4+F7a5coj+FDDHYHcY6XiIMf
3to7eJLmHeAAQe5z1MIKV4mUZGrRB494g0x2Z8rdxZkDSi8YhcwHRkMIA1p6wWY6
1ROXYdUROQ22X1mUO03fCOyyJrfuUQd3WXBtA96c9qZ1Kr8Z6qTFrTU2syRSMK1O
acZ2mSvaRYM7OuS97YqI5WBdqjQ1DRAhIsMbp42MAgEb+CxJflr6viibfw5sWqx6
WcQfHcDO8EsCAwEAAaNQME4wHQYDVR0OBBYEFIwXY1hTrkII98JBWU1o4XcLSJJm
MB8GA1UdIwQYMBaAFIwXY1hTrkII98JBWU1o4XcLSJJmMAwGA1UdEwQFMAMBAf8w
DQYJKoZIhvcNAQEFBQADggEBAEO1lmm0DTLQD0fJHYwIG+WJX2k/ThzNEE7s246m
4Hk+2ws78sdCWPkfvQHiUvCFBnfBNBfTSBToPJKaPxHi85I8VrV52/JjoA1La6pH
yr1bU9WAHv/oHRRaZcHiMqLz8/L8UM2M4VXq39BZ695tu5PI8Zu410u/62G7avht
2QjD1Xsfo5yx4LaFnTJNqq0Qn1pEVWK1QWFqntqu0l+y1zIw2R3dyxaYAkcqKO4R
euQB4LKEfrfwEBoBRK7/YXL2hewKyb/2h/5i6QazkwebLSAKOpV6LpShRbEn6O92
Ev5yliJ0c6fLy1PT0ZDevGEMigbUQo/+Bd2vIDzlrEw7mH8=
-----END CERTIFICATE-----
"""

auth_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDA8zHDYIYDIYsq
okplkfQWac24b67/nTEXANDLjftbBGNj1/fFFK2GuVgcvdtMnqbyD1RMSMoEJa1a
uMldazh3XENTDBxUrdmEoe0Qckh9KScPjQWvxiIjaitpKEZJWZU9lK1v3EZYOweE
Ch50iiV3hIA8pbWphM8C631YxLorBGovGEDBq8q+KHBmZa3U0bByuytxCrCZP34H
NRZQM7rf+webXjqygJ+sVq2miLr5Dr2zxo44enguGsP2VZXzc5xoflQlLRgcl2IM
0u/s7H0p2XlaCBhzgjcTInYqE8I6fKCuZQWRVUkySF1omMmg3bthhGlz66aQZudK
a7HkMj4rAgMBAAECggEAG1ebGqun8fOj6/O5hTEsnKx7mYJCEzjsRu03qVDCaMBz
cSeelc/7UxcatF/3HqFw2OZxNKov7myEZ1G+Pz29b7SkWbViomFMbK4hkO4Q9aOK
RHrgbmsuVURrSGiLpUNLkcFq3mohkckzpHNmo28cJhahsXZuCsqmJyzFw3mFRCkJ
+OGaPzx0llDRkHPVMWxeQsuadDLrT5Kv4u4E7vPWmMBJ9p5Yy/xKUAX8vrtheSjo
eiHM4RW63xedmDQ6G3ofJgAiCLPCyodTtwJJnGY3ZXpCjfX0t0eyGYNkgqOM0eYw
670avZSBABCDCM7ff/w2HzxE9uY2It2VxG7Wr4WtUQKBgQDlvLMf4kE5gAtcpan4
5TJHblm1fNIVP1VMMq1WexeDnY3FHvW5FCCndJAUBW7N+ILDZVtQ+EWEcQF2hASw
6KdxBa/K/F5dLm2UUb4YLUh5ERLN+FPu7Q1jjYQtHVSsS/54YRivjV90PHnrW4G3
xljtp74+TZ/SSp3Rxnk8u8ILmQKBgQDXAemMk0LgxnDhG5PwjY6aoV6WSy4B9rT7
EXrhTDL4QZpdVlTzdGPuSSI74xbjT9B84fD8gLh+1rGVHyDlDOLduxdOuatgs2P8
zaIEBvwX15DVVINves/5gFb5FOd007LsLwfZrTSG9kLL4MR5qzl24d74z3zlB75Q
6xuU/G8SYwKBgHONyntLDouhgBWFrkzm27daJf1HX1QYmwrMoqtRFq643Mo9nFMP
cK1Jz/6CDQ3E5eDqZlf/yNepD5dRKBrjqvUKazWqYrxz0eI8i2UVwdJDaDX5ph4T
Vhyw3b7jdeeEAecCz6vdbBnHIXvkdwa82ZYQPXyRBsZ7iY4uSmTl++BhAoGAC/EX
P6+OL13WNyqI9PtnyD7eOgrC62kAdFFsOcc5rYA3SqfY4Ay+4CU/uYPLaaStN8J0
2BFuLd1Oz7GC6jXlA9u4V68ITb6o9wmUzhR1O/3FFZQ0GKUBmCIAsqTulhaMAYI7
NWPhXv2eiCRbxUY1Ut0IvVkI3s+nSmdEiOncYXECgYEAschHLdYaVl/1tvFUEubC
acabL1CwvSPh/1+xd05w2SUBZguN4q6b5zan2z34E6njRWrXbMpZ8jHroyaCFQha
CkvUOu+kXxjhuolc3LdtVssf2Zupkdwo9u07DR31t6RmJPIi/p461wgtVUI8pCK9
/59DljkBXEter7wmdnitIJg=
-----END PRIVATE KEY-----
"""

auth_certificate = """-----BEGIN CERTIFICATE-----
MIID2TCCAsGgAwIBAgIBBDANBgkqhkiG9w0BAQUFADCBhTELMAkGA1UEBhMCUEwx
DTALBgNVBAgMBExha2ExCzAJBgNVBAcMAlVsMRAwDgYDVQQKDAdQYXNpZWthMSgw
JgYDVQQDDB9BdXRvbWF0aWMgQ2VydGlmaWNhdGUgQXV0aG9yaXR5MR4wHAYJKoZI
hvcNAQkBFg9sdWtlQG5leGVkaS5jb20wHhcNMTEwODMwMDkzOTExWhcNMjEwODI3
MDkzOTExWjBdMQswCQYDVQQGEwJQTDENMAsGA1UECAwETGFrYTEQMA4GA1UECgwH
UGFzaWVrYTENMAsGA1UEAwwEbWF5YTEeMBwGCSqGSIb3DQEJARYPbHVrZUBuZXhl
ZGkuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwPMxw2CGAyGL
KqJKZZH0FmnNuG+u/50xFwDQy437WwRjY9f3xRSthrlYHL3bTJ6m8g9UTEjKBCWt
WrjJXWs4d1xDUwwcVK3ZhKHtEHJIfSknD40Fr8YiI2oraShGSVmVPZStb9xGWDsH
hAoedIold4SAPKW1qYTPAut9WMS6KwRqLxhAwavKvihwZmWt1NGwcrsrcQqwmT9+
BzUWUDO63/sHm146soCfrFatpoi6+Q69s8aOOHp4LhrD9lWV83OcaH5UJS0YHJdi
DNLv7Ox9Kdl5WggYc4I3EyJ2KhPCOnygrmUFkVVJMkhdaJjJoN27YYRpc+umkGbn
Smux5DI+KwIDAQABo3sweTAJBgNVHRMEAjAAMCwGCWCGSAGG+EIBDQQfFh1PcGVu
U1NMIEdlbmVyYXRlZCBDZXJ0aWZpY2F0ZTAdBgNVHQ4EFgQU8fr/I1bRXGM7e14s
jzNA7Tx/nVswHwYDVR0jBBgwFoAUjBdjWFOuQgj3wkFZTWjhdwtIkmYwDQYJKoZI
hvcNAQEFBQADggEBAJ6q6sx+BeIi/Ia4fbjwCrw0ZahGn24fpoD7g8/eZ9XbmBMx
y4o5UlFS5LW1M0RywV0XksztU8jyQZOB8uhWw1eEdMovGqvTWmer0T0PPo14TJhN
iQh+KE90apiM8ohKJoBZ+v6s9+99YDmeW7UOw0o1wtOdT9oyT3ZbjQ57lCEUljjk
7VevyRXKYweEogzNe0lEpKiZLqiOkVtRhIY/O5eB+RYPomLmd/wWFQJrYpdRzWnj
RWYLHZ9aoSO3icgl8uvxT7WYD8fmAxXjdRd0DQVA3Jv8v8QiV+u5rxP1gcG63Bwd
08ckPaJcFIVx2H1euT4xwVDORmvuX8N3uaZLyZQ=
-----END CERTIFICATE-----
"""

if __name__ == '__main__':
  keyfile = tempfile.NamedTemporaryFile()
  keyfile.write(auth_key)
  keyfile.flush()
  certfile = tempfile.NamedTemporaryFile()
  certfile.write(auth_certificate)
  certfile.flush()
  cacerts = tempfile.NamedTemporaryFile()
  cacerts.write(ca_cert)
  cacerts.flush()
  thread = threading.Thread(target=_run_nc_SSL, args=('pla', '127.0.0.1',
      7890, certfile.name, keyfile.name, cacerts.name))
  thread.daemon = True
  thread.start()
  while True:
    time.sleep(1)
