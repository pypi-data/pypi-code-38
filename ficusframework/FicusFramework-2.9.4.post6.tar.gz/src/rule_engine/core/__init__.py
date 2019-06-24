from abc import abstractmethod

from rule_engine import RuleFacts, IRuleListener


class IAgenda:
    """
    规则冲突集.也就是这个地方做匹配
    """

    @abstractmethod
    def get_matched_rules(self, ruleFacts:RuleFacts)->list:
        """
        传入实例,获取匹配的条件
        :param ruleFacts:
        :return:
        """
        pass


class IRuleGroupSession:
    """
    规则组的实例
    """

    @abstractmethod
    def add_facts(self, ruleFacts:RuleFacts):
        """
        添加运行的事实,也就是条件的实例
        :param ruleFacts:
        :return:
        """
        pass

    @abstractmethod
    def add_fact(self, key:str, value):
        """
        添加运行的事实,也就是条件的实例
        :param key:
        :param value:
        :return:
        """
        pass

    @abstractmethod
    def add_rule_listener(self, rule_listener:IRuleListener):
        """
        增加规则执行的消息监听
        :param rule_listener:
        :return:
        """
        pass

    @abstractmethod
    def execute(self)->list:
        """
        执行规则对比,得到结果
        :return:
        """
        pass