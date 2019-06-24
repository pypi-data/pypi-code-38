import uuid

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
