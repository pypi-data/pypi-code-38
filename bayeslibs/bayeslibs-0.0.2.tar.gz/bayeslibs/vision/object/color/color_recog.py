# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/6/12
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.ibridge import vision_color_recog_bridge
from bayeslibs.config import const


class ApolloColorRecognizer:
    """
    颜色识别模块封装类
    """
    def __init__(self):
        pass

    @staticmethod
    def open():
        return open_color_recognizer()

    @staticmethod
    def close():
        return close_color_recognizer()

    @staticmethod
    def colors():
        return get_color_recognized()


def open_color_recognizer():
    """
    开启机器人颜色识别功能
    :param
    :return:result
    :example:
        result = open_face_recognizer()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('开启机器人颜色识别功能')
    result = vision_color_recog_bridge(req_type=const.TYPE_START)
    return result


def close_color_recognizer():
    """
    关闭机器人颜色识别功能
    :param
    :return:result
    :example:
        result = close_face_recognizer()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('关闭机器人颜色识别功能')
    result = vision_color_recog_bridge(req_type=const.TYPE_STOP)
    return result


def get_color_recognized():
    """
    查询机器人颜色识别出的颜色信息
    :return:result
    :example:
        result = get_faces_recognized()
        ------
        result:{
            'status':0,
            'msg':'success',
            'color':'blue'
        }
    """
    print('查询机器人颜色识别出的颜色信息')
    result = vision_color_recog_bridge(req_type=const.TYPE_QUERY)
    return result
