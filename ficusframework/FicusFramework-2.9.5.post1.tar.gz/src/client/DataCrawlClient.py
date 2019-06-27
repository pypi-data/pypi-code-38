"""
Crawl的操作模块
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
        r = do_service(f"remote/dc-service/{site}/{project_code}/{code}")
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
        r = do_service(f"remote/dc-service/exists/{site}/{project_code}/{code}")
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


def query(site, project_code=None, code=None, crawl_type=None, page=1, size=20):
    """
    查询Crawl
    :param site: 站点
    :param project_code: 项目名
    :param code: CE的唯一code
    :param crawl_type: crawl的类型, JDBC/FILE/WEB/CUSTOM
    :param page: 分页页码,从1开始
    :param size: 分页大小,默认20
    :return:
    """
    check_instance_avaliable()

    try:
        r = do_service(f"remote/dc-service/{site}",params={'projectcode': project_code, 'code': code, 'type': crawl_type, 'page': page,
                                 'size': size})
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


def add_crawl(data_crawl):
    """
    新增一个Crawl
    :param data_crawl: crawl对象
    :return: 如果添加失败,就抛出异常,否则无返回
    """
    if data_crawl is None:
        return

    check_instance_avaliable()

    request = None
    if not isinstance(data_crawl, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(data_crawl, dict):
            # 如果是dict类型的,直接发
            request = data_crawl
    else:
        # 说明是munch的,那么就转成Dict的
        request = data_crawl.toDict()

    try:
        r = do_service(f"remote/dc-service/",data=request,method="post",return_type="none")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(e.response._content.decode('utf-8'))
        elif e.response.status_code >= 400 and e.response.status_code < 500:
            # 说明是认证相关的错误
            raise AuthException(f"服务端异常 {str(e)} {e.response._content.decode('utf-8')}")
        raise e
