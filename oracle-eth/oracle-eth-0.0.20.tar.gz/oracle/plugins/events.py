#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
Author:       yuyongpeng@hotmail.com
Github:       https://github.com/yuyongpeng/
Date:         2019-04-17 17:25:06
LastEditors:  
LastEditTime: 2019-04-17 17:25:06
Description:  
"""

import json
from oracle.plugins import Processor
from oracle.database import dbs
from oracle.database import status
from oracle.dids import Did
from oracle.setting import VAR
from oracle.logger import logger
from oracle.database.modles import Army, Organization
from pycontractsdk import keys
from oracle import wechat
from pycontractsdk.contracts import Contract
from oracle.queues import Rabbitmq
from oracle.setting import VAR

@Processor.plugin_register('DIDAttributeChange')
class DIDAttributeChangeEvent(object):
    """
    处理 event = DIDAttributeChange 的数据  army
    """
    def __init__(self):
        pass

    def process(self, entry):
        """
        处理 event=DIDAttributeChange 的函数
        :param entry: 获得的event数据
        :return:
        """
        args = entry['args']
        name = args['name'].strip(b'\x00')
        name = name.decode('utf8')
        # 所有已经注册的插件 都运行
        processor = Processor()
        processor.process_identity(event='DIDAttributeChange' ,identity=name, entry=entry)


@Processor.plugin_register('DIDAttributeConfirmed')
class DIDAttributeConfirmedEvent(object):
    """
    处理 event = DIDAttributeConfirmed 的数据    org
    """
    def __init__(self):
        pass

    def did_attribute_confirmed(self, contract, entry, *args, **kwargs):
        """
        处理 event=DIDAttributeConfirmed 的函数
        验证 机构 上链的数据
        确认军人的身份之后，进行上链操作，告诉大家他是一个军人

        获得的event数据，比 DIDAttributeChange 多了一个签名
        AttributeDict(
        {'args': AttributeDict(
          {
            'identity': '0xB2be7c8722935DB16921D64Ad0dDB5D47A52482a',
            'name': b'\xe5\xa3\xab\xe5\x85\xb5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
            'value': b'{"@context":"https://w3id.org/did/v1","id":"did:ethr:B2be7c8722935DB16921D64Ad0dDB5D47A52482a#soldier",
                        "publicKey":[{"id":"did:ethr:B2be7c8722935DB16921D64Ad0dDB5D47A52482a##proof",
                                      "type":"EciesVerificationKey",
                                      "controller":"did:ethr:B2be7c8722935DB16921D64Ad0dDB5D47A52482a",
                                      "publicKeyHex":"0x04521fbe1f862845cb09ca6c0cdff00417d4a3bf3c04748806eb49079f5d2d5d555c6461ecc3760bd10de1bc7c77421f02bbe3642d6d3e35ee219f84a026478297"}],
                        "authentication":[{"id":"did:ethr:DeCD6626f23bc43cB4D738cB0F2Dde922D691fD2#proof",
                                            "type":"EciesVerificationKey",
                                            "controller":"did:ethr:DeCD6626f23bc43cB4D738cB0F2Dde922D691fD2",
                                            "publicKeyHex":"0x024af3c4d907a75e9349f362b0f854c7d74a89dad457df4f9cbf3c4f9e2f7fbcf8"}],
                        "proof":"6617fd92f9f8b9b930ff051f6c02ece8d27cf0b2912361093ce38e521bc3c4846885eec37fefdbb06ebc699fcaeb4136",
                        "created":1554184638038}
                        \n
                        04a469fb703b394646a995e6681771967beea3f1ca8fe7b370555e4c5a6dca5b071ea5d9bbec76e3b1058b54894ddff9f9d346934f74a511d17bf56e6cb892fa01
                        \n
                        04a469fb703b394646a995e6681771967beea3f1ca8fe7b370555e4c5a6dca5b071ea5d9bbec76e3b1058b54894ddff9f9d346934f74a511d17bf56e6cb892fa01
                        '
          }
        ),
        'event': 'DIDAttributeConfirmed',
        'logIndex': 0,
        'transactionIndex': 0,
        'transactionHash': HexBytes('0xe453910d44ad566093d33593f6411fd73126564617bd1529fedce6fe42be0fa7'),
        'address': '0x5c12AED6613AaD77eC2e84e5cedd9b6Ff29A6e6A',
        'blockHash': HexBytes('0x0c602e8ad51cb5a49ab4952181a252f0bf6f55c9f3fc0cbaa043a9f2b8e5814e'),
        'blockNumber': 293710}
        )

        :param contract: pycontractsdk中的针对 `Contract` 协约的处理对象
        :param entry: 以太坊获得的event数据
                    event DIDAttributeConfirmed(address indexed identity, bytes32 name, bytes value) 函数的参数
        :return:
        """
        # XXX: 需要确认是否会抛异常
        army_private_key = kwargs['army_private_key']           # 军队账号的私钥
        private_key = kwargs['private_key']   # 管理者的私钥
        # operator_private_key = kwargs['operator_private_key']   # 管理者的私钥
        # delegate_private_key = kwargs['delegate_private_key']   # 代理上链者的私钥

        # 数据存到数据库中
        event = dbs.save_organization(entry)
        id = event.id
        args = entry['args']
        identity = args['identity']                         # identity
        name = args['name'].strip(b'\x00')                  # 身份信息描述，比如"士兵"
        value = args['value']                               # did和签名信息
        first_sign_text_bytes = value.split(b'\n')[-2]      # 第一个 签名信息
        second_sign_text_bytes = value.split(b'\n')[-1]     # 第二个 签名信息
        did_json_bytes = b''.join(value.split(b'\n')[:-2])  # did 信息
        did_json_obj = json.loads(did_json_bytes.decode())  # did json对象

        # 验证 did 的签名是否正确 first_sign
        # 第一个签名是用户发起的。必须确认。did['publicKey'][0]['publicKeyHex']
        if not Did.verify_did(did_json_bytes.decode(), first_sign_text_bytes.decode()):
            logger.error('*******************************************************')
            logger.error('* First signature verification error !')
            logger.error('* did: {}'.format(did_json_bytes.decode()))
            logger.error('* sign_text: {}'.format(first_sign_text_bytes.decode()))
            logger.error('*******************************************************')
            # 需要修改数据库的状态为 "验证第一个签名失败"
            Organization.update(status=status.ORG_FIRST_SIGN_VERI_FAILED).where(Organization.id == id).execute()
            return
        # 需要修改数据库的状态为 "验证第一个签名成功"
        Organization.update(status=status.ORG_FIRST_SIGN_VERI_SUCCESS).where(Organization.id == id).execute()

        # 验证 (did + first_sign) 的签名是否正确 second_sign
        # 第二个签名是军队发起的。必须确认。did['authentication'][0]['publicKeyHex']
        message = b'\n'.join(value.split(b'\n')[:-1]).decode()
        # army_public_key = '0x044af3c4d907a75e9349f362b0f854c7d74a89dad457df4f9cbf3c4f9e2f7fbcf8916ac219bb70e64777930b1e85d0a550e1e61ca94fa902dee419849a9a0efe8a'
        try:
            tf = keys.ecdsa_verify(message, signature=second_sign_text_bytes.decode(),
                               public_key=did_json_obj['authentication'][0]['publicKeyHex'])
                                # public_key=army_public_key)
        except Exception as e:
            logger.error(e)
            tf = False
        #
        notice_msg_body = {"type": "validate", "id": did_json_obj['id']}
        rabbitmq = Rabbitmq(VAR['QUEUE_NAME_NOTICE'], VAR['QUEUE_IP'], VAR['QUEUE_PORT'], VAR['QUEUE_USER'], VAR['QUEUE_PASSWORD'], VAR['QUEUE_VHOST'])

        if tf is False:
            logger.error('*******************************************************')
            logger.error('* second signature verification error !')
            logger.error('* did+first_sign: {}'.format(message))
            logger.error('* sign_text: {}'.format(second_sign_text_bytes.decode()))
            logger.error('*******************************************************')
            # 需要修改数据库的状态为 "验证第二个签名失败"
            Organization.update(status=status.ORG_SECOND_SIGN_VERI_FAILED).where(Organization.id == id).execute()
            notice_msg_body['status'] = False
        else:
            pass
            # 需要修改数据库的状态为 "验证第二个签名成功"
            Organization.update(status=status.ORG_SECOND_SIGN_VERI_SUCCESS).where(Organization.id == id).execute()

            # 保存验证通过的数据到最终表中，以最后一次的数据为准
            dbs.save_organization_did(entry)

            # 发送通知信息到队列中，告诉客户端验证成功
            notice_msg_body['status'] = True

        rabbitmq.send_msg(json.dumps(notice_msg_body))

        # 给用户发送微信
        # weixin_openid = dbs.get_openid(identity)
        # if weixin_openid is None:
        #     Organization.update(status=status.ORG_SEND_WECHAT_FAILED).where(Organization.id == id).execute()
        # else:
        #     wechat.send_msg(weixin_openid, VAR['WEIXIN_MSG_TMP'].format(identity, name))
        #     Organization.update(status=status.ORG_SEND_WECHAT_SUCCESS).where(Organization.id == id).execute()


    def process(self, entry):
        """
        处理 event=DIDAttributeConfirmed 的函数
        :param entry: 获得的event数据
        :return:
        """
        provider = VAR['ETH_PROVIDER']
        contract_address = VAR['CONTRACT_ADDRESS']
        abi = VAR['CONTRACT_ABI']
        army_private_key = VAR['ARMY_PRIVATEKEY']
        operator_private_key = VAR['OPERATOR_PRIVATEKEY']
        delegate_private_key = VAR['DELEGATE_PRIVATEKEY']
        contract = Contract(provider=provider, timeout=60, contract_address=contract_address, abi=abi,
                            private_key=operator_private_key
                           )
        self.did_attribute_confirmed(contract=contract,
                                     army_private_key=army_private_key,
                                     private_key=operator_private_key,
                                     entry=entry
                                     )
