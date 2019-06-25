import logging

from api.exceptions import IllegalArgumentException
from client import ComputeExecutionClient, DataCrawlClient
from config.annotation import Value
from factdatasource import FactDatasourceProxyService

log = logging.getLogger('Ficus')


@Value("${actor.name:unknown}")
def actor_name():
    pass


def check_ficus_online():
    """
    检查ficus服务是否存在
    :return:
    """
    from client import check_instance_avaliable
    from api.exceptions import ServiceNoInstanceException
    try:
        check_instance_avaliable()
        return True
    except ServiceNoInstanceException:
        return False


def createNewComputeExecutions(registry, taskHandlerNames, site, projectcode):
    """
    尝试创建ce
    :param taskHandlerNames:
    :return:
    """
    if "computeexecutions" not in registry:
        return

    # region 先尝试添加ce
    needRegistryList = []

    # 表示有ce需要注册
    index = 1
    for computeexecution in registry["computeexecutions"]:

        # region 补默认值
        if "code" not in computeexecution or computeexecution["code"] == "" or computeexecution["code"] is None:
            computeexecution["code"] = f"{actor_name()}-{index}"

        if "execution" not in computeexecution or computeexecution["execution"] is None:
            computeexecution["execution"] = {"schedule": "0 0 0 1 1 ? 2099", "limits": -1, "params": []}
        else:
            if "schedule" not in computeexecution["execution"] or computeexecution["execution"]["schedule"] is None or \
                    computeexecution["execution"]["schedule"] == "":
                computeexecution["execution"]["schedule"] = "0 0 0 1 1 ? 2099"
            if "limits" not in computeexecution["execution"] or computeexecution["execution"]["limits"] is None:
                computeexecution["execution"]["limits"] = -1
            if "params" not in computeexecution["execution"] or computeexecution["execution"]["params"] is None:
                computeexecution["execution"]["params"] = {}
            if "retryTimes" not in computeexecution["execution"] or computeexecution["execution"]["retryTimes"] is None:
                computeexecution["execution"]["retryTimes"] = 0

        if "managed" not in computeexecution or computeexecution["managed"] is None:
            computeexecution["managed"] = {"type": "STANDBY", "serviceName": "STANDBY", "routing": "RANDOM"}
        else:
            if "type" not in computeexecution["managed"] or computeexecution["managed"]["type"] is None or \
                    computeexecution["managed"]["type"] == "":
                computeexecution["managed"]["type"] = "STANDBY"
            if "serviceName" not in computeexecution["managed"] or computeexecution["managed"]["serviceName"] is None or \
                    computeexecution["managed"]["serviceName"] == "":
                computeexecution["managed"]["serviceName"] = "STANDBY"
            if "routing" not in computeexecution["managed"] or computeexecution["managed"]["routing"] is None or \
                    computeexecution["managed"]["routing"] == "":
                computeexecution["managed"]["routing"] = "RANDOM"

        if "outputs" not in computeexecution or computeexecution["outputs"] is None:
            computeexecution["outputs"] = []
        # endregion

        index = index + 1

        # 开始进行validate的校验

        # region 第一轮的校验主要是做数据的验证
        if "name" not in computeexecution or computeexecution["name"] == "":
            raise IllegalArgumentException(f"自注册{computeexecution['code']}失败,名称为空")

        if "handler" not in computeexecution or computeexecution["handler"] == "":
            raise IllegalArgumentException(f"自注册{computeexecution['code']}失败,执行器为空")

        if "inputs" not in computeexecution or len(computeexecution["inputs"]) == 0:
            raise IllegalArgumentException(f"自注册{computeexecution['code']}失败,输入FD为空")

        if computeexecution["handler"] not in taskHandlerNames.keys():
            raise IllegalArgumentException(f"自注册{computeexecution['code']}失败,{computeexecution['handler']} 不存在")
        # endregion

        # region 第二轮的校验是判断东西在不在
        if ComputeExecutionClient.exists(site, projectcode, computeexecution["code"]):
            # 说明已经存在了, 那么就忽略
            continue
        # endregion

        # region 第三轮的校验是对应的fd,是否存在,因为自注册的handler应该不会太多, 它对应的input和output也不会太多,因此,这里就不再先做一次多handler的聚合了
        fds = list()
        fds = fds + computeexecution["inputs"]
        fds += computeexecution["outputs"]

        if not FactDatasourceProxyService.fd_client_proxy().exists_fds(fds):
            # 只要有一个fd不存在,就返回false
            # 表示校验异常了.
            raise IllegalArgumentException(f"自注册{computeexecution['code']}失败,{fds}不存在")
        # endregion

        # 到这的都是要的的
        needRegistryList.append(computeexecution)

    # 上面都是校验,如果到这了就是符合条件的,需要添加的ce了
    for computeexecution in needRegistryList:
        # 构造层ce对象,然后添加
        if taskHandlerNames[computeexecution["handler"]]:
            computeexecution["execution"]["params"]["__isMessageHandler__"] = "true"

        ce = {"type": "JAVA", "sourceFdCodes": computeexecution["inputs"], "outputFdCodes": computeexecution["outputs"],
              "code": computeexecution["code"], "description": computeexecution["description"],
              "projectCode": projectcode, "site": site, "target": computeexecution["handler"],
              "name": computeexecution["name"], "schedule": computeexecution["execution"]["schedule"],
              "limitTimes": computeexecution["execution"]["limits"],
              "params": computeexecution["execution"]["params"],
              "retryTimes": computeexecution["execution"]["retryTimes"],
              "executionType": computeexecution["managed"]["type"],
              "executionServiceName": computeexecution["managed"]["serviceName"],
              "routing": computeexecution["managed"]["routing"]}
        ComputeExecutionClient.add_compute_execution(ce)
        log.info(f"自动注册:{computeexecution['code']} 的ce")
    # endregion


def createNewCrawls(registry, taskHandlerNames, site, projectcode):
    """
    尝试创建crawl
    :param taskHandlerNames:
    :return:
    """
    if "crawls" not in registry:
        return

    # 表示有crawl需要注册
    # region 尝试添加crawl
    needRegistryList = []

    # 表示有crawl需要注册
    index = 1
    for crawl in registry["crawls"]:

        # region 补默认值
        if "code" not in crawl or crawl["code"] == "":
            crawl["code"] = f"{actor_name()}-{index}"

        if "execution" not in crawl:
            crawl["execution"] = {"schedule": "0 0 0 1 1 ? 2099", "limits": -1, "params": []}
        else:
            if "schedule" not in crawl["execution"]:
                crawl["execution"]["schedule"] = "0 0 0 1 1 ? 2099"
            if "limits" not in crawl["execution"]:
                crawl["execution"]["limits"] = -1
            if "retryTimes" not in crawl["execution"] or crawl["execution"][
                "retryTimes"] is None:
                crawl["execution"]["retryTimes"] = 0
            if "params" not in crawl["execution"]:
                crawl["execution"]["params"] = {}

        if "managed" not in crawl:
            crawl["managed"] = {"type": "STANDBY", "serviceName": "STANDBY", "routing": "RANDOM"}
        else:
            if "type" not in crawl["managed"]:
                crawl["managed"]["type"] = "STANDBY"
            if "serviceName" not in crawl["managed"]:
                crawl["managed"]["serviceName"] = "STANDBY"
            if "routing" not in crawl["managed"]:
                crawl["managed"]["routing"] = "RANDOM"

        if "outputs" not in crawl:
            crawl["outputs"] = []
        # endregion

        index = index + 1

        # 开始进行validate的校验

        # region 第一轮的校验主要是做数据的验证
        if "name" not in crawl or crawl["name"] == "":
            raise IllegalArgumentException(f"自注册{crawl['code']}失败,名称为空")

        if "handler" not in crawl or crawl["handler"] == "":
            raise IllegalArgumentException(f"自注册{crawl['code']}失败,执行器为空")

        if "outputs" not in crawl or len(crawl["outputs"]) == 0:
            raise IllegalArgumentException(f"自注册{crawl['code']}失败,输出FD为空")

        if crawl["handler"] not in taskHandlerNames.keys():
            raise IllegalArgumentException(f"自注册{crawl['code']}失败,{crawl['handler']} 不存在")
        # endregion

        # region 第二轮的校验是判断东西在不在
        if DataCrawlClient.exists(site, projectcode, crawl["code"]):
            # 说明已经存在了, 那么就忽略
            continue
        # endregion

        # region 第三轮的校验是对应的fd,是否存在,因为自注册的handler应该不会太多, 它对应的input和output也不会太多,因此,这里就不再先做一次多handler的聚合了
        fds = list()
        fds += crawl["outputs"]

        if not FactDatasourceProxyService.fd_client_proxy().exists_fds(fds):
            # 只要有一个fd不存在,就返回false
            # 表示校验异常了.
            raise IllegalArgumentException(f"自注册{crawl['code']}失败,{fds}不存在")
        # endregion

        # 到这的都是要的的
        needRegistryList.append(crawl)

    # 上面都是校验,如果到这了就是符合条件的,需要添加的ce了
    for crawl in needRegistryList:
        # 构造层ce对象,然后添加
        if taskHandlerNames[crawl["handler"]] :
            crawl["execution"]["params"]["__isMessageHandler__"] = "true"

        cr = {"type": "CUSTOM",
              "outputFdCodes": crawl["outputs"],
              "code": crawl["code"], "description": crawl["description"],
              "projectCode": projectcode, "site": site, "target": crawl["handler"],
              "name": crawl["name"], "schedule": crawl["execution"]["schedule"],
              "limitTimes": crawl["execution"]["limits"],
              "retryTimes": crawl["execution"]["retryTimes"],
              "params": crawl["execution"]["params"],
              "executionType": crawl["managed"]["type"],
              "executionServiceName": crawl["managed"]["serviceName"],
              "routing": crawl["managed"]["routing"]}
        DataCrawlClient.add_crawl(cr)
        log.info(f"自动注册:{crawl['code']} 的crawl")
    # endregion


def registry_after_started():
    """
    服务启动后,检测是否需要注册服务
    :return:
    """

    # 说明有yml文件,开始进行处理
    from registry import REGISTRY_PROPERTIES
    registry = REGISTRY_PROPERTIES

    if registry is None or len(registry) == 0:
        # 说明没有yml文件,不进行注册处理
        log.info("没有配置registry.yml,不进行执行器自动注册")
        return

    if "site" not in registry or "dataproject" not in registry:
        log.info("没有配置site或dataproject,不进行执行器自动注册")
        return

    # 说明还是配置了自注册的文件的,开始处理自注册的文件

    if "computeexecutions" not in registry and "crawls" not in registry:
        # 表示两种都没得,那也是直接返回
        log.info("没有需要注册的ce或crawl,忽略自动注册")
        return

    if not check_ficus_online():
        log.warn("启动时,没有可用的ficus服务,忽略自动注册")
        return

    # 这里开始正式的进行处理

    # 找到这个jar里面的所有的 TaskHandler
    from api.annotation.annotation import TASK_HANDLERS
    if len(TASK_HANDLERS) == 0:
        log.info("无可用的执行器,忽略自动注册")
        return

    # 我们假设 默认 的 site和project都是存在的
    # 找到所有的taskHandler的名称,key是名字,value是否是messageHandler
    taskHandlerNames = {}
    from api.handler.message.IMessageHandler import IMessageHandler
    for name, handler in TASK_HANDLERS.items():
        taskHandlerNames[name] = isinstance(handler, IMessageHandler)

    createNewComputeExecutions(registry, taskHandlerNames, registry["site"], registry["dataproject"])

    createNewCrawls(registry, taskHandlerNames, registry["site"], registry["dataproject"])
