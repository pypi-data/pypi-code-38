# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/6/12
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.ibridge import vision_object_detect_bridge
from bayeslibs.config import const


class ApolloObjectDetector:
    """
    物体检测模块封装类
    """

    def __init__(self):
        pass

    @staticmethod
    def open():
        return open_object_detector()

    @staticmethod
    def close():
        return close_object_detector()

    @staticmethod
    def objects():
        return get_objects_detected()


def open_object_detector():
    """
    开启机器人物体检测功能
    :param
    :return:result
    :example:
        result = open_object_detector()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('开启机器人物体检测功能')
    result = vision_object_detect_bridge(req_type=const.TYPE_START)
    print(result)
    return result


def close_object_detector():
    """
    关闭机器人物体检测功能
    :param
    :return:result
    :example:
        result = close_object_detector()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('关闭机器人物体检测功能')
    result = vision_object_detect_bridge(req_type=const.TYPE_STOP)
    print(result)
    return result


def get_objects_detected():
    """
    查询机器人物体检测出的物体信息
    :return:result
    :example:
        result = get_objects_detected()
        ------
        result:{
            "status":0,
            "msg":"success",
            "data":[
                 {
                   "object_name":'person',
                   "probability":'1',
                   "width":123,
                   "height":223,
                   "top":12,
                   "left":33
                 },
                 {
                   "object_name":'bottle',
                   "probability":'1',
                   "width":53,
                   "height":63,
                   "top":122,
                   "left":133
                 },
                 ...
            ]
        }
    """
    print('查询机器人物体检测出的物体信息')
    result = vision_object_detect_bridge(req_type=const.TYPE_QUERY)
    return result
