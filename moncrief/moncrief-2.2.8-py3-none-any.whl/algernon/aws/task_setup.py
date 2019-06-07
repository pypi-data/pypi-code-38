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
