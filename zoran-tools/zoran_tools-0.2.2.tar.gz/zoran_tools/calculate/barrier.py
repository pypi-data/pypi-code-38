import math
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict


__all__ = ['Barrier', ]


class Barrier(object):
    """
    一个栅栏对象, 表示一组有序的点连成的圈圈
    """
    def __init__(self, points: List, meta: Dict = None):
        """
        :param points: 形如[(x, y), (x, y)...]的列表，列表中每个元素是一组经纬度对
        :param name: 栅栏的名称
        """
        self.meta = meta
        if points[0] != points[-1]:
            points.append(points[-1])
        self.points = [dict(x=point[0], y=point[1]) for point in points]

        self.maxx = max([p[0] for p in points])

        self.lines = [(s, e) for s, e in zip(self.points[:-1], self.points[1:])]
        self.xs = [point['x'] for point in self.points]
        self.ys = [point['y'] for point in self.points]

    @staticmethod
    def intersect(A, B, P, Q):
        """
         判断两条线段AB和PQ是否相交（接触默认为不是相交）
         :param A: dict, 线段AB的起点
         :param B: dict, 线段AB的终点
         :param P: dict, 目标点, 要判断其是否在网格中, PQ的起点
         :param Q: dict, 以P为起点, 水平作一条线段到网格边界(最大横坐标处), 终点为Q
         :return: 返回布尔值是或否
        """
        if (
                (A['y'] > P['y'] and B['y'] > P['y']) or  # AB两点都在PQ上侧
                (A['x'] < P['x'] and B['x'] < P['x']) or  # AB两点都在P左侧
                (A['y'] < P['y'] and B['y'] < P['y'])  # AB两个都在PQ下侧
        ):
            return False
        x = (P['y'] - A['y']) * (B['x'] - A['x']) / (B['y'] - A['y']) + A['x']
        if P['x'] < x <= Q['x']:  # 交点横坐标在PQ两之间
            print('有交点, 且交点在PQ之间', A, B)
            return True
        else:
            return False

    def point_in_net(self, P):
        """
        判断P点是否在self表示的栅栏中
        :param P: 要判断的点
        """
        Q = dict(x=self.maxx, y=P[1])
        P = dict(x=P[0], y=P[1])

        # 计算相交的次数, 如果点P在网格的线上, 认为点在网格内, 直接返回True
        count = 0
        for line in self.lines:
            A, B = line
            if Net.point_in_line(A, B, P):
                print('点在线上')
                return True
            if Net.intersect(A, B, P, Q):
                count += 1

        # 如果PQ与网格的点重合, 会算作相交两次, 所以重合了多少个点, 就要减去多少次
        for point in self.points:
            if point['y'] == P['y'] and (point['x'] - P['x']) * (point['x'] - Q['x']) <= 0:
                count -= 1
        if count % 2 == 1:
            return True
        else:
            return False

    @staticmethod
    def point_in_line(A, B, P):
        """
        判断P点是否在线段AB上
        """
        if A == P or B == P:
            return True
        if Net.slope(A, B) == Net.slope(A, P) and (A['x'] - P['x']) * (B['x'] - P['x']) <= 0:
            return True
        return False

    @staticmethod
    def slope(A, B):
        """
        计算线段AB的斜率
        """
        if A['x'] == B['x']:
            return None
        elif A['y'] == B['y']:
            return 0
        else:
            return (A['y'] - B['y']) / (A['x'] - B['x'])

    def plot(self, P):
        """
        绘图，绘制栅栏和P点
        """
        plt.plot(self.xs, self.ys, 'r-o')
        plt.plot([P[0], self.maxx], [P[1], P[1]])
        is_in = self.point_in_net(P)
        if is_in:
            plt.title("点在网格中", fontproperties='SimHei')
        else:
            plt.title("点不在网格中", fontproperties='SimHei')
        plt.show()
        return is_in


