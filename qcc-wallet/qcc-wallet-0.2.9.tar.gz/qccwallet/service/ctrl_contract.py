# coding:utf-8

from tweb.error_exception import ErrException, ERROR
from tweb import time
from webmother.utils.bson_util import bson_id, json_id
from webmother.service import ctrl_catalog
from webmother.passport import Passport
from .internal import ethereum as in_ethereum
from .external import ethereum as ex_ethereum
from ..db import mongo as db


class Status:
    removed = -10  # 已删除
    sleeping = 0  # 休眠中
    activated = 10  # 活动中

    default = activated

    status_map = {
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


def query_contracts(cid, page_no, page_size, *auth_args):
    """
    查询某区块链下已注册的合约列表
    """
    # c = ctrl_catalog.simple_read(cid)

    # 授权检查
    # Passport().verify(*auth_args).operable('{}/*'.format(c.get('node')), 'contract.read')
    # END

    skip = (page_no - 1) * page_size
    cursor = db.contract.find({
        'catalog': bson_id(cid),
        'status': {'$gte': 0}
    }, {'catalog': 0}).skip(skip).limit(page_size)

    array = list()
    for item in cursor:
        item[f'contract_id'] = json_id(item.pop('_id'))
        array.append(item)
    return array, cursor.count()


def register(cid, data, *auth_args):
    c = ctrl_catalog.simple_read(cid)

    # 授权检查
    Passport().verify(*auth_args).operable('{}/*'.format(c.get('node')), 'contract.create')
    # END

    chain_name = c['name']
    if chain_name not in ['eth']:
        raise ErrException(ERROR.E40000, 'unknown chain name % about id %s' % (chain_name, cid))

    supported = ['main', 'ERC20']

    t = data['type']
    if t not in supported:
        raise ErrException(ERROR.E40000, extra='only support type of %s' % supported)

    now = time.millisecond()
    w = {
        "catalog": bson_id(cid),
        "icon": data.get('icon'),
        "type": t,
        "status": Status.default,
        "created": now,
        "updated": now
    }
    if 'icon' in data:
        w['icon'] = data['icon']
    if t != 'main':
        # 是合约，则增加合约spec
        spec = data['spec']
        if spec is None:
            raise ErrException(ERROR.E40000, extra='no spec field')
        contract_address = spec.get('address').lower()
        if not in_ethereum.is_address(contract_address):
            raise ErrException(ERROR.E40000, extra='invalid contract address')

        if chain_name == 'eth':
            abi = spec.get('data')
            if abi is None:
                raise ErrException(ERROR.E40000, extra='need abi for eth')
            # 校验是否为合法合约参数
            if not in_ethereum.get_contract(contract_address, abi):
                raise ErrException(ERROR.E40000, extra='wrong contract params')

        w['spec'] = {
            'address': contract_address,
            'data': spec.get('data')
        }

        # 保证合约地址不重复
        existed = db.contract.find_one({'spec.address': contract_address, 'status': {'$gte': 0}})
        if existed is not None:
            raise ErrException(ERROR.E40020, extra='existed about the contract address: %s' % contract_address)

        w['name'] = ex_ethereum.contract_call(w, 'name', [])
        w['symbol'] = ex_ethereum.contract_call(w, 'symbol', []).upper()
        w['decimals'] = int(ex_ethereum.contract_call(w, 'decimals', []))

    else:
        if chain_name == 'eth':
            w['name'] = 'Ethereum'
            w['symbol'] = 'ETH'
            w['decimals'] = 18

        existed = db.contract.find_one({'catalog': bson_id(cid), 'type': t, 'status': {'$gte': 0}},
                                       {'catalog': 0})
        if existed is not None:
            existed[f'contract_id'] = json_id(existed.pop('_id'))
            return existed

    result = db.contract.insert_one(w)
    ret = db.contract.find_one(result.inserted_id, {'catalog': 0})
    ret[f'contract_id'] = json_id(ret.pop('_id'))

    return ret


def unregister(cid, contract_id, *auth_args):
    c = ctrl_catalog.simple_read(cid)

    # 授权检查
    Passport().verify(*auth_args).operable('{}/*'.format(c.get('node')), 'contract.remove')
    # END

    db.contract.update_one({'_id': bson_id(contract_id)}, {'$set': {'status': Status.removed}})

    return {}


def read(cid, contract_id, *auth_args):
    # c = ctrl_catalog.simple_read(cid)

    # 授权检查
    # Passport().verify(*auth_args).operable('{}/*'.format(c.get('node')), 'contract.read')
    # END

    return simple_read(contract_id)


def simple_read(contract_id):
    ret = db.contract.find_one({'_id': bson_id(contract_id)})
    if ret is None:
        raise ErrException(ERROR.E40400, extra='eth contract not registered: %s' % contract_id)

    ret[f'contract_id'] = json_id(ret.pop('_id'))
    ret['catalog'] = ctrl_catalog.simple_read(ret['catalog'])

    return ret


def get_main_of_chain(cid):
    existed = db.contract.find_one({'catalog': bson_id(cid), 'type': 'main', 'status': {'$gte': 0}},
                                   {'catalog': 0})
    if existed is None:
        raise ErrException(ERROR.E40400, extra='no main contract registered of %s' % cid)

    existed[f'contract_id'] = json_id(existed.pop('_id'))
    return existed


def get_main_of_contract(contract_id):
    contract = simple_read(contract_id)
    cid = contract['catalog']['cid']
    existed = db.contract.find_one({'catalog': bson_id(cid), 'type': 'main', 'status': {'$gte': 0}},
                                   {'catalog': 0})
    if existed is None:
        raise ErrException(ERROR.E40400, extra='no main contract registered of %s' % cid)

    existed[f'contract_id'] = json_id(existed.pop('_id'))
    return existed
