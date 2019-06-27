from api.exceptions import UnSupportException
from rule_engine import IRuleAction


class DefaultAction(IRuleAction):
    """
    默认的action就是把 action中的东西返回出去
    """

    def do_action(self, action, facts, params: dict):
        if params is None:
            params = {}

        params["_action"] = action

        return params

class UnSupportAction(IRuleAction):
    def do_action(self, action, facts, params: dict):
        raise UnSupportException("此执行动作Python 并不支持")

class PyExpAction(IRuleAction):
    """
    python表达式的方式,类似于JAVA中的MVEL
    """
    def do_action(self, action, facts, params: dict):
        from munch import Munch

        context = facts.get_facts() or {}
        if params is not None:
            context.update(params)
        context = Munch.fromDict(context)

        params_ = Munch.fromDict(context)

        exec(f"def __b(params):\n{self.__reindent(action,1)}\n", context)
        result2 = context["__b"]
        return result2(params_)

    def __reindent(self,s, numSpaces):
        """
        多行代码的统一缩进处理
        :param s:
        :param numSpaces:
        :return:
        """
        leading_space = numSpaces * ' '
        lines = [leading_space + line for line in s.splitlines()]
        return '\n'.join(lines)