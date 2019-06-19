# encoding: utf-8
from __future__ import division, unicode_literals
import json

from django.db import models
from django.conf import settings
from jsonfield import JSONField

from .cache import cacheByTime


class Domain(models.Model):
    host = models.CharField(max_length=128, db_index=True)
    _config = JSONField(db_column='config')
    _hwa = JSONField(db_column='hwa')
    _hac = JSONField(db_column='hac')
    _hma = JSONField(db_column='hma')
    _auth = JSONField(db_column='auth')
    _bigdata = JSONField(db_column='bigdata')

    def __repr__(self):
        return self.host

    @classmethod
    def all(cls):
        try:
            return list(cls.objects.all())
        except Exception:
            return []

    @classmethod
    def pop(cls, host):
        """
        当debug或者测试环境时 不做缓存
        """
        domains = cls.objects.all()
        obj = [x for x in domains if x.host == host]
        if obj:
            return obj[0]
        if domains:
            return domains[0]
        return cls.get(host)

    @classmethod
    @cacheByTime()
    def get(cls, host=''):
        """
        当host为空时
        取Domain表中的第一条数据
        考虑到在domain表没有建立的时候就会调用这个方法，所以做异常处理
        """
        domains = cls.objects.all()
        obj = [x for x in domains if host == x.host]
        if obj:
            return obj[0]
        if domains:
            return domains[0]
        return cls()

    @property
    def config(self):
        """
        给config返回一些默认值
        """
        data = dict(self._config)
        return data

    @property
    def url(self):
        self._config['host'] = self.host
        return getUrl(self._config)

    @property
    def hwa(self):
        data = dict(self._hwa)
        data.setdefault(
            'identify', {
                'identify':
                'Ohmj1y0JEMWEdXYnuWWnDNQ7Ak6xxaeuZPXLBayBGI9xQMQemn7ZqSTHaT092SjEWkuVaP+cxo1n7Tm/UyZiuIPFCqVRNJlx5IH39OF3zM3hoWVAdfxRfSj5YQ/XnzRwuQ0qeo8/qpg4gpRXCiT56SBkhNMRixooLH0YHn7Rets='
            })
        data.setdefault('host', getHost(self.host, 'analytics'))
        return fromDict(data, {})

    @property
    def hma(self):
        data = dict(self._hma)
        data.setdefault('identify', {'identify': 'hypersadmin'})
        data.setdefault('host', getHost(self.host, 'mobile'))
        return fromDict(data, {})

    @property
    def hac(self):
        data = dict(self._hac)
        data.setdefault('identify',
                        {'identify': 'URBahpGT5tYCFd0rjy2EHe1oVYX7O3hb'})
        data.setdefault('host', getHost(self.host, 'account'))
        return fromDict(data, {})

    @property
    def auth(self):
        data = dict(self._auth)
        data.setdefault('identify', {'identify': ''})
        data.setdefault('host', getHost(self.host, 'auth'))
        return fromDict(data, {'oauth2': '/oauth2/profile'})

    @property
    def bigdata(self):
        data = dict(self._bigdata)
        data.setdefault('identify', {'identify': ''})
        data.setdefault('host', 'realtime-adstracker.hypers.com.cn')
        data.setdefault('https', False)
        return fromDict(data)

    @classmethod
    def load(cls, path=''):
        if not path:
            path = str(settings.ROOT_DIR.path('config/config.json'))
        with open(path, 'r') as fd:
            config = json.load(fd)
        configs = config['domain']
        for config in configs:
            projects = {
                x: config.pop(x.split('_')[1], {})
                for x in ['_hwa', '_hma', '_hac', '_auth', '_bigdata']
            }
            host = config.pop('host', '')
            obj, ok = cls.objects.get_or_create(host=host)
            obj._config = config
            for key, value in projects.items():
                setattr(obj, key, value)
            obj.save()
        return obj


def getHost(host, prefix):
    name = host.split('.', 1)[-1]
    return prefix + '.' + name


def getUrl(data):
    https = 'https://' if data.get('https', True) else 'http://'
    return https + data['host']


class Template(object):
    host = ''

    def __repr__(self):
        return self.host


def fromDict(data, urlMap=None):
    obj = Template()
    data['url'] = getUrl(data)
    for key, value in data.items():
        setattr(obj, key, value)
    for name, url in (urlMap or {}).items():
        setattr(obj, name, data['url'] + url)
    return obj
