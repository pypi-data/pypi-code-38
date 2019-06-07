'''
The telemetry module emits messages to Google's Pub/Sub system.
'''
from datetime import datetime
from json import dumps

from google.cloud import pubsub_v1

from .config import CONFIG
from .logger import LOGGER

PUBLISHER = None
TOPIC_PATH = None
SENT_SUCCESS, SENT_FATAL = 0, 0


def send(data, mtype='event', **kwargs):
    '''
    Sends a message to the message queue system.

    :param data: contains a JSON serialized object (payload).
    :param mtype: defines the type of the message (default: `'event'`).
    :param kwargs: keyword list of additional attributes to be attached to the message.
    '''
    global PUBLISHER, TOPIC_PATH
    if PUBLISHER is None:
        PUBLISHER = pubsub_v1.PublisherClient()
        TOPIC_PATH = PUBLISHER.topic_path(
            CONFIG['telemetry']['project_id'],
            CONFIG['telemetry']['topic_name']
        )

    if isinstance(data, str):
        payload = dumps({'payload': data}).encode('utf-8')
    elif isinstance(data, dict):
        payload = dumps(data).encode('utf-8')
    else:
        payload = data

    future = PUBLISHER.publish(TOPIC_PATH,
                               data=payload,
                               type=mtype,
                               timestamp=str(
                                   (datetime.utcnow()-datetime(1970, 1, 1)).total_seconds()),
                               proto=CONFIG['telemetry']['proto'],
                               **kwargs)
    future.add_done_callback(telemetry_callback)


def telemetry_callback(message_future):
    '''
    Handles the message callback and potential errors.
    By default, this logs an error if there happens to be a 30s timeout.

    :param message_future: the future message object
    '''
    # When timeout is unspecified, the exception method waits indefinitely.
    if message_future.exception(timeout=30):
        LOGGER.error('Publishing message on %s threw an exception %s.',
                     CONFIG['telemetry']['topic_name'], message_future.exception())


def started(data, **kwargs):
    '''
    Notify pub/sub about a started task.

    :param data: the JSON data object of the task this event refers to. This can be `None`.
    :param kwargs: keyword list of additional attributes that are attached to the message, e.g. `job_guid='abc'`.
    '''
    send(data, event='started', state='pending', **kwargs)


def success(data, **kwargs):
    '''
    Notify pub/sub about are succesfully completed task.

    :param data: the JSON data object of the task this event refers to. This can be `None`.
    :param kwargs: keyword list of additional attributes that are attached to the message, e.g. `job_guid='abc'`.
   '''
    global SENT_SUCCESS
    SENT_SUCCESS += 1
    send(data, event='completed', state='success', **kwargs)


def failed(data, **kwargs):
    '''
    Notify pub/sub about a failed task.

    :param data: the JSON data object of the task this event refers to. This can be `None`.
    :param kwargs: keyword list of additional attributes that are attached to the message, e.g. `job_guid='abc'`.
    '''
    send(data, event='failed', state='pending', **kwargs)


def fatal(data, **kwargs):
    '''
    Notify pub/sub about a fatally failed task.

    :param data: the JSON data object of the task this event refers to. This can be `None`.
    :param kwargs: keyword list of additional attributes that are attached to the message, e.g. `job_guid='abc'`.
    '''
    global SENT_FATAL
    SENT_FATAL += 1
    send(data, event='disbanded', state='failed', **kwargs)


def retrying(data, **kwargs):
    '''
    Notify pub/sub about an initiated retry of a task.

    :param data: the JSON data object of the task this event refers to. This can be `None`.
    :param kwargs: keyword list of additional attributes that are attached to the message, e.g. `job_guid='abc'`.
    '''
    send(data, event='retry', state='pending', **kwargs)
