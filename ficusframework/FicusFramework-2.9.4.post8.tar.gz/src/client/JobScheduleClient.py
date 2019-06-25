"""
schedule相关的操作
"""
import requests
from munch import Munch

from api.exceptions import ServiceInnerException, AuthException
from client import check_instance_avaliable, do_service


def add_job(job_info):
    """
    新增计划
    :param job_info: jobInfo对象
    :return: 如果成功返回True,否则返回False
    """
    if job_info is None:
        return False

    check_instance_avaliable()

    request = None
    if not isinstance(job_info, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(job_info, dict):
            # 如果是dict类型的,直接发
            request = job_info
    else:
        # 说明是munch的,那么就转成Dict的
        request = job_info.toDict()

    try:
        r = do_service(f"remote/js-service/", data=request, method="post")
        return r
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def reschedule(job_info):
    """
    更新计划
    :param job_info:
    :return:
    """
    if job_info is None:
        return False

    check_instance_avaliable()

    request = None
    if not isinstance(job_info, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(job_info, dict):
            # 如果是dict类型的,直接发
            request = job_info
    else:
        # 说明是munch的,那么就转成Dict的
        request = job_info.toDict()

    try:
        r = do_service(f"remote/js-service/", data=request, method="put")
        return r
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e


def remove(job_id):
    """
    删除一个计划
    :param job_id:
    :return:
    """
    check_instance_avaliable()

    try:
        r = do_service(f"remote/js-service/{job_id}",method="delete")
        if  r is not None:
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


def pause(job_id):
    """
    暂停计划
    :param job_id:
    :return:
    """
    check_instance_avaliable()

    try:
        r = do_service(f"remote/js-service/{job_id}/pause", method="post")
        if  r is not None:
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


def resume(job_id):
    """
    恢复计划
    :param job_id:
    :return:
    """
    check_instance_avaliable()

    try:
        r = do_service(f"remote/js-service/{job_id}/resume", method="post")
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


def stop(job_id):
    """
    停止计划
    :param job_id:
    :return:
    """
    check_instance_avaliable()

    try:
        r = do_service(f"remote/js-service/{job_id}/stop", method="post")
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


def trigger_job(job_id, params=None):
    """
    触发一个计划
    :param job_id:
    :param params:
    :return:
    """
    check_instance_avaliable()

    try:
        r = do_service(f"remote/js-service/{job_id}/trigger",data=params, method="post")
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


def list_jobs():
    """
    列出所有的计划
    :return:
    """
    check_instance_avaliable()

    try:
        r = do_service(f"remote/js-service")
        if r is not None:
            if isinstance(r, list):
                return [Munch(x) for x in r]
            else:
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


def get_jobs(actor_name):
    """
    找到某一个类型的所有计划
    :param actor_name:
    :return:
    """
    check_instance_avaliable()

    try:
        r = do_service(f"remote/js-service/{actor_name}")
        if r is not None:
            if isinstance(r, list):
                return [Munch(x) for x in r]
            else:
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


def find_by_site_and_code(site, project_code, code):
    """
    返回某一个计划
    :param site:
    :param project_code:
    :param code:
    :return:
    """
    check_instance_avaliable()

    try:
        r = do_service(f"remote/js-service/{site}/{project_code}/{code}")
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
