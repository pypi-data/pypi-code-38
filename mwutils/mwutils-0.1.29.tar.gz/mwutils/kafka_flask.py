'''
使用 confluent_kafka 的producer 接口，当confluent_kafka没有安装时，则使用kafka_paython的接口
推荐用kafka_paython_flask单元的Producer 类，理由是简单，不用设定topic的partition，
在指定key的情况下，会自动分派partition，不指定key是会轮流往不同的partition中写数据
'''

from binascii import crc32
from flask import current_app

class PartitionAssign:
    def __init__(self,assign_type,len):
        #assign_type :分配partition方式 hash:以keyhash ,inturn:按顺序
        #len partitions的个数
        self.partition_no =None
        self.assign_type=assign_type
        self.len =len
    def get_partiton_no(self,key=None):
        if self.assign_type == 'hash':
            assert key!=None
            return hash(key) % self.len
        elif self.assign_type =='inturn':
            if self.partition_no==None:
                self.partition_no=0
            else:
                self.partition_no=(self.partition_no+1) % self.len
            return  self.partition_no
        else:
            raise Exception('not support this type:%s' % self.assign_type)

try:
    from confluent_kafka import Producer as Producer_k
    class Producer():
        def __init__(self, app=None):
            self.producer_k = None
            if app is not None:
                self.init_app(app)

        def init_app(self, app):
            conf = app.config.get('KAFKA_CONFIG', None)
            assert conf, 'KAFKA_CONFIG 设定不存在！'
            self.producer_k = Producer_k(**conf)
            self.topics = app.config.get('KAFKA_TOPICS', None)
            assert self.topics, '请设定topics,如："topics":{"mytest":3}'

        def producer(self, topic, **kwargs):
            # 如果有key 就按key来选择partition
            if 'key' in kwargs and 'partition' not in kwargs:
                if self.topics.get(topic, None) is None:
                    current_app.logger.error('the topic (%s) is not definition!' % topic)
                    raise Exception('the topic (%s) is not definition!' % topic)
                partition,_  = divmod(crc32(kwargs['key'].encode()), self.topics[topic])
                kwargs['partition'] = partition
            self.producer_k.produce(topic, **kwargs)
            self.producer_k.poll(0)

        def flush(self):
            self.producer_k.flush()

except ImportError as e:
    from .kafka_paython_flask import Producer as Proceducer_pk
    class Producer(Proceducer_pk):
        def producer(self,topic, key=None, value=None, flush=True, partition=None):
            self.send(topic, key=key,value=value,
                      partition=partition,flush = flush
                      )






