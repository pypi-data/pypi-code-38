"""
缓存相关的操作
"""
import requests
from munch import Munch

from api.exceptions import ServiceInnerException, AuthException
from client import check_instance_avaliable, do_service


def set_value(key, value):
    """
    设置缓存值
    :param key:
    :param value:
    :return:
    """
    if key is None or value is None:
        return

    check_instance_avaliable()

    request = value
    if not isinstance(value, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(value, dict):
            # 如果是dict类型的,直接发
            request = value
    else:
        # 说明是munch的,那么就转成Dict的
        request = value.toDict()

    try:
        r= do_service(f"remote/sc-service/{key}", data=request, method="post",return_type="none")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def set_if_absent(key, value):
    """
    设置缓存自,如果key不存在
    :param key:
    :param value:
    :return:
    """
    if key is None or value is None:
        return False

    check_instance_avaliable()

    request = None
    if not isinstance(value, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(value, dict):
            # 如果是dict类型的,直接发
            request = value
    else:
        # 说明是munch的,那么就转成Dict的
        request = value.toDict()

    try:
        r = do_service(f"remote/sc-service/{key}", data=request, method="put")
        return r
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def get(key):
    """
    获取某一个缓存
    :param key:
    :return:
    """
    check_instance_avaliable()

    try:
        r = do_service(f"remote/sc-service/{key}")
        if r is not None:
            try:
                return Munch(r)
            except (TypeError,ValueError,AttributeError):
                return r
        else:
            return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def delete(key):
    """
    删除某一个缓存
    :param key:
    :return:
    """
    check_instance_avaliable()

    try:
        r = do_service(f"remote/sc-service/{key}",method="delete",return_type="none")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e
