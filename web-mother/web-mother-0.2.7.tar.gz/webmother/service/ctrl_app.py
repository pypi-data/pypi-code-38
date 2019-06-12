# coding:utf-8

from ..db import mongo as db
from tweb.error_exception import ErrException, ERROR
from tweb import time
from ..utils.bson_util import bson_id, json_id
from ..employment import Employment
from ..service.ctrl_org import simple_create, simple_read, Status

internal_org_name = ['vip']


def open_customer_org(oid, data, *auth_args):
    o = simple_read(oid)
    node = o['node']

    # 授权检查
    Employment().verify(*auth_args).operable('{}/*'.format(node), 'app.open', 'org.create')
    # END

    if o['status'] not in (Status.editing, Status.auditing, Status.sleeping, Status.activated):
        raise ErrException(ERROR.E40021)

    existed_customer_oid = o.get('customer_org')
    if existed_customer_oid is not None:
        ret = simple_read(existed_customer_oid)
        return ret

    customer_oid = json_id(data.get('oid'))
    with db.start_session() as s:
        s.start_transaction()

        existed = db.org.find_one({'_id': bson_id(customer_oid), 'status': {'$gte': 0}})
        if existed is not None:
            # 如果是绑定已经存在的组织作为会员管理组，则必须是其子组织
            if existed['parent'] != bson_id(oid):
                raise ErrException(ERROR.E40000, extra='current org is not parent of the org[%s]' % customer_oid)
        else:
            existed = db.org.find_one({'parent': bson_id(oid),
                                       'node': '{}/customer'.format(node),
                                       'status': {'$gte': 0}})
            if existed is None:
                # 按默认参数添加组织作为会员管理组
                customer_org = {
                    'oid': customer_oid,
                    'name': data.get('name', 'customer'),
                    'display': data.get('display', {'zh': '会员管理', 'en': 'Member Manage'}),
                    'owner': oid
                }
                simple_create(oid, customer_org, session=s)
            else:
                customer_oid = json_id(existed['_id'])

                new_data = {
                    'owner': bson_id(oid),
                    'updated': time.millisecond()
                }
                db.org.update_one({'_id': bson_id(customer_oid)}, {'$set': new_data}, session=s)

        new_data = {
            'customer_org': bson_id(customer_oid),
            'updated': time.millisecond()
        }
        db.org.update_one({'_id': bson_id(oid)}, {'$set': new_data}, session=s)

        s.commit_transaction()

    ret = simple_read(customer_oid)
    return ret


def close_customer_org(oid, *auth_args):
    o = simple_read(oid)
    node = o['node']

    # 授权检查
    Employment().verify(*auth_args).operable('{}/*'.format(node), 'app.close')
    # END

    customer_oid = o['customer_org']
    if customer_oid is not None:
        with db.start_session() as s:
            s.start_transaction()

            new_data = {
                'customer_org': None,
                'updated': time.millisecond()
            }
            db.org.update_one({'_id': bson_id(oid)}, {'$set': new_data}, session=s)

            new_data = {
                'owner': None,
                'updated': time.millisecond()
            }
            db.org.update_one({'_id': bson_id(customer_oid)}, {'$set': new_data}, session=s)

            s.commit_transaction()

    return {}
