#! /usr/bin/env python
# -*- coding: utf8 -*-
"""
Author:       yuyongpeng@hotmail.com
Github:       https://github.com/yuyongpeng/
Date:         2019-04-11 11:54:46
LastEditors:  
LastEditTime: 2019-04-11 11:54:46
Description:  
"""
import pika
from kafka import KafkaProducer
from kafka.errors import KafkaError


class Rabbitmq(object):
    """
    Rabbitmq 的处理
    """
    def __init__(self, queue_name, queue_ip, queue_port, queue_user, queue_password, queue_vhost):
        self._queue_name = queue_name
        self._queue_ip = queue_ip
        self._queue_port = queue_port
        self._queue_user = queue_user
        self._queue_password = queue_password
        self._queue_vhost = queue_vhost

    def send_msg(self, body):
        """ 发送消息到队列中 """
        credentials = pika.PlainCredentials(self._queue_user, self._queue_password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(self._queue_ip, self._queue_port, self._queue_vhost, credentials))
        channel = connection.channel()
        # body = '''
        # {"action":"setAttributeSigned","args":{"address":"0xB2be7c8722935DB16921D64Ad0dDB5D47A52482a","signature":"1bac8f2eeaf962ccf9ace9845c40f553453fb0079d80173dfcc7daf05124091734888f4ba7b8591025fddafbba5b9e3c229a49073daeaa203d4b0260aa09b77500","name":"士兵","value":"{\"@context\":\"https://w3id.org/did/v1\",\"id\":\"did:ethr:B2be7c8722935DB16921D64Ad0dDB5D47A52482a#soldier\",\"publicKey\":[{\"id\":\"did:ethr:B2be7c8722935DB16921D64Ad0dDB5D47A52482a#soldier\",\"type\":\"EciesVerificationKey\",\"controller\":\"did:ethr:B2be7c8722935DB16921D64Ad0dDB5D47A52482a\",\"publicKeyHex\":\"0x04521fbe1f862845cb09ca6c0cdff00417d4a3bf3c04748806eb49079f5d2d5d555c6461ecc3760bd10de1bc7c77421f02bbe3642d6d3e35ee219f84a026478297\"}],\"authentication\":[{\"id\":\"did:ethr:DeCD6626f23bc43cB4D738cB0F2Dde922D691fD2#soldier\",\"type\":\"EciesVerificationKey\",\"controller\":\"did:ethr:DeCD6626f23bc43cB4D738cB0F2Dde922D691fD2\",\"publicKeyHex\":\"0x044af3c4d907a75e9349f362b0f854c7d74a89dad457df4f9cbf3c4f9e2f7fbcf8916ac219bb70e64777930b1e85d0a550e1e61ca94fa902dee419849a9a0efe8a\"}],\"proof\":\"5a20a8ab74ba21186197c5315369dea7eb50a9700a0d88c49c360f9e3e926880b7e8f793acd91800c33c2d64ae9c846c\",\"created\":1554808209789}\nb4f2d5447a602dca239d8ab528e1cb1b0ddc409d0941700fcffed5e6bd427c2755658c7e7790a94f69417ce43c5b31c9d82e9b2900d77afcec6d4268d4e446d300"}}
        # '''
        channel.queue_declare(self._queue_name, durable=False)
        tf = channel.basic_publish(exchange='',routing_key=self._queue_name,body=body, mandatory=True)
        connection.close()
        return tf

class Kafka(object):
    """
    Kafaka 的处理
    """
    def __init__(self, queue_ip, queue_port, queue_topic):
        self._queue_ip = queue_ip
        self._queue_port = queue_port
        self._queue_topic = queue_topic

    def send_msg(self, body):
        producer = KafkaProducer(bootstrap_servers=['{}:{}'.format(self._queue_ip, self._queue_port)])
        future = producer.send(self._queue_topic, body.encode())
        try:
            record_metadata = future.get(timeout=10)
        except KafkaError as e:
            print(e)
        # Successful result returns assigned partition and offset
        print(record_metadata.topic)
        print(record_metadata.partition)
        print(record_metadata.offset)
        producer.flush()