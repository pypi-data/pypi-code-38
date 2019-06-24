from api.exceptions import UnSupportException
from rule_engine import IRuleConditionOperation

def compare_equal(lhs,rhs):
    if lhs is rhs:
        return True

    if lhs is None or rhs is None:
        return False

    return lhs == rhs
    # python 直接用==就可以比较 dict list obj 这些
    # if not isinstance(lhs, list):
    #     return lhs == rhs
    # else:
    #     if len(lhs) != len(rhs):
    #         return False
    #     for index, content in enumerate(lhs):
    #         if not  __compare_equal(content,rhs[index]):
    #             return False
    #     return True

class DoNothingOperation(IRuleConditionOperation):
    """
    没用的,永远返回true
    """
    def do_operation(self, factValue, targetValue) -> bool:
        return True

class UnSupportOperation(IRuleConditionOperation):

    def do_operation(self, factValue, targetValue) -> bool:
        raise UnSupportException("此条件动作Python 并不支持")

class DefaultEqualOperation(IRuleConditionOperation):
    def do_operation(self, factValue, targetValue) -> bool:
        # 相等判断
        return compare_equal(factValue,targetValue)

class DefaultNotEqualOperation(IRuleConditionOperation):
    def do_operation(self, factValue, targetValue) -> bool:
        # 相等判断
        return not compare_equal(factValue,targetValue)

class DefaultGTEOperation(IRuleConditionOperation):
    def do_operation(self, factValue, targetValue) -> bool:
        if factValue is None or targetValue is None:
            return False

        try:
            return factValue >= targetValue
        except TypeError:
            raise UnSupportException("不支持 GTE操作")

class DefaultGTOperation(IRuleConditionOperation):
    def do_operation(self, factValue, targetValue) -> bool:
        if factValue is None or targetValue is None:
            return False

        try:
            return factValue > targetValue
        except TypeError:
            raise UnSupportException("不支持 GT操作")

class DefaultLTEOperation(IRuleConditionOperation):
    def do_operation(self, factValue, targetValue) -> bool:
        if factValue is None or targetValue is None:
            return False

        try:
            return factValue <= targetValue
        except TypeError:
            raise UnSupportException("不支持 LTE操作")

class DefaultLTOperation(IRuleConditionOperation):
    def do_operation(self, factValue, targetValue) -> bool:
        if factValue is None or targetValue is None:
            return False

        try:
            return factValue < targetValue
        except TypeError:
            raise UnSupportException("不支持 LT操作")

class DefaultINOperation(IRuleConditionOperation):
    def do_operation(self, factValue, targetValue) -> bool:
        if targetValue is None:
            return False

        if not isinstance(targetValue, list):
            raise UnSupportException("比对目标值并不是一个List,无法对比")

        try:
            return factValue in targetValue
        except TypeError:
            raise UnSupportException("比对目标值并不是一个List,无法对比")

class DefaultRangeOperation(IRuleConditionOperation):
    """
    前开后闭
    """
    def do_operation(self, factValue, targetValue) -> bool:
        if targetValue is None:
            return False

        if not isinstance(targetValue, list) or len(targetValue)!=2:
            raise UnSupportException("比对目标值必须是一个二元数组[start,end]")

        try:
            return factValue >= targetValue[0] and factValue < targetValue[1]
        except TypeError:
            raise UnSupportException("不支持 LT操作")

class PyExpOperation(IRuleConditionOperation):
    """
    python表达式的方式,类似于java中的mvel
    """
    def do_operation(self, factValue, targetValue) -> bool:

        context = factValue or {}

        from munch import Munch
        context = Munch.fromDict(context)
        params = Munch.fromDict(context)

        exec(f"def __b(params):\n{self.__reindent(targetValue,1)}\n", context)
        result2 = context["__b"]
        ar = result2(params)

        return ar if ar is not None else False

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