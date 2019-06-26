# -*- coding: utf-8 -*-
import os
import json
import time
import re
import socket
import asyncio
import logging
import warnings
import traceback
import subprocess
import shlex
from asyncio.events import AbstractEventLoop
from typing import List, Dict

import aiohttp
#from fluent import sender
from get_args import get_args, Arguments


LINE_FORMAT = '%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
LINE_SPLIT = '-' * 10 + ' %s ' + '-' * 10
ENABLE_PROMETHEUS = False
ENABLE_STATSD = False
HTTP_API_TIMEOUT = 5
ETCD_API_TIMEOUT = 5

IP_MATCH = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

logger: logging.Logger = None

try:
    import statsd
    stater: statsd.StatsClient = None
except ImportError:
    pass

try:
    from prometheus_client import Summary, start_http_server, Gauge
except ImportError:
    pass


class JsonFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord):
        return json.dumps({
            'asctime': self.formatTime(record),
            'name': record.name,
            'process': record.process,
            'levelname': record.levelname,
            'message': record.getMessage()
        })


class FluentHandler(logging.Handler):

    def __init__(self, level=logging.NOTSET, host='localhost', port=5160):
        super().__init__(level)

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._addr = (host, port)

    def emit(self, record):
        msg = self.format(record).encode('utf-8')

        try:
            self._sock.sendto(msg, self._addr)
        except (socket.error, RuntimeError):
            # No time for love, Dr. Jones!
            pass


def config_logger(logger, handler_class, level, formatter_class, format):
    handler = handler_class()
    handler.setLevel(level)
    handler.setFormatter(formatter_class(format))
    logger.addHandler(handler)


class DDNSClient:

    etcd_args: Dict
    loop: asyncio.AbstractEventLoop

    def __init__(self, args:Arguments,
                 loop: asyncio.AbstractEventLoop = None):
        self.args = args

        self.loop = loop or asyncio.get_event_loop()
        self.public_apis = args.app_public_ip_api

        self.etcd_args = args.etcd_
        self.etcd_client = None
        self.etcd_cmd = 'etcdctl'
        self.names = args.dns_name
        self.coredns_prefix = args.coredns_prefix or '/dns'
        self.coredns_ttl = int(args.coredns_ttl or 60)
        self.coredns_notext = args.coredns_notext

        self.public_ip = None
        self.last_update = 0
        self.time_loop = int(args.app_time_loop or 1)
        self.time_update = int(args.app_time_update or 10)

        if not self.etcd_args:
            return

        logger.info('etcd config: ' + json.dumps(self.etcd_args, indent=4))
        if self.etcd_args['type'] != 'cmd':
            del self.etcd_args['type'], self.etcd_args['cmd']

            self.etcd_args.setdefault('timeout', ETCD_API_TIMEOUT)

            try:
                import etcd3
            except ImportError:
                logger.critical('cannot import etcd3, please pip3 install `ddns_client[etcd3]`')
                exit(-1)
            else:
                self.etcd_client = etcd3.client(**self.etcd_args)
        else:
            self.etcd_cmd = self.etcd_args['cmd'] or 'etcdctl'

            if not os.path.isfile(self.etcd_cmd):
                logger.critical(f'etcd_cmd: `{self.etcd_cmd}` is not a file or exists.')
                exit(-1)
            else:
                os.putenv('ETCDCTL_API', '3')
                self.etcd_client = self

    def put(self, k, v):
        cmds = [self.etcd_cmd,
                'put',
                '--cacert=' + self.etcd_args['ca_cert'],
                '--cert=' + self.etcd_args['cert_cert'],
                '--key=' + self.etcd_args['cert_key'],
                '--command-timeout=%ss' % ETCD_API_TIMEOUT,
                '--endpoints=%s:%s' % (self.etcd_args['host'], self.etcd_args['port']),
                '-w=json',
                k
                ]
        # with shell=True, args must be str, otherwise [a, b, c] ==> /bin/sh -c a b c, b and c is args to /bin/sh
        # 'a b c' ==> /bin/sh -c 'a b c'
        # reference: https://docs.python.org/3.6/library/subprocess.html#popen-constructor
        proc = subprocess.Popen(' '.join([shlex.quote(c) for c in cmds]), stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        try:
            out, err = proc.communicate(input=v.encode('utf-8'), timeout=ETCD_API_TIMEOUT)
            code = proc.wait(1)
        except subprocess.TimeoutExpired:
            proc.kill()
            raise
        else:
            if code != 0:
                raise Exception('`etcdctl` return code is not 0, error: ' + out.decode('utf-8'))

        return True

    async def _get_public_ip(self, api, index=''):
        try:
            async with aiohttp.ClientSession() as session:
                logger.debug(f'start get ip api{index}: {api}')

                async with session.get(api, timeout=HTTP_API_TIMEOUT) as resp:
                    result = await resp.text()
                    logger.debug(result)

                    _ips = re.findall(IP_MATCH, result)
                    ips = []
                    for i, ip in enumerate(_ips):
                        try:
                            socket.inet_aton(ip)
                        except OSError:
                            pass
                        else:
                            ips.append(ip)

                    if not ips:
                        logger.warning(f'not ip grep from result of http api{index}: {api}')
                    elif len(set(ips)) != 1:
                        logger.warning(f'get multi distinct ip from api{index} {api}: {ips}')
                    else:
                        logger.debug(f'get public ip from api{index} {api}: {ips[0]}')
                        return ips[0]
        except Exception as e:
            logger.warning(f'get api{index} {api} exception: {traceback.format_exc()}')
            return None

    def get_public_ip_apis(self):
        logger.info(LINE_SPLIT % 'get_public_ip_apis')

        if not self.public_apis:
            logger.critical('there is at least one public api to test or use.')
            return False

        tasks: List[asyncio.Future] = [asyncio.ensure_future(self._get_public_ip(api, f'-{i}'))
                                       for i, api in enumerate(self.public_apis)]
        self.loop.run_until_complete(asyncio.wait(tasks))

        public_ip = []
        for task in tasks:
            ip = task.result()
            if ip is not None:
                public_ip.append(ip)

        if not public_ip:
            logger.critical('no apis can be used for get public ip')
            return None
        elif len(set(public_ip)) != 1:
            logger.critical(f'get multi distinct ip from apis: {public_ip}')
            return None
        else:
            logger.info(f'get public ip from all apis: {public_ip[0]}')
            return public_ip[0]

    def _name2path(self, name):
        return self.coredns_prefix + '/' + '/'.join(name.split('.')[::-1])

    def update_ddns(self):
        ip = self.get_public_ip_apis()
        if ip is None:
            return
        elif ip == self.public_ip:
            if time.time() - self.last_update < self.time_update:
                return
        else:
            logger.info(f'public ip changed: {self.public_ip} -> {ip}, should update ddns instantly')
            self.public_ip = ip

        logger.info(LINE_SPLIT % 'update_ddns')
        logger.info(f'update ddns name: {self.names}')

        etcd_content = {
            'host': ip,
            'ttl': self.coredns_ttl,
        }
        if not self.coredns_notext:
            etcd_content['text'] = 'updated by ddns_client at ' + \
                                   time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        etcd_content = json.dumps(etcd_content)

        try:
            for name in self.names:
                logger.debug(f'update ddns {name} -> {ip}: ' + etcd_content)
                self.etcd_client.put(self._name2path(name), etcd_content)
                logger.info(f'update ddns {name} -> {ip} successfully')
        except Exception as e:
            logger.error(f'cannot update ddns: ' + traceback.format_exc())
        else:
            self.last_update = time.time()

    def ddns_start(self):
        if not self.names:
            logger.critical('if not test any args, dns_name must be supplied once at least.')
            return

        while True:
            time.sleep(self.time_loop)
            self.update_ddns()


def main():
    args = get_args(os.path.join(os.path.dirname(__file__), 'get_args.yml'), False)

    # logging
    global logger
    logger = logging.getLogger('ddns_client')
    logger.propagate = False
    logging_type = args.logging_type or 'stderr'
    logging_level = args.logging_level or 'INFO'

    if logging_type == 'stderr':
        stderr_format = args.logging_stderr_format or 'line'
        if stderr_format == 'json':
            config_logger(logger, logging.StreamHandler, logging_level, JsonFormatter, '')
        elif stderr_format == 'message':
            config_logger(logger, logging.StreamHandler, logging_level, logging.Formatter, '%(message)s')
        elif stderr_format == 'line':
            if not args.logging_stderr_nocolor:
                try:
                    import coloredlogs
                    style_level = coloredlogs.DEFAULT_LEVEL_STYLES
                    style_level['info']['color'] = 'cyan'
                    style_level['warning']['color'] = 'red'
                    coloredlogs.install(args.logging_level, logger=logger, fmt=LINE_FORMAT, milliseconds=True)
                except ImportError:
                    warnings.warn('colored logging need to install: ddns_client[color]')
                    config_logger(logger, logging.StreamHandler, logging_level, logging.Formatter, LINE_FORMAT)
            else:
                config_logger(logger, logging.StreamHandler, logging_level, logging.Formatter, LINE_FORMAT)

    elif logging_type == 'fluent':
        fluent_type = args.logging_fluent_type or 'udp'
        fluent_host = args.logging_fluent_host or 'localhost'
        fluent_port = args.logging_fluent_port or 5160

        if fluent_type != 'udp':
            raise Exception('other fluent type not supported now')

        config_logger(logger, lambda: FluentHandler(host=fluent_host, port=fluent_port), logging_level,
                      JsonFormatter, LINE_FORMAT)

    elif logging_type == 'file':
        path = args.logging_file_path or './ddns.log'
        formatter = logging.Formatter if args.logging_file_format else JsonFormatter
        mode = 'a' if args.logging_file_append else 'w'
        newline = '\r\n' if args.logging_file_crlf else '\n'

        if os.name == 'nt':
            stream = open(path, mode, encoding='utf-8', newline=newline)
        else:
            fd = os.open(path, os.O_CREAT | os.O_APPEND)
            stream = open(fd, mode, encoding='utf-8', newline=newline)

        config_logger(logger, lambda: logging.StreamHandler(stream), logging_level, formatter, LINE_FORMAT)

    # metrics
    metrics_type = args.metrics_type or []
    if 'prometheus' in metrics_type:
        global ENABLE_PROMETHEUS
        ENABLE_PROMETHEUS = True

        port = args.metrics_prometheus_port or 1234
        host = args.metrics_prometheus_host or 'localhost'
        start_http_server(port, host)

    elif 'statsd' in metrics_type:
        global stater, ENABLE_STATSD
        ENABLE_STATSD = True

        try:
            stater = statsd.StatsClient()
        except NameError:
            warnings.warn('statsd metrics need to install: ddns_client[statsd]')

    dc = DDNSClient(args=args)
    tests = list(set(args.app_test or []))
    if not tests:
        dc.ddns_start()
        return

    if 'all' in tests:
        tests = ['all', ]

    for test in tests:
        if test == 'ip':
            dc.get_public_ip_apis()
        else:
            dc.update_ddns()


if __name__ == '__main__':
    main()

