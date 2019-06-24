#!/usr/bin/env python
from py_eureka_client import eureka_client

from api.exceptions import ServiceNoInstanceException, IllegalArgumentException
from client.ClientAuth import ClientAuth

FICUS_APP_NAME = "sobeyficus"

def do_service(service="", return_type="json",app_name=FICUS_APP_NAME,
               prefer_ip=False, prefer_https=False,
               method="GET", headers=None,params = None,
               data=None, timeout=None, auth=True):

    def walk_using_requests(url):

        global r
        try:
            if method.lower() == "get":
                r = requests.get(url, json=data, auth=ClientAuth() if auth else None,headers=headers,timeout=timeout,params=params)
            elif method.lower() =="post":
                r = requests.post(url, json=data, auth=ClientAuth() if auth else None,headers=headers,timeout=timeout,params=params)
            elif method.lower() == "put":
                r = requests.put(url, json=data, auth=ClientAuth() if auth else None,headers=headers,timeout=timeout,params=params)
            elif method.lower() =="patch":
                r = requests.patch(url, json=data, auth=ClientAuth() if auth else None,headers=headers,timeout=timeout,params=params)
            elif method.lower() =="delete":
                r = requests.delete(url, json=data, auth=ClientAuth() if auth else None,headers=headers,timeout=timeout,params=params)
            else:
                raise IllegalArgumentException(f"不支持的Rest操作:{method}")
            r.raise_for_status()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            from urllib.error import HTTPError
            raise HTTPError(url,500,"连接错误或超时",str(e),None)

        try:
            if return_type is None or return_type.lower() == "none":
                return None

            if len(r.content) <= 0:
                return None

            if return_type.lower() in ("json", "dict", "dictionary"):
                r.encoding = 'utf-8'
                return r.json()
            else:
                r.encoding = 'utf-8'
                return r.text
        finally:
            r.close()

    cli = eureka_client.get_discovery_client()
    if cli is None:
        raise Exception("Discovery Client has not initialized. ")

    return cli.walk_nodes(app_name, service, prefer_ip, prefer_https, walk_using_requests)

def check_instance_avaliable(app_name=FICUS_APP_NAME):
    cli = eureka_client.get_discovery_client()
    if cli is None:
        raise Exception("Discovery Client has not initialized. ")
    app = cli.applications.get_application(app_name.upper())
    if app.instances is None or len(app.instances)==0:
        raise ServiceNoInstanceException(f"{app_name}服务没有找到可用的实例")

from .ComputeExecutionClient import *
from .DataCrawlClient import *
from .HandlerLogClient import *
from .JobScheduleClient import *
from .ScheduleCacheClient import *
from .ScheduleJobTaskLogClient import *
