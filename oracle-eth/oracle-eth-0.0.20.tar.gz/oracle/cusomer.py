#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
# Author: yuyongpeng@hotmail.com
# Description: rabbitmq 的消费者程序
#  

"""

from abc import ABCMeta, abstractmethod
import pika
import json
import re
import toolz
from oracle.setting import VAR
from oracle.database import dbs
from oracle.logger import logger
from oracle.queues import Rabbitmq, Kafka
from datetime import datetime
import functools

class Cusomer(object):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        self._queue_name = kwargs.pop('queue_name')
        self._queue_user = kwargs.pop('queue_user')
        self._queue_password = kwargs.pop('queue_password')
        self._queue_ip = kwargs.pop('queue_ip')
        self._queue_port = kwargs.pop('queue_port')
        self._queue_vhost = kwargs.pop('queue_vhost')
        self._contract = kwargs.pop('contracrt')

    @abstractmethod
    def cusomer(self):
        pass

    def parse_arg(self, function_args):
        """
        解析json，获得上链的参数
        :param function_args:  {} 对象
        :return:
        """
        args = []
        for arg in function_args:
            name = arg['name']
            value = arg['value']
            arg_type = arg['type']
            source_type = arg.get('source_type', 'string')
            if re.match('bytes.*', arg_type):
                if source_type == 'string':
                    value = value.encode()
                if source_type == 'hex':
                    value = bytes.fromhex(value)
                args.append(value)
            if re.match('.*int.*', arg_type):
                value = int(value)
                args.append(value)
            if re.match('address', arg_type):
                args.append(value)
            if re.match('string', arg_type):
                args.append(value)
            if re.match('bool', arg_type):
                args.append(value)
        return args


    def upload_chain(self, body, queue_flow, wait=False):
        """
        上链操作
        :param body: 消息体  json串
        :return:
        """
        try:
            body_item = json.loads(body)
            queue_flow_id = queue_flow.id;
            body_item.update({'queue_flow': queue_flow_id})
            type = body_item['type']
            retry = body_item.get('retry', 0)  # 第几次重试
            upload_time = body_item.get('upload_time', datetime.fromtimestamp(datetime.now().timestamp()).strftime('%Y-%m-%d %H:%M:%S'))
            if type == 'call_function':
                function_name = body_item['function']['name']
                function_args = body_item['function']['args']
                # 解析args参数，获得调用协约需要的参数列表
                args = self.parse_arg(function_args)
                # 上链
                tf, tx_hash = self._contract.call_function(function_name, True, *args)
                # 更新 receipt hash
                queue_flow.update(receipt=tx_hash).where(queue_flow.id == id).execute()

                # 发送到监听队列，监听是否上链
                body_item.update({'receipt': tx_hash})
                body_item.update({'upload_time': upload_time})
                body_item.update({'retry': int(retry)+1})
                rabbitmq = Rabbitmq(queue_ip=VAR['QUEUE_IP'], queue_port=VAR['QUEUE_PORT'], queue_user=VAR['QUEUE_USER'],
                                    queue_password=VAR['QUEUE_PASSWORD'], queue_name=VAR['QUEUE_NAME_VALIDATION'],
                                    queue_vhost=VAR['QUEUE_VHOST'])
                rabbitmq.send_msg(json.dumps(body_item))

            if type == 'upload_chain':
                data = body_item['data']['msg']
                # TODO: 直接对数据进行上链操作

        except json.JSONDecodeError as j:
            logger.exception('json 解析错误 ')
            logger.error(j)

    def send_notice(self, success, body):
        """
        发送通知
        :param success: 是否上链成功
        :param body:    需要处理的对象，obj
        :return:
        """
        body_item = body
        body_item.update({'success': str(success).lower()})
        queue_msg = json.dumps(body_item)
        # queue
        if 'send_queue' in body_item:
            queue_type = body_item['send_queue']['queue_type']
            if queue_type == "rabbitmq":
                queue_ip = body_item.get('queue_ip', VAR['QUEUE_IP'])
                queue_port = body_item.get('queue_port', VAR['QUEUE_PORT'])
                queue_user = body_item.get('queue_user', VAR['QUEUE_USER'])
                queue_password = body_item.get('queue_password', VAR['QUEUE_PASSWORD'])
                queue_name = toolz.get_in(['send_queue', 'queue_msg', 'queue_name'], body_item, VAR['QUEUE_NAME_NOTICE'])
                queue_vhost = body_item.get('queue_vhost', VAR['QUEUE_VHOST'])
                rabbitmq = Rabbitmq(queue_ip=queue_ip, queue_port=queue_port, queue_user=queue_user,
                                    queue_password=queue_password, queue_name=queue_name, queue_vhost=queue_vhost)
                rabbitmq.send_msg(queue_msg)
            if queue_type == "kafka":
                # TODO: 还没有测试 kafka部分
                queue_ip = body_item.get('queue_ip', VAR['KAFKA_IP'])
                queue_port = body_item.get('queue_port', VAR['KAFKA_PORT'])
                queue_topic = body_item.get('queue_topic', VAR['QUEUE_TOPIC'])
                kafka = Kafka(queue_ip=queue_ip, queue_port=queue_port, queue_topic=queue_topic)
                kafka.send_msg(queue_msg)

        # database
        if 'send_database' in body_item:
            database = body_item['send_database']
            if 'mysql' in database:
                dbs.update_mysql(success=success, **database['mysql'])
            if 'postgresql' in database:
                # TODO: 还没有实现 postgresql部分
                pass

        # mail
        if 'send_email' in body_item:
            email = body_item['send_email'] # list
            from oracle import mail
            mail_subject = "上链成功" if success else "上链失败"
            mail.send_email(mail_subject=mail_subject,
                            mail_host=VAR['MAIL_SMTP'],
                            mail_pass=VAR['MAIL_PASSWORD'],
                            mail_receiver=email,
                            mail_body=queue_msg,
                            mail_sender=VAR['MAIL_USER'])


class CallContract(Cusomer):
    """
    用于上链操作
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def callback(self, ch, method, properties, body):
        """
        队列处理的业务逻辑
        :param ch:          channel
        :param method:
        :param properties:
        :param body:        需要处理的消息体 json
        :return:
        """
        logger.info(body)
        try:
            body_item = json.loads(body)
            # TODO: 把body信息存入数据库中，以备后查
            queue_flow = dbs.get_queue_flow(body)
            retry = body_item.get('retry', 0)           # 第几次重试
            max_retry = body_item.get('max_retry', 3)   # 最大的重试次数
            if retry > max_retry:
                logger.error('************************************************************')
                logger.error('** 重试次数大于{}, 不在进行操作，请查找原因'.format(max_retry))
                logger.error(body)
                logger.error('************************************************************')
                return
            # 上链操作
            self.upload_chain(body, queue_flow)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except json.JSONDecodeError as j:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.exception('json 解析错误 ')
            logger.error(j)
        except Exception as e:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.error('************************************************************')
            logger.error('** JSON 数据处理遇到无法挽回的错误 ')
            logger.error(e)
            logger.error(body)
            logger.error('************************************************************')

    # @retry(pika.exceptions.AMQPConnectionError, delay=5, jitter=(1, 3))
    def cusomer(self):
        # 连接rabbitmq
        credentials = pika.PlainCredentials(self._queue_user, self._queue_password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(self._queue_ip, self._queue_port, self._queue_vhost, credentials))
        channel = connection.channel()
        # channel.queue_delete(queue='cport_call_contract    # 专门用于调用智能协约')
        # exit(1)
        channel.queue_declare(queue=self._queue_name,   # 队列名称
                              passive=False,            # 仅检查队列是否存在
                              durable=False,            # true: 启动不允许修改queue_declare参数，如果有修改，就会报错
                              exclusive=False,          # 只允许通过当前连接访问
                              auto_delete=False,        # 断开连接后自动删除这个队列
                              )

        # 公平调度，使得rabbitmq不会在同一时间给工作者分配多个任务，即只有工作者完成任务之后，才会再次接收到任务。
        channel.basic_qos(prefetch_count=1)
        # 消费
        try:
            channel.basic_consume(queue=self._queue_name,
                                  on_message_callback=self.callback,
                                  auto_ack=False,                # 自动确认模式
                                  exclusive=False,               # 独占模式，不允许有其他的消费者
                                  consumer_tag='call_contract',  # 指定消费者标签
                                  )
        except Exception as ex:
            logger.error(ex)

        logger.info('[*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()


class ValidationContract(Cusomer):
    """
    用于验证上链是否成功
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def callback(self, ch, method, properties, body):
        """
        监测是否上链完成
        :param ch:          pika.Channel
        :param method:      pika.spec.Basic.Deliver
        :param properties:  pika.spec.BasicProperties
        :param body:        bytes
        :return:
        """
        logger.info(body)
        try:
            body_item = json.loads(body)
            # 把body信息存入数据库中，以备后查
            queue_flow = dbs.get_queue_flow(body)

            retry = body_item.get('retry', 0)  # 第几次重试
            max_retry = body_item.get('max_retry', 3)  # 最大的重试次数

            upload_time = datetime.strptime(body_item['upload_time'], '%Y-%m-%d %H:%M:%S')
            timeout = int(body_item['upload_timeout'])
            now = int(datetime.now().timestamp())
            send_msg = functools.partial(Rabbitmq, queue_ip=VAR['QUEUE_IP'], queue_port=VAR['QUEUE_PORT'],
                                         queue_user=VAR['QUEUE_USER'], queue_password=VAR['QUEUE_PASSWORD'],
                                         queue_vhost=VAR['QUEUE_VHOST'])
            # 查看是否存在 receipt 的 tx_hash
            if 'receipt' not in body_item:
                logger.error('************************************************************')
                logger.error('** JSON 数据中 不存在 receipt hash，没法处理，发回上链队列重新上链')
                logger.error(body)
                logger.error('************************************************************')
                ch.basic_ack(delivery_tag=method.delivery_tag)

            # 查看数据是否上链成功
            tf, receipt = self._contract.is_tx_sucess(body_item['receipt'])
            if tf is True: # 上链 完成 发送通知
                body_item.update({'success': True})
                self.send_notice(tf, body_item)
            else: # 上链 未完成 重新进入查询队列
                if (now - int(upload_time.timestamp())) > timeout:  # 超时 发送回上链队列，重新进行上链操作
                    if retry >= max_retry:
                        body_item.update({'success': False})
                        self.send_notice(tf, body_item)
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                        return
                    else:
                        rabbitmq = send_msg(queue_name=VAR['QUEUE_NAME'])
                        rabbitmq.send_msg(json.dumps(body_item))
                else:
                    rabbitmq = send_msg(queue_name=VAR['QUEUE_NAME_VALIDATION'])
                    rabbitmq.send_msg(json.dumps(body_item))

                rabbitmq = send_msg(queue_name=VAR['QUEUE_NAME_VALIDATION'])
                rabbitmq.send_msg(json.dumps(body_item))

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except json.JSONDecodeError as j:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.exception('json 解析错误 ')
            logger.error(j)
        except Exception as e:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.error('************************************************************')
            logger.error('** JSON 数据处理遇到无法挽回的错误 ')
            logger.error(e)
            logger.error(body)
            logger.error('************************************************************')

    # @retry(pika.exceptions.AMQPConnectionError, delay=5, jitter=(1, 3))
    def cusomer(self):
        # 连接rabbitmq
        credentials = pika.PlainCredentials(self._queue_user, self._queue_password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(self._queue_ip, self._queue_port, self._queue_vhost, credentials))
        channel = connection.channel()
        # self._queue_name = 'cport_notice_contract'
        channel.queue_declare(queue=self._queue_name,   # 队列名称
                              passive=False,            # 仅检查队列是否存在
                              durable=False,            # 在代理重新启动后仍然是存活的
                              exclusive=False,          # 只允许通过当前连接访问
                              auto_delete=False)        # 断开连接后自动删除这个队列

        # 公平调度，使得rabbitmq不会在同一时间给工作者分配多个任务，即只有工作者完成任务之后，才会再次接收到任务。
        channel.basic_qos(prefetch_count=1)
        # 消费
        try:
            channel.basic_consume(queue=self._queue_name,
                                  on_message_callback=self.callback,
                                  auto_ack=False,    # 自动确认模式
                                  exclusive=False,   # 独占模式，不允许有其他的消费者
                                  consumer_tag='ValidationContract',    # 指定消费者标签
                                  )
        except Exception as ex:
            logger.error(ex)

        logger.info('[*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()


import multiprocessing
from pycontractsdk.contracts import Contract
class ValidationChainWorker(multiprocessing.Process):
    def __init__(self, intval):
        multiprocessing.Process.__init__(self)
        self.intval = intval

    def run (self):
        # 实例化 Contract
        provider = VAR['ETH_PROVIDER']
        contract_address = VAR['CONTRACT_ADDRESS']
        abi = VAR['CONTRACT_ABI']
        operator_private_key = VAR['OPERATOR_PRIVATEKEY']
        delegate_private_key = VAR['DELEGATE_PRIVATEKEY']
        gas = VAR['GAS']
        gas_prise = VAR['GAS_PRISE']
        concart = Contract(provider=provider, timeout=60, contract_address=contract_address, abi=abi,
                           private_key=operator_private_key,
                           gas=gas,
                           gas_prise=gas_prise
                           )
        # 启动 消费者程序
        cus = ValidationContract(
            contracrt=concart,
            queue_name=VAR['QUEUE_NAME_VALIDATION'],
            queue_ip=VAR['QUEUE_IP'],
            queue_port=VAR['QUEUE_PORT'],
            queue_user=VAR['QUEUE_USER'],
            queue_password=VAR['QUEUE_PASSWORD'],
            queue_vhost=VAR['QUEUE_VHOST'],
        )
        cus.cusomer()
