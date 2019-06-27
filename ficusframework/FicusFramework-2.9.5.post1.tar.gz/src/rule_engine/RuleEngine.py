# 规则引擎
from readerwriterlock import rwlock

from rule_engine import RuleGroupInfo

# 缓存, key是 project_name
from rule_engine.core import IRuleGroupSession
from rule_engine.core.SimpleRuleGroupSession import SimpleRuleGroupSession

__cache = {}

__read_write_lock = rwlock.RWLockRead()

def __groupKey(name,project):
    return f"{project}_{name}"

def register_rule_group(rule_group_info:RuleGroupInfo):
    """
    增加一个规则组,如果原来的存在,就替换
    :arg rule_group_info 规则
    :return:
    """
    key = __groupKey(rule_group_info.name,rule_group_info.project)

    with __read_write_lock.gen_wlock():
        __cache[key] = rule_group_info

def unregister_rule_group(project:str, name:str):
    """
    删除掉一个规则组
    :param project:
    :param name:
    :return:
    """
    key = __groupKey(name,project)
    with __read_write_lock.gen_wlock():
        del __cache[key]

def clear_rule_group(project:str):
    """
    清除一个规则组
    :param project:
    :return:
    """
    with __read_write_lock.gen_wlock():
        for k in list(__cache.keys()):
            if k.startswith(f"{project}_"):
                del __cache[k]


def list_rule_group_names(project:str):
    """
    列出规则组的名字
    :param project:
    :return:
    """
    result = []
    with __read_write_lock.gen_rlock():
        for k in list(__cache.keys()):
            if k.startswith(f"{project}_"):
                result.append(k.replace(f"{project}_",""))

    return result

def create_new_session(group_name:str, project:str)->IRuleGroupSession:
    """
    执行一个规则
    :param group_name:
    :param project:
    :return:
    """
    key = __groupKey(group_name, project)
    with __read_write_lock.gen_rlock():
        if key not in __cache:
            from api.exceptions import IllegalArgumentException
            raise IllegalArgumentException(f"没有找到{project}:{group_name}的规则组")

        rule_group_info = __cache[key]

    return SimpleRuleGroupSession(rule_group_info)