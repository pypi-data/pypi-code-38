#!/usr/bin/env python
# -*- coding=UTF-8 -*-

from oracle.business import BaseEvent, import_event
from oracle import setting
import click
from oracle import cusomer
from oracle.setting import VAR
from pycontractsdk.contracts import Contract
from oracle.utils import import_plugins
from oracle.database import dbs
import time
from oracle.database import status
from oracle.plugins.solider import Solider


@click.command()
@click.option('-f', "--file", default='./oracle_army.cfg', help='指定配置文件的路径（默认: ./oracle_army.cfg）')
def army(file):
    # TODO: 军队 运行的验证程序"
    # 初始化配置信息
    setting.read_config2(file)
    # 导入`event` 插件
    import_plugins()
    event = BaseEvent()
    event.monitor_event('DIDAttributeChange')


@click.command()
@click.option('-f', "--file", default='./oracle_army.cfg', help='指定配置文件的路径（默认: ./oracle_army.cfg）')
def army_reprocess(file):
    """ 处理军队中未完成的数据 """
    # 初始化配置信息
    setting.read_config2(file)

    solider = Solider()
    while True:
        armys = dbs.get_army_datas()
        for army in armys:
            st = army.status
            if st == status.EVENT_NORMAL:   # 初始状态
                solider.army_verification_sign(army)
                solider.army_decrypt(army)
                solider.army_search_army(army)
                solider.army_upload_chain(army)
            elif st == status.EVENT_SIGN_VERI_SUCCESS:  # 签名验证成功
                solider.army_decrypt(army)
                solider.army_search_army(army)
                solider.army_upload_chain(army)
            elif st == status.EVENT_DECRYPTION_SUCCESS: # 密文解密成功
                solider.army_search_army(army)
                solider.army_upload_chain(army)
            elif st == status.EVENT_VERI_COMP or st == status.EVENT_ETHEREUM_SUBMIT_FAILED :
                # 数据验证完成（到这一步就可以进行上链操作了） or 以太坊发送失败
                solider.army_upload_chain(army)

        time.sleep(3600)  # 1小时


@click.command()
@click.option('-f', "--file", default='./oracle_org.cfg', help='指定配置文件的路径（默认: ./oracle_org.cfg）')
def organization(file):
    # TODO: 机构 运行的oracle程序"
    # 初始化配置信息
    import_plugins()
    setting.read_config2(file)
    event = BaseEvent()
    event.monitor_event('DIDAttributeConfirmed')

    # organization = OrganizationEvent()
    # organization.monitor_event('DIDAttributeConfirmed')


@click.command()
@click.option('-f', "--file", default='/etc/oracle.cfg', help='指定配置文件的路径（默认: /etc/oracle.cfg）')
def impevent(file):
    """
    导入event数据到数据库中
    :param file: 配置文件的路径
    :return:
    """
    # global PATH
    # setting.PATH = os.path.dirname(os.path.abspath(__file__))
    import_plugins()
    # 初始化配置信息
    setting.read_config2(file)
    # business.monitor_event('DIDOwnerChanged')
    import_event()


if __name__ == "__main__":
    army_reprocess()
    # impevent()
    # army()
    # army('/Users/yuyongpeng/git/hard-chain/cport/oracle/oracle_army.conf')
    # organization('/Users/yuyongpeng/git/hard-chain/cport/oracle/oracle.conf')
    # upload_chain()
    # validation_chain_multi_proc()
