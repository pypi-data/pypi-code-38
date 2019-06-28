# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/6/26
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.vbridge import voice_acr_bridge
from bayeslibs.config import const


class ApolloACRer:
    """
    语音识别模块封装类
    """

    def __init__(self):
        pass

    @staticmethod
    def open():
        return open_acr()

    @staticmethod
    def close():
        return close_acr()

    @staticmethod
    def status():
        return get_acr_status()


def open_acr():
    """
    开启机器人语音识别
    :param:
    :return:result
    :example:
        result = open_casr()
        ------
        result:{
            'status':0,
            'msg':'success',
            'text':'今天30度'
        }
    """
    result = voice_acr_bridge(req_type=const.TYPE_START)
    print('开始语音识别:{}'.format(result))
    return result


def close_acr():
    """
    关闭机器人语音识别
    :param
    :return:result
    :example:
        result = close_casr()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    result = voice_acr_bridge(req_type=const.TYPE_STOP)
    print('关闭语音识别:{}'.format(result))
    return result


def get_acr_status():
    """
    查询语音识别状态
    :param
    :return:result
    :example:
        result = get_casr_status()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    result = voice_acr_bridge(req_type=const.TYPE_QUERY)
    print('查询语音识别状态:{}'.format(result))
    return result
