import json
import sys

import os
import threading
import time
import logging
import pika
import collections
import functools
from abc import ABCMeta, abstractmethod

from shared.utils import *
from shared.constants import *
from shared.job import *
import queue

LOG = logging.getLogger(LOG_APP)
PLOG = logging.getLogger(LOG_PERF)

class CoordinatorClient(threading.Thread):

    def __init__(self, callable_worker, worker_type, auto_send_heartbeat = True, data_supported = None, jobs_capacity = 1, auto_ready_confirmation = True):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.callable_worker = callable_worker
        self.channel = None
        self.consumer_tag = None
        self.should_work = True
        self.worker_type = worker_type
        self.id = None
        self.auto_send_heatbeat = auto_send_heartbeat
        self.jobs_capacity = jobs_capacity
        if data_supported:
            if isinstance(data_supported, str):
                self.data_supported = json.loads(data_supported)
            else:
                self.data_supported = data_supported
        else:
            self.data_supported = None
        self.jobs = {}
        self.jobs_ordered = []
        self.auto_ready_confirmation = auto_ready_confirmation
        self.jobs_submitted = []



    def run(self):
        LOG.debug('Starting')
        self.connection = create_mq_connection()
        if not self.connection:
            LOG.error('Failed to create mq connection - exiting')
            return
        while self.should_work:
            try:
                self.id = None
                self.registerAndWait()
            except Exception as e:
                pass
                LOG.error(e, exc_info=True)
        time.sleep(1)
        LOG.debug('Finishing')



    def mq_callback(self, ch, method, properties, body):
        # ch.basic_ack(delivery_tag=method.delivery_tag, multiple=False)
        # print("{}".format(method.routing_key))
        # print("{}".format(properties.correlation_id))
        # print("{}".format(body.decode()))
        try:
            operation = None
            if method.routing_key == self.queue_name:
                operation = properties.correlation_id
            else:
                operation = method.routing_key
            if operation == MQ_WORKER_REGISTERED_ID:
                d = json.loads(body.decode())
                self.id = d['id']
                self.channel.queue_bind(exchange=MQ_COORDINATOR_EXCHANGE, queue=self.queue_name, routing_key=self.id)
                LOG.info('Registered as worker id {} type {} queue {}'.format(self.id, self.worker_type, self.queue_name))
            if operation == MQ_WORKER_UNREGISTERED:
                d = json.loads(body.decode())
                if self.id == d['id']:
                    LOG.info('Worker is unregistered id {} type {} queue {}'.format(self.id, self.worker_type, self.queue_name))
                    self.id = None
                    # situacia ked sme odregistrovany napr. kvoli dlhym timeoutom - musime sa zaregistrovat znovu
                    if self.should_work:
                        self.connection.add_callback_threadsafe(self.register)
                else:
                    LOG.warning('Received unkown id {}, my id is {}'.format(d['id'], self.id))
            elif operation == MQ_JOB_ASSIGN:
                LOG.info('{} Job assigned {}'.format(self.get_id(),body.decode()))
                self.job_assign(ch, method, properties, body)
            elif operation == MQ_JOB_UNASSIGN:
                LOG.info('{} Job unassigned {}'.format(self.get_id(),body.decode()))
                self.job_unassign(ch, method, properties, body)
            elif operation == MQ_JOB_STATUS:
                LOG.info('{} Job status {}'.format(self.get_id(),body.decode()))
                self.job_status(ch, method, properties, body)
            elif operation == MQ_JOB_SUBMIT_REQUESTED_ID:
                LOG.info('{} Job submit requested id {}'.format(self.get_id(), body.decode()))
                self.job_submit_requested_id(ch, method, properties, body.decode())
        except Exception as e:
            LOG.error(e, exc_info=True)

    #TODO - toto zavolat az ked sa zinicializuje samotny worker, napr. ked natiahne network
    # pretoze potom hned zacnu prichadzat requesty
    def registerAndWait(self):
        LOG.debug('Registering')
        if self.connection and self.connection.is_closed:
            LOG.warning('Reconnecting')
            self.connection = create_mq_connection()
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=MQ_COORDINATOR_EXCHANGE, exchange_type=MQ_COORDINATOR_EXCHANGE_TYPE)
        result = self.channel.queue_declare('', exclusive=False, durable=False, auto_delete=True )
        self.queue_name = result.method.queue
        for x in MQ_COORDINATOR_WORKER_BINDINGS:
            self.channel.queue_bind(exchange=MQ_COORDINATOR_EXCHANGE, queue=self.queue_name, routing_key=x)
        self.channel.queue_bind(exchange=MQ_COORDINATOR_EXCHANGE, queue=self.queue_name, routing_key=self.queue_name)
        self.consumer_tag = self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.mq_callback, auto_ack=True)
        self.channel.confirm_delivery()
        self.register()
        if self.auto_send_heatbeat:
            self.shedule_heartbeat_send()
        LOG.info('Waiting for commands')
        self.channel.start_consuming()

    def register(self):
        message = {
            'worker_type': self.worker_type,
            'queue': self.queue_name,
            'jobs_capacity': self.jobs_capacity
        }
        if self.data_supported:
            message['data_supported'] = self.data_supported
        delivered = False
        while not delivered:
            try:
                self.channel.basic_publish(
                    exchange=MQ_COORDINATOR_EXCHANGE, routing_key=MQ_WORKER_REGISTER,
                            properties=pika.BasicProperties(
                                reply_to=self.queue_name),
                    body=json.dumps(message), mandatory=True)
                delivered = True
            except:
                LOG.warning('Waiting for coordinator to be up')
                time.sleep(1)
                continue
            if delivered:
                LOG.debug('Routed to coordinator')


    def shedule_heartbeat_send(self):
        self.connection.call_later(HEARTBEAT_SEND_INTERVAL,
                                           self.heartbeat_send)

    def heartbeat_send(self):
        try:
            if self.id:
                message = {
                    'id': self.id
                }
                self.channel.basic_publish(
                    exchange=MQ_COORDINATOR_EXCHANGE, routing_key=MQ_WORKER_HEARTBEAT,
                    body=json.dumps(message))
        except Exception as e:
            LOG.error(e, exc_info=True)
        finally:
            self.shedule_heartbeat_send()

    def get_id(self):
        return self.id

    def _set_job_status_request(self , job_id, status, customer_id):
        try:
            message = {
                'job_id': job_id,
                'customer_id': customer_id
            }
            self.channel.basic_publish(
                exchange=MQ_COORDINATOR_EXCHANGE, routing_key=status,
                body=json.dumps(message))
        except Exception as e:
            LOG.error(e, exc_info=True)

    def _submit_job_request(self , job_data):
        try:
            self.channel.basic_publish(
                exchange=MQ_COORDINATOR_EXCHANGE, routing_key=MQ_JOB_SUBMIT_REQUEST,
                properties=pika.BasicProperties(
                    reply_to=self.queue_name),
                body=json.dumps(job_data))
        except Exception as e:
            LOG.error(e, exc_info=True)

    def _confirm_ready_for_job_start(self, job_id, customer_id ):
        try:
            message = {
                'id': self.get_id(),
                'job_id': job_id,
                'customer_id': customer_id
            }
            self.channel.basic_publish(
                exchange=MQ_COORDINATOR_EXCHANGE, routing_key=MQ_WORKER_READY_FOR_JOB_START,
                body=json.dumps(message))
        except Exception as e:
            LOG.error(e, exc_info=True)

    def _stop(self):
        try:
            LOG.debug('Trying to stop')
            if not self.id is None:
                message = {
                    'id': self.id
                }
                self.channel.basic_publish(
                    exchange=MQ_COORDINATOR_EXCHANGE, routing_key=MQ_WORKER_UNREGISTER,
                    body=json.dumps(message))
            self.should_work = False
            self.channel.stop_consuming(self.consumer_tag)
            close_mq_connection(self.connection)
        except Exception as e:
            LOG.error(e, exc_info=True)

    def job_submit_requested_id(self, ch, method, properties, body_decoded ):
        self.jobs_submitted.append(json.loads(body_decoded))

    def job_assign(self,ch, method, properties, body ):
        LOG.debug('entering job_assign')
        job = Job()
        job.from_dict(json.loads(body))

        if job.id in self.jobs:
            LOG.warning('Worker {} Job already assigned {}'.format( self.get_id(), job.id))
        else:
            self.jobs[job.id] = job
            self.jobs_ordered.append(job)
            self.callable_worker.add_callback_threadsafe(
                functools.partial( self.callable_worker.job_assign_callback,job.id)
            )
        LOG.debug('returning job_assign')

    def job_unassign(self,ch, method, properties, body ):
        LOG.debug('entering job_unassign')
        d = json.loads(body)
        id = d['id']
        if id in self.jobs:
            self.callable_worker.add_callback_threadsafe(
                functools.partial( self.callable_worker.job_unassign_callback,id)
            )
        else:
            LOG.warning('Worker {} job  not assigned {}'.format(self.get_id(), id))
        LOG.debug('returning job_unassign')

    def job_status(self,ch, method, properties, body ):
        LOG.debug('entering job_status')
        d = json.loads(body)
        id = d['id']
        if id in self.jobs:
            self.jobs[id].job_status = d['job_status']
            self.callable_worker.add_callback_threadsafe(
                functools.partial( self.callable_worker.job_status_callback,id)
            )
        else:
            LOG.warning('Worker {} job  not assigned {}'.format(self.get_id(), id))
        LOG.debug('returning job_status')

    # Thread safe functions - to use this class connection and channel
    # direct calls will do strange behaviour because PIKA is not thread safe

    def thread_safe_stop(self):
        try:
            if self.channel is None:
                self.should_work = False
                return
            self.connection.add_callback_threadsafe(self._stop)
        except Exception as e:
            LOG.error(e, exc_info=True)

    def thread_safe_set_job_status_request(self, job_id, status, customer_id):
        try:
            self.connection.add_callback_threadsafe(
                functools.partial(self._set_job_status_request, job_id, status, customer_id)
            )
        except Exception as e:
            LOG.error(e, exc_info=True)

    def thread_safe_submit_job_request(self, job_data):
        validate_job_schema(job_data)
        try:
            self.connection.add_callback_threadsafe(
                functools.partial(self._submit_job_request, job_data)
            )
        except Exception as e:
            LOG.error(e, exc_info=True)

    def thread_safe_confirm_ready_for_job_start(self, job_id, customer_id):
        try:
            self.connection.add_callback_threadsafe(
                functools.partial(self._confirm_ready_for_job_start, job_id, customer_id)
            )
        except Exception as e:
            LOG.error(e, exc_info=True)

class ProcessingClient(threading.Thread):

    def __init__(self,callable_worker, worker_type ):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.worker_type = worker_type
        self.should_work = True
        self.message_que = queue.Queue()
        self.consumer_tag = None
        self.ready_for_processing = False
        self.callable_worker = callable_worker


    def run(self):
        LOG.info('Starting ProcessingClient {}'.format(self.worker_type))
        self.connection = create_mq_connection()
        if not self.connection:
            LOG.error('Failed to create mq connection - exiting')
            return
        while self.should_work:
            try:
                self.dataWait()
            except Exception as e:
                LOG.error(e, exc_info=True)
        LOG.info('Finishing ProcessingClient {}'.format(self.worker_type))

    def _stop(self):
        try:
            LOG.debug('Trying to stop ProcessingClient')
            self.should_work = False
            if self.data_channel:
                self.data_channel.stop_consuming(self.consumer_tag)
            close_mq_connection(self.connection)
        except Exception as e:
            LOG.error(e, exc_info=True)

    def thread_safe_stop(self):
        try:
            if self.connection:
                self.connection.add_callback_threadsafe(self._stop)
        except Exception as e:
            LOG.error(e, exc_info=True)

    def dataWait(self):
        LOG.debug('ProcessingClient starting data wait')
        if self.connection and self.connection.is_closed:
            LOG.warning('Reconnecting')
            self.connection = create_mq_connection()
        self.data_channel = self.connection.channel()
        self.data_channel.exchange_declare(exchange=MQ_DATA_EXCHANGE, exchange_type=MQ_DATA_EXCHANGE_TYPE)
        result = self.data_channel.queue_declare(queue=self.worker_type, exclusive=False )
        self.queue_name = result.method.queue
        self.data_channel.queue_bind(exchange=MQ_DATA_EXCHANGE, queue=self.queue_name, routing_key=self.queue_name)
        self.consumer_tag =  self.data_channel.basic_consume(queue=self.queue_name, on_message_callback=self.mq_data_callback, auto_ack=True)
        # self.data_channel.confirm_delivery()
        LOG.debug('ProcessingClient waiting for data')
        self.ready_for_processing = True
        try:
            self.data_channel.start_consuming()
        finally:
            self.ready_for_processing = False

    def mq_data_callback(self, ch, method, properties, body):
        try:
            job_id, step_id = job_step_from_props(properties)
            body_data = json.loads(body.decode())
            LOG.debug('mq_data_callback job id {} step {} correlation_id {} body {}'.format(job_id, step_id, properties.correlation_id, body ))
            self.callable_worker.add_callback_threadsafe(
                functools.partial( self.callable_worker.process_callback,job_id, step_id, properties.correlation_id, body_data)
            )
        except Exception as e:
            LOG.error(e, exc_info=True)

    def _next(self , job, actual_step_id, body_data):
        next_step = job.get_next_step_(actual_step_id)
        if next_step:
            LOG.debug('Next is {} {}'.format(next_step.id, next_step.worker_type, body_data))
            self.data_channel.basic_publish(
                exchange=MQ_DATA_EXCHANGE,
                routing_key=next_step.worker_type,
                properties=pika.BasicProperties(
                    correlation_id=job.id,
                    headers=job_headers(job.id, next_step.id)
                ),
                body=json.dumps(body_data))
            return True
        else:
            LOG.debug('This was last step {} {}'.format(actual_step_id, body_data))
            return False

    def _fist(self , job, route_name, body_data):
        first_step = job.get_first_step(route_name)
        if first_step:
            LOG.debug('First is {} {}'.format(first_step.id, first_step.worker_type, body_data))
            self.data_channel.basic_publish(
                exchange=MQ_DATA_EXCHANGE,
                routing_key=first_step.worker_type,
                properties=pika.BasicProperties(
                    correlation_id=job.id,
                    headers=job_headers(job.id, first_step.id)
                ),
                body=json.dumps(body_data))
            return True
        else:
            LOG.debug('First step not found in route {}'.format(route_name))
            return False

    def thread_safe_next(self, job, actual_step_id, body_data):
        if self.connection:
            self.connection.add_callback_threadsafe(
                functools.partial(self._next, job, actual_step_id, body_data)
            )

    def thread_safe_first(self, job, route_name, body_data):
        if self.connection:
            self.connection.add_callback_threadsafe(
                functools.partial(self._fist, job, route_name, body_data)
            )

class ProcessingContext():

    def __init__(self, job, configuration, step_id, correlation_id, body_data):
        self.job = job
        self.config = configuration
        self.step_id = step_id
        self.correlation_id = correlation_id
        self.body_data = body_data


    def get_config_value(self, key, default_value = None):
        if not self.config:
            if default_value:
                return default_value
            else:
                return None
        if not key in self.config:
            if default_value:
                return default_value
            else:
                return None
        return self.config[key]

class AbstractWorker(threading.Thread):
    __metaclass__ = ABCMeta

    def __init__(self, worker_type, auto_ready_confirmation, auto_send_heartbeat = True, data_supported = None, jobs_capacity = 1 ):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.should_work = True
        self.processing_client = ProcessingClient(self, worker_type)
        self.processing_client_started = False
        self.coordinator_client = CoordinatorClient(self, worker_type, auto_send_heartbeat=auto_send_heartbeat, data_supported=data_supported, jobs_capacity=jobs_capacity, auto_ready_confirmation=auto_ready_confirmation)
        self.coordinator_client_started = False
        # Callbacks requested via `add_callback`
        self._callbacks = collections.deque()
        self._sync = threading.Event()

    def sleep(self, t):
        self.coordinator_client.connection.sleep(t)

    @abstractmethod
    def start_processing(self, job_id):
        pass

    @abstractmethod
    def stop_processing(self, job_id):
        pass

    @abstractmethod
    def save_current_checkpoint(self, job_id):
        pass

    @abstractmethod
    def allocate_resources(self, job_id):
        pass

    @abstractmethod
    def free_resources(self, job_id):
        pass

    @abstractmethod
    def process(self, ctx):
        pass

    @property
    def jobs(self):
        return self.coordinator_client.jobs

    @property
    def jobs_ordered(self):
        return self.coordinator_client.jobs_ordered

    @property
    def jobs_submitted(self):
        return self.coordinator_client.jobs_submitted

    @property
    def worker_type(self):
        return self.coordinator_client.worker_type

    @property
    def jobs_capacity(self):
        return self.coordinator_client.jobs_capacity


    def get_id(self):
        return self.coordinator_client.get_id()

    def set_job_status_request(self, job_id, status, customer_id):
        self.coordinator_client.thread_safe_set_job_status_request(job_id,status, customer_id)

    def submit_job_request(self, job_data):
        self.coordinator_client.thread_safe_submit_job_request(job_data)

    def confirm_ready_for_job_start(self, job_id, customer_id):
        self.coordinator_client.thread_safe_confirm_ready_for_job_start(job_id, customer_id)

    def first(self, job, route_name, body_data):
        self.processing_client.thread_safe_first(job,route_name,body_data)

    def next(self, job, actual_step_id, body_data):
        self.processing_client.thread_safe_next(job,actual_step_id,body_data)

    def get_configuration(self, job_id):
        if job_id in self.coordinator_client.jobs:
            job = self.coordinator_client.jobs[job_id]
            return job.get_config(self.coordinator_client.worker_type)
        return None

    def add_callback_threadsafe(self, callback):
        if not callable(callback):
            raise TypeError(
                'callback must be a callable, but got %r' % (callback,))
        self._callbacks.append(callback)
        self._sync.set()
        LOG.debug('add_callback_threadsafe: added callback=%r', callback)

    def run_callbacks(self):
        self._sync.clear()
        for _ in range(len(self._callbacks)):
            try:
                callback = self._callbacks.popleft()
                LOG.debug('invoking callback=%r', callback)
                callback()
            except Exception as e:
                LOG.error(e, exc_info=True)
        self._sync.wait(0.1)


    def process_callback(self, job_id, step_id, correlation_id, body_data ):
        if job_id in self.coordinator_client.jobs:
            job = self.coordinator_client.jobs[job_id]
            ctx = ProcessingContext(job, self.get_configuration(job_id), step_id, correlation_id, body_data)
            self.process(ctx)
        else:
            LOG.warning('Job not found {}'.format(job_id))

    # JOB_STATUS_WAIT = 'status.wait' =  processing paused, save status, keep resources, job will continue
    # JOB_STATUS_STARTED = 'status.started' = start processing
    # JOB_STATUS_FINISHED = 'status.finished' = processing finished correctly, free resources, job will not continue
    # JOB_STATUS_CANCELED = 'status.canceled' = processing finished unexpectedly, free resources, job will not continue
    # JOB_STATUS_STOP = 'status.stop' = job stop - processing paused, save status, free resources, job will continue
    def job_status_callback(self, job_id):
        if job_id in self.coordinator_client.jobs:
            job = self.coordinator_client.jobs[job_id]
            if job.job_status == JOB_STATUS_WAIT:
                self.stop_processing(job_id)
                self.save_current_checkpoint(job_id)
            elif job.job_status == JOB_STATUS_STARTED:
                self.start_processing(job_id)
            elif job.job_status in [JOB_STATUS_FINISHED, JOB_STATUS_CANCELED]:
                self.stop_processing(job_id)
                self.free_resources(job_id)
            elif job.job_status == JOB_STATUS_STOP:
                self.stop_processing(job_id)
                self.save_current_checkpoint(job_id)
                self.free_resources(job_id)
        else:
            LOG.warning('Job not found {}'.format(job_id))

    def job_assign_callback(self, job_id):
        LOG.debug('Worker {} Job assign {}'.format(self.get_id(), job_id))
        if job_id in self.coordinator_client.jobs:
            job = self.coordinator_client.jobs[job_id]
            try:
                self.allocate_resources(job_id)
            except Exception as e:
                LOG.error(e, exc_info=True)
            if self.coordinator_client.auto_ready_confirmation:
                self.coordinator_client.thread_safe_confirm_ready_for_job_start(job.id, job.customer_id)
        else:
            LOG.warning('Job not found {}'.format(job_id))

    def job_unassign_callback(self, job_id):
        try:
            self.free_resources(job_id)
        except Exception as e:
            LOG.error(e, exc_info=True)
        # remove assignment
        job =  self.coordinator_client.jobs[job_id]
        self.coordinator_client.jobs.pop(job_id)
        self.coordinator_client.jobs_ordered.remove(job)
        LOG.debug('Worker {} job unassigned {}'.format(self.get_id(), job_id))

    # start stop sekvencie
    def start_coordinator_client(self):
        if not self.coordinator_client_started:
            self.coordinator_client.start()
            self.coordinator_client_started = True
        while self.coordinator_client.get_id() is None:
            LOG.debug('Waiting for registration')
            time.sleep(1)

    def start_processing_client(self):
        if not self.processing_client_started:
            self.processing_client.start()
            self.processing_client_started = True
        while not self.processing_client.ready_for_processing:
            LOG.debug('Waiting for ProcessingClient startup')
            time.sleep(0.1)

    def stop(self):
        self.should_work = False
        self.coordinator_client.thread_safe_stop()
        self.processing_client.thread_safe_stop()

    def initial_sequence(self):
        LOG.debug("Entering initial sequence")
        self.start_processing_client()
        self.start_coordinator_client()

    def run(self):
        self.initial_sequence()
        while self.should_work:
            try:
                self.run_callbacks()
            except Exception as e:
                LOG.error(e, exc_info=True)
        LOG.info('Finishing AbstractWorker {}'.format(self.coordinator_client.worker_type))

class QueueWorker(AbstractWorker):

    def __init__(self, worker_type, auto_ready_confirmation, auto_send_heartbeat = True, data_supported = None, jobs_capacity = 1):
        super().__init__(worker_type, auto_ready_confirmation, auto_send_heartbeat, data_supported, jobs_capacity)
        self.message_que = queue.Queue()

    def start_processing(self, job_id):
        LOG.debug('start_processing {}'.format(job_id))

    def stop_processing(self, job_id):
        LOG.debug('stop_processing {}'.format(job_id))

    def save_current_checkpoint(self, job_id):
        LOG.debug('save_current_checkpoint {}'.format(job_id))

    def allocate_resources(self, job_id):
        LOG.debug('allocate_resources {}'.format(job_id))

    def free_resources(self, job_id):
        LOG.debug('free_resources {}'.format(job_id))

    def process(self, ctx):
        LOG.debug('process {}'.format(ctx.job.id))
        self.message_que.put_nowait(ctx)