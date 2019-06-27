import logging
from typing import Any

from rule_engine import RuleFacts, RuleConditionRelationEnum
from rule_engine.core.SimpleValueProvider import SimpleValueProvider

log = logging.getLogger('Ficus')

def match(conditions:list,facts:RuleFacts) -> bool:
    """
    条件的比对
    :param conditions:
    :param facts:
    :return:
    """
    global factClass
    matchResult = True

    # 遍历每一个规则因子
    for condition in conditions:
        if not condition.enable:
            log.info(f"规则因子:{condition.source}未启用,直接跳过")
            continue

        relation = condition.relation

        if condition.subs is not None and len(condition.subs)>0:
            # 有子条件的,做递归
            matchResult = relation.relation(matchResult,match(condition.subs,facts))
            if relation == RuleConditionRelationEnum.AND and not matchResult:
                # 如果关系是AND,并且结果是失败,那就直接返回了
                return False
        else:
            # 无子条件的
            # 2.找到规则因子的名字.这个名字就是事实的名字
            # 3.找到该规则因子的事实值
            factValue = facts.get_facts() if condition.source is None or condition.source.strip()=="" else facts.get_fact(condition.source)
            target = None
            if condition.target_provider is None:
                # 如果没有自定义targetProvider,那么就是用默认的
                # 这里需要猜测target的类型
                classes = condition.operation.allowed_target_type()

                if len(classes)==0:
                    target = SimpleValueProvider().get_value(condition.target)

                # 说明是有类型的
                if factValue is None:
                    # 没有入参,或者入参 是空,没法猜
                    target = SimpleValueProvider().get_value(condition.target)
                else:
                    # 如果输入是数组或集合(list,set,dict)
                    if hasattr(factValue,"__iter__") and not isinstance(factValue,dict):
                        if len(factValue)==0:
                            # 没法取到入参的类型
                            target = SimpleValueProvider().get_value(condition.target)
                        else:
                            factClass = type(next(iter(factValue)))
                    else:
                        factClass = type(factValue)

                    if target is None:
                        find = False
                        for a_class in classes:
                            if issubclass(factClass,a_class):
                                target = SimpleValueProvider(a_class).get_value(condition.target)
                                find=True
                                break

                        if not find:
                            # 没有找到,也就是说类型可能不匹配操作
                            target = SimpleValueProvider().get_value(condition.target)

            else:
                target = condition.target_provider.get_value(condition.target)


            # 开始做匹配
            matchResult = relation.relation(matchResult,condition.rule_operation.do_operation(factValue,target))

            if relation == RuleConditionRelationEnum.AND and not matchResult:
                # 一个条件因子匹配不成功, 就返回false
                return False

    return True