# coding:utf-8

from config import MongoServer
import pymongo
from pymongo import ASCENDING, DESCENDING
from tweb import time
from .. import employment
from ..extra_passport import max_lic_text
from ucenter.db import mongo as uc_db
import logging

MongoCfg = {
    'authSource': 'ocdb',
    'username': 'app',
    'password': 'Octl2app',
    'connecttimeoutms': 60 * 1000
}

mongo_client = None
mongo_db = None

catalog = None
org = None
org2user = None
catalog2org = None


def init():
    if not MongoServer['active']:
        return

    global mongo_client
    global mongo_db
    global catalog
    global org
    global org2user
    global catalog2org

    if mongo_client is not None:
        return

    server = MongoServer['mongodb'].split(':')
    host = server[0]
    port = int(server[1]) if len(server) > 1 else 27017

    mongo_client = pymongo.MongoClient(host=host, port=port, **MongoCfg)
    mongo_db = mongo_client[MongoCfg['authSource']]

    # collections
    catalog = mongo_db.catalog
    org = mongo_db.org
    org2user = mongo_db.org2user
    catalog2org = mongo_db.catalog2org

    # 创建索引
    _catalog_index()
    _org_index()
    _org2user_index()
    _catalog2org_index()

    # 初始化系统数据
    _init_data()


def start_session():
    return mongo_client.start_session()


def _catalog_index():
    """
    {
        "_id": ObjectId("5c710622e155ac0c39c8b66d"),
        "parent": ObjectId('5c710a88e155ac0cae6b1edb'),  # 父目录的ID, 为空是表示是根节点
        "node": "root/cat1/mycat",                       # 节点标示，规则：代表了路径，eg. 根目录是root，父目录是root/cat1，当前目录是root/cat1/mycat
        "status": 30,                                    # 状态：-10:已删除；0:编辑中；10:待审；20:休眠中；30:已激活；
        "display": {
            "zh": "我的分类",
            "en": "My Catalog"
        },
        "icon": "http://your.com/icon/mycat.png",
        "created": 1550911010096,
        "updated": 1550911010096
    }
    """
    catalog.create_index('node')
    catalog.create_index([
        ('parent', ASCENDING),
        ("created", DESCENDING)
    ])


def _org_index():
    """
    {
        "_id": ObjectId('5c72aac2e155ac16da86a1d1'),
        "parent": ObjectId('5c72ab8fe155ac16da86a1d2'),  # 父组织ID，为空则表示是根组织
        "node": "root/udl/dev",                          # 节点标示，规则：代表了路径，eg. 根目录是root，父目录是root/cat1，当前目录是root/cat1/mycat
        "status": 30,                                    # 状态：-10:已删除；0:编辑中；10:待审；20:休眠中；30:已激活；
        "display": {
            "zh": "开发部",
            "en": "Dev department"
        },
        "desc": {
            "zh": "负责开发",
            "en": "Design and develop"
        },
        "icon": "http://your.com/icon/org.png",
        "customer_org": ObjectId('5cbc6d23e155ac68b7edac60'),  # 客户组ID
        "sort": 1,                  # 排序用
        "created": 1551018723088,
        "updated": 1551018723088
    }
    """
    org.create_index([('parent', ASCENDING), ("sort", ASCENDING), ("node", ASCENDING)])


def _org2user_index():
    """
    {
        "_id": ObjectId('5c738423e155ac16da86a1d3'),
        "org": ObjectId('5c72aac2e155ac16da86a1d1'),  # 组织ID
        "org_node": "udl/dev",                        # 组织节点名
        "user" : {
            "uid" : ObjectId("5c6519b3e155ac198ee63bac"),
            "name" : "admin",
            "nickname" : "Admin",
            "icon": "http://your.com/icon/admin.png"
        },
        "employment": 'member:0000;;|org:000000000;0;', # 身份授权记录
        "type": 0,                                    # 成员类型：0-管理类；1-客户类
        "created": 1551074938026
    }
    """
    org2user.create_index([('org', ASCENDING), ('user.uid', ASCENDING)])
    org2user.create_index([('user.uid', ASCENDING), ('org', ASCENDING)])
    org2user.create_index('org_node')


def _catalog2org_index():
    """
    {
        "_id": ObjectId('5c7385ede155ac16da86a1d5'),
        "catalog": ObjectId('5c710622e155ac0c39c8b66d'),        # 分类节点ID
        "catalog_node": "root/cat1/mycat",                      # 分类节点名
        "org": ObjectId('5c72aac2e155ac16da86a1d1'),            # 组织ID
        "passport": '0000000000000000000000000000000000000000',  # 许可证授权记录
        "created": 1551074929275,
        "updated": 1551074929275
    }
    """
    catalog2org.create_index([('catalog', ASCENDING), ('org', ASCENDING)])
    catalog2org.create_index([('org', ASCENDING), ('catalog', ASCENDING)])
    catalog2org.create_index('catalog_node')


def _init_data():
    now = time.millisecond()

    world_catalog = catalog.find_one({'node': 'world'})
    if world_catalog is None:
        result = catalog.insert_one({
            "_id": '0',
            "node": "world",
            "status": 30,
            "display": {
                "zh": "根",
                "en": "Root"
            },
            "created": now,
            "updated": now
        })
        world_catalog = catalog.find_one({'_id': result.inserted_id})

    god_org = org.find_one({'node': 'god'})
    if god_org is None:
        result = org.insert_one({
            "_id": "0",
            "node": "god",
            "status": 30,
            "display": {
                "zh": "系统管理",
                "en": "Administration"
            },
            "created": now,
            "updated": now
        })
        god_org = org.find_one({'_id': result.inserted_id})

    c2o = catalog2org.find_one({'catalog': world_catalog['_id'], 'org': god_org['_id']})
    if c2o is None:
        catalog2org.insert_one({
            "catalog": world_catalog['_id'],
            "catalog_node": world_catalog['node'],
            "org": god_org['_id'],
            "passport": max_lic_text,
            "created": now,
            "updated": now
        })

    # 从UC读取admin信息
    admin = uc_db.users.find_one({'name': 'admin'}, {'_id': 1, 'name': 1})
    if admin is not None:
        admin['uid'] = admin.pop('_id')

        # 只能保证有一个超级管理员, 如有则删除其他用户
        cursor = org2user.find(({'org': god_org['_id'], 'user.uid': {'$ne': admin['uid']}}))
        for item in cursor:
            org2user.delete_one({'org': god_org['_id'], 'user.uid': item['user']['uid']})

        o2u = org2user.find_one(({'org': god_org['_id'], 'user.uid': admin['uid']}))
        if o2u is None:
            org2user.insert_one({
                "org": god_org['_id'],
                "org_node": god_org['node'],
                "user": admin,
                "employment": employment.max_lic_text,
                "created": now,
                "updated": now
            })
    else:
        logging.warning('Please register admin in UC, then restart...')
