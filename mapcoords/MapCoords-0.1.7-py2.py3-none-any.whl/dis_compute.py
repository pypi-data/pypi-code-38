# ！/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/6/18 18:37
# @Author   : Run (18817363043@163.com)
# @File     : dis_compute.py
# @Software : PyCharm

"""
【距离计算】
计算经纬度坐标间的球面大弧距离
1. 地球的模型有球体和椭球体两种，后者更精确。
2. 经纬度坐标系（GPS、GCJ、BD等），计算的应当是球面大弧距离；投影坐标系（墨卡托），计算的应当是欧式距离。
3. geopy模块中已有两点间球面大弧距离的计算函数，但是对两列点计算距离矩阵似乎并未提供较直接高效的方式，本模块以geopy中的函数来检验结果。
4. 本模块中球面大弧距离的计算，等同于geopy模块中使用同样的地球半径的球体模型，通过几组对照试验发现，其与椭球体模型相比，千米大概误差一米。
5. todo 关于效率，由于距离矩阵的计算是CPU密集型任务，所以采用多核的计算机多进程计算可能可以提速（尚未编写和测试，因为目前速度足够快了）
6. scipy.spatial.distance模块中的cdist函数实现了对多种类型距离的距离矩阵的计算，其中对欧氏距离的计算效率要高于我自己用numpy的实现；
   并且可以自定义距离函数，但是用这种方式来计算球面大弧距离效率超乎想象的低，我并没有等到结果计算出来。
   [scipy.spatial.distance.cdist文档](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cdist.html)
7. 在此致谢以上提到的两个模块geopy和scipy中相关函数的编写者。

Notes:
1. a = b = np.arange(10)
    1. a = a * 2  a更改，b不更改
    2. a *= 2  a和b同步更改
"""

from collections import Iterable
import numpy as np
from scipy.spatial.distance import cdist


DIS_COMPUTE_EARTH_RADIUS = 6372795  # 6371008.7


def _haver_sin(theta):
    """

    :param theta: 弧度，数据类型为float或np.ndarray
    :return:
    """
    return (np.sin(theta / 2)) ** 2


def compute_arc_dis(lgt1, lat1, lgt2, lat2, is_radian=False, earth_radius=DIS_COMPUTE_EARTH_RADIUS):
    """
    计算两（列）点间的球面大弧距离

    e.g.
        1. input: 第一个点：x1           第二个点：y1           output: dis(x1, y1)
        2. input: 第一批点：x1, x2, x3   第二个点：y1           output: dis(x1, y1), dis(x2, y1), dis(x3, y1)
        3. input: 第一批点：x1, x2, x3   第二批点：y1, y2, y3   output: dis(x1, y1), dis(x2, y2), dis(x3, y3)

    Notes:
        1. 测试时发现，在计算距离时由于使用的球体模型，本身估算就带有一定误差，因此对于坐标系并不敏感，只要不是投影坐标系，都可以用该公式来估算距离。
            当然最准确的应该还是WGS84坐标（也即GPS坐标）。

    References:
        1. https://www.cnblogs.com/softfair/p/distance_of_two_latitude_and_longitude_points.html
        2. https://en.wikipedia.org/wiki/Great-circle_distance

    :param lgt1: 点1的经度，数据类型为float或者可迭代对象（list\np.ndarray等）
    :param lat1: 点1的纬度
    :param lgt2: 点2的经度
    :param lat2: 点2的纬度
    :param is_radian: bool. 传入的坐标是否为弧度制，若是则为True，若为原始经纬度坐标则为False
    :param earth_radius: 地球半径（米）
    :return: distance: 距离（米）。传入两个点时返回值数据类型为float，传入两列点时返回值数据类型为np.ndarray
    """
    # format data
    if isinstance(lgt1, Iterable):
        lgt1 = np.asarray(lgt1)
        lat1 = np.asarray(lat1)
    if isinstance(lgt2, Iterable):
        lgt2 = np.asarray(lgt2)
        lat2 = np.asarray(lat2)

    # angle -> radian
    if not is_radian:
        lgt1 = lgt1 * np.pi / 180
        lat1 = lat1 * np.pi / 180
        lgt2 = lgt2 * np.pi / 180
        lat2 = lat2 * np.pi / 180

    h = _haver_sin(lat2 - lat1) + np.cos(lat1) * np.cos(lat2) * _haver_sin(lgt2 - lgt1)
    distance = 2 * earth_radius * np.arcsin(np.sqrt(h))

    return distance


def compute_arc_dis_matrix(lgts1, lats1, lgts2, lats2, is_radian=False):
    """
    计算两列点之间的球面大弧距离矩阵

    e.g. input: points1: x1, x2, x3   points2: y1, y2
         output: np.array([[dis(x1, y1), dis(x1, y2)],
                           [dis(x2, y1), dis(x2, y2)],
                           [dis(x3, y1), dis(x3, y2)]])
    效率测试：21763*21763 cost 24s
    :param lgts1: 第一批点的经度，可迭代对象（list\np.ndarray等）
    :param lats1: 第一批点的纬度
    :param lgts2: 第二批点的经度
    :param lats2: 第二批点的纬度
    :param is_radian: bool. 传入的坐标是否为弧度制，若是则为True，若为原始经纬度坐标则为False
    :return: 距离矩阵（米）. np.ndarray
    """
    # format data
    lgts1 = np.asarray(lgts1)
    lats1 = np.asarray(lats1)
    lgts2 = np.asarray(lgts2)
    lats2 = np.asarray(lats2)

    # angle -> radian
    if not is_radian:
        lgts1 = lgts1 * np.pi / 180
        lats1 = lats1 * np.pi / 180
        lgts2 = lgts2 * np.pi / 180
        lats2 = lats2 * np.pi / 180

    dist_m = np.zeros((len(lgts1), len(lgts2)))
    for i in range(len(lgts2)):
        dist_m[:, i] = compute_arc_dis(lgts1, lats1, lgts2[i], lats2[i], True)

    return dist_m


def compute_arc_dis_matrix_symmetric(lgts, lats, is_radian=False):
    """
    计算同一列点之间的球面大弧距离矩阵
    只计算对角线以上部分，同时赋值给对称的区域，缩减了一半时间左右。
    效率测试：21763*21763 cost 12s
    注意：不要使用numpy的转置和求和来得到对称阵，numpy的矩阵运算效率超乎想象的低。
    :param lgts: 可迭代对象（list\np.ndarray等）
    :param lats:
    :param is_radian: bool. 传入的坐标是否为弧度制，若是则为True，若为原始经纬度坐标则为False
    :return:
    """
    # format data
    lgts = np.asarray(lgts)
    lats = np.asarray(lats)

    # angle -> radian
    if not is_radian:
        lgts = lgts * np.pi / 180
        lats = lats * np.pi / 180

    l = len(lgts)
    dist_m = np.zeros((l, l))
    for i in range(1, l):
        dist_m[i, : i] = dist_m[: i, i] = compute_arc_dis(lgts[: i], lats[: i], lgts[i], lats[i], True)
    # dist_m += dist_m.T  # 矩阵运算耗时超乎想象

    return dist_m


def compute_line_dis_matrix(points1, points2):
    """
    计算两组点间的平面欧氏距离矩阵
    直接调用了scipy.spatial.distance中的函数cdist，该函数功能强大，通过传入参数metric，可以计算多种不同距离，如曼哈顿距离等等。
    :param points1: 平面上一组点的坐标。注意：如果只有一个点，也要以类似[[x, y]]或[(x,y)]或np.array([[x, y]])的方式传入
    :param points2:
    :return:
    """
    return cdist(points1, points2)


def _compute_line_dis_matrix_not_recommended(lgts1, lats1, lgts2, lats2):
    """
    根据投影坐标系的坐标来计算平面上的欧氏距离，效率低于scipy中已有的实现
    注意：不推荐使用！
    :param lgt1:
    :param lat1:
    :param lgt2:
    :param lat2:
    :return:
    """
    distance_matrix = np.zeros((len(lgts1), len(lgts2)))
    for i in range(len(lgts2)):
        distance_matrix[:, i] = np.sqrt((lgts1 - lgts2[i]) ** 2 + (lats1 - lats2[i]) ** 2)

    return distance_matrix


if __name__ == "__main__":
    from geopy.distance import vincenty, great_circle
    import time
    import gc

    # 国内较远两点坐标
    tiananmen = (39.9073285, 116.391242416486)  # 注意纬度在前，经度在后
    xiaozhai = (34.2253171, 108.9426205)
    # 国内较近两点坐标
    shanghai1 = (31.298877, 121.506998)
    shanghai2 = (31.306607, 121.500808)
    # 国外两点坐标
    newport_ri = (41.49008, -71.312796)
    cleveland_oh = (41.499498, -81.695391)

    print("国内较远两点坐标 球面大弧距离计算")
    print("[compute_arc_dis 球体 R=6372795m]", compute_arc_dis(tiananmen[1], tiananmen[0], xiaozhai[1], xiaozhai[0]))
    print("[geopy 球体 R=6372.795km]", great_circle(tiananmen, xiaozhai).meters)
    print("[geopy 球体 R=6371.0087km]", great_circle(tiananmen, xiaozhai, radius=6371.0087).meters)
    print("[geopy 椭球体 坐标系: WGS-84]", vincenty(tiananmen, xiaozhai, ellipsoid="WGS-84").meters)
    print("[geopy 椭球体 坐标系: GRS-80]", vincenty(tiananmen, xiaozhai, ellipsoid="GRS-80").meters)
    print()

    print("国内较近两点坐标 球面大弧距离计算")
    print("[compute_arc_dis 球体 R=6372795m]", compute_arc_dis(shanghai1[1], shanghai1[0], shanghai2[1], shanghai2[0]))
    print("[geopy 球体 R=6372.795km]", great_circle(shanghai1, shanghai2).meters)
    print("[geopy 球体 R=6371.0087km]", great_circle(shanghai1, shanghai2, radius=6371.0087).meters)
    print("[geopy 椭球体 坐标系: WGS-84]", vincenty(shanghai1, shanghai2, ellipsoid="WGS-84").meters)
    print("[geopy 椭球体 坐标系: GRS-80]", vincenty(shanghai1, shanghai2, ellipsoid="GRS-80").meters)
    print()

    print("国外两点坐标 球面大弧距离计算")
    print("[compute_arc_dis 球体 R=6372795m]",
          compute_arc_dis(newport_ri[1], newport_ri[0], cleveland_oh[1], cleveland_oh[0]))
    print("[geopy 球体 R=6372.795km]", great_circle(newport_ri, cleveland_oh).meters)
    print("[geopy 球体 R=6371.0087km]", great_circle(newport_ri, cleveland_oh, radius=6371.0087).meters)
    print("[geopy 椭球体 坐标系: WGS-84]", vincenty(newport_ri, cleveland_oh, ellipsoid="WGS-84").meters)
    print("[geopy 椭球体 坐标系: GRS-80]", vincenty(newport_ri, cleveland_oh, ellipsoid="GRS-80").meters)
    print()

    print("球面大弧距离 对称阵 效率对比")
    file = np.load('data_demo/coords.npz')
    lgts = file['lgts']
    lats = file['lats']
    time1 = time.time()
    results1 = compute_arc_dis_matrix(lgts, lats, lgts, lats)
    print("{0}*{1} style1:".format(len(lgts), len(lgts)), time.time() - time1)
    # 注意：这里一定要用copy()，否则尽管del掉了变量results1指向其内存空间，但是results1_sample仍然指向那一块内存空间，gc.collect()强制垃圾回收无效
    results1_sample = results1[: 100, : 100].copy()
    del results1
    gc.collect()
    time1 = time.time()
    results2 = compute_arc_dis_matrix_symmetric(lgts, lats)
    # 当内存中有大量垃圾存在以至于内存不够用时，python会自动进行垃圾回收来管理内存，仍然不够时会报错memory error，在进行垃圾回收时python并不能同时进行其他运算，所以会耗费额外的时间
    print("{0}*{1} style2:".format(len(lgts), len(lgts)), time.time() - time1)
    results2_sample = results2[: 100, : 100].copy()
    del results2
    gc.collect()
    if results1_sample.tolist() == results2_sample.tolist():
        print("results equal.")
    else:
        print("results doesn't equal!")
    print()

    print("平面欧氏距离 效率对比")
    points = list(zip(lgts, lats))
    time1 = time.time()
    results1 = compute_line_dis_matrix(points, points)
    print("{0}*{1} style1:".format(len(lgts), len(lgts)), time.time() - time1)
    results1_sample = results1[: 100, : 100].copy()
    del results1
    gc.collect()
    time1 = time.time()
    results2 = _compute_line_dis_matrix_not_recommended(lgts, lats, lgts, lats)
    print("{0}*{1} style2:".format(len(lgts), len(lgts)), time.time() - time1)
    results2_sample = results2[: 100, : 100].copy()
    del results2
    gc.collect()
    if (results1_sample == results2_sample).all():
        print("results equal.")
    else:
        print("results doesn't equal!")
