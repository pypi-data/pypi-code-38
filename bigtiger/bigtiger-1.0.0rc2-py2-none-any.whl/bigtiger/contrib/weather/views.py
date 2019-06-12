# -*- coding: utf-8 -*-

"""
@tableName: 天气获取
@author: cdhongsheng.com
Created on 2016-6-11

示例地址: http://api.map.baidu.com/telematics/v3/weather?location=%E5%8C%97%E4%BA%AC&output=json&ak=E4805d16520de693a3fe707cdc962045
API地址: http://developer.baidu.com/map/index.php?title=car/api/weather&qq-pf-to=pcqq.c2c
"""

from __future__ import unicode_literals

import json
import urllib2
from datetime import date

from django.core.cache import cache
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from bigtiger.views.decorators import jsonresponse


def _get_baidu_weather_url():
    if not hasattr(settings, 'BAIDU_WEATHER_AK'):
        raise ImproperlyConfigured('BAIDU_WEATHER_AK not find in settings')

    if not hasattr(settings, 'BAIDU_WEATHER_LOCATION'):
        raise ImproperlyConfigured(
            'BAIDU_WEATHER_LOCATION  not find in settings')

    ak = settings.BAIDU_WEATHER_AK
    location = settings.BAIDU_WEATHER_LOCATION

    url = ('http://api.map.baidu.com/telematics/v3/weather?'
           'location={location}&output=json&ak={ak}').format(location=location, ak=ak)
    return url


@jsonresponse()
def baidu_weather(request):
    """获取百度天气预报信息
    """
    today = date.today()
    w = cache.get('BIGTIGER_WEATHER')
    if w is not None and w['date'] == today:
        return w['data']

    try:
        url = _get_baidu_weather_url()
        req = urllib2.Request(url)
        resp = urllib2.urlopen(req)
        content = resp.read()
        result = {'date': today, 'data': json.loads(content)}
        cache.set('BIGTIGER_WEATHER', result, 3600 * 12)
        return result['data']
    except urllib2.HTTPError, e:
        print "Error Code:", e.code
    except urllib2.URLError, e:
        print "Error Reason:", e.reason
    except Exception, e:
        print e
    return []
