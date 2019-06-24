from api.exceptions import IllegalArgumentException
from rule_engine import IRuleAction, IRuleConditionOperation

__RULE_ENGINE_CUSTOM_CACHE__ = {}


def _is_subclass(v,clazz)->bool:
    cc = None
    if clazz=="IRuleAction":
        cc = IRuleAction
    elif clazz=="IRuleConditionOperation":
        cc = IRuleConditionOperation

    if cc is None:
        return False
    return issubclass(v,cc)

def _find_class(context:dict,clazz):
    script_class = None
    for k, v in context.items():
        if k != clazz and isinstance(v, type) and _is_subclass(v,clazz):
            script_class = v
    return script_class


def load_instance(code_source: str, clazz,name: str=None):
    if name is not None and  name in __RULE_ENGINE_CUSTOM_CACHE__:
        # 说明在缓存中,直接返回
        return __RULE_ENGINE_CUSTOM_CACHE__[name]
    # 说明还没有实例化,
    if code_source is None or len(code_source) == 0:
        raise IllegalArgumentException(f"加载{name or '代码'} 失败,源码为空")
    else:
        # 说明是有东西的,开始尝试加载
        context = {}
        exec(code_source, context)  # None

        # 找到类定义
        script_class = _find_class(context, clazz)

        if  script_class is None:
            # 说明没有找到,报错
            raise IllegalArgumentException(f"加载{name or code_source} 源码失败,没有继承自IRuleAction/IRuleConditionOperation")

        # 放入缓存
        if name is not None:
            __RULE_ENGINE_CUSTOM_CACHE__[name] = script_class()
            # 返回结果
            return __RULE_ENGINE_CUSTOM_CACHE__[name]
        else:
            return script_class()

