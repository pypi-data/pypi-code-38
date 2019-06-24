import logging
import os
import traceback
import uuid

import boto3
import rapidjson

from algernon.aws import Bullhorn, StoredData
from algernon.serializers import AlgJson


def _callback(original_payload, bullhorn=None, result=None, ):
    callback_fn = original_payload.get('callback')
    if not callback_fn:
        return bullhorn
    if bullhorn is None:
        bullhorn = Bullhorn.retrieve()
    topic_arn = bullhorn.find_task_arn(callback_fn)
    if result is None:
        result = {}
    if result:
        result = StoredData.from_object(uuid.uuid4(), result, full_unpack=True)
    msg = {'task_name': callback_fn, 'task_kwargs': result}
    bullhorn.publish('callback', topic_arn, AlgJson.dumps(msg))
    return bullhorn


def queued(production_fn):
    def wrapper(*args):
        results = []
        event = args[0]
        context = args[1]
        bullhorn = None
        local_context = {}
        for entry in event['Records']:
            entry_body = rapidjson.loads(entry['body'])
            original_payload = rapidjson.loads(entry_body['Message'])
            local_context.update(original_payload)
            result = production_fn(local_context, context)
            results.append(result)
            bullhorn = _callback(original_payload, bullhorn, result)

        return results

    return wrapper


def stated(production_fn):
    def wrapper(*args):
        event = args[0]
        context = args[1]
        queue_url = event.get('queue_url', os.getenv('QUEUE_URL'))
        warning_level = event.get('warning_level', os.getenv('WARNING_LEVEL', 90))
        batch_size = event.get('message_batch_size', os.getenv('MESSAGE_BATCH_SIZE', 10))
        if not queue_url:
            raise RuntimeError('functions with the @stated decorator must have a queue_url provided by the event, '
                               'or set under the key QUEUE_URL as an environment variable')
        queue = boto3.resource('sqs').Queue(queue_url)
        bullhorn = Bullhorn.retrieve()
        time_remaining = context.get_remaining_time_in_millis()
        while time_remaining >= (warning_level*1000):
            messages = queue.recieve_messages(WaitTimeSeconds=20,  MaxNumberOfMessages=int(batch_size))
            for message in messages:
                message_body = rapidjson.loads(message.body)
                payload = rapidjson.loads(message_body['Message'])
                callback_fn = payload.get('callback')
                event.update(payload)
                try:
                    results = production_fn(event, context)
                    if results:
                        event.update(results)
                        if callback_fn:
                            topic_arn = bullhorn.find_task_arn(callback_fn)
                            stored_results = StoredData.from_object(uuid.uuid4(), results, full_unpack=True)
                            msg = {'task_name': callback_fn, 'task_kwargs': stored_results}
                            bullhorn.publish('callback', topic_arn, AlgJson.dumps(msg))
                    message.delete()
                except Exception as e:
                    trace = traceback.format_exc()
                    exception = e.args
                    logging.error(f'encountered an exception while working a state machine event: {event}, '
                                  f'exception args: {exception}, traceback: {trace}')
            time_remaining = context.get_remaining_time_in_millis()
        return AlgJson.dumps(event)

    return wrapper
