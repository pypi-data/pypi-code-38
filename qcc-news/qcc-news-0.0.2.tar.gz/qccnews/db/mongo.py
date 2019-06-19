# coding:utf-8

from config import MongoServer
import pymongo
from pymongo import ASCENDING, DESCENDING

MongoCfg = {
    'authSource': 'newsdb',
    'username': 'app',
    'password': 'News2app',
    'connecttimeoutms': 60 * 1000
}

# product DB
mongo_client = None
mongo_db = None

news = None


def init():
    if not MongoServer['active']:
        return

    global mongo_client
    global mongo_db

    global news

    if mongo_client is not None:
        return

    server = MongoServer['mongodb'].split(':')
    host = server[0]
    port = int(server[1]) if len(server) > 1 else 27017

    mongo_client = pymongo.MongoClient(host=host, port=port, **MongoCfg)
    mongo_db = mongo_client[MongoCfg['authSource']]

    # my collections
    news = mongo_db.news
    # END

    # 创建索引
    _news_index()

    # 初始化系统数据
    _init_data()


def start_session():
    return mongo_client.start_session()


def _news_index():
    """
    {
        "_id": ObjectId('5c729df2e155ac16da86a1d0'),
        "title": '', // 标题
        "time": '', // 时间
        "origin": '', // 来源
        "tags": [], // 标签
        "desc": '', // 描述
        "content": '' // 内容
        "created": 1551015331186,
        "updated": 1551015331186
    }
    """
    news.create_index('name')
    news.create_index([('title', ASCENDING), ("time", DESCENDING)], unique=True)


def _init_data():
    pass
