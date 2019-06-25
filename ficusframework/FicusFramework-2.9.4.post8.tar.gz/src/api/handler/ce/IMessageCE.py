import threading

from confluent_kafka.cimpl import Consumer, KafkaError, KafkaException

from api.exceptions import IllegalArgumentException
from api.handler.message.IMessageHandler import IMessageHandler
from api.model.ResultVO import ResultVO, FAIL_CODE, SUCCESS
from config.annotation import Value
from factdatasource import FactDatasourceProxyService
from schedule.utils.log import FrameworkHandlerLogger



class IMessageCE(IMessageHandler):
    """

    """

    @Value("${actor.name:unknown}")
    def actor_name(self):
        pass

    def init_message_ce(self, site, projectCode, code) -> ResultVO:
        """
        初始化消息CE
        :param site:
        :param projectCode:
        :param code:
        :return:
        """
        from client import ComputeExecutionClient
        dataComputeExecution = ComputeExecutionClient.get(site, projectCode, code)

        if dataComputeExecution is None:
            return ResultVO(FAIL_CODE, f"执行失败,没有找到Code:{code}的Ce")

        self.dataComputeExecution = dataComputeExecution

        # 找到kafka的 来源
        sourceFdCodes = dataComputeExecution.sourceFdCodes
        if sourceFdCodes is None or len(sourceFdCodes) == 0:
            return ResultVO(FAIL_CODE, f"执行失败,没有找到Code:{code}的Ce 没有配置sourceFactData")

        sourceFd = None

        for sourceFdCode in sourceFdCodes:
            # 找到FD的定义
            fd = FactDatasourceProxyService.fd_client_proxy().fd(sourceFdCode)
            if fd is None:
                return ResultVO(FAIL_CODE, f"执行失败,没有找到Code:{code}的Ce 配置的sourceFactData {sourceFdCode} 不存在")
            if fd.type in ["KAFKA", "AMQP", "JMS"]:
                # 说明找到了kafka或amqp或jms的来源fd,只找头一个
                sourceFd = fd
                break

        if sourceFd is None:
            return ResultVO(FAIL_CODE, f"执行失败,没有找到Code:{code}的Ce 没有配置消息的来源")

        # 到这里来fd只可能是两种: KAFKA或AMQP或jms
        # 现在先只支持kafka

        # 启动消息队列的监听
        self.t = MessageListener(self, f"{site}.{projectCode}.{code}", sourceFd.target, sourceFd.connection)
        self.t.setDaemon(False)  # 设置为非守护线程.
        self.t.start()

        return SUCCESS

    def check_and_init(self):
        """
        定期执行，检测是否初始化，如果没有则初始化
        :return:
        """
        if self.is_initialed():
            return

        # 说明ficus都没有启动,没法始化消息监听,放弃
        if not self.check_ficus_online():
            FrameworkHandlerLogger.log_error("启动时,没有可用的ficus服务,忽略初始化消息监听")
            return

        self.set_initialed()

        # region 找到自己这个类的名字和对象,如果是空的就放弃
        from api.annotation.annotation import TASK_HANDLERS
        if len(TASK_HANDLERS) == 0:
            return

        task_handler_name = None
        for k, v in TASK_HANDLERS.items():
            if v is self:
                task_handler_name = k
                break

        if task_handler_name is None:
            return
        # endregion

        FrameworkHandlerLogger.log_info("MessageCE开始初始化消息队列")

        from registry import REGISTRY_PROPERTIES
        registry = REGISTRY_PROPERTIES

        if registry is None or len(registry) == 0 or "computeexecutions" not in registry:
            # 说明没有yml文件,不进行注册处理
            FrameworkHandlerLogger.log_warn("MessageCE开始初始化消息队列,registry.yml中没有配置ce 不自动初始化.请使用调度触发")
            return

        # 遍历,找到这个CE的配置
        index = 1
        for computeexecution in registry["computeexecutions"]:
            if "handler" not in computeexecution or computeexecution["handler"] == "":
                raise IllegalArgumentException(f"初始化消息队列{computeexecution['code']}失败,执行器为空")

            if task_handler_name == computeexecution["handler"]:
                # 说明是一样的ce
                # 那么这里就需要开始进行初始化

                if "code" not in computeexecution or computeexecution["code"] == "" or computeexecution["code"] is None:
                    computeexecution["code"] = f"{self.actor_name()}-{index}"

                code = computeexecution["code"]
                site = registry["site"]
                dataproject = registry["dataproject"]

                stringResultVO = self.init_message_ce(site, dataproject, code)

                FrameworkHandlerLogger.log_info(
                    "MessageCE开始初始化消息队列,初始化CE:" + site + "_" + dataproject + "_" + code + " 完成,结果:" + stringResultVO.msg)

                from api.model.ResultVO import SUCCESS_CODE
                if stringResultVO.code == SUCCESS_CODE:
                    # 成功一个就不继续了
                    self.set_params({"site_": site, "projectCode_": dataproject, "code_": code})
                    break

            index = index + 1

    def whileCheck(self):
        while self.is_initialed() == False:
            self.check_and_init()
            import time
            time.sleep(30)

    def __init__(self):
        IMessageHandler.__init__(self)

        # 这里启动一个线程来检测是否启动了
        self.mthread = threading.Thread(target=self.whileCheck)
        self.mthread.setDaemon(False)
        self.mthread.start()

        self.t = None

    def stop(self):
        if self.t is not None:
            self.t.stop()

        self.initialed = False


class MessageListener(threading.Thread):
    """
        消息队列的处理器
    """

    def __init__(self, messageCe: IMessageCE, group_id, topic, brokers):
        threading.Thread.__init__(self)
        # 初始化
        self.messageCe = messageCe

        # 开启kafka的消息监听
        config = {'bootstrap.servers': brokers, 'group.id': group_id, 'session.timeout.ms': 6000,
                  'default.topic.config': {'auto.offset.reset': 'largest'}}
        import logging
        self.consumer = Consumer(config, logger=logging.getLogger("Ficus"))  # TODO 这里的入参好像有问题
        self.consumer.subscribe([topic])

        self.go_on = True

    def stop(self):
        self.go_on = False

    def run(self):
        """
        监听消息
        :return:
        """

        # 开始循环接收消息
        while self.go_on:
            try:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        # Error
                        raise KafkaException(msg.error())
                else:
                    # 进行消息的处理
                    self.messageCe.message(msg.value())
            except Exception as e:
                FrameworkHandlerLogger.log_error(f"接收消息出现问题,", e)
            finally:
                if self.go_on == False:
                    # 把消息队列关闭掉
                    self.consumer.close()
