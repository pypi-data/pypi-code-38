from __future__ import (absolute_import, division, print_function, unicode_literals)

from pprint import pprint

import requests
from past.builtins import basestring

from .klass_data import Data
from .klass_tool import Tool

CONSOLE, CMDLINE, TOP = 'console', 'cmdline', 'top'


class Consumer(object):
    def __init__(self, host='127.0.0.1', port=5000, token=None):
        self.host = host
        self.port = port
        self.token = token
        self.data = []

    def _send(self, mode):
        assert mode in ['console', 'cmdline', 'top'], 'The mode [%s] is not implemented' % mode
        headers = {'WS_TOKEN': self.token}
        data = self.data
        res = requests.post('http://%s:%s' % (self.host, self.port), json={mode: data}, headers=headers)
        self.result = res.json()
        return self.result

    def stop(self):
        headers = {'WS_TOKEN': self.token}
        res = requests.post('http://%s:%s/shutdown' % (self.host, self.port), json={}, headers=headers)
        self.result = res.json()
        return self.result

    def ping(self):
        headers = {'WS_TOKEN': self.token}
        res = requests.post('http://%s:%s/ping' % (self.host, self.port), json={}, headers=headers)
        self.result = res.json()
        return self.result

    def info(self):
        headers = {'WS_TOKEN': self.token}
        res = requests.post('http://%s:%s/info' % (self.host, self.port), json={}, headers=headers)
        self.result = res.json()
        return self.result

    def cmdline(self, *args):
        if args:
            with Tool.protecting_attributes(self, ['data'], data=[]):
                self.add(*args)
                return self._send(CMDLINE)
        else:
            return self._send(CMDLINE)

    def console(self, *args):
        if args:
            with Tool.protecting_attributes(self, ['data'], data=[]):
                self.add(*args)
                return self._send(CONSOLE)
        else:
            return self._send(CONSOLE)

    def top(self, path=[]):
        if path:
            if not isinstance(path, (list, tuple)):
                path = [path]
            with Tool.protecting_attributes(self, ['data'], data=[]):
                self.add({'path': path})
                return self._send(TOP)
        else:
            return self._send(TOP)

    def print(self):
        data = self.result['data']
        if isinstance(data, basestring):
            for line in data.replace('\\n', '\n').split('\n'):
                print(line)
        else:
            pprint(data)

    def add(self, *args):
        self.data.extend(args)

    def flush(self):
        self.data = []
        self.result = ""

    def __getattr__(self, item):
        if item.startswith('table_'):
            item = item[6:]
            tbl_data = self.result[item]
            Data(tbl_data).show()
            try:
                print('Total: %s' % (len(tbl_data) - 1))
            except:
                pass
            return lambda: 'End'
        elif item.startswith('print_'):
            item = item[6:]
            tbl_data = self.result[item]
            pprint(tbl_data)
            try:
                print('Total: %s' % (len(tbl_data) - 1))
            except:
                pass
            return lambda: 'End'
        elif item.startswith('data_'):
            item = item[5:]
            tbl_data = self.result[item]
            return lambda: tbl_data
        else:
            return super(Consumer, self).__getattr__(item)
