#encoding:utf-8
import json
from pprint import pprint


def _handle_datatype(values):
    """
    处理数据类型
    """
    if isinstance(values, list):
        record = {}
        for val in values:
            if 'name' in val and 'value' in val:
                name = val.pop("name")
                value = val.pop("value")
                value = _handle_datatype(value)
                record[name] = value
            record.update(val)
        return record
    elif isinstance(values, dict):
        result = {}
        for key, val in values.items():
            v = _handle_datatype(val)
            result[key] = v
        return result
    return values

def handle_request(request):
    """
    请求处理
    """
    response  = {}
    for key, val in request.items():
        val = _handle_datatype(val)
        response[key] = val
    return response

def harparser(filename, debug=False):
    req_list = []
    resp_list = []
    with open(filename) as f:
        data = f.read()
        records = json.loads(data)
        logs = records.get("log", {})
        entries = logs.get("entries",[])
        for entry in entries:
            request = entry.get("request",{})
            response = entry.get("response",{})
            req = handle_request(request)
            resp = handle_request(response)
            req_list.append(req)
            resp_list.append(resp)
            if debug:
                print(req)
                print(resp)
                print('-'*80)
    return req_list, resp_list

if __name__ == '__main__':
    filename = "har/127.0.0.1-8000+2019-06-27+11-57-05.har"
    harparser(filename, True)