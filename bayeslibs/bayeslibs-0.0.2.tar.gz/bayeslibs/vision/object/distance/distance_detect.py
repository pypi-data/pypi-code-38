# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/6/12
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.ibridge import vision_distance_detect_bridge
from bayeslibs.config import const


class ApolloDistanceDetector:
    """
    距离检测模块封装类
    """

    def __init__(self):
        pass

    @staticmethod
    def open(pos, is_show=True):
        return open_distance_detector(pos, is_show)

    @staticmethod
    def close():
        return close_distance_detector()

    @staticmethod
    def distance():
        return get_distance_detected()


def open_distance_detector(pos, is_show=True):
    """
    开启机器人距离检测功能
    :param
    :return:result
    :example:
        result = open_distance_detector()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('开启机器人距离检测功能')
    result = vision_distance_detect_bridge(req_type=const.TYPE_START, pos=pos, is_show=is_show)
    print(result)
    return result


def close_distance_detector():
    """
    关闭机器人距离检测功能
    :param
    :return:result
    :example:
        result = close_people_detector()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('关闭机器人距离检测功能')
    result = vision_distance_detect_bridge(req_type=const.TYPE_STOP)
    print(result)
    return result


def get_distance_detected():
    """
    查询机器人距离检测出的距离信息
    :return:result
    :example:
        result = get_distance_detected()
        ------
        result:{
            "status":0,
            "msg":"success",
            "distance": 2.3
        }
    """
    print('查询机器人距离检测出的距离信息')
    result = vision_distance_detect_bridge(req_type=const.TYPE_QUERY)
    return result
