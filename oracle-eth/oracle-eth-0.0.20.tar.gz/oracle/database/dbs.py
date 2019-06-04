# -*- coding: utf-8 -*-

"""
存放的是数据库的CRUD操作
"""

from datetime import datetime
from datetime import timedelta
import json
import peewee
from oracle.setting import VAR
from oracle.database.modles import (
    Person, PersonDc, Soldiers, Keys, Contract, Events, Army, Organization, db, Account, QueueFlow, OrganizationDid
)
from oracle import utils
from oracle.logger import logger
from oracle.exceptions import ContractError
from pycontractsdk.keys import value_to_hex
from oracle.database import status


@db.atomic()
def example_atomic():
    """ 包装器，这个方法是原子的 """
    pass


def example_transaction():
    """ 显示的事务 """
    with db.transaction() as txn:
        Person.create(name='yuyongpeng')
        txn.commit()
        Person.create(name='yuyongpeng2')
        txn.rollback()
    pass


def is_exist_soldier(encrypted_string):
    """
    查询军人的身份信息是否存在于数据库中
    :param encrypted_string:  加密后的身份信息
    :return: 如果查询到了信息就返回True，如果没有查询到就返回False
    """
    count = Soldiers.select().where(encrypted_string == encrypted_string).count()
    if count == 1:
        return True
    else:
        return False


def get_soldier(encrypted_string):
    """ 获得士兵的信息 """
    return Soldiers.get_or_none(encrypted_string=encrypted_string)


def save_soldier(soldier):
    """ 保存士兵的信息 """
    soldier.save()


def query_keys(machine):
    """
    如果数据库中存在这个machine，就直接返回这条数据
    如果数据库中不存在这个machine，就取出一条没有使用的数据，更新状态后返回
    :return: Key对象
    """
    key = Keys.select().where(Keys.machine == machine.strip())
    if len(key) == 1:
        # 如果有数据，就直接使用这条数据
        return key[0]
    if len(key) == 0:
        with db.transaction() as txn:
            # 没有数据，需要得到一条没有使用的key，标识为自己的机器id
            keys = Keys.select().where(Keys.status == 0, ((Keys.machine.is_null()) | (Keys.machine == ''))).limit(1).for_update()
            if len(keys) == 0:
                logger.error("***********************************************************")
                logger.error("* 数据库中没有可使用的key, 程序没法启动，请查看cp_keys表中的数据 *")
                logger.error("***********************************************************")
                exit(2)
            ky = keys[0]
            ky.machine = machine
            ky.status = 1
            ky.updates = datetime.now()
            ky.save()
        return ky
    if len(key) > 1:
        raise ValueError('Table keys where machine=%s count > 1', machine)
    # return key


def query_contract():
    """ 获得一条协约数据 """
    contract = Contract.select().where(Contract.status == 0)
    if len(contract) == 1:
        return contract[0]
    if len(contract) == 0:
        raise ContractError('can not find contract in database')
    if len(contract) > 1:
        raise ContractError('The contract obtained from the database is greater than 1')


def save_event(entry):
    """
    保存event
    :param entry:
    :return:
    """
    args = entry['args']
    event_name = entry['event']
    log_index = entry['logIndex']
    transaction_index = entry['transactionIndex']
    transaction_hash = value_to_hex(entry['transactionHash'])
    address = entry['address']
    block_hash = value_to_hex(entry['blockHash'])
    block_number = entry['blockNumber']
    # 根据table中的唯一索引来查询
    # 先插入数据，如果抛出了唯一索引的异常，就直接更新数据
    print(entry)
    try:
        with db.atomic():
            event = Events.create(
                args=str(args),
                event_name=event_name,
                log_index=log_index,
                transaction_index=transaction_index,
                transaction_hash=transaction_hash,
                address=address,
                block_hash=block_hash,
                block_number=block_number,
            )
        return event
    except peewee.IntegrityError:
        # `username` is a unique column, so this username already exists,
        # making it safe to call .get().
        # query = Events.update(
        #     args=str(args),
        #     log_index=log_index,
        #     address=address,
        #     block_hash=block_hash,
        #     block_number=block_number,
        #     updates=datetime.datetime.now(),
        # ).where(
        #     Events.event_name == event_name,
        #     Events.transaction_index == transaction_index,
        #     Events.transaction_hash == transaction_hash,
        # )
        # query.execute()
        event = Events.get(
            Events.args == str(args),
            Events.event_name == event_name,
            Events.log_index == log_index,
            Events.transaction_hash == transaction_hash,
            Events.address == address,
            Events.block_hash == block_hash,
            Events.block_number == block_number
        )
        event.updates = datetime.now()
        event.save()
        return event
    # 这种实现方式不好 ，没有都会先查询
    # event = Events.get_or_none(
    #     event_name=event_name,
    #     transaction_index=transaction_index,
    #     transaction_hash=transaction_hash,
    # )
    # if event is None:
    #     Events.create(
    #         args=str(args),
    #         event_name=event_name,
    #         log_index=log_index,
    #         transaction_index=transaction_index,
    #         transaction_hash=transaction_hash,
    #         address=address,
    #         block_hash=block_hash,
    #         block_number=block_number,
    #     )
    # else:
    #     event.updates = datetime.datetime.now()
    #     event.save()


def save_army(entry):
    """
    保存军队使用的event
    :param entry:
    :return:
    """
    datas = utils.EventToJson(entry)
    args = entry['args']
    identity = args['identity']                         # event 参数 identity 的数据
    name = args['name'].strip(b'\x00')                  # event 参数 name 的数据
    value = args['value']                               # event 参数 value 的数据 (did + \n + 签名信息)
    sign_text_bytes = value.split(b'\n')[-1]            # 第一个 签名信息
    did_json_bytes = b''.join(value.split(b'\n')[:-1])  # did 信息 bytes
    did_json_obj = json.loads(did_json_bytes.decode())  # did json对象

    event_name = entry['event']
    log_index = entry['logIndex']
    transaction_index = entry['transactionIndex']
    transaction_hash = value_to_hex(entry['transactionHash'])
    address = entry['address']
    block_hash = value_to_hex(entry['blockHash'])
    block_number = entry['blockNumber']
    # 根据table中的唯一索引来查询
    # 先插入数据，如果抛出了唯一索引的异常，就直接更新数据
    print(entry)
    try:
        with db.atomic():
            event = Army.create(
                datas=json.dumps(datas),
                args=str(args),
                identity=identity,
                event_name=event_name,
                log_index=log_index,
                transaction_index=transaction_index,
                transaction_hash=transaction_hash,
                address=address,
                block_hash=block_hash,
                block_number=block_number,
                first_sign=sign_text_bytes.decode(),
                did_json=did_json_bytes.decode(),
                created=did_json_obj['created'],
                created2=datetime.fromtimestamp(int(did_json_obj['created'] / 1000)),
                did_id=did_json_obj['id']
            )
        return event
    except peewee.IntegrityError as e:
        print(e)
        event = Army.get(
            # Army.args == str(args),
            Army.event_name == event_name,
            # Army.log_index == log_index,
            Army.transaction_hash == transaction_hash,
            Army.transaction_index == transaction_index,
            # Army.address == address,
            # Army.block_hash == block_hash,
            # Army.block_number == block_number
        )
        event.updates = datetime.now()
        event.save()
        # event.update()
        return event


def get_army_datas():
    """
    从 army 数据库中获得没有完成数据的datas字段的值
    :return:
    """
    dates = datetime.now() - timedelta(hours=1)
    return Army.select().where(Army.status.in_((status.EVENT_NORMAL,
                                status.EVENT_SIGN_VERI_SUCCESS,
                                status.EVENT_DECRYPTION_SUCCESS,
                                status.EVENT_ETHEREUM_SUBMIT_FAILED,
                                status.EVENT_VERI_COMP)), Army.created2<dates)


def save_organization(entry):
    """
    保存 机构 使用的event
    :param entry: event数据
    :return: 返回到数据库的这个实例
    """
    args = entry['args']
    identity = args['identity']                         # event 参数 identity 的数据
    name = args['name'].strip(b'\x00')                  # event 参数 name 的数据
    value = args['value']                               # event 参数 value 的数据 (did + \n + 签名信息)
    first_sign_text_bytes = value.split(b'\n')[-2]      # 第一次的签名信息 （个人用户）
    sencond_sign_text_bytes = value.split(b'\n')[-1]    # 第二次的签名信息 （军队）
    did_json_bytes = b''.join(value.split(b'\n')[:-2])  # did 信息 byte
    did_json_obj = json.loads(did_json_bytes.decode())  # did json对象
    event_name = entry['event']
    log_index = entry['logIndex']
    transaction_index = entry['transactionIndex']
    transaction_hash = value_to_hex(entry['transactionHash'])
    address = entry['address']
    block_hash = value_to_hex(entry['blockHash'])
    block_number = entry['blockNumber']
    # 根据table中的唯一索引来查询
    # 先插入数据，如果抛出了唯一索引的异常，就直接更新数据
    # logger.info(entry)
    try:
        with db.atomic():
            event = Organization.create(
                args=str(args),
                identity=identity,
                event_name=event_name,
                log_index=log_index,
                transaction_index=transaction_index,
                transaction_hash=transaction_hash,
                address=address,
                block_hash=block_hash,
                block_number=block_number,
                did_json=did_json_bytes.decode(),
                first_sign=first_sign_text_bytes.decode(),
                second_sign=sencond_sign_text_bytes.decode(),
                created=did_json_obj['created'],
                did_id=did_json_obj['id'],
                mark=name
            )
        return event
    except peewee.IntegrityError as e:
        logger.error(e)
        event = Organization.get(
            # Organization.args == str(args),
            Organization.event_name == event_name,
            # Organization.log_index == log_index,
            Organization.transaction_hash == transaction_hash,
            Organization.transaction_index == transaction_index,
            # Organization.address == address,
            # Organization.block_hash == block_hash,
            # Organization.block_number == block_number
        )
        event.updates = datetime.now()
        event.save()
        return event


def save_organization_did(entry):
    """
    保存 机构 验证通过的数据
    :param entry: event数据
    :return: 返回到数据库的这个实例
    """
    args = entry['args']
    identity = args['identity']                         # event 参数 identity 的数据
    name = args['name'].strip(b'\x00')                  # event 参数 name 的数据
    value = args['value']                               # event 参数 value 的数据 (did + \n + 签名信息 + \n + 签名信息)
    first_sign_text_bytes = value.split(b'\n')[-2]      # 第一次的签名信息 （个人用户）
    sencond_sign_text_bytes = value.split(b'\n')[-1]    # 第二次的签名信息 （军队）
    did_json_bytes = b''.join(value.split(b'\n')[:-2])  # did 信息 byte
    did_json_obj = json.loads(did_json_bytes.decode())  # did json对象
    event_name = entry['event']
    log_index = entry['logIndex']
    transaction_index = entry['transactionIndex']
    transaction_hash = value_to_hex(entry['transactionHash'])
    address = entry['address']
    block_hash = value_to_hex(entry['blockHash'])
    block_number = entry['blockNumber']

    # 根据table中的唯一索引来查询
    # 先插入数据，如果抛出了唯一索引的异常，就直接更新数据
    # print(entry)
    if len(str(did_json_obj['created'])) == 13:
        created = datetime.fromtimestamp(did_json_obj['created'] / 1000)
    if len(str(did_json_obj['created'])) == 10:
        created = datetime.fromtimestamp(did_json_obj['created'])

    try:
        with db.atomic():
            OrganizationDid.create(
                args=str(args),
                identity=identity,
                event_name=event_name,
                log_index=log_index,
                transaction_index=transaction_index,
                transaction_hash=transaction_hash,
                address=address,
                block_hash=block_hash,
                block_number=block_number,
                first_sign=first_sign_text_bytes.decode(),
                second_sign=sencond_sign_text_bytes.decode(),
                did_json=did_json_bytes.decode(),
                created=created,
                did_id=did_json_obj['id'],      # 唯一索引
                # did_json_obj['id'].split()[-1] if len(did_json_obj['id'].split()) > 1 else '',
                mark=name

            )
    except peewee.IntegrityError as e:
        logger.error(e)
        query = OrganizationDid.update(
            args=str(args),
            event_name=event_name,
            log_index=log_index,
            transaction_index=transaction_index,
            transaction_hash=transaction_hash,
            address=address,
            block_hash=block_hash,
            block_number=block_number,
            updates=datetime.now(),
            first_sign=first_sign_text_bytes.decode(),
            second_sign=sencond_sign_text_bytes.decode(),
            did_json=did_json_bytes.decode(),
            created=did_json_obj['created'],
            did_id=did_json_obj['id'],
            identity=did_json_obj['id'].split()[-1] if len(did_json_obj['id'].split()) > 1 else ''
        ).where(
            Organization.did_id == did_json_obj['id']
        )
        query.execute()


def get_openid(address: str) -> str:
    """
    根据用户的address查询这个用户对应的openid
    :param address:
    :return:
    """
    with db.atomic():
        query = (Person.select(Person, Account).join(Account).where(Person.address == address))
        if query.count < 1:
            return None
        else:
            return query[0].account.weixin_openid



def save_person_dc(name: str, sign: str, identity: str, organization_hash: str = '',
                   organization_address: str = '') -> PersonDc:
    """
    保存数据到 person_dc 中
    :param name:
    :param sign:
    :param identity:
    :return:
    """
    persondc = PersonDc.create(value=name, person_hash=sign,
                    person_address=identity,
                    organization_hash=organization_hash,
                    organization_address=organization_address)
    return persondc

    pass

def update_complited(status: bool):
    """
    上链完成后调用，更新数据库的状态
    :param status: 需要更新的状态值
    :return:
    """
    # TODO: 需要和学文确定具体的表和列和状态值

    pass

def get_queue_flow(entity):
    """
    根据队列中的json串建立对象
    :param entity:
    :return:
    """
    obj = json.loads(entity)
    id = obj.get('queue_flow', 0)
    type = obj.get('type')
    retry = obj.get('retry', 0)
    upload_time = obj.get('upload_time', '')
    receipt = obj.get('receipt', '')
    if isinstance(entity, bytes):
        data = entity.decode()
    creates = datetime.now()
    updates = datetime.now()
    if id == 0:
        with db.atomic():
            queue = QueueFlow.create(
            type=type,
            retry=retry,
            upload_time=datetime.now() if upload_time is ''  else upload_time,
            receipt=receipt,
            data=data,
            creates=creates,
            updates=updates
            )
    else:
        queue = QueueFlow.get_by_id(id)
    return queue


def update_mysql(success, *args, **kwargs):
    """
    更新数据库的状态
    :param success:  True: 成功上链，False: 上链失败
    :param args:
    :param kwargs:
    :return:
    """
    ip = kwargs.pop('ip', VAR['MYSQL_IP'])
    port = kwargs.pop('port', VAR['MYSQL_PORT'])
    user = kwargs.pop('user', VAR['MYSQL_USER'])
    password = kwargs.pop('password', VAR['MYSQL_PASSWORD'])
    charset = VAR['MYSQL_CHARSET']
    schema = kwargs.pop('schema', VAR['MYSQL_SCHEMA'])
    table = kwargs.pop('table')
    column = kwargs.pop('column')
    id_column = kwargs.pop('id_column')
    id = kwargs.pop('id')
    db = peewee.MySQLDatabase(
        host=ip,
        database=schema,
        port=port,
        user=user,
        passwd=password,
        charset=charset
    )
    value = kwargs.pop('success_tag') if success else kwargs.pop('failed_tag')
    sql = "update {}.{} set {}=%s where {}=%s".format(schema, table, column, id_column)
    # sql = "update {}.{} set {}={} where {}={}".format(schema, table, column, value, id_column, id)
    print(sql)
    cursor = db.execute_sql(sql, (value, id))
    db.commit()
    cursor.close()
    db.close()














