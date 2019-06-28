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


def motion_map_bridge(req_type, data=None):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type
    }
    if data:
        request_json['data'] = data
    return Http.request_json(APOLLO_CONFIG.get_motion_map_url(), request_json)


def motion_move_bridge(req_type, data=None):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type
    }
    if data:
        request_json['data'] = data
    return Http.request_json(APOLLO_CONFIG.get_motion_move_url(), request_json)


def motion_rotate_bridge(req_type, data=None):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type
    }
    if data:
        request_json['data'] = data
    return Http.request_json(APOLLO_CONFIG.get_motion_rotate_url(), request_json)


def motion_navigate_bridge(req_type, data=None):
    request_json = {
        'uuid': APOLLO_CONFIG.get_uid(),
        'type': req_type
    }
    if data:
        request_json['data'] = data
    return Http.request_json(APOLLO_CONFIG.get_motion_nav_url(), request_json)
