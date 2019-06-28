# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.utils.bridge.vbridge import voice_tts_bridge
from bayeslibs.config import const


class ApolloSpeaker:
    """
    语音合成模块封装类
    """
    def __init__(self):
        pass

    @staticmethod
    def stop():
        return stop_speak()

    @staticmethod
    def speak(text):
        return start_speak(text)

    @staticmethod
    def status():
        return get_speak_status()


def stop_speak():
    """
    关闭机器人语音合成
    :param
    :return:result
    :example:
        result = close_speaker()
        print('result:', result)
        ------
        result:True
    """
    print('关闭语音合成')
    result = voice_tts_bridge(req_type=const.TYPE_STOP)
    return result


def start_speak(text):
    """
    机器人播放具体文本语音
    :param text
    :return:result
    :example:
        result = start_speak('今天心情很好')
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    result = voice_tts_bridge(req_type=const.TYPE_START, text=text)
    if result and result['status'] == 0:
        print('播放文本数据:{}'.format(text))
    else:
        print('播放文本数据:{}'.format('连接失败'))
    return result


def get_speak_status():
    """
    查询机器人语音播放状态
    :param
    :return:result
    :example:
        result = get_speak_status()
        ------
        result:{
            'status':0,
            'msg':'success'
        }
    """
    result = voice_tts_bridge(req_type=const.TYPE_QUERY)
    print('查询机器人语音播放状态:{}'.format(result))
    return result
