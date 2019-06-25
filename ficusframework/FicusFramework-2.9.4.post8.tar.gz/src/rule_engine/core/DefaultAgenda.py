import logging

from rule_engine import RuleFacts, RuleGroupInfo
from rule_engine.core import IAgenda, PattenMatcher

log = logging.getLogger('Ficus')

class DefaultAgenda(IAgenda):


    def __init__(self, rule_group_info:RuleGroupInfo, rule_listeners:list) -> None:
        self.__rule_group_info = rule_group_info
        self.__rule_listeners = rule_listeners

    def get_matched_rules(self, rule_facts: RuleFacts) -> list:

        if not self.__rule_group_info.enable:
            log.info(f"规则组:{self.__rule_group_info.name}未启用,直接返回")
            return []

        # 1.取出所有的规则.开始遍历
        rules = self.__rule_group_info.rules

        # 是否匹配全部.如果是,就需要把每一个都遍历了.如果不是,只匹配到第一个符合条件的就返回
        is_match_all = self.__rule_group_info.match_all

        results = []

        for rule in rules:
            if not self.__triggerListenersBeforeEvaluate(rule, rule_facts):
                log.info(f"规则:{rule.name}在执行匹配前被忽略")
                continue

            if PattenMatcher.match(rule.when, rule_facts):
                # 如果匹配成功.就添加到结果中去
                self.__triggerListenersAfterEvaluate(rule, rule_facts, True)
                results.append(rule)
                if  not is_match_all:
                    # 匹配中一个就退出
                    break
            else:
                # 匹配失败
                self.__triggerListenersAfterEvaluate(rule, rule_facts, False)

        if len(results)==0:
            # 如果默认的不为空,并且是可使用的.就使用默认的
            if self.__rule_group_info.default_rule is not None and self.__rule_group_info.default_rule!="":
                for rule in rules:
                    if rule.name == self.__rule_group_info.default_rule:
                        results.append(rule)
                        log.info(f"规则组:{self.__rule_group_info.name}虽然没有匹配到规则,但是配置了默认规则{rule.name},命中默认规则")
                        break

        # 如果添加了默认的处理器还是空.就返回空
        return results

    # region 消息相关
    def __triggerListenersBeforeEvaluate(self, rule, facts):
        if self.__rule_listeners is not None:
            for listener in self.__rule_listeners:
                if not listener.before_evaluate(rule,facts):
                    return False
        return True

    def __triggerListenersAfterEvaluate(self, rule, facts, evaluation_result):
        if self.__rule_listeners is not None:
            for listener in self.__rule_listeners:
                listener.after_evaluate(rule, facts, evaluation_result)
    # endregion

