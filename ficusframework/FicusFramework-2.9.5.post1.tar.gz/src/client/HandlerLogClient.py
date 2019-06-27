"""
日志记录相关的操作
"""
import requests
from munch import Munch

from api.exceptions import ServiceInnerException, AuthException
from client import check_instance_avaliable, do_service

__all__ = ["log_debug", "log_info", "log_warn", "log_error"]


def log_debug(message):
    """
    打印debug日志
    :param message: 日志记录
    :return:
    """
    if message is None:
        return

    check_instance_avaliable()

    _inner_request(message, "debug")


def log_info(message):
    """
    打印info日志
    :param message: 日志记录
    :return:
    """
    if message is None:
        return

    check_instance_avaliable()

    _inner_request(message, "info")


def log_warn(message):
    """
    打印warn日志
    :param message: 日志记录
    :return:
    """
    if message is None:
        return

    check_instance_avaliable()

    _inner_request(message, "warn")


def log_error(message):
    """
    打印error日志
    :param message: 日志记录
    :return:
    """
    if message is None:
        return

    check_instance_avaliable()

    _inner_request(message, "error")


def _inner_request(message, level):
    """
    构造请求,并发送
    :param message: 消息
    :param level: 级别
    :return:
    """
    request = None
    if not isinstance(message, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(message, dict):
            # 如果是dict类型的,直接发
            request = message
    else:
        # 说明是munch的,那么就转成Dict的
        request = message.toDict()
    try:
        r = do_service(f"remote/hl-service/{level}",data=request,method="post",return_type="none")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e
