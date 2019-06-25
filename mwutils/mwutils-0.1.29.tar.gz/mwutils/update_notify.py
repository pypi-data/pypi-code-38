'''
同步数据到redis 中
每天凌晨重新同步所有的基本资料到redis，并发出所有资料变更通知（预留异步同步资料的接口）
每笔监控资料的修改都会同步到redis 并发出变更通知
'''

from enum import Enum
import json
from mwutils.utils import toUTCtime
import sys
from collections import OrderedDict
from datetime import datetime

# CHANNEL ='bdupd.{table}.{key}'# bdupd.表名.Key

class UpdateType(Enum):
    add    = 0
    update = 1
    delete = 2

def notifyUpdate(table,key,updateType,tables = None):
    '''
    bdupd.fleet.F99999_{"time": 1473385816, "tables": ["fleet"], "act": "upd"}
    :param table: 变更的表名
    :param key: key的值
    :param updateType: 变更类型，见UpdateType类
    :param tables: 变更的表名
    :return:
    '''
    def delivery_callback(err, msg):
        if err:
            sys.stderr.write('%% Message failed delivery: %s\n' % err)
        else:
            sys.stderr.write('%% Message delivered to %s [%d]\n' % \
                             (msg.topic(), msg.partition()))
    if tables is None:
        tables = [table]
    msg = OrderedDict()
    msg['table'] = table
    msg['key'] = key
    if UpdateType.delete.value == updateType:
        msg["act"] = 'del'
    elif UpdateType.add.value == updateType:
        msg['act'] = 'inst'
    else:
        msg['act'] = 'upd'
    msg["time"] = toUTCtime(datetime.now())
    msg["updtables"] = tables
    ntfMsg = json.dumps(msg)
    # todo:写kafka product
    # p.producer('bd_updatekeys', value=json.dumps(msg), callback=delivery_callback)




