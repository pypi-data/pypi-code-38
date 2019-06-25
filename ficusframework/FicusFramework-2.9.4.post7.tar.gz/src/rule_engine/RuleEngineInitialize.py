import json

import yaml
from munch import Munch

from api.exceptions import IllegalArgumentException
from rule_engine import *

# region 私有方法
from rule_engine import RuleEngineCustomScriptFactory


def __find_class_from_str(clazz:str):
    """
    从str获取类class
    :param clazz:
    :return:
    """
    ss = clazz.rsplit('.', 1)
    try:
        if len(ss) == 2:
            package = __import__(ss[0])
            return getattr(package, ss[1])
        else:
            package = __import__("")
            return getattr(package, clazz)
    except:
        # 有可能类加载不出来,因为是JAVA的,或者类路径写错了
        return None

def __parseStr(rule_groups:str,func):
    """
    从字符串转换成为rule_group_info对象
    :param rule_groups:
    :param func: 解析字符串到dict的函数
    :return:
    """
    dic = func(rule_groups)

    yml = Munch.fromDict(dic)

    results = []

    try:
        cof = yml.sobeyficus.ruleengine
        if len(cof.groups) == 0:
            return results
    except AttributeError:
        # 说明没有配置这个键,直接返回
        raise IllegalArgumentException("解析规则组内容失败,没有节点:sobeyficus.ruleengine ")

    # 开始构造模型
    groups = yml.sobeyficus.ruleengine.groups

    # 在配置文件中找到了相关的规则配置,那么就需要加工,并放入到规则引擎中
    for group in groups:
        rule_group_info = __build_rule_group(group)
        results.append(rule_group_info)

    return results

# endregion


# region 构建模型
def __build_rule_then(then):
    thens = []

    if then is not None and len(then) > 0:
        for th in then:
            t = RuleAction()
            thens.append(t)

            try:
                t.action = th.action
            except AttributeError:
                pass

            try:
                t.type = RuleActionTypeEnum[th.type]
            except AttributeError:
                pass

            try:
                t.params = th.params
            except AttributeError:
                pass

    return thens


def __build_rule_when(when):
    whens = []

    if when is not None and len(when) > 0:
        for wh in when:
            w = RuleConditionInfo()
            whens.append(w)

            try:
                w.source = wh.source
            except AttributeError:
                pass

            try:
                w.target = wh.target
            except AttributeError:
                pass

            try:
                w.operation = RuleConditionOperationEnum[wh.operation]
            except AttributeError:
                pass

            try:
                w.enable = wh.enable
            except AttributeError:
                pass

            try:
                w.relation = RuleConditionRelationEnum[wh.relation]
            except AttributeError:
                pass

            try:
                w.subs = __build_rule_when(wh.subs)
            except AttributeError:
                pass

    return whens


def __build_rule_info(rules):
    """
    构建ruleInfo对象
    :param rules:
    :return:
    """
    rs = []

    if rules is not None and len(rules)>0:
        for rule in rules:
            r = RuleInfo()
            rs.append(r)

            try:
                r.name = rule.name
            except AttributeError:
                pass

            try:
                r.description = rule.description
            except AttributeError:
                pass

            try:
                r.enable = rule.enable
            except AttributeError:
                pass

            try:
                r.then = __build_rule_then(rule.then)
            except AttributeError:
                pass

            try:
                r.when = __build_rule_when(rule.when)
            except AttributeError:
                pass

    return rs

def __build_rule_group(group:Munch):
    """
    构建 rulegroup对象
    :param group:
    :return:
    """
    rule_group_info = RuleGroupInfo()
    try:
        rule_group_info.name = group.name
    except AttributeError:
        pass

    try:
        rule_group_info.project = group.project
    except AttributeError:
        pass

    try:
        rule_group_info.match_all = group.matchAll
    except AttributeError:
        pass

    try:
        rule_group_info.enable = group.enable
    except AttributeError:
        pass

    try:
        rule_group_info.default_rule = group.defaultRule
    except AttributeError:
        pass

    try:
        rule_group_info.rules = __build_rule_info(group.rules)
    except AttributeError:
        pass

    return rule_group_info
# endregion


# region 规则校验
def __inner_check_rule_group(rule_group_info):
    """
    校验规则组
    :param rule_group_info:
    :return:
    """
    if rule_group_info.name is None or rule_group_info.name=="":
        raise IllegalArgumentException("校验规则组失败:名称为空")

    if rule_group_info.project is None or rule_group_info.project=="":
        raise IllegalArgumentException("校验规则组失败:项目为空")

    if rule_group_info.rules is None or len(rule_group_info.rules)==0:
        raise IllegalArgumentException("校验规则组失败:规则为空")

    if rule_group_info.default_rule is not None:
        for rule in rule_group_info.rules:
            if rule.name == rule_group_info.default_rule:
                return
        raise IllegalArgumentException(f"校验规则组失败:默认规则{rule_group_info.default_rule} 不存在")


def __inner_check_rule(rule:RuleInfo):
    """
    校验规则
    :param rule:
    :return:
    """
    if rule.name is None or rule.name=="":
        raise IllegalArgumentException("校验规则失败:名称为空")

    if rule.when is None or len(rule.when)==0:
        raise IllegalArgumentException(f"校验规则{rule.name}失败:规则条件为空")


def __inner_check_rule_condition(when:RuleConditionInfo):
    """
    校验条件
    :param when:
    :return:
    """
    if len(when.subs)==0 and when.operation is None:
        raise IllegalArgumentException(f"校验规则条件失败:条件比对方式为空")

    if len(when.subs)>0 and when.operation is not None:
        raise IllegalArgumentException(f"校验规则条件失败:有子条件,条件比对方式必须为空")

    if when.operation is not None:
        if not (when.operation in [RuleConditionOperationEnum.MVEL,RuleConditionOperationEnum.AVIATOR,RuleConditionOperationEnum.BEAN,RuleConditionOperationEnum.CLASS,RuleConditionOperationEnum.PY_BEAN,RuleConditionOperationEnum.PY_CLASS,RuleConditionOperationEnum.PY_EXP] or (when.source is not None and when.source !="")):
            raise IllegalArgumentException(f"校验规则条件失败:规则条件为空或不合法")

    if when.operation is not None:
        # 校验每一个方式的合法性
        if when.operation == RuleConditionOperationEnum.PY_BEAN:
            # 校验源码加载
            RuleEngineCustomScriptFactory.load_instance(when.target,"IRuleConditionOperation")
        elif when.operation == RuleConditionOperationEnum.PY_CLASS:
            # 校验获取类路径
            clazz = __find_class_from_str(when.target)
            if clazz is None or not issubclass(clazz,IRuleConditionOperation):
                raise IllegalArgumentException(f"校验规则条件失败:规则不合法")
        # 其他类型的可以不校验

    if len(when.subs)>0:
        for sub in when.subs:
            # 递归校验子条件
            __inner_check_rule_condition(sub)

def __inner_check_rule_action(rule_action:RuleAction):
    """
    校验结果
    :param then:
    :return:
    """
    if rule_action.type is None:
        raise IllegalArgumentException("校验规则条件失败:执行类型为空")

    if rule_action.type is not None:
        if not ((rule_action.type in [RuleActionTypeEnum.MVEL,RuleActionTypeEnum.CLASS,RuleActionTypeEnum.BEAN,RuleActionTypeEnum.AVIATOR,RuleActionTypeEnum.PY_CLASS,RuleActionTypeEnum.PY_BEAN,RuleActionTypeEnum.PY_EXP] and (rule_action.action is not None and rule_action.action!="")) or rule_action.type==RuleActionTypeEnum.DEFAULT):
            raise IllegalArgumentException("校验规则条件失败:执行动作为空")

    if rule_action.type is not None:
        # 校验每一个方式的合法性
        if rule_action.type == RuleActionTypeEnum.PY_BEAN:
            # 校验源码加载
            RuleEngineCustomScriptFactory.load_instance(rule_action.action,"IRuleAction")
        elif rule_action.type == RuleActionTypeEnum.PY_CLASS:
            # 校验获取类路径
            clazz = __find_class_from_str(rule_action.action)
            if clazz is None or not issubclass(clazz, IRuleAction):
                raise IllegalArgumentException(f"校验规则条件失败:规则不合法")
        # 其他类型的可以不校验

def __check_rule_group(rule_group_info:RuleGroupInfo):
    """
    校验rule_group的合法性
    :param rule_group_info:
    :return:
    """
    # 校验规则组
    __inner_check_rule_group(rule_group_info)

    for rule in rule_group_info.rules:
        __inner_check_rule(rule)

        for when in rule.when:
            __inner_check_rule_condition(when)

        for then in rule.then:
            __inner_check_rule_action(then)
# endregion


# region 规则补全
def __inner_rebuild_rule_condition(when:RuleConditionInfo):
    if when.operation == None:
        when.operation = RuleConditionOperationEnum.DO_NOTHING

    # 主要是处理IRuleConditionOperation 和 targetProvider
    when.rule_operation = when.operation.condition_operation()

    if when.operation == RuleConditionOperationEnum.PY_BEAN or when.operation == RuleConditionOperationEnum.PY_CLASS:
        if when.rule_operation is not None:
            raise IllegalArgumentException("operation已经指定,不能重复自定义")

        if when.operation == RuleConditionOperationEnum.PY_BEAN:
            when.rule_operation = RuleEngineCustomScriptFactory.load_instance(when.target,"IRuleConditionOperation")
        elif when.operation == RuleConditionOperationEnum.PY_CLASS:
            clazz = __find_class_from_str(when.target)
            when.rule_operation = clazz()

    # 递归构造子条件
    if len(when.subs)>0:
        for sub in when.subs:
            __inner_rebuild_rule_condition(sub)

def __inner_rebuild_rule_action(then:RuleAction):
    then.rule_action = then.type.actions()

    if then.type == RuleActionTypeEnum.PY_BEAN or then.type == RuleActionTypeEnum.PY_CLASS:
        if then.rule_action is not None:
            raise IllegalArgumentException("action已经指定,不能重复自定义")

        if then.type == RuleActionTypeEnum.PY_BEAN:
            then.rule_action = RuleEngineCustomScriptFactory.load_instance(then.action,"IRuleAction")
        elif then.type == RuleActionTypeEnum.PY_CLASS:
            clazz = __find_class_from_str(then.action)
            then.rule_action = clazz()


def __rebuild_rule_group(rule_group_info:RuleGroupInfo):

    for rule in rule_group_info.rules:

        for when in rule.when:
            __inner_rebuild_rule_condition(when)

        for then in rule.then:
            __inner_rebuild_rule_action(then)
# endregion


def __initialize(group)->RuleGroupInfo:

    rule_group_info = __build_rule_group(group)

    __check_rule_group(rule_group_info)

    __rebuild_rule_group(rule_group_info)

    return rule_group_info


def initialize_from_obj(rule_group_info:RuleGroupInfo)->RuleGroupInfo:
    """
    从构造器构造的RuleGroupInfo实例,初始化规则引擎
    :param rule_group_info:
    :return:
    """
    if rule_group_info is None:
        raise IllegalArgumentException("初始化规则引擎失败,传入的规则组实例为空")

    # 检测规则是否合法
    __check_rule_group(rule_group_info)

    # 构造info中的必填项
    __rebuild_rule_group(rule_group_info)

    from rule_engine import RuleEngine
    RuleEngine.register_rule_group(rule_group_info)

    return rule_group_info

def initialize_from_str(rule_groups:str):
    """
    从规则字符串中,初始化规则引擎
    :param rule_groups:  可以是 json 也可以是 yaml
    :return:
    """
    if rule_groups is None or rule_groups.strip()=="":
        raise IllegalArgumentException("初始化规则引擎失败,传入的规则组字符串为空")

    rule_groups = rule_groups.strip()

    if rule_groups.startswith("{") and rule_groups.endswith("}"):
        # 说明可能是json格式的
        result = __parseStr(rule_groups,lambda x:json.loads(x))
    else:
        # 说明是yaml格式的
        result = __parseStr(rule_groups, lambda x: yaml.load(x))

    if result is not None:
        for ruleGroupInfo in result:
            initialize_from_obj(ruleGroupInfo)

    return result


def initialize_from_remote():
    """
    从yaml配置中,初始化规则引擎
    :return:
    """
    from config import annotation

    # 获取远程配置中的配置项.判断是否有规则引擎相关的配置
    yml = Munch.fromDict(annotation.REMOTE_YML_CONFIG)

    try:
        cof = yml.sobeyficus.ruleengine
        if len(cof.groups) == 0 :
            return
    except AttributeError:
        # 说明没有配置这个键,直接返回
        return

    # 开始构造模型
    groups = yml.sobeyficus.ruleengine.groups

    # 在配置文件中找到了相关的规则配置,那么就需要加工,并放入到规则引擎中
    from rule_engine import RuleEngine
    for group in groups:
        rule_group_info = __initialize(group)
        RuleEngine.register_rule_group(rule_group_info)

