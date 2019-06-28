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


def vision_object_detect_bridge(req_type, is_show=True):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type,
        'is_show': is_show
    }
    return Http.request_json(APOLLO_CONFIG.get_vision_object_detect_url(), request_json)


def vision_distance_detect_bridge(req_type, pos=None, is_show=True):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type,
        'is_show': is_show
    }
    if pos:
        request_json['pos'] = pos
    return Http.request_json(APOLLO_CONFIG.get_vision_distance_detect_url(), request_json)


def vision_color_recog_bridge(req_type, is_show=True):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type,
        'is_show': is_show
    }
    return Http.request_json(APOLLO_CONFIG.get_vision_color_recog_url(), request_json)


def vision_face_detect_bridge(req_type, is_show=True):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type,
        'is_show': is_show
    }
    return Http.request_json(APOLLO_CONFIG.get_vision_face_detect_url(), request_json)


def vision_face_recog_bridge(req_type, is_show=True):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type,
        'is_show': is_show
    }
    return Http.request_json(APOLLO_CONFIG.get_vision_face_recog_url(), request_json)


def vision_age_gender_recog_bridge(req_type, is_show=True):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type,
        'is_show': is_show
    }
    return Http.request_json(APOLLO_CONFIG.get_vision_age_gender_recog_url(), request_json)


def vision_emotion_recog_bridge(req_type, is_show=True):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type,
        'is_show': is_show
    }
    return Http.request_json(APOLLO_CONFIG.get_vision_emotion_recog_url(), request_json)


def vision_headpose_recog_bridge(req_type, is_show=True):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type,
        'is_show': is_show
    }
    return Http.request_json(APOLLO_CONFIG.get_vision_headpose_recog_url(), request_json)


def vision_beauty_recog_bridge(req_type, is_show=True):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type,
        'is_show': is_show
    }
    return Http.request_json(APOLLO_CONFIG.get_vision_beauty_recog_url(), request_json)


def vision_handpose_recog_bridge(req_type, is_show=True):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type,
        'is_show': is_show
    }
    return Http.request_json(APOLLO_CONFIG.get_vision_handpose_recog_url(), request_json)


def vision_skeleton_recog_bridge(req_type, is_show=True):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type,
        'is_show': is_show
    }
    return Http.request_json(APOLLO_CONFIG.get_vision_skeleton_recog_url(), request_json)
