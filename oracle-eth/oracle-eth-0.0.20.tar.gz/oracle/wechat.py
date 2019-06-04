#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
# Author: yuyongpeng@hotmail.com
# Description: 微信相关的函数
#  

"""

from oracle.setting import VAR

from wechatpy import WeChatClient
from redis import Redis
from wechatpy.session.redisstorage import RedisStorage
from wechatpy.exceptions import WeChatClientException


def get_client():
    redis_client = Redis.from_url('redis://'.join([VAR['REDIS_IP'], ':', VAR['REDIS_PORT'], '/', VAR['REDIS_DATABASE']]))
    session_interface = RedisStorage(
        redis_client,
        prefix="wechatpy"
    )
    wechat_client = WeChatClient(
        VAR['WECHAT_APPID'],
        VAR['WECHAT_SECRET'],
        session=session_interface
    )
    return wechat_client


def send_msg(weixin_openid, msg):
    """
    给订阅了公众号的用户发送信息
    :param weixin_openid: 已经订阅了公众号的用户  OpenID
    :param msg: 要发送的信息
    :return:
    """
    wechat_client = get_client()
    # print(wechat_client.access_token)
    wechat_client.message.send_text(weixin_openid, msg)


def is_user(user_id):
    """
    查询这个用户是否订阅的公众号
    :param user_id: 已经订阅了公众号的用户  OpenID
    :return: 所有分组列表或用户所在分组 ID
    """
    wechat_client = get_client()
    try:
        wechat_client.user.get(user_id)
    except WeChatClientException as e:
        if '40003' == e.errcode:
            return False
    else:
        return True














