# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.ibridge import vision_headpose_recog_bridge
from bayeslibs.config import const


class ApolloHeadPoseRecognizer:
    """
    头部姿态识别模块封装类
    """
    def __init__(self):
        pass

    @staticmethod
    def open():
        return open_headpose_recognizer()

    @staticmethod
    def close():
        return close_headpose_recognizer()

    @staticmethod
    def headposes():
        return get_headpose_recognized()


def open_headpose_recognizer():
    """
    开启机器人头部姿态识别功能
    :param
    :return:result
    :example:
        result = open_headpose_recognizer()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('开启机器人头部姿态识别功能')
    result = vision_headpose_recog_bridge(req_type=const.TYPE_START)
    return result


def close_headpose_recognizer():
    """
    关闭机器人头部姿态识别功能
    :param
    :return:result
    :example:
        result = close_headpose_recognizer()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('关闭机器人头部姿态识别功能')
    result = vision_headpose_recog_bridge(req_type=const.TYPE_STOP)
    return result


def get_headpose_recognized():
    """
    查询机器人头部姿态识别出的头部姿态信息
    :return:result
    :example:
        result = get_headpose_recognized()
        ------
        result:{
            "status":0,
            "msg":"success",
            "data":[
                 {
                    "yaw":-10,
                    "pitch":25,
                    "roll":23,
                    "width":63,
                    "height":223,
                    "top":12,
                    "left":33
                 },
                 ...
            ]
        }
    """
    print('查询机器人头部姿态识别出的头部姿态信息')
    result = vision_headpose_recog_bridge(req_type=const.TYPE_QUERY)
    return result
