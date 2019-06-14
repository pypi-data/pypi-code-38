from __future__ import (absolute_import, division, print_function, unicode_literals)

import json
import logging
import os
import shutil
import subprocess
import sys
import threading
import time
import traceback
from pprint import pprint

import psutil as psutil
import requests
from flask import Flask, request, Response
from past.builtins import basestring

from .klass_convert import Convert
from .klass_str import Str
from .klass_tool import Tool

logger = logging.getLogger(__name__)
CONSOLE, CMDLINE, TOP = 'console', 'cmdline', 'top'
BUILTINS = '__builtins__'


class WS(object):
    def __init__(self, port=5000, env=None, host='0.0.0.0', token=None, name=None, ctx={}, **kwargs):
        self.app = Flask(name or 'Remote WS')
        self.app.add_url_rule('/', 'index', self.action, methods=['POST', 'GET'])
        self.app.add_url_rule('/shutdown', 'shutdown', self.shutdown, methods=['POST', 'GET'])
        self.app.add_url_rule('/ping', 'ping', self.ping, methods=['POST', 'GET'])
        self.app.add_url_rule('/info', 'info', self.info, methods=['POST', 'GET'])
        self.port = port
        self.host = host
        self.token = token
        self.env = env
        self.debug = kwargs.get('debug', False)
        self.ctx = {}
        self.ctx = {
            'env': self.env,
            'e': self.env,
            'os': os,
            'sys': sys,
            'shutil': shutil,
            'pprint': pprint,
        }
        self.ctx.update(ctx)

    def _check_permission(self):
        if self.token is not None:
            if request.headers.get('WS_TOKEN') != self.token:
                code = 401
                data = {
                    'code': code,
                    'data': 'Access denied',
                }
                return self.response(data, code)
        return False

    def response(self, data, code=200):
        data.setdefault('code', code)
        return Response(
            json.dumps(data) if isinstance(data, dict) else data,
            status=code,
            mimetype='application/json'
        )

    def _process_top_data(self, data):
        def fv(value):
            value = Convert.data(value, 'b', 'mb')
            return Str(value, suffix='MB').with_separator()

        virtual_memory = psutil.virtual_memory()
        partitions = psutil.disk_partitions()
        res = {'data':
            {
                'cpu': {
                    'percent': psutil.cpu_percent(),
                    'count_logical': psutil.cpu_count(),
                    'count': psutil.cpu_count(logical=False),
                },
                'memory': {
                    'percent': virtual_memory.percent,
                    'total': fv(virtual_memory.total),
                    'available': fv(virtual_memory.available),
                    'used': fv(virtual_memory.used),
                    'free': fv(virtual_memory.free),
                }
            }
        }
        for partition in partitions:
            disk_usage = psutil.disk_usage(partition.mountpoint)
            res['data'][partition.mountpoint] = {
                'total': fv(disk_usage.total),
                'used': fv(disk_usage.used),
                'free': fv(disk_usage.free),
                'percent': disk_usage.percent,
            }
        for item in data:
            for path in item.get('path', []):
                disk_usage = psutil.disk_usage(path)
                res['data'][path] = {
                    'total': fv(disk_usage.total),
                    'used': fv(disk_usage.used),
                    'free': fv(disk_usage.free),
                    'percent': disk_usage.percent,
                }
        return res

    def _process_cmdline_data(self, data):
        res = {'data': ''}
        for cmd_line in data:
            if isinstance(cmd_line, basestring):
                cmd_line = cmd_line.split()
            try:
                result = subprocess.check_output(cmd_line)
            except:
                result = traceback.format_exc()
            res['data'] = '%s\n%s' % (res['data'], result)
        return res

    def _process_console_data(self, data):
        res = {}
        res.setdefault('data', '')
        ctx = self.ctx.copy()
        with Tool.stdout_in_memory(res):
            script = '\n'.join(data)
            exec(script, ctx)
        for k, v in ctx.items():
            try:
                json.dumps(k)
                json.dumps(v)
                res[k] = v
            except:
                pass
        return res

    def action(self):
        res = self._check_permission()
        if res:
            return res
        data = request.get_json()
        code = 200
        if self.debug:
            print('Received data :')
            pprint(data)
        if CONSOLE in data:
            res_data = self._process_console_data(data[CONSOLE])
        elif CMDLINE in data:
            res_data = self._process_cmdline_data(data[CMDLINE])
        elif TOP in data:
            res_data = self._process_top_data(data[TOP])
        else:
            code = 500
            res_data = {'data': 'Not implemented', 'code': code}
        return self.response(res_data, code)

    def info(self):
        res = self._check_permission()
        if res:
            return res
        data = {}
        for k, v in self.ctx.items():
            if k == BUILTINS:
                continue
            try:
                k, v = str(k), str(v)
                data[k] = v
            except:
                pass
        res_data = {'data': data}
        return self.response(res_data)

    def ping(self):
        res_data = {'data': 'It works !'}
        return self.response(res_data)

    def start(self):
        run_kwargs = {}
        if self.port:
            run_kwargs['port'] = self.port
        if self.host:
            run_kwargs['host'] = self.host
        thread = threading.Thread(target=self.app.run, args=(), kwargs=run_kwargs)
        thread.start()
        self.thread = thread

    def shutdown(self):
        res = self._check_permission()
        if res:
            return res
        func = request.environ.get('werkzeug.server.shutdown')
        code = 200
        if func is None:
            code = 500
            return self.response({'code': code, 'data': 'Not running with the Werkzeug Server'}, code)
        func()
        return self.response({'code': code, 'data': 'The server is down'}, code)

    def stop(self):
        time.sleep(1)
        url = "http://127.0.0.1:%s/shutdown" % self.port
        requests.post(url)
