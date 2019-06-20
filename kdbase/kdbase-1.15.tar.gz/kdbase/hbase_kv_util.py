#!/usr/bin/env python

import os
import sys
import json
import urllib2
import traceback

from kd_exception import *

from log import *

#raise ConnectTimeOutException
def hbase_kv_set(kv_set_url, key, value, namespace, retry_time=3):
    url = '%s?key=%s&namespace=%s' % (kv_set_url, key, namespace)
    logger().info('kv set url:%s', url)
    try:
        req = urllib2.Request(url, data=value)
        ret = urllib2.urlopen(req)
        status = ret.getcode()
        result = False
        if status == 200:
            res = ret.read()
            logger().info('save kv namespace[%s], key[%s], '
                    'result:%s', namespace, key, res)
            result = json.loads(res)['result']
            return result
        raise ConnectException('url request', status)
    except Exception as e:
        if retry_time == -1:
            raise ConnectTimeOutException('url request', 4)
        err_msg = traceback.format_exc()
        logger().error(err_msg)
        return hbase_kv_set(kv_set_url, key, value, namespace, retry_time - 1)

#raise ConnectTimeOutException
def hbase_kv_get(kv_get_url, key, namespace, retry_time=3):
    url = '%s?key=%s&namespace=%s' % (kv_get_url, key, namespace)
    logger().info('kv get url:%s', url)
    try:
        ret = urllib2.urlopen(url)
        status = ret.getcode()
        content_type = ret.headers.getheader('Content-Type')
        value = None
        if status == 200 and content_type != 'application/json':
            value = ret.read().strip()
            logger().info('get kv namespace[%s] key[%s] result:%s, '
                    'Content-Type:%s' % (namespace, key, value[:100], 
                    content_type))
            return value
        raise ConnectException('url request', status)
    except Exception as e:
        if retry_time == -1:
            raise ConnectTimeOutException('url request', 4)
        err_msg = traceback.format_exc()
        logger().error(err_msg)
        return hbase_kv_get(kv_get_url, key, namespace, retry_time - 1)

if __name__ == "__main__":
    n = 'recognition_quality'
    u = 'http://192.168.8.16:9527/prd/kv/get/v2'
    v = '400110713_20190325160823858'
    print hbase_kv_get(u, v, n)
