# -*- coding: utf-8 -*-

from wsgiref.simple_server import make_server
from server.server_handle import application
import sys
if sys.version < '3':
    reload(sys)
    sys.setdefaultencoding('utf8')


def boot_start(port):
    httpd = make_server('', port, application)
    print('Serving HTTP on port {}...'.format(port))
    httpd.serve_forever()

