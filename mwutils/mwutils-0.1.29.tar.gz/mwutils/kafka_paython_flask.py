from kafka import KafkaProducer

class Producer():
    def __init__(self, app=None):
        self.producer_k = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        conf = app.config.get('KAFKA_CONFIG', None)
        assert conf, 'KAFKA_CONFIG 设定不存在！,请在config.py中指定'
        self.producer_k = KafkaProducer(bootstrap_servers=conf['bootstrap.servers'].split(','))

    def send(self, topic, key=None, value=None, flush=True, partition=None):
        self.producer_k.send(topic,
                             key=key.encode(),
                             value=value.encode(),
                             partition=partition
                             )
        # 同步写入需flush
        if flush:
            self.producer_k.flush()

    def flush(self,timeout = None):
        self.producer_k.flush(timeout=timeout)

    def close(self,timeout = None):
        self.producer_k.close(timeout)