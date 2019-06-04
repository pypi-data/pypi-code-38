#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存放的是业务逻辑
"""
import asyncio
import time
from pycontractsdk.events import filter_event
from pycontractsdk.contracts import Contract
from oracle.setting import VAR
from oracle.utils import write_blocknum, get_cache_blocknum
from oracle.database import dbs
from oracle.database.modles import OrganizationDid
from oracle.logger import logger
from oracle.plugins import Processor

class BaseEvent(object):
    def __init__(self):
        pass

    def did_attribute_change(self, cport, entry, *args, **kwargs):
        """ 处理 event=DIDAttributeChange 的函数 """
        args = entry['args']
        name = args['name'].strip(b'\x00')
        name = name.decode('utf8')
        # 所有已经注册的插件 都运行
        Processor.process(event='DIDAttributeChange' ,identity=name, entry=entry)

    def monitor_event(self, event_name, cache_file=None):
        """
        监控 指定的 event_name 的数据做处理
        :param event_name: 示例：DIDAttributeChange
        :param cache_file: 缓存blockNum的文件
        :return:
        """
        provider = VAR['ETH_PROVIDER']
        contract_address = VAR['CONTRACT_ADDRESS']
        abi = VAR['CONTRACT_ABI']
        if cache_file is None:
            cache_file = VAR['BLOCKNUM_CACHE_FILE']
        blocknum_inc = VAR['BLOCKNUM_INC']
        operator_private_key = VAR['OPERATOR_PRIVATEKEY']
        delegate_private_key = VAR['DELEGATE_PRIVATEKEY']

        from_block = get_cache_blocknum(cache_file)
        # from_block = 293700
        contract = Contract(provider=provider, timeout=60, contract_address=contract_address, abi=abi,
                         private_key=operator_private_key
                        )
        while True:
            block_number = contract.block_number
            print("block_number: {}".format(block_number))
            if from_block > block_number:
                logger.error("******************************************************************************************************")
                logger.error("** The block number of the current query is larger than the largest block number in the blockchain! **")
                logger.error("******************************************************************************************************")
                assert("The block number of the current query is larger than the largest block number in the blockchain! ")
                exit(2)
            if (from_block+blocknum_inc) >= block_number:
                to_block = block_number
            else:
                to_block = from_block + blocknum_inc
            try:
                # 获得 event数据
                entries = filter_event(
                    provider=provider,
                    contract_address=contract_address,
                    abi=abi,
                    event_name=event_name,
                    from_block=0 if from_block == 0 else from_block,
                    to_block=to_block
                )

                for entry in entries:
                    print(entry)
                    # 如果注册了对应的event插件就运行
                    processor = Processor()
                    processor.process_event(event=event_name, entry=entry)

                    # 所有任务处理完成后，才把块号写入到缓存文件中
                    block_num = entry['blockNumber']
                    write_blocknum(cache_file, block_num)
                write_blocknum(cache_file, to_block)
                from_block = to_block
                time.sleep(10)
            except Exception as e:
                logger.error(e)
                time.sleep(3)
                continue


class ThirdPartyVerification(BaseEvent):
    """
    第三方结构验证event数据，并上链
    """


    def monitor_event(self, event_name):
        """
        军队的将监控程序监控event的数据，导入到数据库中
        :param event_name: DIDAttributeChange
        :return:
        """
        super().monitor_event(event_name, VAR['blocknum_cache_file'])




def handle_event(entries, *argc, **kwargs):
    """
    处理event
    :param entries:
    :return:
    """
    provider = kwargs['provider']
    contract_address = kwargs['contract_address']
    abi = kwargs['abi']
    for entry in entries:
        # 数据存到数据库中
        dbs.save_event(entry)
        block_num = entry['blockNumber']
        write_blocknum(VAR['BLOCKNUM_CACHE_FILE'], block_num)
        args = entry['args']
        event_name = entry['event']
        if event_name == 'ContractOwnerChange':
            pass
            # contract_owner_change()
        elif event_name == 'DIDOwnerChanged':
            pass
            # did_owner_changed()
        elif event_name == 'DIDDelegateChanged':
            pass
            # did_delegate_changed()
        elif event_name == 'DIDAttributeChange':
            pass
            # if check_data() == True:
            #     # TODO: 修改数据库的状态 并且在以太坊中提交状态
            #     cport = Cport(provider=provider, timeout=60, contract_address=contract_address, abi=abi)
            #     cport.confirm_attribute()
            #     pass
            # else:
            #     pass
        elif event_name == 'DIDAttributeConfirmed':
            pass
            # did_attribute_confirmed()


def monitor_event(event_name):
    """
    军队的将监控程序监控event的数据，导入到数据库中
    :param event_name:
    :return:
    """
    provider = VAR['ETH_PROVIDER']
    contract_address = VAR['CONTRACT_ADDRESS']
    abi = VAR['CONTRACT_ABI']
    cache_file = VAR['BLOCKNUM_CACHE_FILE']
    blocknum_inc = VAR['BLOCKNUM_INC']

    army_private_key = VAR['ARMY_PRIVATEKEY']
    operator_private_key = VAR['OPERATOR_PRIVATEKEY']
    delegate_private_key = VAR['DELEGATE_PRIVATEKEY']
    gas = VAR['GAS']
    gas_prise = VAR['GAS_PRISE']

    # block_n = get_cache_blocknum(cache_file)
    block_n = 268748
    cport = Contract(provider=provider, timeout=60, contract_address=contract_address, abi=abi,
                  operator_private_key=operator_private_key,
                  delegate_private_key=delegate_private_key,
                  gas=gas,
                  gas_prise=gas_prise
                  )
    while True:
        try:
            entries = filter_event(
                provider=provider,
                contract_address=contract_address,
                abi=abi,
                event_name=event_name,
                from_block=0 if block_n == 0 else block_n-1,
                to_block=block_n+blocknum_inc
            )
            print(entries)
        except Exception as e:
            print(e)
            time.sleep(3)
            continue
        for entry in entries:
            # 数据存到数据库中
            dbs.save_event(entry)
            block_num = entry['blockNumber']
            write_blocknum(VAR['BLOCKNUM_CACHE_FILE'], block_num)
            args = entry['args']
            event_name = entry['event']
            if event_name == 'ContractOwnerChange':
                pass
                # contract_owner_change(cport)
            elif event_name == 'DIDOwnerChanged':
                pass
                # did_owner_changed(cport)
            elif event_name == 'DIDDelegateChanged':
                pass
                # did_delegate_changed(cport)
            elif event_name == 'DIDAttributeChange':
                pass

                # did_attribute_change(cport=cport,
                #                      army_private_key=army_private_key,
                #                      operator_private_key=operator_private_key,
                #                      delegate_private_key=delegate_private_key,
                #                      args=args,
                #                      identity=VAR['IDENTITY']
                #                      )
            elif event_name == 'DIDAttributeConfirmed':
                # did_attribute_confirmed(cport)
                pass
        block_n = block_n + blocknum_inc
        write_blocknum(VAR['BLOCKNUM_CACHE_FILE'], block_n)
        time.sleep(10)


async def log_loop(provider, contract_address, abi, event_name, from_block, blocknum_inc=200, poll_interval=2):
    cport = Contract(provider=provider, timeout=60, contract_address=contract_address, abi=abi)
    contract = cport.get_contract()
    while True:
        print('blocknum: {}'.format(cport.block_number))
        block_number = cport.block_number
        event_filter = contract.events[event_name].createFilter(fromBlock=from_block, toBlock=from_block+blocknum_inc)
        print('event_name={}, from_block={}, to_block={}'.format(event_name, from_block, from_block+blocknum_inc))
        for event in event_filter.get_all_entries():
            # for event in event_filter.get_new_entries():
            dbs.save_event(event)
        if (from_block+blocknum_inc) >= block_number:
            from_block = block_number
            await asyncio.sleep(10)
        else:
            from_block = from_block + blocknum_inc
            await asyncio.sleep(poll_interval)
        write_blocknum(VAR[event_name], from_block)


def import_event():
    provider = VAR['ETH_PROVIDER']
    contract_address = VAR['CONTRACT_ADDRESS']
    abi = VAR['CONTRACT_ABI']
    blocknum_inc = VAR['BLOCKNUM_INC']
    ContractOwnerChange_blocknum = get_cache_blocknum(VAR['ContractOwnerChange'])
    DIDOwnerChanged_blocknum = get_cache_blocknum(VAR['DIDOwnerChanged'])
    DIDDelegateChanged_blocknum = get_cache_blocknum(VAR['DIDDelegateChanged'])
    DIDAttributeChange_blocknum = get_cache_blocknum(VAR['DIDAttributeChange'])
    DIDAttributeConfirmed_blocknum = get_cache_blocknum(VAR['DIDAttributeConfirmed'])
    DIDAttributeChange_blocknum = 293600
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            asyncio.gather(
                log_loop(provider=provider, contract_address=contract_address, abi=abi,
                         event_name='ContractOwnerChange', from_block=ContractOwnerChange_blocknum, blocknum_inc=blocknum_inc),
                log_loop(provider=provider, contract_address=contract_address, abi=abi,
                         event_name='DIDOwnerChanged', from_block=DIDOwnerChanged_blocknum, blocknum_inc=blocknum_inc),
                log_loop(provider=provider, contract_address=contract_address, abi=abi,
                         event_name='DIDDelegateChanged', from_block=DIDDelegateChanged_blocknum, blocknum_inc=blocknum_inc),
                log_loop(provider=provider, contract_address=contract_address, abi=abi,
                         event_name='DIDAttributeChange', from_block=DIDAttributeChange_blocknum, blocknum_inc=blocknum_inc),
                log_loop(provider=provider, contract_address=contract_address, abi=abi,
                         event_name='DIDAttributeConfirmed', from_block=DIDAttributeConfirmed_blocknum, blocknum_inc=blocknum_inc),
            )
        )
    finally:
        loop.close()


# class OrganizationEvent(BaseEvent):
#     def contract_owner_change(self, cport):
#         """ 处理 event=ContractOwnerChange 的函数 """
#         pass
#
#     def did_owner_changed(self, cport):
#         """ 处理 event=DIDOwnerChanged 的函数  """
#         pass
#
#     def did_attribute_change(self, cport):
#         """ 处理 event=DIDAttributeChange 的函数 """
#         pass
#
#     # def did_attribute_confirmed(self, cport, entry, army_private_key, operator_private_key, delegate_private_key):
#     def did_attribute_confirmed(self, cport, entry, *args, **kwargs):
#         """
#         处理 event=DIDAttributeConfirmed 的函数
#         验证 机构 上链的数据
#         确认军人的身份之后，进行上链操作，告诉大家他是一个军人
#
#         获得的event数据，比 DIDAttributeChange 多了一个签名
#         AttributeDict(
#         {'args': AttributeDict(
#           {
#             'identity': '0xB2be7c8722935DB16921D64Ad0dDB5D47A52482a',
#             'name': b'\xe5\xa3\xab\xe5\x85\xb5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
#             'value': b'{"@context":"https://w3id.org/did/v1","id":"did:ethr:B2be7c8722935DB16921D64Ad0dDB5D47A52482a#soldier",
#                         "publicKey":[{"id":"did:ethr:B2be7c8722935DB16921D64Ad0dDB5D47A52482a##proof",
#                                       "type":"EciesVerificationKey",
#                                       "controller":"did:ethr:B2be7c8722935DB16921D64Ad0dDB5D47A52482a",
#                                       "publicKeyHex":"0x04521fbe1f862845cb09ca6c0cdff00417d4a3bf3c04748806eb49079f5d2d5d555c6461ecc3760bd10de1bc7c77421f02bbe3642d6d3e35ee219f84a026478297"}],
#                         "authentication":[{"id":"did:ethr:DeCD6626f23bc43cB4D738cB0F2Dde922D691fD2#proof",
#                                             "type":"EciesVerificationKey",
#                                             "controller":"did:ethr:DeCD6626f23bc43cB4D738cB0F2Dde922D691fD2",
#                                             "publicKeyHex":"0x024af3c4d907a75e9349f362b0f854c7d74a89dad457df4f9cbf3c4f9e2f7fbcf8"}],
#                         "proof":"6617fd92f9f8b9b930ff051f6c02ece8d27cf0b2912361093ce38e521bc3c4846885eec37fefdbb06ebc699fcaeb4136",
#                         "created":1554184638038}
#                         \n
#                         04a469fb703b394646a995e6681771967beea3f1ca8fe7b370555e4c5a6dca5b071ea5d9bbec76e3b1058b54894ddff9f9d346934f74a511d17bf56e6cb892fa01
#                         \n
#                         04a469fb703b394646a995e6681771967beea3f1ca8fe7b370555e4c5a6dca5b071ea5d9bbec76e3b1058b54894ddff9f9d346934f74a511d17bf56e6cb892fa01
#                         '
#           }
#         ),
#         'event': 'DIDAttributeConfirmed',
#         'logIndex': 0,
#         'transactionIndex': 0,
#         'transactionHash': HexBytes('0xe453910d44ad566093d33593f6411fd73126564617bd1529fedce6fe42be0fa7'),
#         'address': '0x5c12AED6613AaD77eC2e84e5cedd9b6Ff29A6e6A',
#         'blockHash': HexBytes('0x0c602e8ad51cb5a49ab4952181a252f0bf6f55c9f3fc0cbaa043a9f2b8e5814e'),
#         'blockNumber': 293710}
#         )
#
#         :param cport: pycontractsdk中的针对 cport 协约的处理对象
#         :param entry: 以太坊获得的event数据
#                     event DIDAttributeConfirmed(address indexed identity, bytes32 name, bytes value) 函数的参数
#         :return:
#         """
#         # XXX: 需要确认是否会抛异常
#         army_private_key = kwargs['army_private_key']           # 军队账号的私钥
#         operator_private_key = kwargs['operator_private_key']   # 管理者的私钥
#         delegate_private_key = kwargs['delegate_private_key']   # 代理上链者的私钥
#
#         # 数据存到数据库中
#         event = dbs.save_organization(entry)
#         id = event.id
#         args = entry['args']
#         identity = args['identity']                         # identity
#         name = args['name'].strip(b'\x00')                  # 身份信息描述，比如"士兵"
#         value = args['value']                               # did和签名信息
#         first_sign_text_bytes = value.split(b'\n')[-2]      # 第一个 签名信息
#         second_sign_text_bytes = value.split(b'\n')[-1]     # 第二个 签名信息
#         did_json_bytes = b''.join(value.split(b'\n')[:-2])  # did 信息
#         did_json_obj = json.loads(did_json_bytes.decode())  # did json对象
#
#         # 验证 did 的签名是否正确 first_sign
#         # 第一个签名是用户发起的。必须确认。did['publicKey'][0]['publicKeyHex']
#         if not Did.verify_did(did_json_bytes.decode(), first_sign_text_bytes.decode()):
#             logger.error('*******************************************************')
#             logger.error('* First signature verification error !')
#             logger.error('* did: {}'.format(did_json_bytes.decode()))
#             logger.error('* sign_text: {}'.format(first_sign_text_bytes.decode()))
#             logger.error('*******************************************************')
#             # 需要修改数据库的状态为 "验证第一个签名失败"
#             Organization.update(status=status.ORG_FIRST_SIGN_VERI_FAILED).where(Organization.id == id).execute()
#             return
#         # 需要修改数据库的状态为 "验证第一个签名成功"
#         Organization.update(status=status.ORG_FIRST_SIGN_VERI_SUCCESS).where(Organization.id == id).execute()
#
#         # 验证 (did + first_sign) 的签名是否正确 second_sign
#         # 第二个签名是军队发起的。必须确认。did['authentication'][0]['publicKeyHex']
#         message = b'\n'.join(value.split(b'\n')[:-1]).decode()
#         # army_public_key = '0x044af3c4d907a75e9349f362b0f854c7d74a89dad457df4f9cbf3c4f9e2f7fbcf8916ac219bb70e64777930b1e85d0a550e1e61ca94fa902dee419849a9a0efe8a'
#         tf = keys.ecdsa_verify(message, signature=second_sign_text_bytes.decode(),
#                                public_key=did_json_obj['authentication'][0]['publicKeyHex'])
#                                 # public_key=army_public_key)
#         if tf is False:
#             logger.error('*******************************************************')
#             logger.error('* second signature verification error !')
#             logger.error('* did+first_sign: {}'.format(message))
#             logger.error('* sign_text: {}'.format(second_sign_text_bytes.decode()))
#             logger.error('*******************************************************')
#             # 需要修改数据库的状态为 "验证第二个签名失败"
#             Organization.update(status=status.ORG_SECOND_SIGN_VERI_FAILED).where(Organization.id == id).execute()
#             return
#         # 需要修改数据库的状态为 "验证第二个签名成功"
#         Organization.update(status=status.ORG_SECOND_SIGN_VERI_SUCCESS).where(Organization.id == id).execute()
#
#         # 保存验证通过的数据到最终表中，以最后一次的数据为准
#         dbs.save_organization_did(entry)
#
#         # 给用户发送微信
#         weixin_openid = dbs.get_openid(identity)
#         if weixin_openid is None:
#             Organization.update(status=status.ORG_SEND_WECHAT_FAILED).where(Organization.id == id).execute()
#         else:
#             wechat.send_msg(weixin_openid, VAR['WEIXIN_MSG_TMP'].format(identity, name))
#             Organization.update(status=status.ORG_SEND_WECHAT_SUCCESS).where(Organization.id == id).execute()
#
#
#     def monitor_event(self, event_name):
#         """
#         机构 的监控程序
#         监控event的数据，进行对应的处理
#         :param event_name: 监控的事件名称
#         :return:
#         """
#         provider = VAR['ETH_PROVIDER']
#         contract_address = VAR['CONTRACT_ADDRESS']
#         abi = VAR['CONTRACT_ABI']
#         cache_file = VAR['ORGANIZATION_BLOCKNUM_CACHE_FILE']
#         blocknum_inc = VAR['BLOCKNUM_INC']
#         army_private_key = VAR['ARMY_PRIVATEKEY']
#         operator_private_key = VAR['OPERATOR_PRIVATEKEY']
#         delegate_private_key = VAR['DELEGATE_PRIVATEKEY']
#         gas = VAR['GAS']
#         gas_prise = VAR['GAS_PRISE']
#         # from_block = get_cache_blocknum(cache_file)
#         from_block = 293709
#         cport = Cport(provider=provider, timeout=60, contract_address=contract_address, abi=abi,
#                       operator_private_key=operator_private_key,
#                       delegate_private_key=delegate_private_key,
#                       gas=gas,
#                       gas_prise=gas_prise
#                       )
#         while True:
#             block_number = cport.block_number
#             logger.info("block_number: {}".format(block_number))
#             if from_block > block_number:
#                 """
#                 如果从缓存文件中获得的块号 大于 区块链中的最后一个块号，必须手动修改缓存的块号
#                 """
#                 logger.error("******************************************************************************************************")
#                 logger.error("** The block number of the current query is larger than the largest block number in the blockchain! **")
#                 logger.error("******************************************************************************************************")
#                 assert("The block number of the current query is larger than the largest block number in the blockchain! ")
#                 exit(2)
#             if (from_block+blocknum_inc) >= block_number:
#                 to_block = block_number
#             else:
#                 to_block = from_block + blocknum_inc
#             try:
#                 # 从以太坊中获得event数据
#                 entries = filter_event(
#                     provider=provider,
#                     contract_address=contract_address,
#                     abi=abi,
#                     event_name=event_name,
#                     from_block=0 if from_block == 0 else from_block,
#                     to_block=to_block
#                 )
#                 logger.info(entries)
#             except Exception as e:
#                 # 如果从以太坊中获得event出错了，就暂停一会儿，重新再尝试，直到获得了数据为止
#                 logger.error(e)
#                 time.sleep(3)
#                 continue
#             for entry in entries:
#                 block_num = entry['blockNumber']        # event 存放在哪个块上
#                 event_name = entry['event']
#                 # 只处理军人身份的数据
#                 if event_name == 'DIDAttributeConfirmed':
#                     # 处理获得的event数据
#                     self.did_attribute_confirmed(cport=cport,
#                                                  army_private_key=army_private_key,
#                                                  operator_private_key=operator_private_key,
#                                                  delegate_private_key=delegate_private_key,
#                                                  entry=entry
#                                                  )
#                 # 所有任务处理完成后，才把块号写入到缓存文件中
#                 write_blocknum(cache_file, block_num)
#             write_blocknum(cache_file, to_block)
#             from_block = to_block
#             time.sleep(10)



# class ArmyEvent(BaseEvent):
#     def contract_owner_change(self, cport):
#         """ 处理 event=ContractOwnerChange 的函数 """
#         pass
#
#     def did_owner_changed(self, cport):
#         """ 处理 event=DIDOwnerChanged 的函数  """
#         pass
#
#     def did_attribute_change(self, cport, army_private_key, operator_private_key, delegate_private_key, entry):
#         """
#         处理 event=DIDAttributeChange 的函数
#         确认军人的身份之后，进行上链操作，告诉大家他是一个军人
#
#         获得的 event 数据内容
#         AttributeDict(
#         {'args': AttributeDict(
#           {
#             'identity': '0xB2be7c8722935DB16921D64Ad0dDB5D47A52482a',
#             'name': b'\xe5\xa3\xab\xe5\x85\xb5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
#             'value': b'{"@context":"https://w3id.org/did/v1","id":"did:ethr:B2be7c8722935DB16921D64Ad0dDB5D47A52482a#soldier",
#                         "publicKey":[{"id":"did:ethr:B2be7c8722935DB16921D64Ad0dDB5D47A52482a##proof",
#                                       "type":"EciesVerificationKey",
#                                       "controller":"did:ethr:B2be7c8722935DB16921D64Ad0dDB5D47A52482a",
#                                       "publicKeyHex":"0x04521fbe1f862845cb09ca6c0cdff00417d4a3bf3c04748806eb49079f5d2d5d555c6461ecc3760bd10de1bc7c77421f02bbe3642d6d3e35ee219f84a026478297"}],
#                         "authentication":[{"id":"did:ethr:DeCD6626f23bc43cB4D738cB0F2Dde922D691fD2#proof",
#                                             "type":"EciesVerificationKey",
#                                             "controller":"did:ethr:DeCD6626f23bc43cB4D738cB0F2Dde922D691fD2",
#                                             "publicKeyHex":"0x024af3c4d907a75e9349f362b0f854c7d74a89dad457df4f9cbf3c4f9e2f7fbcf8"}],
#                         "proof":"6617fd92f9f8b9b930ff051f6c02ece8d27cf0b2912361093ce38e521bc3c4846885eec37fefdbb06ebc699fcaeb4136",
#                         "created":1554184638038}
#                         \n
#                         04a469fb703b394646a995e6681771967beea3f1ca8fe7b370555e4c5a6dca5b071ea5d9bbec76e3b1058b54894ddff9f9d346934f74a511d17bf56e6cb892fa01
#                         '
#           }
#         ),
#         'event': 'DIDAttributeChange',
#         'logIndex': 0,
#         'transactionIndex': 0,
#         'transactionHash': HexBytes('0xe453910d44ad566093d33593f6411fd73126564617bd1529fedce6fe42be0fa7'),
#         'address': '0x5c12AED6613AaD77eC2e84e5cedd9b6Ff29A6e6A',
#         'blockHash': HexBytes('0x0c602e8ad51cb5a49ab4952181a252f0bf6f55c9f3fc0cbaa043a9f2b8e5814e'),
#         'blockNumber': 293710}
#         )
#
#         :param cport:
#         :param army_private_key: 军队账号的私钥
#         :param operator_private_key: 管理者的私钥
#         :param delegate_private_key: 代理上链者的私钥
#         :param entry:
#         :param args:  event=DIDAttributeChange(address indexed identity, bytes32 name, bytes value) 函数的参数
#         :return:
#         """
#         # 数据存到数据库中
#         event = dbs.save_army(entry)
#         # 数据库中记录的是 已经上链成功 就不需要再处理了
#         if event.status == status.EVENT_ETHEREUM_SUBMIT_SUCCESS:
#             return
#         id = event.id
#         args = entry['args']
#         identity = args['identity']                         # 用户的address
#         name = args['name'].strip(b'\x00')                  # 身份 比如"士兵"
#         value = args['value']                               # did和签名信息
#         sign_text_bytes = value.split(b'\n')[-1]            # 学文的签名信息
#         did_json_bytes = b''.join(value.split(b'\n')[:-1])  # did 信息 bytes
#         did_json_obj = json.loads(did_json_bytes.decode())  # did json对象
#         created_timestamp = did_json_obj['created']
#
#         if not Did.verify_did(did_json_bytes.decode(), sign_text_bytes.decode()):
#             logger.error('First signature verification error !')
#             logger.error('did: {}'.format(did_json_bytes.decode()))
#             logger.error('sign_text: {}'.format(sign_text_bytes.decode()))
#             # 需要修改数据库的状态为验证签名失败
#             Army.update(status=status.EVENT_SIGN_VERI_FAILED).where(Army.id == id).execute()
#             return
#         # 数据签名验证成功
#         Army.update(status=status.EVENT_SIGN_VERI_SUCCESS).where(Army.id == id).execute()
#         army_privatekey = VAR['ARMY_PRIVATEKEY']
#         # ephemPublicKey 存放在did json串中 (加密者的公钥)
#         ephem_public_key = did_json_obj['publicKey'][0]['publicKeyHex']
#         # 得到学文加密用的iv
#         iv = crypto.get_iv(str(created_timestamp))
#         # 从did中得到加密串
#         ciphertext = Did.get_ciphertext(did_json_obj)
#         # # 解密
#         original = crypto.decrypt_ecies(private_key=army_privatekey,
#                                         ephemPublicKey=ephem_public_key,
#                                         ciphertext=ciphertext,
#                                         iv=iv).strip()
#         if len(str(original)) == 0:
#             Army.update(status=status.EVENT_DECRYPTION_FAILED).where(Army.id == id).execute()   # 解密失败
#         else:
#             Army.update(status=status.EVENT_DECRYPTION_SUCCESS).where(Army.id == id).execute()   # 解密成功
#
#         # 解密数据 并且在 退伍士兵中查询是否有这个士兵
#         (check, soldier) = crypto.check_ecies_in_database(private_key=army_private_key,
#                                                           ephem_public_key=ephem_public_key,
#                                                           ciphertext=ciphertext,
#                                                           iv=iv)
#         if check is False:
#             # 数据库中不存在士兵的这条数据
#             Army.update(status=status.EVENT_ETHEREUM_SOLDIER_NOTEXIST).where(Army.id == id).execute()
#             logger.error('Verification failed: {}'.join(ciphertext))
#         if check is True:
#             # 数据验证完成
#             Army.update(status=status.EVENT_VERI_COMP).where(Army.id == id).execute()
#             logger.info('Verification success: {}'.join(ciphertext))
#
#             # 生成第二个签名数据, 并且保存到数据库中
#             second_sign_str = Did.sign_did(did_json_bytes.decode(), sign_text_bytes.decode(), VAR['ARMY_PRIVATEKEY'])
#             Army.update(second_sign=second_sign_str).where(Army.id == id).execute()
#             data = '{did_json_str}\n{first_sign}\n{second_sign}'.format(did_json_str=did_json_bytes.decode(),
#                                                                         first_sign=sign_text_bytes.decode(),
#                                                                         second_sign=second_sign_str)
#
#             # 上链操作
#             tf, txhash = cport.confirm_attribute(identity, name, data.encode())
#             if tf is True:
#                 Army.update(status=status.EVENT_ETHEREUM_SUBMIT_SUCCESS, txhash=txhash).where(Army.id == id).execute()
#             if tf is False:
#                 Army.update(status=status.EVENT_ETHEREUM_SUBMIT_FAILED, txhash=txhash).where(Army.id == id).execute()
#             # Army.save()
#             # cport.confirm_attribute()
#             # celery异步上链操作
#             # tasks.confirm_attribute.delay(cport, identity, name, value)
#
#     def did_attribute_confirmed(self, cport):
#         """ 处理 event=DIDAttributeConfirmed 的函数 """
#         pass
#
#     def monitor_event(self, event_name):
#         """
#         军队的将监控程序监控event的数据，导入到数据库中
#         :param event_name:
#         :return:
#         """
#         provider = VAR['ETH_PROVIDER']
#         contract_address = VAR['CONTRACT_ADDRESS']
#         abi = VAR['CONTRACT_ABI']
#         cache_file = VAR['ARMY_BLOCKNUM_CACHE_FILE']
#         blocknum_inc = VAR['BLOCKNUM_INC']
#         identity = VAR['IDENTITY']
#         army_private_key = VAR['ARMY_PRIVATEKEY']
#         operator_private_key = VAR['OPERATOR_PRIVATEKEY']
#         delegate_private_key = VAR['DELEGATE_PRIVATEKEY']
#
#         # from_block = get_cache_blocknum(cache_file)
#         from_block = 293700
#         cport = Cport(provider=provider, timeout=60, contract_address=contract_address, abi=abi,
#                       operator_private_key=operator_private_key,
#                       delegate_private_key=delegate_private_key
#                       )
#         while True:
#             block_number = cport.block_number
#             print("block_number: {}".format(block_number))
#             if from_block > block_number:
#                 logger.error("******************************************************************************************************")
#                 logger.error("** The block number of the current query is larger than the largest block number in the blockchain! **")
#                 logger.error("******************************************************************************************************")
#                 assert("The block number of the current query is larger than the largest block number in the blockchain! ")
#                 exit(2)
#             if (from_block+blocknum_inc) >= block_number:
#                 to_block = block_number
#             else:
#                 to_block = from_block + blocknum_inc
#             try:
#                 entries = filter_event(
#                     provider=provider,
#                     contract_address=contract_address,
#                     abi=abi,
#                     event_name=event_name,
#                     from_block=0 if from_block == 0 else from_block,
#                     to_block=to_block
#                 )
#                 print(entries)
#             except Exception as e:
#                 print(e)
#                 time.sleep(3)
#                 continue
#             for entry in entries:
#                 block_num = entry['blockNumber']
#                 args = entry['args']
#                 name = args['name'].strip(b'\x00')
#                 name = name.decode('utf8')
#                 event_name = entry['event']
#                 # 只处理军人身份的数据
#                 if event_name == 'DIDAttributeChange' and name == identity:
#                     self.did_attribute_change(cport=cport,
#                                           army_private_key=army_private_key,
#                                           operator_private_key=operator_private_key,
#                                           delegate_private_key=delegate_private_key,
#                                           entry=entry
#                                           )
#                 # 所有任务处理完成后，才把块号写入到缓存文件中
#                 write_blocknum(cache_file, block_num)
#             write_blocknum(cache_file, to_block)
#             from_block = to_block
#             time.sleep(10)


