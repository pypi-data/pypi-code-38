# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from bayeslibs.config.setting import ApolloConfig
from bayeslibs.utils.comm.http import Http

APOLLO_CONFIG = ApolloConfig()


def voice_wts_bridge(req_type, text=None):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type,
        'text': text
    }
    return Http.request_json(APOLLO_CONFIG.get_voice_wts_url(), request_json)


def voice_tts_bridge(req_type, text=None):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type
    }
    if text:
        request_json['text'] = text
    return Http.request_json(APOLLO_CONFIG.get_voice_tts_url(), request_json)


def voice_asr_bridge(req_type):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type
    }
    return Http.request_json(APOLLO_CONFIG.get_voice_asr_url(), request_json)


def voice_acr_bridge(req_type):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type
    }
    return Http.request_json(APOLLO_CONFIG.get_voice_acr_url(), request_json)


def voice_chat_bridge(req_type, text=None):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type
    }
    if text:
        request_json['text'] = text
    return Http.request_json(APOLLO_CONFIG.get_voice_chat_url(), request_json)


def voice_music_bridge(req_type, text=None):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type
    }
    if text:
        request_json['text'] = text
    return Http.request_json(APOLLO_CONFIG.get_voice_music_url(), request_json)
