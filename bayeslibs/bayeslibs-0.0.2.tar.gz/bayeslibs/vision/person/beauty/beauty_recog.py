# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.ibridge import vision_beauty_recog_bridge
from bayeslibs.config import const


class ApolloBeautyRecognizer:
    """
    年龄性别识别模块封装类
    """
    def __init__(self):
        pass

    @staticmethod
    def open():
        return open_beauty_recognizer()

    @staticmethod
    def close():
        return close_beauty_recognizer()

    @staticmethod
    def beauties():
        return get_beauties_recognized()


def open_beauty_recognizer(is_show=True):
    """
    开启机器人年龄性别识别功能
    :param
    :return:result
    :example:
        result = open_beauty_recognizer()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('开启机器人年龄性别识别功能')
    result = vision_beauty_recog_bridge(req_type=const.TYPE_START, is_show=is_show)
    return result


def close_beauty_recognizer():
    """
    关闭机器人年龄性别识别功能
    :param
    :return:result
    :example:
        result = close_beauty_recognizer()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('关闭机器人年龄性别功能')
    result = vision_beauty_recog_bridge(req_type=const.TYPE_STOP)
    return result


def get_beauties_recognized():
    """
    查询机器人识别出的年龄性别信息
    :return:result
    :example:
        result = get_beauties_recognized()
        ------
        result:{
            "status":0,
            "msg":"success",
            "data":[
                 {
                    "gender":"male",
                    "gender_confidence":0.98,
                    "age": 27,
                    "width":123,
                    "height":223,
                    "top":12,
                    "left":33
                 },
                 ...
            ]
        }
    """
    print('查询机器人年龄性别出的年龄性别信息')
    result = vision_beauty_recog_bridge(req_type=const.TYPE_QUERY)
    return result


if __name__ == '__main__':
    # open_beauty_recognizer(True)
    close_beauty_recognizer()
