import logging

from api.exceptions import IllegalArgumentException, ServiceInnerException
from rule_engine import RuleFacts, RuleGroupInfo, RuleResult
from rule_engine.core import IRuleGroupSession
from rule_engine.core.DefaultAgenda import DefaultAgenda

log = logging.getLogger('Ficus')


class SimpleRuleGroupSession(IRuleGroupSession):

    def __init__(self, rule_group_info:RuleGroupInfo) -> None:
        self.__added_fact = False
        self.__rule_listeners = []
        self.__rule_facts = None
        self.__agenda = DefaultAgenda(rule_group_info,self.__rule_listeners)

    def add_facts(self, rule_facts: RuleFacts):
        if rule_facts is None:
            self.__rule_facts = RuleFacts()

        if self.__rule_facts is None:
            self.__rule_facts = rule_facts
        else:
            self.__rule_facts.add_facts(rule_facts)

        self.__added_fact = True

    def add_fact(self, key: str, value):
        if self.__rule_facts is None:
            self.__rule_facts = RuleFacts()

        self.__rule_facts.add_fact(key,value)

        self.__added_fact = True


    def add_rule_listener(self, rule_listener):
        self.__rule_listeners.append(rule_listener)

    def execute(self):
        if not self.__added_fact:
            raise IllegalArgumentException("未添加规则事实,无法进行规则匹配")

        log.info(f"开始一次规则的匹配,{self.__agenda}")

        log.debug(f"规则事实:{self.__rule_facts}")

        # 把事实传入.然后匹配出符合条件的规则.
        infos = self.__agenda.get_matched_rules(self.__rule_facts)

        if infos is None or len(infos)==0:
            log.info(f"没有匹配到规则,{self.__agenda}")
            return None

        results = []

        log.info(f"成功匹配到规则,{self.__agenda}")

        log.debug(f"匹配到的规则:{infos}")

        for info in infos:
            # 执行结果
            try:
                if not self.__triggerListenersBeforeExecute(info,self.__rule_facts):
                    log.info(f"规则 {info.name} 跳过执行action阶段")
                    continue

                rule_result = RuleResult(info.name)
                results.append(rule_result)

                then = info.then
                if then is not None and len(then)>0:
                    for rule_action in then:
                        action = rule_action.rule_action.do_action(rule_action.action,self.__rule_facts,rule_action.params)
                        rule_result.add_result(action)
                self.__triggerListenersOnSuccess(info,self.__rule_facts,rule_result)
            except Exception as e:
                log.error(f"执行匹配的规则 {info.name} 失败,{str(e)}")
                self.__triggerListenersOnFailure(info,e,self.__rule_facts)
                raise ServiceInnerException(f"执行匹配的规则 {info.name} 失败,{str(e)}")

        return results

    # region 消息相关
    def __triggerListenersBeforeExecute(self, rule, rule_facts):
        for rule_listener in  self.__rule_listeners:
            if not rule_listener.before_action(rule,rule_facts):
                return False

        return True

    def __triggerListenersOnSuccess(self, rule, rule_facts, rule_result):
        for rule_listener in self.__rule_listeners:
            rule_listener.on_success(rule,rule_facts,rule_result)

    def __triggerListenersOnFailure(self, rule, e, rule_facts):
        for rule_listener in self.__rule_listeners:
            rule_listener.on_failure(rule, rule_facts, e)
    # endregion