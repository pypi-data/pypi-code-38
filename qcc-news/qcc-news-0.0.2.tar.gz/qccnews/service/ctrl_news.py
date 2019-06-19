# coding:utf-8

from ..db import mongo as db
from tweb.json_util import filter_keys
from tweb.error_exception import ErrException, ERROR
from tweb import time
from webmother.utils.bson_util import bson_id, json_id
from webmother.service import ctrl_catalog
from webmother.passport import Passport


# 分类节点状态以及状态迁移定义
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


async def create(cid, news_data, *auth_args):
    c = ctrl_catalog.simple_read(cid)

    # 授权检查
    Passport().verify(*auth_args).operable(c.get('node'), 'news.create')
    # END

    if c['status'] not in [ctrl_catalog.Status.sleeping, ctrl_catalog.Status.activated]:
        raise ErrException(ERROR.E40300, extra='can not add something into catalog because it not audited')

    title = news_data.get('title')
    pub_time = news_data.get('time')
    if db.news.find_one({'title': title, 'time': pub_time, 'status': {'$gte': 0}}) is not None:
        raise ErrException(ERROR.E40020)

    news_data['catalog'] = bson_id(cid)
    news_data['status'] = Status.default

    now = time.millisecond()
    news_data['created'] = now
    news_data['updated'] = now

    result = db.news.insert_one(news_data)
    return simple_read(result.inserted_id)


async def read(news_id):
    # 授权检查
    min_stat = Status.activated
    # END

    return simple_read(news_id, min_stat)


def simple_read(news_id, min_stat=0):
    p = db.news.find_one({'_id': bson_id(news_id), 'status': {'$gte': min_stat}}, {'catalog': 0})
    if p is None:
        raise ErrException(ERROR.E40400, extra=f'the news({news_id}) not existed')

    p['news_id'] = json_id(p.pop('_id'))

    return p


async def update(cid, news_id, news_data, *auth_args):
    """
    修改新闻文章信息
    :param cid: 新闻文章所属分类节点ID
    :param news_id: 新闻文章id
    :param news_data: 新闻文章信息
    :param auth_args: 鉴权参数：(signed, nonce), 即("签名的授权字符串", "临时一致性标示，需与生成签名时使用的nonce相同")
    :return:
    """
    c = ctrl_catalog.simple_read(cid)

    # 授权检查
    Passport().verify(*auth_args).operable('{}/*'.format(c.get('node')), 'news.update')
    # END

    p = simple_read(news_id)
    if p is None:
        raise ErrException(ERROR.E40400, extra='wrong news id')

    if p['status'] not in (Status.editing, Status.auditing, Status.sleeping, Status.activated):
        raise ErrException(ERROR.E40021)

    new_data = filter_keys(news_data, {
        'title': 1,
        'time': 1,
        'origin': 1,
        'tags': 1,
        'desc': 1,
        'content': 1
    })

    new_data['status'] = Status.default
    new_data['updated'] = time.millisecond()

    db.news.update_one({'_id': bson_id(news_id)}, {'$set': new_data})
    return simple_read(news_id)


async def change_status(cid, news_id, action, *auth_args):
    """
    :param cid: 新闻文章所属分类节点ID
    :param news_id: 新闻文章id
    :param action: 操作（提交，过审，驳回，上架，下架，删除等）
    :param auth_args: 鉴权参数：(signed, nonce), 即("签名的授权字符串", "临时一致性标示，需与生成签名时使用的nonce相同")
    :return:
    """
    c = ctrl_catalog.simple_read(cid)

    # 授权检查
    Passport().verify(*auth_args).operable('{}/*'.format(c.get('node')), f'news.{action}')
    # END

    p = simple_read(news_id)
    if p is None:
        raise ErrException(ERROR.E40400, extra='wrong news id')

    cur_status = p.get('status')
    new_status = Status.trans(cur_status, action)

    new_data = {
        'status': new_status,
        'updated': time.millisecond()
    }

    db.news.update_one({'_id': bson_id(news_id)}, {'$set': new_data})

    return {'id': news_id, 'status': new_status, 'old_status': cur_status}


async def move(cid, news_id, cid_to, *auth_args):
    """
    把cid节点下的news_id新闻文章移到cid_to标示的节点之下
    :param cid: 原节点ID
    :param news_id: 新闻文章ID
    :param cid_to: 新节点ID
    :param auth_args: 鉴权参数：(signed, nonce), 即("签名的授权字符串", "临时一致性标示，需与生成签名时使用的nonce相同")
    :return:
    """
    c = ctrl_catalog.simple_read(cid)
    c_to = ctrl_catalog.simple_read(cid_to)

    if cid == cid_to:
        raise ErrException(ERROR.E40000, extra='the same node, not need move')

    # 授权检查
    Passport().verify(*auth_args).operable('{}/*'.format(c['node']), 'news.remove')
    Passport().verify(*auth_args).operable('{}/*'.format(c_to['node']), 'news.create')
    # END

    p = simple_read(news_id)
    if p['status'] not in (Status.editing, Status.auditing, Status.sleeping, Status.activated):
        raise ErrException(ERROR.E40021)

    now = time.millisecond()

    tmp_p = {
        'catalog': bson_id(cid_to),
        'updated': now
    }

    db.news.update_one({'_id': bson_id(news_id)}, {'$set': tmp_p})

    return simple_read(news_id)


async def query_news(cid, page_no, page_size):
    # 授权检查
    min_stat = Status.activated
    # END

    skip = (page_no - 1) * page_size
    cond = {
        'catalog': bson_id(cid),
        'status': {'$gte': min_stat}
    }
    cursor = db.news.find(cond, {'catalog': 0}).skip(skip).limit(page_size)

    array = list()
    for item in cursor:
        item['news_id'] = json_id(item.pop('_id'))

        array.append(item)

    return array, cursor.count()
