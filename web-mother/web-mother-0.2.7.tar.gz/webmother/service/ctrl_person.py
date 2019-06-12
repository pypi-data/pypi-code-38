# coding:utf-8

from ..db import mongo as db
from tweb.error_exception import ErrException, ERROR
from tweb import time
from ..utils.bson_util import json_id, bson_id
from ..employment import Employment
from ..service import ctrl_org

from ucenter.services import ctrl_user


def add(oid, indicator, employment_json, *auth_args):
    """
    向组织中添加用户
    :param oid: 组织ID
    :param indicator: 用户标示，可以是uid, 登录名，email, 手机号
    :param employment_json: 授权信息对象
    :param auth_args: 鉴权参数：(signed, nonce), 即("签名的授权字符串", "临时一致性标示，需与生成签名时使用的nonce相同")
    :return:
    """
    u = ctrl_user.get(indicator)
    if u is None:
        raise ErrException(ERROR.E40000, extra='invalid user [%s]' % indicator)

    uid = u['id']
    user = {
        'uid': bson_id(uid),
        'name': u.get('name'),
        'nickname': u.get('nickname'),
        'email': u.get('email'),
        'mobile': u.get('mobile'),
        'icon': u.get('icon')
    }

    o = ctrl_org.simple_read(oid)

    # 授权检查
    # 允许给自己的组织添加成员，相当于雇佣平级同事，但权限不会超过自己的权限
    idt = Employment().verify(*auth_args).operable('{}/*'.format(o.get('node')), 'employ.add')
    # END

    node = o['node']
    cursor = db.org2user.find({'user.uid': bson_id(uid)}, {'user': 0})
    for item in cursor:
        other = item['org_node']
        # 如果已经加入，则无需再加入
        if node == other:
            raise ErrException(ERROR.E40020, extra=f'user({uid}) have been in org({other})')

    now = time.millisecond()
    db.org2user.insert_one({
        "org": bson_id(oid),
        "org_node": node,
        "employment": Employment().update(node, uid, employment_json, idt).text,
        "member_type": 0,
        "user": user,
        "created": now,
        "updated": now
    })

    return simple_member_read(oid, uid)


def get(oid, uid, *auth_args):
    o = ctrl_org.read(oid, *auth_args)

    # 授权检查
    Employment().verify(*auth_args).operable(o.get('node'), 'org.read')
    # END

    return simple_member_read(oid, uid)


def simple_member_read(oid, uid):
    # 首先从UCenter更新最新的用户信息
    u = ctrl_user.get(uid)
    if u is None:
        raise ErrException(ERROR.E40000, extra='invalid user [%s]' % uid)

    user = {
        'uid': bson_id(uid),
        'name': u.get('name'),
        'nickname': u.get('nickname'),
        'email': u.get('email'),
        'mobile': u.get('mobile'),
        'icon': u.get('icon')
    }

    # 读取会员信息
    o2u = db.org2user.find_one({'org': bson_id(oid), 'user.uid': bson_id(uid)}, {'org': 0})
    if o2u is None:
        raise ErrException(ERROR.E40400)

    # 如果UCenter中的信息更新，则同步更新到会员系统
    if user != o2u['user']:
        db.org2user.update_one({'org': bson_id(oid), 'user.uid': bson_id(uid)}, {'$set': {'user': user}})
        o2u['user'] = user

    o2u['open_id'] = json_id(o2u.pop('_id'))
    o2u['user']['uid'] = json_id(o2u['user']['uid'])
    o2u['employment'] = Employment().parse(o2u['employment']).json

    return o2u


def update(oid, uid, employment_json, *auth_args):
    o = ctrl_org.read(oid, *auth_args)

    # 授权检查
    idt = Employment().verify(*auth_args).operable(o.get('node'), 'employ.add')
    # END

    o2u = db.org2user.find_one({'org': bson_id(oid), 'user.uid': bson_id(uid)})
    if o2u is None:
        raise ErrException(ERROR.E40400)

    temp = dict()
    temp['employment'] = Employment().parse(o2u.get('employment')).update(o['node'], uid, employment_json, idt).text
    temp['updated'] = time.millisecond()
    db.org2user.update_one({'_id': o2u['_id']}, {'$set': temp})

    return simple_member_read(oid, uid)


def remove(oid, uid, *auth_args):
    """
    从组织中移除用户
    :param oid: 组织ID
    :param uid: 用户ID
    :param auth_args: 鉴权参数：(signed, nonce), 即("签名的授权字符串", "临时一致性标示，需与生成签名时使用的nonce相同")
    :return:
    """
    o = ctrl_org.simple_read(oid)

    # 授权检查
    Employment().verify(*auth_args).operable(o.get('node'), 'employ.remove')
    # END

    # 使已签名的授权无效
    Employment.invalidate_signed(o.get('node'), uid)

    db.org2user.delete_one({'org': bson_id(oid), 'user.uid': bson_id(uid)})

    return {}


def query(oid, page_no, page_size, *auth_args):
    o = ctrl_org.simple_read(oid)

    # 授权检查
    Employment().verify(*auth_args).operable(o.get('node'), 'org.read')
    # END

    skip = (page_no - 1) * page_size
    cursor = db.org2user.find({'org': bson_id(oid)}, {'org': 0}).skip(skip).limit(page_size)

    array = list()
    for item in cursor:
        item['open_id'] = json_id(item.pop('_id'))
        item['user']['uid'] = json_id(item['user']['uid'])
        if 'employment' in item:
            item['employment'] = Employment().parse(item['employment']).json
        if 'membership' in item:
            item['membership'] = Employment().parse(item['membership']).json
        array.append(item)

    return array, cursor.count()
