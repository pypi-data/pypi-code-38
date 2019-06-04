#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
# Author: yuyongpeng@hotmail.com
# Description:
#  

"""

# cp_army 数据库表的状态
EVENT_NORMAL = 0                        # 初始状态
EVENT_SIGN_VERI_FAILED = 1              # 签名验证失败
EVENT_SIGN_VERI_SUCCESS = 2             # 签名验证成功
EVENT_DECRYPTION_FAILED = 3             # 密文解密失败
EVENT_DECRYPTION_SUCCESS = 4            # 密文解密成功
EVENT_ETHEREUM_SUBMIT_FAILED = 5        # 发送到以太坊失败
EVENT_ETHEREUM_SUBMIT_SUCCESS = 6       # 发送到以太坊成功
EVENT_ETHEREUM_SOLDIER_NOTEXIST = 7     # 士兵不存在
EVENT_VERI_COMP = 8                     # 数据验证完成（到这一步就可以进行上链操作了）

# cp_organization 表的状态
ORG_NORMAL = 0                          # 初始状态
ORG_FIRST_SIGN_VERI_FAILED = 1          # 验证第一个签名失败
ORG_FIRST_SIGN_VERI_SUCCESS = 2         # 验证第一个签名成功
ORG_SECOND_SIGN_VERI_FAILED = 3         # 验证第二个签名失败
ORG_SECOND_SIGN_VERI_SUCCESS = 4        # 验证第二个签名成功
ORG_SEND_WECHAT_SUCCESS = 5             # 微信消息发送成功
ORG_SEND_WECHAT_FAILED = 6              # 微信消息发送失败

# person_dc 表的状态
DC_NORMAL = 0                           # 初始状态
DC_UP_CHAIN_TIMEOUT = 1                 # 上链超时
DC_UP_CHAIN_FAILED = 2                  # 上链失败
DC_UP_CHAIN_SUCCESS = 3                 # 上链成功



