# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:speech to text
"""
from bayeslibs.utils.bridge.vbridge import voice_asr_bridge
from bayeslibs.config import const


class ApolloASRer:
    """
    语音识别模块封装类
    """

    def __init__(self):
        pass

    @staticmethod
    def start():
        return open_asr()

    @staticmethod
    def stop():
        return close_asr()

    @staticmethod
    def status():
        return get_asr_status()


def open_asr():
    """
    开启机器人语音识别
    :param:
    :return:result
    :example:
        result = open_asr()
        ------
        result:{
            'status':0,
            'msg':'success',
            'text':'今天30度'
        }
    """
    result = voice_asr_bridge(req_type=const.TYPE_START)
    print('开始语音识别:{}'.format(result))
    return result


def close_asr():
    """
    关闭机器人语音识别
    :param
    :return:result
    :example:
        result = close_asr()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    result = voice_asr_bridge(req_type=const.TYPE_STOP)
    print('关闭语音识别:{}'.format(result))
    return result


def get_asr_status():
    """
    查询语音识别状态
    :param
    :return:result
    :example:
        result = get_asr_status()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    result = voice_asr_bridge(req_type=const.TYPE_QUERY)
    print('查询语音识别状态:{}'.format(result))
    return result
