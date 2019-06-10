import base64
import gzip
import json


def lambda_handler(event, context):
    records = []
    for record in event['records']:
        # from cloudwath log event (gzip compressed)
        payload = json.loads(gzip.decompress(base64.b64decode(record['data'])).decode())
        events = []
        try:
            for log_event in payload['logEvents']:
                m = json.loads(log_event['message'])
                message = {
                    "time": m["time"],
                    "index": m["index"],
                    "source": m["source"],
                    "sourcetype": m["sourcetype"],
                    "host": m["host"]
                }
                if "event" in m:
                    message["event"] = m["event"]
                elif "raw" in m:
                    message["raw"] = m["raw"]
                else:
                    raise "Message must have event or raw key"
                events.append(json.dumps(message, ensure_ascii=False))
            result_code = 'Ok'
        except Exception as e:
            print(e)
            result_code = 'ProcessingFailed'
            events = [_['message'] for _ in payload['logEvents']]
        records.append({
            'recordId': record['recordId'],
            'result': result_code,
            'data': base64.b64encode("\n".join(events).encode()).decode()
        })
    return {'records': records}
