from abc import abstractmethod


class IMessageHandler:
    """

    """
    def __init__(self):
        self.initialed = False
        self.params = {}

    def is_initialed(self)->bool:
        return self.initialed

    def set_initialed(self, initialed=True):
        self.initialed = initialed

    def set_params(self,params):
        self.params = params

    def check_ficus_online(self):
        """
        检查ficus服务是否存在
        :param eureka_client:
        :return:
        """
        from client import check_instance_avaliable
        from api.exceptions import ServiceNoInstanceException
        try:
            check_instance_avaliable()
            return True
        except ServiceNoInstanceException:
            return False

    @abstractmethod
    def message(self,data):
        """
        将消息处理后存到目标fd,需要实现
        :param data:
        :return:
        """
        pass

    @abstractmethod
    def kill(self):
        """
        需要实现的结束的东西
        :return:
        """
        pass