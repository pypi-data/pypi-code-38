# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.vbridge import voice_wts_bridge
from bayeslibs.config import const


class ApolloWakeUper:
    """
    语音唤醒模块封装类
    """
    def __init__(self):
        pass

    @staticmethod
    def open(text):
        return open_wakeup(text)

    @staticmethod
    def close():
        return close_wakeup()

    @staticmethod
    def status():
        return get_wakeup_status()


def open_wakeup(text=''):
    """
    开启机器人语音唤醒
    :param:
    :return:result
    :example:
        result = open_wakeup()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('开始语音合成')
    result = voice_wts_bridge(req_type=const.TYPE_START, text=text)
    return result


def close_wakeup():
    """
    关闭机器人语音唤醒
    :param
    :return:result
    :example:
        result = close_wakeup()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    print('关闭语音合成')
    result = voice_wts_bridge(req_type=const.TYPE_STOP)
    return result


def get_wakeup_status():
    """
    查询机器人语音唤醒状态
    :param
    :return:result
    :example:
        result = get_wakeup_status()
        ------
        result:{
            'status':0,
            'msg':'success',
            'angle':120
        }
    """
    print('查询语音唤醒状态')
    result = voice_wts_bridge(req_type=const.TYPE_QUERY)
    return result
