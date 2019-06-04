#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/05/08 18:56
# @Author  : niuliangtao
# @Site    : 
# @File    : ItemUtils.py
# @Software: PyCharm


import logging

import demjson
import urllib3

logger = logging.getLogger('ItemUtils')

__all__ = ['fill_item_info']


def fill_item_info(item_list=None):
    if item_list is None or not isinstance(item_list, list):
        raise Exception('入参 item_list 是list')
    items = ','.join(item_list)
    url = 'http://pluto.vdian.net/solution/query?solutionId=1004&itemIdList=' + items

    r = urllib3.PoolManager().request('GET', url)

    logger.debug('url:' + url)

    response = demjson.decode(r.data)

    logger.debug('response:' + str(response))
    result = response['result']['result']
    for res in result:
        res['priceInfo'] = res['price']
        res['price'] = res['priceInfo']['price']
    return result


def fill_item_info_dict(item_list=None):
    if item_list is None or not isinstance(item_list, list):
        raise Exception('入参 item_list 是list')

    item_ids = set()

    for item in item_list:
        if 'itemId' not in item.keys() or item['itemId'] is None:
            continue
        item_ids.add(item['itemId'])


    items = ','.join(item_ids)
    url = 'http://pluto.vdian.net/solution/query?solutionId=1004&itemIdList=' + items

    r = urllib3.PoolManager().request('GET', url)

    logger.debug('url:' + url)

    response = demjson.decode(r.data)

    logger.debug('response:' + str(response))
    result = response['result']['result']

    res_map = {}
    for res in result:
        res['priceInfo'] = res['price']
        res['price'] = res['priceInfo']['price']
        res_map[str(res['itemId'])]=res

    for item in item_list:
        item.update(res_map.get(item['itemId'],{}))

    return item_list


def test():
    items = ['2738806530', '2760741906', '2631178932', '2760230700', '2748823895', '2761505903', '2628266453',
             '2752052591', '2765499871', '2742365760', '2744653329', '1989132998', '2686634456', '2761004936',
             '2681965956', '2739988567', '2624065058', '2587058292', '2101007226', '2667069886', '2222309442',
             '2623494760', '2740694950', '2708570975', '2539204758', '2758790542', '2237694006', '2746753146',
             '2766035761', '2753452981', '2747920412', '2117541291', '2677931630', '2598108903', '2605797338',
             '2720272394', '2600869963', '2677017720', '2613621399', '2762853944', '2744145960', '2598164434',
             '2562663177', '2698842428', '2745672602', '2650834293', '2720262800', '2628145052', '2713967535',
             '2728856804']
    res = fill_item_info(items)
    print(res)


def test2():
    items = [{'itemId': '2738806530'}]
    res = fill_item_info_dict(items)
    print(res)

#test()