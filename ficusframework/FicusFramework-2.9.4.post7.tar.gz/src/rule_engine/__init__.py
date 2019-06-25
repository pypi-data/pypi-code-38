import datetime
import time
from abc import abstractmethod
from collections import Iterable
from enum import Enum
from typing import Iterator


# region 对象模型
class RuleActionTypeEnum(Enum):
    DEFAULT = 1     # 默认,直接返回 params
    MVEL = 2        # 用MVEL表达式 执行 action中的内容  PYTHON不支持
    BEAN = 3        # 从action中的字符串作为bean的源码,获取实现了 IAction的 源码  PYTHON不支持
    CLASS = 4       # 从action中的字符串作为类路径,反射获取 IAction实例  PYTHON不支持
    AVIATOR = 5     # 用aviator表达式 执行 action中的内容  PYTHON不支持
    PY_CLASS = 6    # python源码
    PY_BEAN = 7     # python类路径
    PY_EXP = 8      # python表达式  这里可能还需要一种 python表达式的类型,  因为 PY_BEAN或PY_CLASS其实都是需要实现IRuleAction接口的,应该需要一种表达式可以不限制输入的

    def actions(self):
        """
        返回默认实现
        :return:
        """
        if self in [RuleActionTypeEnum.MVEL,RuleActionTypeEnum.BEAN,RuleActionTypeEnum.CLASS,RuleActionTypeEnum.AVIATOR]:
            from rule_engine.action import UnSupportAction
            return UnSupportAction()
        elif  self == RuleActionTypeEnum.DEFAULT:
            from rule_engine.action import DefaultAction
            return DefaultAction()
        elif self == RuleActionTypeEnum.PY_EXP:
            from rule_engine.action import PyExpAction
            return PyExpAction()
        return None


class RuleConditionOperationEnum(Enum):
    DO_NOTHING = 0
    EQUAL = 1
    NOTEQUAL =2
    GT =3
    GTE =4
    LT =5
    LTE = 6
    IN = 7
    RANGE =8
    MVEL = 9        # 用MVEL表达式 执行 target 中的内容   PYTHON不支持
    BEAN = 10       # 从target中的字符串作为bean的源码,获取实现了 IRuleConditionOperation 的 bean  PYTHON不支持
    CLASS = 11      # 从target中的字符串作为类路径,反射获取 IRuleConditionOperation 实例 PYTHON不支持
    AVIATOR = 12    # 用aviator表达式 执行 target中的内容   PYTHON不支持
    PY_BEAN = 13     # python源码
    PY_CLASS = 14   # python类路径
    PY_EXP = 15     # python表达式  这里可能还需要一种 python表达式的类型,  因为 PY_BEAN或PY_CLASS其实都是需要实现IRuleConditionOperation接口的,应该需要一种表达式可以不限制输入的

    def allowed_target_type(self):
        """
        返回允许的字段类型
        :return:
        """
        if self in [RuleConditionOperationEnum.EQUAL,RuleConditionOperationEnum.NOTEQUAL,RuleConditionOperationEnum.IN]:
            return [int,float,str,time.struct_time,datetime.datetime,bool,Enum,dict,object]
        elif self in [RuleConditionOperationEnum.GT,RuleConditionOperationEnum.GTE,RuleConditionOperationEnum.LT,RuleConditionOperationEnum.LTE]:
            return [int,float,time.struct_time,datetime.datetime,object]
        elif self in [RuleConditionOperationEnum.RANGE]:
            return [int,float,object]

        return []

    def condition_operation(self):
        """
        返回类型的实例
        :return:
        """
        if self in [RuleConditionOperationEnum.MVEL,RuleConditionOperationEnum.BEAN,RuleConditionOperationEnum.CLASS,RuleConditionOperationEnum.AVIATOR]:
            from rule_engine.operation import UnSupportOperation
            return UnSupportOperation()
        elif self == RuleConditionOperationEnum.DO_NOTHING:
            from rule_engine.operation import DoNothingOperation
            return DoNothingOperation()
        elif self == RuleConditionOperationEnum.EQUAL:
            from rule_engine.operation import DefaultEqualOperation
            return DefaultEqualOperation()
        elif self == RuleConditionOperationEnum.NOTEQUAL:
            from rule_engine.operation import DefaultNotEqualOperation
            return DefaultNotEqualOperation()
        elif self == RuleConditionOperationEnum.IN:
            from rule_engine.operation import DefaultINOperation
            return DefaultINOperation()
        elif self == RuleConditionOperationEnum.GT:
            from rule_engine.operation import DefaultGTOperation
            return DefaultGTOperation()
        elif self == RuleConditionOperationEnum.GTE:
            from rule_engine.operation import DefaultGTEOperation
            return DefaultGTEOperation()
        elif self == RuleConditionOperationEnum.LT:
            from rule_engine.operation import DefaultLTOperation
            return DefaultLTOperation()
        elif self == RuleConditionOperationEnum.LTE:
            from rule_engine.operation import DefaultLTEOperation
            return DefaultLTEOperation()
        elif self == RuleConditionOperationEnum.RANGE:
            from rule_engine.operation import DefaultRangeOperation
            return DefaultRangeOperation()
        elif self == RuleConditionOperationEnum.PY_EXP:
            from rule_engine.operation import PyExpOperation
            return PyExpOperation()
        return None

class RuleConditionRelationEnum(Enum):
    """
    规则条件 相对于上一个条件的 逻辑关系, 默认是AND
    """
    AND = 1     #默认关系
    OR = 2

    def relation(self,one:bool,other:bool)->bool:
        if self == RuleConditionRelationEnum.OR:
            return one or other
        else:
            return one and other

class RuleConditionInfo:

    def __init__(self, source:str=None, operation:RuleConditionOperationEnum=None, rule_operation=None, target:str=None, target_provider=None, enable=True, subs:list=[], relation:RuleConditionRelationEnum=None) -> None:
        """

        :param source:
        :param operation:
        :param rule_operation:
        :param target:
        :param target_provider:
        :param enable:
        :param subs:
        :param relation:
        """
        self.source = source
        self.operation = operation
        self.rule_operation = rule_operation
        self.target = target
        self.target_provider = target_provider
        self.enable = enable
        self.subs = subs
        self.relation = relation or RuleConditionRelationEnum.AND

class RuleGroupInfo:
    """
    规则组对象
    """

    def __init__(self, name=None, project=None, match_all=False, enable=True, default_rule:str=None, rules=[]) -> None:
        self.name = name
        self.project = project
        self.match_all = match_all        # false表示 规则组中的规则具有排他性，满足某一规则后不再匹配组内其他规则.true 规则组中的规则无排他性，满足某一规则后继续匹配组内其他规则
        self.enable = enable        # 是否启用
        self.default_rule = default_rule      # 默认的规则ID
        self.rules = rules      # 规则 RuleInfo

class RuleAction:

    def __init__(self, action:str=None, rule_action=None, type:RuleActionTypeEnum=RuleActionTypeEnum.DEFAULT, params:dict = None) -> None:
        self.action = action
        self.rule_action = rule_action
        self.type = type
        self.params = params

class RuleInfo:

    def __init__(self,name=None,description=None,then=[],enable=True,when=[]) -> None:
        self.name = name
        self.description = description
        self.then = then or []
        self.enable = enable
        self.when = when or []

    def add_when(self, conditionInfo:RuleConditionInfo):
        self.when.append(conditionInfo)

    def add_then(self, action:RuleAction):
        self.then.append(action)

class RuleResult:

    def __init__(self, rule_name, success=True, result=[]) -> None:
        self.rule_name = rule_name
        self.success = success
        self.result = result or []

    def add_result(self, action):
        self.result.append(action)

    def __str__(self):
        return "{'rule_name':"+self.rule_name+",'success':"+str(self.success)+",result:"+str(self.result)+"}"

    def __repr__(self):
        return "{'rule_name':"+self.rule_name+",'success':"+str(self.success)+",result:"+str(self.result)+"}"

class RuleFacts(Iterable):
    """
    条件事实.key表示了一个规则因子的名字. value表示的是事实的值
    """

    def __init__(self,key:str=None,value=None,facts:dict=None) -> None:
        self.__facts = facts or {}
        if key is not None:
            self.add_fact(key,value)

    def add_fact(self, key:str, value):
        self.__facts[key] = value

    def add_facts(self, rule_facts):
        self.__facts.update(rule_facts.get_facts())

    def get_facts(self)->dict:
        return self.__facts

    def get_fact(self,key:str):
        # 这里需要使用python表达式或至少是点号表达式.  因为别个可能是 a.b.c 这样写的

        from munch import Munch
        dot_dic = Munch.fromDict(self.__facts)

        keys = key.split(".")

        result = None
        for k in keys:
            try:
                result = getattr(dot_dic,k)
                dot_dic = result if not isinstance(result,dict) else Munch.fromDict(result)
            except:
                return None

        if result is not None and isinstance(result,Munch):
            return result.toDict()

        return result

    def __iter__(self) -> Iterator:
        return self.__facts.__iter__()
# endregion

# region 接口方法
class IRuleAction:
    """
    注意,如果是在数据库里面写的是 $java:xxxxxxxxxxx 这种实例化出来的是单例的
    """

    @abstractmethod
    def do_action(self, action:str, facts:RuleFacts, params:dict):
        """

        :param action:
        :param facts:
        :param params:
        :return:
        """
        pass

class IRuleConditionOperation:
    """
    操作类型的接口定义.这个里面就决定了如何比较数值
    """
    @abstractmethod
    def do_operation(self, factValue:dict, targetValue)->bool:
        """
        对两个值进行比较,如果满足条件就返回true.否则返回false
        :param factValue:
        :param targetValue:
        :return:
        """
        pass

class IRuleListener:

    @abstractmethod
    def before_evaluate(self, rule, facts)->bool:
        """
        在一个规则比较前触发
        :param rule:
        :param facts:
        :return: true表示继续往下走,false表示强制取消这个规则的比较
        """
        pass

    @abstractmethod
    def after_evaluate(self, rule, facts, evaluation_result:bool):
        """
        比较后触发
        :param rule:
        :param facts:
        :param evaluation_result: 表示比较的结果
        :return:
        """
        pass

    @abstractmethod
    def before_action(self, rule, facts)->bool:
        """
        执行action动作前触发
        :param rule:
        :param facts:
        :return: true表示继续往下走,false表示不执行这个规则的action
        """
        pass

    @abstractmethod
    def on_success(self, rule, facts, result):
        """
        在action动作成功后触发
        :param rule:
        :param facts:
        :param result:
        :return:
        """
        pass

    @abstractmethod
    def on_failure(self, rule, facts, exception:Exception):
        """
        在action动作失败后触发
        :param rule:
        :param facts:
        :param exception:
        :return:
        """
        pass

class IRuleValueProvider:
    """
    数据值的提供者.他负责在运行时给各种规则提供数据
    使用这个接口的目的在于用户可以定制
    """

    @abstractmethod
    def get_value(self, value:str):
        """
        获取数据
        :param value:
        :return:
        """
# endregion