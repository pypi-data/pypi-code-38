# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.ibridge import vision_skeleton_recog_bridge
from bayeslibs.config import const


class ApolloSkeletonRecognizer:
    """
    年龄性别识别模块封装类
    """
    def __init__(self):
        pass

    @staticmethod
    def open():
        return open_skeleton_recognizer()

    @staticmethod
    def close():
        return close_skeleton_recognizer()

    @staticmethod
    def get_face_recognized():
        return get_skeletons_recognized()


def open_skeleton_recognizer():
    """
    开启机器人年龄性别识别功能
    :param
    :return:result
    :example:
        result = open_skeleton_recognizer()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('开启机器人年龄性别识别功能')
    result = vision_skeleton_recog_bridge(req_type=const.TYPE_START)
    return result


def close_skeleton_recognizer():
    """
    关闭机器人年龄性别识别功能
    :param
    :return:result
    :example:
        result = close_skeleton_recognizer()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('关闭机器人年龄性别功能')
    result = vision_skeleton_recog_bridge(req_type=const.TYPE_STOP)
    return result


def get_skeletons_recognized():
    """
    查询机器人识别出的年龄性别信息
    :return:result
    :example:
        result = get_skeletons_recognized()
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
    result = vision_skeleton_recog_bridge(req_type=const.TYPE_QUERY)
    return result


if __name__ == '__main__':
    # open_skeleton_recognizer()
    close_skeleton_recognizer()
