#！/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/6/21 13:38
# @Author   : Run (18817363043@163.com)
# @File     : rings.py
# @Software : PyCharm

"""
【环线爬取】
城市环线坐标序列数据集及相关函数
本模块的实现基于高德地图的api
todo 1. 继续扩充坐标库  2. 将绘图操作移至RunEcharts

【Notes】
1. 自动化爬取并清洗坐标
    爬取：已完成，但有可能会爬取失败
    清洗：比较难以实现自动清洗，目前必须要肉眼辅助进行一些判断
2. 未实现第一条之前，需要不断更新该坐标库，向其中添加手工爬取清洗后的新的环线坐标
"""

import pandas as pd
import matplotlib.path as mplPath
import numpy as np
import h5py
import os
import codecs
import requests


CITY_RINGS_FILE_PATH = os.path.dirname(os.path.realpath(__file__))


def in_the_polygon(point, polygon):
    """
    判断一个点是否在多边形内
    利用matplotlib模块内的函数
    注意：当一个点位于边界线上时，返回False

    :param point: [x, y]
    :param polygon:
        多边形的平面坐标表示，e.g. [[-1, -1], [-1, 1], [1, 1], [1, -1], [-1, -1]]
        首尾的点可以不重合，没有影响，也即上述例子也可以传参为：[[-1, -1], [-1, 1], [1, 1], [1, -1]]
    :return: bool型

    """

    bbPath = mplPath.Path(np.array(polygon))
    return bbPath.contains_point(point)


def ring_directory(style=0):
    """
    展示库中目前含有哪些环线坐标

    :param style: 返回的结果类型
        0: （默认） list  e.g. [[city_name, ring_name, coords_type], ...]
        1: pd.DataFrame
    :return:
    """

    results_list = []

    file = h5py.File(os.path.join(CITY_RINGS_FILE_PATH, "city_rings/rings.hdf5"), "r")
    for city in file.keys():
        for ring in file[city].keys():
            for coord_type in file[city][ring].keys():
                results_list.append([city, ring, coord_type])
    file.close()

    if style == 0:
        return results_list
    elif style == 1:
        return pd.DataFrame(columns=['city', 'ring', 'coord_type'], data=results_list)
    else:
        raise Exception("Please input style correctly!")


def crawl_ring(city_name_cn, ring_name_cn):
    """
    按照crawl_city_ring_coords目录下crawl_city_ring_coords.ipynb中的思路编写了代码
    但由于可能搜索不到关键词、网页请求可能会出错等原因，不保证自动爬取一定一次成功（甚至始终不能成功），推荐手动进行爬取
    注意：事先一定要在高德地图里搜索环线名，以确定地图上的确可以显示该环线

    :param city_name: 城市的中文名，e.g. 北京
    :param ring_name_cn: 想要爬取的环线的中文名，e.g. 四环
    :return:
    """

    url1 = "http://restapi.amap.com/v3/config/district?key=e58bae199679e49544969133bc20896e" \
           "&keywords={0}&subdistrict=0&extensions=base".format(city_name_cn)
    try:
        adcode = requests.get(url1).json()['districts'][0]['adcode']
    except:
        raise Exception("获取城市编码失败")

    url2 = "https://www.amap.com/service/poiInfo?query_type=TQUERY&pagesize=1&pagenum=1&" \
           "qii=true&cluster_state=5&need_utd=true&utd_sceneid=1000&div=PC1000&addr_poi_merge=true&" \
           "is_classify=true&zoom=10.19&city={0}&keywords={1}".format(adcode, ring_name_cn)
    try:
        infos = requests.get(url2).json()['data']['poi_list'][0]
    except:
        raise Exception("搜索请求失败")

    if city_name_cn not in infos['cityname'] or ring_name_cn != infos['disp_name']:
        raise Exception("在该城市无法搜索到该环线信息")

    for temp in infos['domain_list']:
        if temp['name'] == 'roadaoi':
            coords_str = temp['value']
            return [[[float(y) for y in x.split(',')] for x in z.split('_')] for z in coords_str.split('|')]

    raise Exception("无该环线信息")


def load_ring(city_name, ring_name, coords_type):
    """
    载入环线数据
    目前库中所含的环线有
    shanghai   neihuan     gd/bd
    shanghai   zhonghuan   gd/bd
    shanghai   waihuan     gd/bd
    beijing    wuhuan      gd/bd

    :param city_name: 城市名称
    :param ring_name: 环线名称
    :param coords_type: 坐标系类型（gd/bd）
    :return:
    """

    rings = ring_directory()
    if [city_name, ring_name, coords_type] not in rings:
        print("Sorry, we don't have this ring's coords, please choose from below:")
        print(rings)
        return "doesn't exist"

    file = h5py.File(os.path.join(CITY_RINGS_FILE_PATH, "city_rings/rings.hdf5"), "r")
    coords_arr = file[city_name][ring_name][coords_type].value
    file.close()

    return coords_arr


def add_ring(city_name, ring_name, coords_type, coords):
    """
    向坐标库中添加新的环线坐标
    注意：一定要保证坐标的正确性（通过可视化展示以肉眼进行判断，待改进）

    :param city_name:
    :param ring_name:
    :param coords_type:
    :param coords:
    :return:
    """

    if [city_name, ring_name, coords_type] in ring_directory():
        print("Thanks for your contribution, but we already have this ring's coords.")
        return "already exist"

    file = h5py.File(os.path.join(CITY_RINGS_FILE_PATH, "city_rings/rings.hdf5"), "r+")
    if city_name not in file.keys():
        file.create_group('/{0}/{1}'.format(city_name, ring_name))
    else:
        if ring_name not in file[city_name].keys():
            file[city_name].create_group(ring_name)
    file[city_name][ring_name][coords_type] = np.array(coords)
    file.close()
    return "add successfully"


def write_utf8_html_file(file_name, html_content):
    """
    摘取自包pyecharts，在此致谢。

    :param file_name:
    :param html_content:
    :return:
    """

    with codecs.open(file_name, "w", encoding="utf-8") as f:
        f.write(html_content)


def gen_ring_html(file_name="ring.html", coords=[[]]):
    """
    生成环线在地图上的可视化静态网页，并以Chrome打开

    :param file_name:
    :param coords:
    :return:
    """
    coords = [list(x) for x in coords]
    a = coords[0]
    b = coords[len(coords) // 2]
    center = [round((a[0] + b[0]) / 2, 2), round((a[1] + b[1]) / 2, 2)]

    with codecs.open(os.path.join(CITY_RINGS_FILE_PATH, "html_templates/static_ring.html"), "r", "utf-8") as file:
        cont = file.read()
    cont = cont.replace("中心点坐标", str(center)).replace("多边形线条坐标", str(coords))
    write_utf8_html_file(file_name, cont)

    try:
        os.system("Chrome.exe {0}".format(file_name))
    except:
        pass


def gen_delay_display_html(file_name="delay_display.html", gap=10, coords=[[]]):
    """
    生成环线在地图上动态前行直至闭合的可视化网页，并以Chrome打开
    辅助判断爬取到的环线坐标是否正确，避免其中出现逆向反复的坐标

    :param file_name:
    :param gap: 间隔点数
    :param coords:
    :return:
    """

    coords = [list(x) for x in coords]
    a = coords[0]
    b = coords[len(coords) // 2]
    center = [round((a[0] + b[0]) / 2, 2), round((a[1] + b[1]) / 2, 2)]

    with codecs.open(os.path.join(CITY_RINGS_FILE_PATH, "html_templates/delay_display_ring.html"), "r", "utf-8") as file:
        cont = file.read()
    cont = cont.replace("中心点坐标", str(center)).replace("多边形线条坐标", str(coords)).replace("间隔点数", str(gap))
    write_utf8_html_file(file_name, cont)

    try:
        os.system("Chrome.exe {0}".format(file_name))
    except:
        pass


if __name__ == "__main__":

    coords_arr = load_ring("shanghai", "waihuan", "gd")
    print(len(coords_arr))

    coords = crawl_ring("北京", "四环")
    print(coords)
