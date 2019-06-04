#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
Author:       yuyongpeng@hotmail.com
Github:       https://github.com/yuyongpeng/
Date:         2019-04-17 12:38:25
LastEditors:  
LastEditTime: 2019-04-17 12:38:25
Description:  
"""

import json
from oracle.plugins import Processor
from oracle.database import dbs
from oracle.database import status
from oracle.dids import Did
from oracle.database.modles import Army
from oracle.setting import VAR
from oracle.logger import logger
from oracle import crypto
from pycontractsdk.contracts import Contract
from oracle import utils

@Processor.plugin_register('DIDAttributeChange', ['soldier', '士兵'])
class Solider(object):
    """
    处理 event = DIDAttributeChange 中， 身份为 士兵 的数据
    """
    def __init__(self):
        pass

    def did_attribute_change(self, contract, army_private_key, entry):
        """
        处理 event=DIDAttributeChange 的函数
        确认军人的身份之后，进行上链操作，告诉大家他是一个军人

        获得的 event 数据内容
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
                        '
          }
        ),
        'event': 'DIDAttributeChange',
        'logIndex': 0,
        'transactionIndex': 0,
        'transactionHash': HexBytes('0xe453910d44ad566093d33593f6411fd73126564617bd1529fedce6fe42be0fa7'),
        'address': '0x5c12AED6613AaD77eC2e84e5cedd9b6Ff29A6e6A',
        'blockHash': HexBytes('0x0c602e8ad51cb5a49ab4952181a252f0bf6f55c9f3fc0cbaa043a9f2b8e5814e'),
        'blockNumber': 293710}
        )

        :param contract: pycontractsdk.contract 对象，用于上链
        :param army_private_key: 军队账号的私钥
        :param entry:
        :param entry:  获得的event数据
        :return:
        """
        # 数据存到数据库中
        event = dbs.save_army(entry)
        # 数据库中记录的是 已经上链成功 就不需要再处理了
        if event.status == status.EVENT_ETHEREUM_SUBMIT_SUCCESS:
            return
        id = event.id
        args = entry['args']
        identity = args['identity']                         # 用户的address
        name = args['name'].strip(b'\x00')                  # 身份 比如"士兵"
        value = args['value']                               # did和签名信息
        sign_text_bytes = value.split(b'\n')[-1]            # 学文的签名信息
        did_json_bytes = b''.join(value.split(b'\n')[:-1])  # did 信息 bytes
        did_json_obj = json.loads(did_json_bytes.decode())  # did json对象
        created_timestamp = did_json_obj['created']

        if not Did.verify_did(did_json_bytes.decode(), sign_text_bytes.decode()):
            logger.error('First signature verification error !')
            logger.error('did: {}'.format(did_json_bytes.decode()))
            logger.error('sign_text: {}'.format(sign_text_bytes.decode()))
            # 需要修改数据库的状态为验证签名失败
            Army.update(status=status.EVENT_SIGN_VERI_FAILED).where(Army.id == id).execute()
            return
        # 数据签名验证成功
        Army.update(status=status.EVENT_SIGN_VERI_SUCCESS).where(Army.id == id).execute()
        army_privatekey = VAR['ARMY_PRIVATEKEY']
        # ephemPublicKey 存放在did json串中 (加密者的公钥)
        ephem_public_key = did_json_obj['publicKey'][0]['publicKeyHex']
        # 得到学文加密用的iv
        iv = crypto.get_iv(str(created_timestamp))
        # 从did中得到加密串
        ciphertext = Did.get_ciphertext(did_json_obj)
        # 解密
        original = crypto.decrypt_ecies(private_key=army_privatekey,
                                        ephemPublicKey=ephem_public_key,
                                        ciphertext=ciphertext,
                                        iv=iv).strip()
        if len(str(original)) == 0:
            Army.update(status=status.EVENT_DECRYPTION_FAILED).where(Army.id == id).execute()   # 解密失败
        else:
            Army.update(status=status.EVENT_DECRYPTION_SUCCESS).where(Army.id == id).execute()   # 解密成功

        # 解密数据 并且在 退伍士兵中查询是否有这个士兵
        (check, soldier) = crypto.check_ecies_in_database(private_key=army_private_key,
                                                          ephem_public_key=ephem_public_key,
                                                          ciphertext=ciphertext,
                                                          iv=iv)
        if check is False:
            # 数据库中不存在士兵的这条数据
            Army.update(status=status.EVENT_ETHEREUM_SOLDIER_NOTEXIST).where(Army.id == id).execute()
            logger.error('There is no data for this soldier in the database.  Verification failed ! ciphertext : {}'.format(ciphertext))
        if check is True:
            # 数据验证完成
            Army.update(status=status.EVENT_VERI_COMP).where(Army.id == id).execute()
            logger.info('The data of the soldier in the database. Verification success! ciphertext : {}'.format(ciphertext))

            # 生成第二个签名数据, 并且保存到数据库中
            second_sign_str = Did.sign_did(did_json_bytes.decode(), sign_text_bytes.decode(), VAR['ARMY_PRIVATEKEY'])
            Army.update(second_sign=second_sign_str).where(Army.id == id).execute()
            data = '{did_json_str}\n{first_sign}\n{second_sign}'.format(did_json_str=did_json_bytes.decode(),
                                                                        first_sign=sign_text_bytes.decode(),
                                                                        second_sign=second_sign_str)

            # 上链操作 confirmAttribute(identity, name, value)
            tf, tx_hash = contract.call_function('confirmAttribute', True, *(identity, name, data.encode()))
            # tf, tx_hash = cport.confirm_attribute(identity, name, data.encode())
            if tf is True:
                Army.update(status=status.EVENT_ETHEREUM_SUBMIT_SUCCESS, txhash=tx_hash).where(Army.id == id).execute()
            if tf is False:
                Army.update(status=status.EVENT_ETHEREUM_SUBMIT_FAILED, txhash=tx_hash).where(Army.id == id).execute()
            # Army.save()
            # cport.confirm_attribute()
            # celery异步上链操作
            # tasks.confirm_attribute.delay(cport, identity, name, value)

    def army_verification_sign(self, army):
        """ 验证签名 """
        id = army.id
        datas = army.datas
        datas_obj = json.loads(datas)
        did_json_str = datas_obj['args']['value']
        sign_text_str = did_json_str.split('\n')[-1]  # 学文的签名信息
        did_json_str = ''.join(did_json_str.split('\n')[:-1])  # did 信息 bytes

        if not Did.verify_did(did_json_str, sign_text_str):
            logger.error('First signature verification error !')
            logger.error('did: {}'.format(did_json_str.decode()))
            logger.error('sign_text: {}'.format(sign_text_str))
            # 需要修改数据库的状态为验证签名失败
            Army.update(status=status.EVENT_SIGN_VERI_FAILED).where(Army.id == id).execute()
            return False
        # 数据签名验证成功
        Army.update(status=status.EVENT_SIGN_VERI_SUCCESS).where(Army.id == id).execute()
        return True

    def army_decrypt(self, army):
        """ 对`did`数据进行解密操作 """
        id = army.id
        datas = army.datas
        datas_obj = json.loads(datas)
        did_json_str = datas_obj['args']['value']
        did_json_obj = json.loads(did_json_str.split('\n')[0])
        created_timestamp = did_json_obj['created']
        # 得到学文加密用的iv
        iv = crypto.get_iv(str(created_timestamp))
        # 从did中得到加密串
        ciphertext = Did.get_ciphertext(did_json_obj)
        # 解密
        army_privatekey = VAR['ARMY_PRIVATEKEY']
        ephem_public_key = did_json_obj['publicKey'][0]['publicKeyHex']
        original = crypto.decrypt_ecies(private_key=army_privatekey,
                                        ephemPublicKey=ephem_public_key,
                                        ciphertext=ciphertext,
                                        iv=iv).strip()
        if len(str(original)) == 0:
            Army.update(status=status.EVENT_DECRYPTION_FAILED).where(Army.id == id).execute()  # 解密失败
            return False
        else:
            Army.update(status=status.EVENT_DECRYPTION_SUCCESS).where(Army.id == id).execute()  # 解密成功
            return True

    def army_search_army(self, army):
        """ 查询数据库中是否有这个士兵 """
        id = army.id
        datas = army.datas
        datas_obj = json.loads(datas)
        did_json_str = datas_obj['args']['value']
        did_json_obj = json.loads(did_json_str.split('\n')[0])
        created_timestamp = did_json_obj['created']
        # 得到学文加密用的iv
        iv = crypto.get_iv(str(created_timestamp))
        # 从did中得到加密串
        ciphertext = Did.get_ciphertext(did_json_obj)
        # 解密数据 并且在 退伍士兵中查询是否有这个士兵
        army_private_key = VAR['ARMY_PRIVATEKEY']
        ephem_public_key = did_json_obj['publicKey'][0]['publicKeyHex']
        (check, soldier) = crypto.check_ecies_in_database(private_key=army_private_key,
                                                          ephem_public_key=ephem_public_key,
                                                          ciphertext=ciphertext,
                                                          iv=iv)
        if check is False:
            # 数据库中不存在士兵的这条数据
            Army.update(status=status.EVENT_ETHEREUM_SOLDIER_NOTEXIST).where(Army.id == id).execute()
            logger.error(
                'There is no data for this soldier in the database.  Verification failed ! ciphertext : {}'.format(
                    ciphertext))
        if check is True:
            # 数据验证完成
            Army.update(status=status.EVENT_VERI_COMP).where(Army.id == id).execute()
            logger.info(
                'The data of the soldier in the database. Verification success! ciphertext : {}'.format(ciphertext))
        return check

    def army_upload_chain(self, army):
        """ 将数据库中的数据进行上链操作 """
        id = army.id
        datas = army.datas
        datas_obj = json.loads(datas)
        name = datas_obj['args']['name'].strip(u'\u0000')
        identity = datas_obj['args']['identity']
        did_json = datas_obj['args']['value']
        second_sign = army.second_sign
        data = '{did_json_str}\n{second_sign}'.format(did_json_str=did_json, second_sign=second_sign)
        contract = utils.get_contract()
        # 上链操作 confirmAttribute(identity, name, value)
        tf, tx_hash = contract.call_function('confirmAttribute', True, *(identity, name.encode(), data.encode()))
        # tf, tx_hash = cport.confirm_attribute(identity, name, data.encode())
        if tf is True:
            Army.update(status=status.EVENT_ETHEREUM_SUBMIT_SUCCESS, txhash=tx_hash).where(Army.id == id).execute()
        if tf is False:
            Army.update(status=status.EVENT_ETHEREUM_SUBMIT_FAILED, txhash=tx_hash).where(Army.id == id).execute()
        return tf

    def process(self, entry):
        """
        处理 士兵 的 event数据
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
                      private_key=operator_private_key, gas=VAR['GAS'], gas_prise=VAR['GAS_PRISE']
                      )
        # contract = utils.get_contract()
        self.did_attribute_change(contract=contract,
                                  army_private_key=army_private_key,
                                  entry=entry
                                  )

if __name__ == '__main__':
    # 测试
    print("xx")
    processor = Processor()  # 这条数据还没有运行，就已经把插件注册好了
    processed = processor.process_identity(event='DIDAttributeChange', identity="Solider", entry="ttttt")
    processed = processor.process_identity(event='DIDAttributeChange', identity="士兵", entry="士兵")
