#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
# Author: yuyongpeng@hotmail.com
# Description: 监听器
#  

"""


from oracle.setting import VAR
from pycontractsdk.contracts import Cport
from oracle.database import dbs
from oracle import utils
from oracle.utils import write_blocknum
from pycontractsdk.events import filter_event
import time


class Listener(object):
    def __init__(self):
        self.provider = VAR['ETH_PROVIDER']
        self.contract_address = VAR['CONTRACT_ADDRESS']
        self.abi = VAR['CONTRACT_ABI']
        self.cache_file = VAR['BLOCKNUM_CACHE_FILE']
        self.blocknum_inc = VAR['BLOCKNUM_INC']

        self.army_private_key = VAR['ARMY_PRIVATEKEY']
        self.operator_private_key = VAR['OPERATOR_PRIVATEKEY']
        self.delegate_private_key = VAR['DELEGATE_PRIVATEKEY']
        self.army_blockum_cache_file = VAR['ARMY_BLOCKNUM_CACHE_FILE']


class ArmyListener(Listener):
    def __init__(self):
        super(ArmyListener, self).__init__()

    def army_handle_event(self, entries):
        """
        处理events的业务逻辑
        :param entries:
        :return:
        """
        for entry in entries:
            # 数据存到数据库中
            dbs.save_event(entry)
            block_num = entry['blockNumber']
            write_blocknum(VAR['BLOCKNUM_CACHE_FILE'], block_num)
            args = entry['args']
            identity = args['identity']
            name = str(args['name'], 'utf8')
            event_name = entry['event']
            if event_name == 'DIDAttributeChange':
                # TODO: 解析加密的数据，获得军人的身份数据，去数据库中匹配，
                # TODO: 如果匹配上了就需在数据库中修改这条数据的状态为完成，然后在发送到以太坊中,必须确保一定上链
                # TODO: 如果没有匹配上，就输出log，不做任何处理
                key = self.army_private_key
                if dbs.is_exist_soldier(key):
                    pass
                else:
                    pass
                pass

    def run(self):
        cport = Cport(provider=self.provider, timeout=60, contract_address=self.contract_address, abi=self.abi)
        from_block = utils.get_cache_blocknum(self.army_blockum_cache_file)
        while True:
            block_number = cport.block_number
            try:
                filter_event(
                    provider=self.provider,
                    contract_address=self.contract_address,
                    abi=self.abi,
                    event_name=self.army_handle_event,
                    from_block=from_block,
                    to_block=from_block + self.blocknum_inc
                )
            except Exception as e:
                print(e)
                time.sleep(5)
                continue
            if (from_block + self.blocknum_inc) >= block_number:
                from_block = block_number
            else:
                from_block = from_block + self.blocknum_inc
            write_blocknum(self.army_blockum_cache_file, from_block)
            time.sleep(10)