"""
nameko service response wrapper
"""

import json


class RpcResponse(object):
    """RPC 调用返回响应"""

    def __init__(self, data=None, code=200, msg=None, *, format=None):
        """
        Args:
            data: 响应结果（正常或异常返回结果）
            code: 响应码（对应于HTTP响应码）
            msg: 附加消息
            format: dict/json
        """

        self.data = data
        self.code = code
        self.msg = msg
        self.format = format        # dict/json/only_data

    @property
    def result(self):
        """将RPC响应封装为字典对象
        result:
            {
                'data': self.data,
                'code': self.code,
                'msg': self.msg,
                ...
            }
        """

        result = {
            'data': self.data,
            'code': self.code,
            'msg': self.msg
        }

        # 输出格式选择
        if not self.format or self.format == 'dict':
            return result
        elif self.format == 'json':
            return json.dumps(result)
        elif self.format == 'only_data':
            return result['data']
        else:
            return result
