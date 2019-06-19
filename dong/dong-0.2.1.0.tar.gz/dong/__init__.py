import os

#__version__ = "0.1"

PROG_NAME = "dong"

try:
    os.environ['DONG_DEBUG']
except KeyError:
    SERVER_IP = 'http://api.libgirl.com'
else:
    SERVER_IP = 'http://127.0.0.1:8000'

SERVER_NAME = 'api.libgirl.com'
