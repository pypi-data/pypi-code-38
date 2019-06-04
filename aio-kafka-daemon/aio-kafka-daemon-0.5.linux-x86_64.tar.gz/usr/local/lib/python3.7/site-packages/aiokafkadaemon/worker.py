import asyncio
import logging
import traceback
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer


logger = logging.getLogger('aiokafkadaemon')


class Worker:
    def __init__(self, kafka_broker_addr=None, kafka_group_id='',
                 consumer_topic='', producer_topic='',
                 create_consumer=True, create_producer=False,
                 on_run=None):
        loop = asyncio.get_event_loop()
        self._kafka_broker_addr = kafka_broker_addr
        self._kafka_group_id = kafka_group_id
        self._consumer_topic = consumer_topic
        self._producer_topic = producer_topic
        self._on_run = on_run
        if not producer_topic:
            self._producer_topic = consumer_topic
        self._consumer = None
        self._producer = None
        self._on_consumer_subscribe = None
        self._on_consumer_message = None
        if create_consumer:
            self._consumer = Worker.make_consumer(loop, kafka_broker_addr,
                                                  kafka_group_id)
        if create_producer:
            self._producer = Worker.make_producer(loop, kafka_broker_addr)

    @classmethod
    def make_consumer(cls, loop, broker_addr, group_id):
        """
        Creates and connects Kafka  consumer to the broker
        :param loop:
        :param broker_addr:
        :return:
        """
        logger.debug('Creating instance of kafka consumer')
        consumer = AIOKafkaConsumer(loop=loop,
                                    bootstrap_servers=broker_addr,
                                    group_id=group_id,
                                    session_timeout_ms=60000)
        logger.info('Connected consumer to kafka on {}'.format(broker_addr))
        return consumer

    @classmethod
    def make_producer(cls, loop, broker_addr):
        """
        Creates an instance of the AIOKafka producer
        :param loop:
        :param broker_addr:
        :return:
        """
        logger.debug('Creating instance of producer')
        producer = AIOKafkaProducer(loop=loop,
                                    bootstrap_servers=broker_addr,
                                    compression_type='snappy')
        logger.info('Producer connected to kafka on {}'.format(broker_addr))
        return producer

    async def __aenter__(self):
        """
        Async iterator-enter coroutine
        :return:
        """
        return self

    async def __aexit__(self):
        """
        Async iterator-exit coroutine
        :return:
        """
        return await self.stop()

    async def start(self):
        if self._consumer_topic:
            self._consumer.subscribe([self._consumer_topic])
        if self._consumer:
            logger.info('Kafka consumer started')
            await self._consumer.start()
        if self._producer:
            logger.info('Kafka producer started')
            await self._producer.start()

    async def stop_kafka(self, stop_producer=False):
        if self._consumer:
            await self._consumer.stop()
            logger.warning('Consumer has been stopped')

        if stop_producer and self._producer:
            await self._producer.stop()
            logger.warning('Producer has been stopped')

    async def stop(self):
        logger.warning('System stopping, stopping consumer first')
        await self.stop_kafka(False)

    async def run(self):
        """
        Main method for the worker. Any child class can either
        overload it, or just implement on_run asyn callback,
        to perform specific tasks.
        :return:
        """
        try:
            await self.start()
            on_run = getattr(self, 'on_run', None)
            if on_run and callable(on_run):
                await on_run()
        except Exception as exc:
            # Only deadling with generic and Kafka critical
            # errors here. ie, UnknownMemberIdError and any
            # heartbeat error, like RequestTimedOutError, is
            # logged only, not raised again
            # https://bit.ly/2IWG8Mn
            # https://bit.ly/2ZCNCtE
            logger.error('Error causing system failure, '
                         '{}:\n{}'.format(exc, traceback.format_exc()))
        finally:
            # it's to better to stop kafka components, better
            # than keep it running with problems.
            await self.stop_kafka()
