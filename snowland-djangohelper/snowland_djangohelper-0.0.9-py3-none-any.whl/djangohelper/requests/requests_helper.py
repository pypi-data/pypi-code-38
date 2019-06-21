#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: www.snowland.ltd
# @file: requests_helper.py
# @time: 2018/11/7 9:15
# @Software: PyCharm

import requests as req
host = 'smssh1.253.com'
port = 80
service = '/msg/balance/json'
method = 'post'
headers = {"Content-type": "application/json"}
prefix = 'http://'


def request(method=method, host=host, port=port, service=service, params={}, headers=headers, prefix=prefix):
    if method.lower() == 'get':
        host = host if host.startswith(prefix) else prefix + host
        service = service if service.endswith('/') else service + '/'
        url = host + ':' + str(port) + '/' + service
        res = req.get(url=url, params=params, headers=headers)
    elif method.lower() == 'post':
        host = host if host.startswith(prefix) else prefix + host
        service = service if service.endswith('/') else service + '/'
        url = host + ':' + str(port) + '/' + service
        res = req.post(url, data=params, headers=headers)
    try:
        return str(res.json())
    except:
        return 'it is not a json response'


if __name__ == '__main__':
    params = {'account': 'xx', 'password': 'xx'}
    print(request(params=params))
