# coding:utf-8

from ..db import mongo as db
from ..employment import Employment
from ..membership import Membership
from ..service import ctrl_org, ctrl_catalog
from ..passport import Passport
from tweb.error_exception import ErrException, ERROR
from ucenter.services import ctrl_user
from tweb import time
from ..utils.bson_util import bson_id, json_id


def query_employments(oid, uid, access_token):
    """
    查询我的身份（组织）列表
    :param oid: 组织ID
    :param uid:
    :param access_token:
    :return:
    """
    o = ctrl_org.simple_read(oid)
    if o is None:
        raise ErrException(ERROR.E40400, extra='invalid org id %s' % oid)
    node = o['node']

    cond = {
        'user.uid': bson_id(uid),
        'employment': {'$exists': True},
        'org_node': {'$regex': r'^{}'.format(node)},
    }

    customer_oid = o.get('customer_org')
    if customer_oid is not None:
        customer_org = ctrl_org.simple_read(customer_oid)
        member_node = customer_org['node']
        sub = member_node.replace(node, '', 1)
        cond['org_node'] = {'$regex': r'^{}(?!{})'.format(node, sub)}

    cursor = db.org2user.find(cond, {'user': 0})
    array = list()
    for item in cursor:
        idt = Employment().parse(item['employment'])
        item['signed_employment'] = idt.signed(item['org_node'], uid, access_token)
        item['employment'] = idt.json

        item['open_id'] = json_id(item.pop('_id'))
        item['org'] = ctrl_org.simple_read(item['org'])

        array.append(item)

    return array, Employment.display


def employ_passports(system, *auth_args):
    """
    获取员工所在组织的通证列表
    :param system: 系统名称
    :param auth_args: 鉴权参数：(signed, nonce), 即("签名的授权字符串", "临时一致性标示，需与生成签名时使用的nonce相同")
    :return:
    """
    nonce = auth_args[1]

    # 授权检查, 被查询组织必须是身份认证的组织
    idt = Employment().verify(*auth_args)
    org_node = idt.node
    # END

    return _query_passports(org_node, system, nonce)


def query_customer_passports(system, oid, uid, access_token):
    """
    客户加入会员且获取会员所在会员组的通证列表
    :param system: 系统名称
    :param oid: 组织ID
    :param uid: 用户ID
    :param access_token: 用户登录UCenter后获取的访问token
    :return:
    """
    ret = dict()
    if uid is not None and access_token is not None:
        o2u = _get_membership(oid, uid, access_token)
        org_node = o2u['org_node']
        ret['vip'] = o2u['org']
    else:
        o = _get_app_org(oid)
        org_node = o['node']
        access_token = None
    passports, display = _query_passports(org_node, system, access_token)
    ret['list'] = passports
    return ret


def _get_app_org(oid):
    o = ctrl_org.simple_read(oid)
    owner_oid = o.get('owner')
    if owner_oid is None:
        customer_oid = o.get('customer_org')
        if customer_oid is None:
            raise ErrException(ERROR.E40300, extra='the appid is invalid: %s' % oid)

        oid = customer_oid
        o = ctrl_org.simple_read(oid)
    return o


def _get_membership(oid, uid, access_token):
    """
    获取VIP会员信息，如果没有注册会员，默认会添加到level=0的vip组中
    :param oid: 组织ID, 或者组织的客户组ID
    :param uid: 用户ID
    :param access_token: 用户登录UCenter后获取的访问token
    """
    o = _get_app_org(oid)
    oid = o['oid']

    node = o['node']

    u = ctrl_user.get(uid)
    if u is None:
        raise ErrException(ERROR.E40000, extra='invalid user [%s]' % uid)

    uid = u['id']
    user = {
        'uid': bson_id(uid),
        'name': u.get('name'),
        'nickname': u.get('nickname'),
        'email': u.get('email'),
        'mobile': u.get('mobile'),
        'icon': u.get('icon')
    }

    o2u = db.org2user.find_one({
        'membership': {'$exists': True},
        'org_node': {'$regex': r'^{}'.format(node)},
        'user.uid': bson_id(uid)
    }, {'user': 0})

    if o2u is None:
        # 查询会员组下子组列表，且取排序最小的org；如果没有则直接使用会员组org，即会员不分级
        vip_org = db.org.find_one({'parent': bson_id(oid), 'status': {'$gte': 0}})
        if vip_org is None:
            vip_org = o
            vip_org['_id'] = bson_id(vip_org['oid'])

        # 如果没有，则将用户添加到level为0的会员组中
        now = time.millisecond()
        result = db.org2user.insert_one({
            "org": vip_org['_id'],
            "org_node": vip_org['node'],
            "membership": Membership().text,
            "user": user,
            "created": now,
            "updated": now
        })
        o2u = db.org2user.find_one(result.inserted_id, {'user': 0})

    o2u['member_id'] = json_id(o2u.pop('_id'))
    o2u['org'] = ctrl_org.simple_read(o2u['org'])

    idt = Membership().parse(o2u.pop('membership'))
    o2u['membership'] = idt.json
    o2u['signed_membership'] = idt.signed(o2u['org_node'], uid, access_token)

    return o2u


def _query_passports(org_node, system, nonce):
    o = ctrl_org.read_with_node(org_node)
    oid = o['oid']

    cursor = db.catalog2org.find({'org': bson_id(oid)}, {'_id': 0, 'org': 0})

    array = list()
    for item in cursor:
        if nonce is not None:
            if 'passport' not in item:
                continue

            pp = Passport(system).parse(item['passport'])
            # 没有任何有效权限
            if len(pp.json) == 0:
                continue

            item['signed_passport'] = pp.signed(item['catalog_node'], oid, nonce)
            item['passport'] = pp.json
        else:
            if 'anon_passport' not in item:
                continue

            pp = Passport(system).parse(item['anon_passport'])
            # 没有任何有效权限
            if len(pp.json) == 0:
                continue

            item['signed_passport'] = pp.signed(item['catalog_node'], None, None)
            item['anon_passport'] = pp.json

        item['catalog'] = ctrl_catalog.simple_read(item['catalog'])

        array.append(item)

    return array, Passport(system).display
