import uuid

import rapidjson

from algernon.aws import Bullhorn, StoredData
from algernon.serializers import AlgJson


def _generate_callback(current_task_name: str, callback: str):
    if not callback:
        return None, False
    chain_links = callback.split('#')
    if len(chain_links) == 1:
        return callback, False
    if current_task_name not in chain_links:
        return chain_links[0], True
    for pointer, link in enumerate(chain_links):
        if link == current_task_name:
            try:
                return chain_links[pointer+1], True
            except IndexError:
                return None, False


def _callback(original_payload, bullhorn=None, result=None, ):
    callback_fn, chained = _generate_callback(original_payload['task_name'], original_payload.get('callback'))
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
    if chained:
        msg['callback'] = original_payload.get('callback')
    bullhorn.publish('callback', topic_arn, AlgJson.dumps(msg))
    return bullhorn


def rebuild_event(original_event):
    return AlgJson.loads(AlgJson.dumps(original_event))


def queued(production_fn):
    def wrapper(*args):
        results = []
        event = args[0]
        bullhorn = None
        local_context = {'aws': args[1]}
        for entry in event['Records']:
            entry_body = rapidjson.loads(entry['body'])
            original_payload = rapidjson.loads(entry_body['Message'])
            result = production_fn(original_payload, local_context)
            results.append(result)
            bullhorn = _callback(original_payload, bullhorn, result)
        return results

    return wrapper
