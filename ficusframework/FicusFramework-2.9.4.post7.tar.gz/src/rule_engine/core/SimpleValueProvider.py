from api.exceptions import IllegalArgumentException, ServiceInnerException
from rule_engine import IRuleValueProvider
import re


class SimpleValueProvider(IRuleValueProvider):

    def __init__(self, data_type=None) -> None:
        self.__data_type = data_type

    def get_value(self, value):
        if value is None:
            return None
        elif self.__data_type is None:
            # 未知的类型,而且值又不为空,那么传进去的是什么 就是什么
            return value
        elif isinstance(value, str) and re.fullmatch(r"^\[([^\[^\].]+) TO ([^\[^\].]+)\]$", value):
            # 是范围的   '[10 TO 20]'
            # 表示是 如果是匹配的[XX TO XX]的格式,采用特殊方式解析
            aaa = re.findall(r"^\[([^\[^\].]+) TO ([^\[^\].]+)\]$", value)
            start_str = aaa[0][0]
            end_str = aaa[0][1]

            return [self.__convertValue(start_str,self.__data_type),self.__convertValue(end_str,self.__data_type)]
        elif isinstance(value, list) and len(value) == 1 and re.fullmatch(r"^([^\[^\].]+) TO ([^\[^\].]+)$", value[0]):
            # 同样是范围   list('10 TO 20')
            aaa = re.findall(r"^([^\[^\].]+) TO ([^\[^\].]+)$", value[0])
            start_str = aaa[0][0]
            end_str = aaa[0][1]

            return [self.__convertValue(start_str, self.__data_type), self.__convertValue(end_str, self.__data_type)]
        elif isinstance(value,list):
            # 是数组
            res = []
            for v in value:
                if isinstance(v,str):
                    res.append(self.__convertValue(v,self.__data_type))
                else:
                    res.append(v)
            return res
        elif isinstance(value,str) and re.fullmatch(r"^\[.+\]$", value):
            # 是数组字符串
            import json
            j = json.loads(value)
            res = []
            for v in j:
                if isinstance(v, str):
                    res.append(self.__convertValue(v, self.__data_type))
                else:
                    res.append(v)
            return res
        else:
            # 简单的值,直接转换
            return self.__convertValue(value,self.__data_type)

    def __convertValue(self,value,typeClass):
        if typeClass is None:
            raise IllegalArgumentException("类型转换错误,没有转换的目标类型")
        elif typeClass == object:
            # 这种也是没法转换的
            return value

        # 这有可能报转换异常
        try:
            import time
            import datetime
            from enum import Enum
            if typeClass in [time.struct_time,datetime.datetime]:
                # 日期特殊处理
                if typeClass == time.struct_time:
                    return time.strptime(value, "%Y-%m-%d")
                else:
                    return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            elif typeClass == Enum:
                return typeClass[value]
            elif typeClass == dict:
                import json
                return json.loads(value)
            else:
                return typeClass(value)
        except (TypeError,ValueError) as e:
            raise ServiceInnerException(f"字段值{value}失败.期望是:{typeClass}")