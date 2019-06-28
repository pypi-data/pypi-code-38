# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.ibridge import vision_emotion_recog_bridge
from bayeslibs.config import const


class ApolloEmotionRecognizer:
    """
    表情识别模块封装类
    """
    def __init__(self):
        pass

    @staticmethod
    def open():
        return open_emotion_recognizer()

    @staticmethod
    def close():
        return close_emotion_recognizer()

    @staticmethod
    def emotions():
        return get_emotions_recognized()


def open_emotion_recognizer():
    """
    开启机器人表情识别功能
    :param
    :return:result
    :example:
        result = open_emotion_recognizer()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('开启机器人表情识别功能')
    result = vision_emotion_recog_bridge(req_type=const.TYPE_START)
    return result


def close_emotion_recognizer():
    """
    关闭机器人表情识别功能
    :param
    :return:result
    :example:
        result = close_emotion_recognizer()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('关闭机器人表情识别功能')
    result = vision_emotion_recog_bridge(req_type=const.TYPE_STOP)
    return result


def get_emotions_recognized():
    """
    查询机器人表情识别出的人脸信息
    :return:result
    :example:
        result = get_emotions_recognized()
        ------
        result:{
            "status":0,
            "msg":"success",
            "data":[
                 {
                    "emotion":"happy",
                    "score":88,
                    "width":123,
                    "height":223,
                    "top":12,
                    "left":33
                 },
                 ...
            ]
        }
    """
    print('查询机器人表情识别出的人脸信息')
    result = vision_emotion_recog_bridge(req_type=const.TYPE_QUERY)
    return result
