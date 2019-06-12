# coding:utf-8

from ..db import mongo as db
from tweb.error_exception import ErrException, ERROR
from tweb import time
from ..utils.bson_util import bson_id, json_id
from ..service import ctrl_catalog, ctrl_org
from ..passport import Passport


def passport_create(cid, oid, passport_json, is_anon, *auth_args):
    """
    分类与组织建立绑定关系
    :param cid: 分类节点ID
    :param oid: 组织ID
    :param passport_json: 授权描述信息
    :param is_anon: 是否是匿名授权, 0: 否， 1: 是
    :param auth_args: 鉴权参数：(signed, nonce), 即("签名的授权字符串", "临时一致性标示，需与生成签名时使用的nonce相同")
    :return:
    """
    c = ctrl_catalog.simple_read(cid)

    # 授权检查
    pp = Passport().verify(*auth_args)
    # END

    with db.start_session() as s:
        s.start_transaction()
        # begin
        node = c['node']
        cursor = db.catalog2org.find({'org': bson_id(oid)}, {'org': 0})
        for item in cursor:
            other = item['catalog_node']
            # 如果已经授权或者授权给父节点，则无需再授权
            if node.find(other) == 0:
                raise ErrException(ERROR.E40020, extra=f'org({oid}) has got passport at catalog({other})')

            # 如果已经授权该组织给下级节点，则首先删除，再添加（相当于移动，升级到更高级资源节点）
            if other.find(node) == 0:
                db.catalog2org.delete_one({'catalog': item['catalog'], 'org': bson_id(oid)}, session=s)

        now = time.millisecond()
        passport_text = Passport().update(node, oid, passport_json, pp).text
        new_data = {
            "catalog": bson_id(cid),
            "catalog_node": node,
            "org": bson_id(oid),
            "created": now,
            "updated": now
        }
        if is_anon:
            new_data['anon_passport'] = passport_text
        else:
            new_data['passport'] = passport_text

        db.catalog2org.insert_one(new_data, session=s)
        # end
        s.commit_transaction()

    return passport_read(cid, oid)


def passport_read(cid, oid):
    c2o = db.catalog2org.find_one({'catalog': bson_id(cid), 'org': bson_id(oid)}, {'_id': 0})
    if c2o is None:
        raise ErrException(ERROR.E40400)

    c2o['catalog'] = json_id(c2o['catalog'])
    c2o['org'] = ctrl_org.simple_read(c2o['org'])

    if 'passport' in c2o:
        pp = Passport().parse(c2o['passport'])
        c2o['passport'] = pp.json
    if 'anon_passport' in c2o:
        pp = Passport().parse(c2o['anon_passport'])
        c2o['anon_passport'] = pp.json

    c2o['passport_display'] = Passport().display

    return c2o


def passport_update(cid, oid, passport_json, is_anon, *auth_args):
    """
    更新组织对分类以及分类下资源的授权
    :param cid: 分类节点ID
    :param oid: 组织ID
    :param passport_json: 授权描述信息
    :param is_anon: 是否是匿名授权, 0: 否， 1: 是
    :param auth_args: 鉴权参数：(signed, nonce), 即("签名的授权字符串", "临时一致性标示，需与生成签名时使用的nonce相同")
    :return:
    """
    # 授权检查
    pp = Passport().verify(*auth_args)
    # END

    return simple_update(cid, oid, passport_json, is_anon, pp)


def simple_update(cid, oid, passport_json, is_anon=0, my_passport=None):
    """
    更新组织对分类以及分类下资源的授权
    :param cid: 分类节点ID
    :param oid: 组织ID
    :param passport_json: 授权描述信息
    :param is_anon: 是否是匿名授权, 0: 否， 1: 是
    :param my_passport: 操作者的通证，授权范围不能超过此限制
    :return:
    """
    c = ctrl_catalog.simple_read(cid)

    c2o = db.catalog2org.find_one({'catalog': bson_id(cid), 'org': bson_id(oid)})
    if c2o is None:
        raise ErrException(ERROR.E40400)

    temp = dict()
    if is_anon:
        pp = Passport().parse(c2o.get('anon_passport'))
        temp['anon_passport'] = pp.update(c['node'], oid, passport_json, my_passport).text
    else:
        pp = Passport().parse(c2o.get('passport'))
        temp['passport'] = pp.update(c['node'], oid, passport_json, my_passport).text

    temp['updated'] = time.millisecond()
    db.catalog2org.update_one({'_id': c2o['_id']}, {'$set': temp})

    return passport_read(cid, oid)


def passport_remove(cid, oid, *auth_args):
    """
    解除分类与组织的关系
    :param cid: 分类节点ID
    :param oid: 组织ID
    :param auth_args: 鉴权参数：(signed, nonce), 即("签名的授权字符串", "临时一致性标示，需与生成签名时使用的nonce相同")
    :return:
    """
    c = ctrl_catalog.simple_read(cid)

    # 授权检查
    Passport().verify(*auth_args).operable(c['node'], 'catalog.remove')
    # END

    # 使已签名的授权无效
    Passport.invalidate_signed(c['node'], oid)

    # 最后删除记录
    db.catalog2org.delete_one({'catalog': bson_id(cid), 'org': bson_id(oid)})

    return {}


def passports_query(cid):
    """
    获取分类节点的被授权的组织列表
    :param cid:
    :return:
    """
    cursor = db.catalog2org.find({'catalog': bson_id(cid)}, {'_id': 0, 'catalog': 0})
    array = list()
    for item in cursor:
        item['org'] = ctrl_org.simple_read(item['org'])
        if 'passport' in item:
            pp = Passport().parse(item['passport'])
            item['passport'] = pp.json
        if 'anon_passport' in item:
            pp = Passport().parse(item['anon_passport'])
            item['anon_passport'] = pp.json

        array.append(item)

    return array, Passport().display
