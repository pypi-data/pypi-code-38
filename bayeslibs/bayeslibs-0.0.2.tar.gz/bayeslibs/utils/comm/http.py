"""
@project:medical_robot_backend
@language:python3
@create:2019/4/26
@author:qianyang@aibayes.com
@description:none
"""
import json
from urllib.request import Request, urlopen


class Http:
    def __init__(self):
        pass

    @staticmethod
    def request_json(url, data=None):
        if not data:
            return None
        data = json.dumps(data).encode('utf-8')
        header = {'Content-Type': 'application/json'}
        req = Request(url, data, header)
        try:
            f = urlopen(req, timeout=5)
            result_json = f.read().decode('utf-8')
            result_json = json.loads(result_json)
            f.close()
            return result_json
        except Exception as err:
            print('http request timeout: {}'.format(err))
            res = {'status': 404, 'msg': 'http request timeout'}
            return res


if __name__ == '__main__':
    pass
