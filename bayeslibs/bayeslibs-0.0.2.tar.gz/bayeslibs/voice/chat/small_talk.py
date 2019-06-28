# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.vbridge import voice_chat_bridge
from bayeslibs.config import const


class ApolloChatter:
    """
    语音闲聊模块封装类
    """
    def __init__(self):
        pass

    @staticmethod
    def start(text):
        return start_small_talk(text)

    @staticmethod
    def stop():
        return stop_small_talk()


def start_small_talk(text):
    """
    开启机器人语音闲聊
    :param:
    :return:result
    :example:
        result = start_small_talk('你好帅')
        ------
        result:{
            'status':0,
            'msg':'success',
            'answer':'你才帅了'
        }
    """
    print('聊天问题:{}'.format(text))
    result = voice_chat_bridge(req_type=const.TYPE_START, text=text)
    print('聊天回复:{}'.format(result))
    return result


def stop_small_talk():
    """
    关闭机器人语音闲聊
    :param
    :return:result
    :example:
        result = stop_small_talk()
        ------
        result:True
    """
    print('关闭语音闲聊')
    result = voice_chat_bridge(req_type=const.TYPE_STOP)
    return result
