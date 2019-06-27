import sense_core as sd
import os
import time


def test_object_id():
    print(sd.generate_object_id())


def test_log_info():
    import logging
    # sd.set_log_name("xxx")
    sd.log_init_config('core', 'console')
    # logging.root.setLevel(logging.WARNING)
    sd.set_log_process_name(True)
    sd.set_log_thread_name(True)
    sd.log_info('logxxxxx')
    logging.info("aaaa")


def test_log_error():
    sd.log_init_config('core', '../logs', monit_queue='rabbit_monit')
    sd.log_error('error xxx')


def test_log_fatal():
    sd.log_init_config('core', '/tmp', monit_queue='rabbit_monit')
    sd.log_fatal('error xxx')


def test_log_task():
    sd.log_init_config('core', '/tmp/', 'rabbit_monit')
    sd.log_task_schedule("stock_tag_222", 60 * 10, "stock", "17-18")


def test_log_notice():
    sd.log_init_config('core', '/tmp/', 'rabbit_monit')
    sd.log_notice("中文测试")


def test_log_error_monit():
    sd.log_init_config('core', '../logs', 'rabbit1')
    sd.log_error('error xxx')


def test_log_exception():
    sd.log_init_config('core', '../logs')
    try:
        print(5 / 0)
    except Exception as ex:
        sd.log_exception(ex)


def test_config():
    print(sd.config('db_stock', 'dbms'))
    print(sd.config('database'))
    print(sd.config('log_level'))


def consume_message(msg):
    print(msg)
    print('deal one')
    # sd.log_info('consumer ' + str(os.getpid()) + ' msg=' + msg)
    # time.sleep(2)


def test_rabbit_produce():
    sd.log_init_config('core', '/tmp/')
    producer = sd.RabbitProducer()
    for i in range(1, 10):
        producer.send('test1', 'helloo=%d' % i)


def test_kafka_consumer():
    sd.log_init_config('core', '/tmp/logs')
    consumer = sd.RabbitConsumer(topic='test3',
                                 config_info={'user': 'admin', 'password': 'sense_mq@2018', 'host': '52.82.30.135',
                                              'port': 5672})
    consumer.execute(consume_message)


def handle_process_work(job):
    sd.log_info("job={0}".format(job))
    time.sleep(0.1)


@sd.catch_raise_exception
def raise_exception():
    return 1 / 0


def test_raise_exception():
    sd.log_init_config('core', '/tmp')
    raise_exception()


@sd.try_catch_exception
def try_catch_exception():
    return 1 / 0


def test_catch_exception():
    sd.log_init_config('core', '/tmp')
    try_catch_exception()


def test_multi_process():
    sd.log_init_config('core', '/tmp')
    sd.set_log_process_name(True)
    jobs = list()
    for i in range(100):
        jobs.append(i)
    sd.execute_multi_core("dumb", handle_process_work, jobs, 4, True)


def test_mq():
    factory = sd.RabbitmqFactory('rabbit_monit')
    print(factory.list_queues())


def function_cal(body):
    import json
    msg = json.loads(body)
    print(msg['msg_header']['msg_idx'])
    time.sleep(1)


def test_rabbit_produce1():
    sd.log_init_config('core', '/tmp/')
    producer = sd.RabbitProducer()
    producer.send('test1', 'helloo=%d' % 1)
    # for i in range(1, 10):
    #     producer.send('test1', 'helloo=%d' % i)


def test_rabbit_consume():
    sd.log_init_config('core', '/tmp/')
    consumer = sd.RabbitConsumer('test1', 'rabbit')
    consumer.execute_safely(rabbit_consume, prefetch_count=1, no_ack=False)


def rabbit_consume(body):
    sd.log_info(str(body))
    time.sleep(100)


def function_test():
    sd.log_init_config('core', '/tmp/logs')
    consumer = sd.RabbitConsumer('cloud_data_pdf_test', 'rabbit_cloud')
    consumer.execute_safely(function_cal)


def test_thread_scale():
    factory = sd.ThreadAutoFactory(queue='cloud_data_pdf_test', label='rabbit_cloud', monitor=60)
    factory.execute(function_test)

def test_db():
    from sense_core import get_db_factory, DBACTION
    mysqlet = get_db_factory('mysql_stock')
    res = mysqlet.findKeySql(DBACTION.EXE_BY_SQL, sql='select * from sites')
    print(res)
