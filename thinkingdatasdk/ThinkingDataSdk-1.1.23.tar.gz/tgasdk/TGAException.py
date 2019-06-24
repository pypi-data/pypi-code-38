#encoding:utf8
class TGAException(Exception):
    pass


class TGAIllegalDataException(TGAException):
    """
    在发送的数据格式有误时，SDK会抛出此异常，用户应当捕获并处理。
    """
    pass


class TGANetworkException(TGAException):
    """
    在因为网络或者不可预知的问题导致数据无法发送时，SDK会抛出此异常，用户应当捕获并处理。
    """
    pass


class TGADebugException(Exception):
    """
    Debug模式专用的异常
    """
    pass