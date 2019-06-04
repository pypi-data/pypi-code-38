# -*- coding: utf-8 -*-

"""
存放的是数据库的模型
"""

# from peewee import *
from peewee import ForeignKeyField, Model, CharField, DateTimeField, IntegerField, TimestampField, AutoField
from oracle.setting import VAR
from playhouse.pool import PooledMySQLDatabase
import datetime

# 将peewee的操作输出详细的日志
import logging

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# url: mysql+pool://root:root@127.0.0.1:3306/appmanage?max_connections=300&stale_timeout=300
# db = connect(url=setting.MYSQL_URL)

# db = MySQLConnectorDatabase(
#     setting.MYSQL_SCHEMA,
#     host=setting.MYSQL_IP,
#     user=setting.MYSQL_USER,
#     password=setting.MYSQL_PASSWORD,
#     charset=setting.MYSQL_CHARSET )

# db = PooledMySQLDatabase(
#     setting.VAR['MYSQL_SCHEMA'],
#     host=setting.VAR['MYSQL_IP'],
#     user=setting.VAR['MYSQL_USER'],
#     password=setting.VAR['MYSQL_PASSWORD'],
#     charset=setting.VAR['MYSQL_CHARSET'],
#     max_connections=8,
#     stale_timeout=300)

# 放到后面通过 db.init()方式来初始化连接
# https://peewee.readthedocs.io/en/latest/peewee/database.html#run-time-database-configuration
db = PooledMySQLDatabase(None)


def make_table_name(model_class):
    """ 指定表的前缀 """
    model_name = model_class.__name__
    return VAR['MYSQL_TABLE_PRE'] + '_' + model_name.lower()


class BaseModel(Model):
    """A base model that will use our MySQL database"""

    class Meta:
        database = db
        table_function = make_table_name


class Soldiers(BaseModel):
    """
    退伍军人的hash信息
    """
    encrypted_string = CharField(column_name='encrypted_string', help_text='身份加密后的信息')
    verification_num = IntegerField(column_name='verification_num', help_text='验证的次数（目前没有使用）')
    update_time = DateTimeField(column_name='update_time', default=datetime.datetime.now, help_text='数据更新时间')
    create_time = DateTimeField(column_name='create_time', help_text='数据建立时间')


class Keys(BaseModel):
    """
    用于加密解密和签名的公钥，私钥信息
    """
    private_key = CharField(column_name='private_key', help_text='账号的私钥')
    public_key = CharField(column_name='public_key', help_text='账号对应的公钥')
    address = CharField(column_name='address', help_text='账号的address')
    status = IntegerField(column_name='status', help_text='账号的状态 数据的状态 0: 正常，1:删除')
    updates = DateTimeField(column_name='updates', default=datetime.datetime.now, help_text='数据的更新时间')
    machine = CharField(column_name='machine', help_text='机器的唯一标识符，程序启动的时候会固化')


class Contract(BaseModel):
    """
    记录了智能协约的address和abi
    """
    contract_address = CharField(column_name='contract_address')
    abi = CharField(column_name='abi')
    status = IntegerField(column_name='status')
    updates = DateTimeField(column_name='updates', default=datetime.datetime.now)


class Verification(BaseModel):
    """
    记录了events的数据，用于验证和签名
    """
    event = CharField(column_name='event', help_text='event名称')
    mechanism = CharField(column_name='mechanism', help_text='机构')
    owner_address = CharField(column_name='owner_address', help_text='所有者的address')
    identity_address = CharField(column_name='identity', help_text='用户的address')
    name = CharField(column_name='name', help_text='属性名')
    value = CharField(column_name='value', help_text='属性值')
    sign_text = CharField(column_name='sign_text', help_text='DID的签名数据（R,S,V）')
    scrpto_text = CharField(column_name='scrpto_text', help_text='公钥签名的数据')
    user_id = IntegerField(column_name='user_id', help_text='用户表的id，通过这个查找微信用户的OpenID')
    status = IntegerField(column_name='status', help_text='0:未验证，1:已验证，2:加密后发送')
    generation = CharField(column_name='generation', help_text='数据导入的时间(不会变更)')
    updates = DateTimeField(column_name='updates', default=datetime.datetime.now)


class Events(BaseModel):
    """
    记录了所有的日志信息
    CREATE TABLE `cp_events` (
      `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
      `args` mediumtext COMMENT 'event的参数',
      `event_name` varchar(200) DEFAULT NULL COMMENT 'event的名称',
      `log_index` int(10) DEFAULT NULL COMMENT 'log的索引号',
      `transaction_index` int(10) DEFAULT NULL COMMENT '交易的索引号',
      `transaction_hash` varchar(200) DEFAULT NULL COMMENT '交易的hash',
      `address` varchar(200) DEFAULT NULL COMMENT '所属智能协约的地址',
      `block_hash` varchar(200) DEFAULT NULL COMMENT '所属块的hash',
      `block_number` int(10) DEFAULT NULL COMMENT '所属的块号',
      `generation` datetime DEFAULT NULL COMMENT '数据生成时间',
      `updates` datetime DEFAULT NULL COMMENT '更新时间',
      `first_sign` mediumtext COMMENT '第一次签名的数据',
      `second_sign` mediumtext COMMENT '第二次签名的数据',
      `did` mediumtext COMMENT 'did 数据',
      PRIMARY KEY (`id`),
      UNIQUE KEY `tx` (`event_name`,`transaction_hash`,`transaction_index`) USING BTREE COMMENT '标识唯一的一个event'
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='存放监听到的所有event数据'
    """
    args = CharField(column_name='args', help_text='event的参数')
    event_name = CharField(column_name='event_name', help_text='event的名称')
    log_index = IntegerField(column_name='log_index', help_text='log的索引')
    transaction_index = IntegerField(column_name='transaction_index', help_text='交易的索引号')
    transaction_hash = CharField(column_name='transaction_hash', help_text='交易的hash值')
    address = CharField(column_name='address', help_text='event所属的智能协约地址')
    block_hash = CharField(column_name='block_hash', help_text='所属块的hash')
    block_number = IntegerField(column_name='block_number', help_text='所属的块号')
    generation = CharField(column_name='generation', default=datetime.datetime.now, help_text='数据导入的时间(不会变更)')
    updates = DateTimeField(column_name='updates', default=datetime.datetime.now, help_text='数据更新时间')
    first_sign = CharField(column_name='first_sign', help_text='第一次签名的数据')
    second_sign = CharField(column_name='second_sign', help_text='第二次签名的数据')
    did = CharField(column_name='did', help_text='did 数据')


class Army(BaseModel):
    """
    记录了 军队 验证event的数据流水
    """
    datas = CharField(column_name='datas', help_text='完整的event数据')
    args = CharField(column_name='args', help_text='event的参数')
    event_name = CharField(column_name='event_name', help_text='event的名称')
    log_index = IntegerField(column_name='log_index', help_text='log的索引')
    transaction_index = IntegerField(column_name='transaction_index', help_text='交易的索引号')
    transaction_hash = CharField(column_name='transaction_hash', help_text='交易的hash值')
    address = CharField(column_name='address', help_text='event所属的智能协约地址')
    block_hash = CharField(column_name='block_hash', help_text='所属块的hash')
    block_number = IntegerField(column_name='block_number', help_text='所属的块号')
    generation = CharField(column_name='generation', default=datetime.datetime.now, help_text='数据导入的时间(不会变更)')
    updates = DateTimeField(column_name='updates', default=datetime.datetime.now, help_text='数据更新时间')
    first_sign = CharField(column_name='first_sign', help_text='第一次签名的数据')
    second_sign = CharField(column_name='second_sign', help_text='第二次签名的数据')
    did_json = CharField(column_name='did_json', help_text='did 数据')
    created = IntegerField(column_name='created', help_text='did中的created时间 13位的时间戳，只处理时间比这个大的')
    created2 = DateTimeField(column_name='created2', help_text='did中的created时间转换为10位的时间戳')
    status = DateTimeField(column_name='status', help_text='数据的状态字段 0:正常, 1:名验证失败, 2:签名验证成功, 3:密文解密失败, 4:密文解密成功, 5:发送到以太坊失败, 6:发送到以太坊成功, 7:士兵不存在')
    did_id = CharField(column_name='did_id', help_text='存放当前用户的id（did串的id）')
    txhash = CharField(column_name='txhash', help_text='数据第二次上链后获得的交易hash')

class Organization(BaseModel):
    """
    记录了 机构 验证event的数据流水
    """
    args = CharField(column_name='args', help_text='event的参数')
    identity = CharField(column_name='identity', help_text='event中记录的identity字段的数据')
    event_name = CharField(column_name='event_name', help_text='event的名称')
    log_index = IntegerField(column_name='log_index', help_text='log的索引')
    transaction_index = IntegerField(column_name='transaction_index', help_text='交易的索引号')
    transaction_hash = CharField(column_name='transaction_hash', help_text='交易的hash值')
    address = CharField(column_name='address', help_text='event所属的智能协约地址')
    block_hash = CharField(column_name='block_hash', help_text='所属块的hash')
    block_number = IntegerField(column_name='block_number', help_text='所属的块号')
    generation = CharField(column_name='generation', default=datetime.datetime.now, help_text='数据导入的时间(不会变更)')
    updates = DateTimeField(column_name='updates', default=datetime.datetime.now, help_text='数据更新时间')
    first_sign = CharField(column_name='first_sign', help_text='第一次签名的数据')
    second_sign = CharField(column_name='second_sign', help_text='第二次签名的数据')
    did_json = CharField(column_name='did_json', help_text='did 数据')
    created = IntegerField(column_name='created', help_text='did中的created时间，只处理时间比这个大的')
    status = DateTimeField(column_name='status', help_text='数据的状态字段 0:正常, 1:验证第一个签名失败, 2:验证第一个签名成功, 3:验证第二个签名失败, 4:验证第二个签名成功')
    did_id = CharField(column_name='did_id', help_text='存放当前用户的id（did串的id）')
    mark = CharField(column_name='mark', help_text='人的身份标识（士兵，公务员，学生...）')


class OrganizationDid(BaseModel):
    """
    记录了 机构 验证event的数据流水
    """
    args = CharField(column_name='args', help_text='event的参数')
    identity = CharField(column_name='identity', help_text='event中记录的identity字段的数据')
    event_name = CharField(column_name='event_name', help_text='event的名称')
    log_index = IntegerField(column_name='log_index', help_text='log的索引')
    transaction_index = IntegerField(column_name='transaction_index', help_text='交易的索引号')
    transaction_hash = CharField(column_name='transaction_hash', help_text='交易的hash值')
    address = CharField(column_name='address', help_text='event所属的智能协约地址')
    block_hash = CharField(column_name='block_hash', help_text='所属块的hash')
    block_number = IntegerField(column_name='block_number', help_text='所属的块号')
    generation = CharField(column_name='generation', default=datetime.datetime.now, help_text='数据导入的时间(不会变更)')
    updates = DateTimeField(column_name='updates', default=datetime.datetime.now, help_text='数据更新时间')
    first_sign = CharField(column_name='first_sign', help_text='第一次签名的数据')
    second_sign = CharField(column_name='second_sign', help_text='第二次签名的数据')
    did_json = CharField(column_name='did_json', help_text='did 数据')
    created = DateTimeField(column_name='created', help_text='did中的created时间，只处理时间比这个大的')
    status = DateTimeField(column_name='status', help_text='数据的状态字段 0:正常')
    did_id = CharField(column_name='did_id', help_text='存放当前用户的id（did串的id）')
    mark = CharField(column_name='mark', help_text='人的身份标识（士兵，公务员，学生...）')

    class Meta:
        table_name = 'cp_organization_did'


class Area(BaseModel):
    area_id = IntegerField(column_name='area_id', primary_key=True)
    area_province = CharField(column_name='area_province')
    area_city = CharField(column_name='area_city')
    modify_id = IntegerField(column_name='modify_id')
    modify_time = TimestampField(column_name='modify_time', help_text='')

    class Meta:
        table_name = 'area'


class Person(BaseModel):
    person_id = IntegerField(column_name='person_id', primary_key=True)
    address = CharField(column_name='address', help_text='')
    public_key = CharField(column_name='public_key', help_text='')
    name = CharField(column_name='name', help_text='')
    sex = IntegerField(column_name='sex', help_text='')
    age = IntegerField(column_name='age', help_text='')
    education = CharField(column_name='education', help_text='')
    working_experience = CharField(column_name='working_experience', help_text='')
    area = ForeignKeyField(Area, column_name='area_id', backref='person')
    modify_time = TimestampField(column_name='modify_time', help_text='')
    iphone = CharField(Area, column_name='iphone', help_text='')

    class Meta:
        table_name = 'person'


class PersonDc(BaseModel):
    id = IntegerField(column_name='id', primary_key=True)
    modify_time = TimestampField(column_name='modify_time', help_text='')
    value = CharField(column_name='value', help_text='')
    person_hash = CharField(column_name='person_hash', help_text='')
    organization_hash = CharField(column_name='organization_hash', help_text='')
    person_address = CharField(column_name='person_address', help_text='')
    organization_address = CharField(column_name='organization_address', help_text='')
    status = IntegerField(column_name='status', help_text='0:正常，1上链超时，2：上链失败，3：上链成功')
    tx_hash = CharField(column_name='tx_hash', help_text='交易的hash值')

    class Meta:
        table_name = 'person_dc'


class Account(BaseModel):
    """ 记录了用户的账号信息 """
    account_id = IntegerField(column_name='account_id', primary_key=True, help_text='id')
    weixin_openid = IntegerField(column_name='weixin_openid', help_text='微信的openid')
    weixin_unionid = IntegerField(column_name='weixin_unionid', help_text='weixin_unionid')
    iphone = IntegerField(column_name='iphone')
    modify_time = TimestampField(column_name='modify_time')
    # person_id = IntegerField(column_name='person_id')
    person = ForeignKeyField(Person, backref='account', column_name='person_id')

    class Meta:
        table_name = 'account'


class QueueFlow(BaseModel):
    """ 队列的流水表 """
    id = AutoField()
    type = CharField(column_name='type', help_text='[call_function|upload_chain] 类型')
    retry = IntegerField(column_name='retry', help_text='重试次数')
    upload_time = DateTimeField(column_name='upload_time', help_text='上链时间')
    status = IntegerField(column_name='status', help_text='0：初始状态，1：上链成功，2：上链失败')
    receipt = CharField(column_name='receipt', help_text='receipt hash')
    data = DateTimeField(column_name='data', help_text='队列中的json串')
    creates = DateTimeField(column_name='creates', default=datetime.datetime.now, help_text='数据插入到数据库的时间')
    updates = DateTimeField(column_name='updates', help_text='数据更新的时间')

    class Meta:
        table_name = 'queue_flow'


class DpContractSurplus(BaseModel):
    """ 用于记录每次打款的数据 """
    star_id = IntegerField(column_name='star_id', help_text='明星id')
    address = CharField(column_name='address', help_text='协约地址')
    surplus = IntegerField(column_name='surplus', help_text='当前剩余值')
    success_time = TimestampField(column_name='sucess_time', help_text='数据的更新时间')

    class Meta:
        table_name = 'dp_contract_surplus'
