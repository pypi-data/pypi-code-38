from nameko.rpc import rpc as nameko_rpc

from marshmallow.exceptions import ValidationError

from .response import RpcResponse
from .exceptions import ServiceException


def rpc(func):
    """
    Nameko Rpc Dispatch Result Wrapper

    作用： 添加自定义响应`RpcResponse`内容返回和自定义异常处理`ServiceException`

        为了有效的处理服务异常，服务所有异常应继承自ServiceException
    """

    @nameko_rpc
    def wrapper(*args, **kwargs):
        try:
            call_result = func(*args, **kwargs)
        except ServiceException as e:
            exception_info = e.msg if hasattr(e, 'msg') else None
            return RpcResponse(msg=exception_info, code=e.code).result
        except ValidationError as schema_error:
            # 捕捉表单验证异常
            return RpcResponse(data=schema_error.normalized_messages(), code=400).result
        # except Exception as E:
        #     print(E)
        #     print('Uncaught RPC response exception: {}.'.format(E))
        #     return RpcResponse(data={'info': 'Service error'}, code=500).result
        else:
            return call_result.result

    return wrapper
