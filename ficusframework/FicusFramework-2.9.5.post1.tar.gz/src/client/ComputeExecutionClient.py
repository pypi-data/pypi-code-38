"""
CE的操作模块
"""
import requests
from munch import Munch

from api.exceptions import ServiceInnerException, AuthException
from client import check_instance_avaliable, do_service


def get(site, project_code, code):
    """
    获取CE
    :param site: 站点
    :param project_code: 项目名
    :param code: CE的唯一code
    :return: 如果这个ce存在,返回ce对象.否则返回空
    """
    check_instance_avaliable()

    try:
        r = do_service(f"remote/ce-service/{site}/{project_code}/{code}")

        if r is not None:
            return Munch(r)
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


def exists(site, project_code, code):
    """
    校验CE是否存在
    :param site: 站点
    :param project_code: 项目名
    :param code: CE的唯一code
    :return: 如果这个ce存在,返回true.否则,返回false
    """
    check_instance_avaliable()

    try:
        r = do_service(f"remote/ce-service/exists/{site}/{project_code}/{code}")

        if r is not None:
            return r
        else:
            return False
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code<500 and e.response.status_code!=404:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def add_compute_execution(data_compute_execution):
    """
    新增一个CE
    :param data_compute_execution: ce对象
    :return: 如果添加失败,就抛出异常,否则无返回
    """
    if data_compute_execution is None:
        return

    check_instance_avaliable()

    request = None
    if not isinstance(data_compute_execution, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(data_compute_execution, dict):
            # 如果是dict类型的,直接发
            request = data_compute_execution
    else:
        # 说明是munch的,那么就转成Dict的
        request = data_compute_execution.toDict()

    try:
        r = do_service(f"remote/ce-service/",method="post",data=request,return_type="none")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e
