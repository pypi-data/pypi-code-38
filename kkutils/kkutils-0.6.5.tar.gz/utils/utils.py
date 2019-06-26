#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author: zhangkai
Email: zhangkai@cmcm.com
Last modified: 2018-01-04 21:46:42
'''
import asyncio
import collections
import datetime
import decimal
import functools
import json
import math
import os
import smtplib
import socket
import threading
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email.utils import formatdate
from socket import inet_aton
from socket import inet_ntoa
from struct import pack
from struct import unpack

import aiosmtplib
import numpy as np
import pymongo
from tqdm import tqdm


class tqdm(tqdm):

    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], pymongo.cursor.Cursor):
            kwargs.setdefault('total', args[0].count())
        super().__init__(*args, **kwargs)

    def update(self, n=None, total=None, incr=None):
        if total is not None:
            self.total = total
        if n is not None:
            super().update(max(0, n - self.n))
        elif incr is not None:
            super().update(incr)


def floor(number, ndigits=0):
    '''当ndigits大于等于number的小数点位数时，直接返回
    '''
    if ndigits == 0:
        return math.floor(number)
    else:
        if float(f'{number:.{ndigits}f}') == number:
            return number
        else:
            return float(decimal.Decimal(number).quantize(decimal.Decimal(f'{0:.{ndigits}f}'), rounding=decimal.ROUND_DOWN))


def ceil(number, ndigits=0):
    if ndigits == 0:
        return math.ceil(number)
    else:
        if float(f'{number:.{ndigits}f}') == number:
            return number
        else:
            return float(decimal.Decimal(number).quantize(decimal.Decimal(f'{0:.{ndigits}f}'), rounding=decimal.ROUND_UP))


def to_str(*args):
    result = tuple(map(lambda x: x.decode() if isinstance(x, bytes) else x if isinstance(x, str) else str(x), args))
    return result[0] if len(args) == 1 else result


def to_bytes(*args):
    result = tuple(map(lambda x: x.encode() if isinstance(x, str) else x if isinstance(x, bytes) else str(x).encode(), args))
    return result[0] if len(args) == 1 else result


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'
    finally:
        s.close()


def connect(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        return True
    except Exception:
        return False
    finally:
        s.close()


def ip2int(ip):
    return unpack("!I", inet_aton(ip))[0]


def int2ip(i):
    return inet_ntoa(pack("!I", i))


def str2int(str_time):
    return int(time.mktime(time.strptime(str_time, "%Y-%m-%d %H:%M:%S")))


def int2str(int_time):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int_time))


def property_wraps(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        key = f'_{method.__name__}'
        if not hasattr(self, key):
            setattr(self, key, method(self, *args, **kwargs))
        return getattr(self, key)
    return wrapper


def time_wraps(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = method(*args, **kwargs)
        print(f'{method.__name__} cost time: {time.time() - start_time:.5f}')
        return result
    return wrapper


class JSONEncoder(json.encoder.JSONEncoder):
    '''针对某些不能序列化的类型如datetime，使用json.dumps(data, cls=JSONEncoder)
    '''

    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, (np.floating, decimal.Decimal)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        try:
            return super().default(obj)
        except Exception:
            return str(obj)


class Singleton(type):
    _instance_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            with Singleton._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Dict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            self.__setitem__(key, value)

    def to_dict(self):
        return DictUnwrapper(self)

    def __delattr__(self, key):
        try:
            del self[key]
            return True
        except Exception:
            return False

    def __getattr__(self, key):
        try:
            return self[key]
        except Exception:
            return None

    def __setitem__(self, key, value):
        super().__setitem__(key, DictWrapper(value))

    __setattr__ = __setitem__

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

    # def __repr__(self):
    #     return 'Dict<%s>' % dict.__repr__(self)

    # def __str__(self):
    #     return json.dumps(self, cls=JSONEncoder, ensure_ascii=False)


class DefaultDict(collections.defaultdict):

    def __delattr__(self, key):
        try:
            del self[key]
            return True
        except Exception:
            return False

    def __getattr__(self, key):
        return self[key]


def DictWrapper(*args, **kwargs):
    if args and len(args) == 1:
        if isinstance(args[0], collections.defaultdict):
            return DefaultDict(args[0].default_factory, args[0])
        elif isinstance(args[0], dict):
            return Dict(args[0])
        elif isinstance(args[0], (tuple, list)):
            return type(args[0])(map(DictWrapper, args[0]))
        else:
            return args[0]
    elif args:
        return type(args)(map(DictWrapper, args))
    else:
        return Dict(**kwargs)


def DictUnwrapper(doc):
    if isinstance(doc, DefaultDict):
        return collections.defaultdict(doc.default_factory, doc)
    if isinstance(doc, Dict):
        return dict(map(lambda x: (x[0], DictUnwrapper(x[1])), doc.items()))
    if isinstance(doc, (tuple, list)):
        return type(doc)(map(DictUnwrapper, doc))
    return doc


class EmailBase:

    def __init__(self, sender=None, smtp=None, user=None, pwd=None):
        self.sender = sender or os.environ.get('EMAIL_SENDER')
        self.smtp = smtp or os.environ.get('EMAIL_SMTP')
        self.user = user or os.environ.get('EMAIL_USER')
        self.pwd = pwd or os.environ.get('EMAIL_PWD')

    def pack(self, receivers, title=None, content=None, files=None, cc=None):
        msg = MIMEMultipart()

        if content:
            mime = MIMEText(content, 'html', 'utf-8')
            msg.attach(mime)

        if files:
            if isinstance(files, (str, bytes)):
                files = [files]
            for i, fname in enumerate(files):
                '''
                _type, _ = mimetypes.guess_type(fname)
                if _type:
                    _type = _type.split('/')
                    att = MIMEBase(_type[0], _type[1], filename=fname)
                else:
                    att = MIMEBase('application', 'octet-stream')
                with open(fname, 'rb') as fp:
                    att.set_payload(fp.read())
                encoders.encode_base64(att)
                att['Content-ID'] = str(i)
                att["Content-Disposition"] = f'attachment; filename="{ os.path.basename(fname) }"'
                '''
                att = MIMEApplication(open(fname, 'rb').read())
                att.add_header('Content-ID', str(i))
                # att.add_header('X-Attachment-Id', str(i))
                att.add_header('Content-Type', 'application/octet-stream')
                att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(fname))
                msg.attach(att)

        if cc:
            if not isinstance(cc, list):
                cc = [cc]
            msg['cc'] = COMMASPACE.join(cc)

        msg['subject'] = title
        msg['date'] = formatdate(localtime=True)
        msg['from'] = self.sender
        if not isinstance(receivers, list):
            receivers = [receivers]
        msg['to'] = COMMASPACE.join(receivers)
        return msg


class Email(EmailBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = smtplib.SMTP()
        # self.client = smtplib.SMTP('localhost')
        # self.sender = self.client.local_hostname

    def send(self, *args, **kwargs):
        msg = self.pack(*args, **kwargs)
        self.client.connect(self.smtp)
        self.client.docmd('ehlo', self.smtp)
        self.client.login(self.user, self.pwd)
        self.client.send_message(msg)
        self.client.quit()


class AioEmail(EmailBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loop = asyncio.get_event_loop()
        self.client = aiosmtplib.SMTP(loop=loop)
        # self.client = smtplib.SMTP('localhost')
        # self.sender = self.client.hostname

    async def send(self, *args, **kwargs):
        msg = self.pack(*args, **kwargs)
        await self.client.connect(self.smtp)
        await self.client.login(self.user, self.pwd)
        await self.client.send_message(msg)
        await self.client.quit()


if __name__ == '__main__':
    email = AioEmail()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(email.send('mpbase1@163.com', 'hello', 'world'))
