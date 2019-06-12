# coding:utf-8

from ..db import mongo as db
from tweb.json_util import filter_keys
from tweb.error_exception import ErrException, ERROR
from tweb import time
from bson.errors import InvalidId
from ..utils.bson_util import bson2json, json2bson, json_id, bson_id
from ..employment import Employment
import re


# 组织节点状态以及状态迁移定义
class Status:
    removed = -10  # 已删除
    editing = 0  # 编辑中
    auditing = 10  # 待审(审核中)
    sleeping = 20  # 休眠中
    activated = 30  # 已激活

    default = activated

    status_map = {
        editing: {'submit': auditing, 'remove': removed},
        auditing: {'reject': editing, 'audit': sleeping, 'remove': removed},
        sleeping: {'activate': activated, 'remove': removed},
        activated: {'deactivate': sleeping}
    }

    @staticmethod
    def trans(cur_status, action):
        """
        在当前状态，进行操作将会得到新的状态
        :param cur_status: 当前状态
        :param action: 操作名称
        :return: 新的状态
        """

        valid_actions = Status.status_map.get(cur_status)
        if valid_actions is None:
            raise ErrException(ERROR.E40022, extra=f'current status is {cur_status}, forbid change status')

        new_status = valid_actions.get(action)
        if new_status is None:
            raise ErrException(ERROR.E40022, extra=f'current status is {cur_status}, wrong action [{action}]')

        return new_status


def create(oid, data, *auth_args):
    """
    向oid节点中添加org_meta描述的子节点
    """
    o = simple_read(oid)

    # 授权检查
    # 因为授权限制操作授权本级节点，故在这里加一个'/org'，表示是创建子节点
    Employment().verify(*auth_args).operable('{}/*'.format(o.get('node')), 'org.create')
    # END

    new_oid = simple_create(oid, data)
    return simple_read(new_oid)


def _verify_name(name):
    if not re.match(r'^[\w]{1,48}$', name):
        raise ErrException(ERROR.E40000,
                           extra='"%s" should be letter, number, and beginning with letter, and more than 1' % name)


def simple_create(oid, data, session=None):
    o = simple_read(oid)

    # 可以子定义cid，也可以不指定，由系统自动分配
    new_oid = None
    if 'oid' in data:
        new_oid = data.pop('oid')
        _verify_name(new_oid)
    new_oid = bson_id(new_oid)

    # 如果没指定name则使用id的字符串形式
    name = str(json_id(new_oid))
    if 'name' in data:
        name = data.pop('name').lower()
        _verify_name(name)

    data['_id'] = new_oid
    data['node'] = '{}/{}'.format(o['node'], name)
    data['parent'] = bson_id(oid)
    owner_oid = data.get('owner')
    if owner_oid is not None:
        data['owner'] = bson_id(owner_oid)

    if db.org.find_one({'node': data['node'], 'status': {'$gte': 0}}) is not None:
        raise ErrException(ERROR.E40020)

    data['status'] = Status.default
    now = time.millisecond()
    data['created'] = now
    data['updated'] = now

    result = db.org.insert_one(data, session=session)
    return result.inserted_id


def read(oid, *auth_args):
    o = simple_read(oid)

    # 授权检查
    Employment().verify(*auth_args).operable(o.get('node'), 'org.read')
    # END

    return o


def simple_read(oid, raw=False):
    try:
        oid_obj = bson_id(oid)
    except InvalidId:
        raise ErrException(ERROR.E40000, extra='wrong org id')

    o = db.org.find_one({'_id': oid_obj, 'status': {'$gte': 0}})
    if o is None:
        raise ErrException(ERROR.E40400, extra=f'the org({oid}) not existed')

    if not raw:
        bson2json(o)
        o['oid'] = o.pop('_id')

    return o


def read_with_node(node, raw=False):
    o = db.org.find_one({'node': node, 'status': {'$gte': 0}})
    if o is None:
        return None

    if not raw:
        bson2json(o)
        o['oid'] = o.pop('_id')

    return o


def update(oid, data, *auth_args):
    """
    :param oid: 组织节点id
    :param data: 组织信息
    :param auth_args: 鉴权参数：(signed, nonce), 即("签名的授权字符串", "临时一致性标示，需与生成签名时使用的nonce相同")
    :return:
    """
    o = simple_read(oid)

    # 授权检查
    Employment().verify(*auth_args).operable(o.get('node'), 'org.update')
    # END

    if o['status'] not in (Status.editing, Status.auditing, Status.sleeping, Status.activated):
        raise ErrException(ERROR.E40021)

    new_data = filter_keys(data, {
        'display': 1,
        'icon': 1
    })

    new_data['status'] = Status.default
    new_data['updated'] = time.millisecond()

    db.org.update_one({'_id': bson_id(oid)}, {'$set': new_data})
    return simple_read(oid)


def change_status(oid, action, *auth_args):
    """
    :param oid: 组织节点id
    :param action: 操作（提交，过审，驳回，激活，去激活，删除等）
    :param auth_args: 鉴权参数：(signed, nonce), 即("签名的授权字符串", "临时一致性标示，需与生成签名时使用的nonce相同")
    :return:
    """
    o = simple_read(oid)

    # 授权检查
    Employment().verify(*auth_args).operable(o.get('node'), 'org.{}'.format(action))
    # END

    cur_status = o.get('status')
    new_status = Status.trans(cur_status, action)

    new_data = {
        'status': new_status,
        'updated': time.millisecond()
    }

    db.org.update_one({'_id': bson_id(oid)}, {'$set': new_data})

    return {'id': oid, 'status': new_status, 'old_status': cur_status}


def children(oid, *auth_args):
    o = simple_read(oid)

    # 授权检查
    # 因为授权限制操作授权本级节点，故在这里加一个'/children'，表示是读取子节点
    idt = Employment().verify(*auth_args).operable('{}/*'.format(o.get('node')), 'org.read')
    visible_level = idt.number(o.get('node'), 'org.visible_level')
    min_stat = Status.activated - visible_level
    # END

    cursor = db.org.find({'parent': bson_id(oid), 'status': {'$gte': min_stat}})
    array = list()
    for item in cursor:
        bson2json(item)
        item['oid'] = item.pop('_id')

        array.append(item)
    return array


def move(oid, oid_to, *auth_args):
    """
    把oid标示的节点移到oid_to标示的节点之下
    :param oid: 被移动节点ID
    :param oid_to: 新的父节点ID
    :param auth_args: 鉴权参数：(signed, nonce), 即("签名的授权字符串", "临时一致性标示，需与生成签名时使用的nonce相同")
    :return:
    """
    o = simple_read(oid, raw=True)
    o_to = simple_read(oid_to, raw=True)

    if o['parent'] == oid_to:
        raise ErrException(ERROR.E40000, extra='the same node, not need move')

    # 授权检查
    Employment().verify(*auth_args).operable(o['node'], 'org.remove', 'employ.remove')
    Employment().verify(*auth_args).operable(o_to['node'], 'org.create', 'employ.add')
    # END

    if o['status'] not in (Status.editing, Status.auditing, Status.sleeping, Status.activated):
        raise ErrException(ERROR.E40021)

    now = time.millisecond()

    name = o['node'].split('/').pop()
    node = f'{o_to["node"]}/{name}'

    if db.org.find_one({'node': node, 'status': {'$gte': 0}}) is not None:
        raise ErrException(ERROR.E40020)

    tmp_o = {
        'node': node,
        'parent': bson_id(oid_to),
        'status': Status.auditing,
        'updated': now
    }

    tmp_o2u = {
        'org_node': node,
        'updated': now
    }

    # 还需要同步修改与此节点相关org2user记录，因为里面记录了节点的node值。多个地方更新需要用到事务！
    with db.start_session() as s:
        s.start_transaction()
        db.org2user.update_many({'org': bson_id(oid)}, {'$set': tmp_o2u}, session=s)
        db.org.update_one({'_id': bson_id(oid)}, {'$set': tmp_o}, session=s)
        s.commit_transaction()

    return simple_read(oid)
