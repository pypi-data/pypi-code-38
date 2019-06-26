import traceback
from . import ALog
from . import AError

class Debug_Error(AError.Error):
    pass


def decorate_logTracebackOnException(func):
    """ 发生异常时日志堆栈.
    【示例】
    @decorate_logTracebackOnException
    def test():
        raise Runtime('123')

    test()
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            ALog.error(traceback.format_exc())
            raise

    return wrapper
