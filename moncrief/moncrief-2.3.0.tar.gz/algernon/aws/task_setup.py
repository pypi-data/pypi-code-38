import os

import boto3
import rapidjson


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
        time_remaining = context.get_remaining_time_in_millis() / 1000
        while time_remaining >= warning_level:
            messages = queue.recieve_messages(WaitTimeSeconds=20,  MaxNumberOfMessages=int(batch_size))
            for message in messages:
                payload = rapidjson.loads(message)
                production_fn(payload, context)
            time_remaining = context.get_remaining_time_in_millis() / 1000

    return wrapper
