import logging
import os
import traceback

import boto3
import rapidjson
from algernon.serializers import AlgJson


def queued(production_fn):
    def wrapper(*args):
        results = []
        event = args[0]
        context = args[1]
        for entry in event['Records']:
            entry_body = rapidjson.loads(entry['body'])
            original_payload = rapidjson.loads(entry_body['Message'])
            results.append(production_fn(original_payload, context))
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
        time_remaining = context.get_remaining_time_in_millis()
        while time_remaining >= (warning_level*1000):
            messages = queue.recieve_messages(WaitTimeSeconds=20,  MaxNumberOfMessages=int(batch_size))
            for message in messages:
                payload = rapidjson.loads(message.body)
                event.update(payload)
                try:
                    results = production_fn(event, context)
                    if results:
                        event.update(results)
                    message.delete()
                except Exception as e:
                    trace = traceback.format_exc()
                    exception = e.args
                    logging.error(f'encountered an exception while working a state machine event: {event}, '
                                  f'exception args: {exception}, traceback: {trace}')
            time_remaining = context.get_remaining_time_in_millis()
        return AlgJson.dumps(event)

    return wrapper
