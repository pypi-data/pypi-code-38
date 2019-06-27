REMOTE_YML_CONFIG = {}


def Value(value):
    """
    spring-cloud的配置获取注解
    :param value: ${zookeeper.timeout:10000}   冒号后面是默认值 可以没有
    :return:
    """

    def decorate(func):
        def wrapper(*arg, **kvargs):  # 包装的具体过程
            # 这里访问eureka去读取配置文件
            tup = _do_parse_expression(value)
            if tup[0] == "":
                return _convertStr2Other(tup[1])

            # arr[0]有值,说明需要到REMOTE_YML_CONFIG里面去找
            keys = tup[0].split(".")
            tmp = REMOTE_YML_CONFIG
            try:
                for key in keys:
                    tmp = tmp[key]
                return _convertStr2Other(tmp)
            except:
                # 默认值
                if tup[1] is None or tup[1] == ":" or tup[1] == "":
                    return None
                else:
                    return _convertStr2Other(tup[1][1:])

        return wrapper

    return decorate


def _do_parse_expression(value: str):
    """
    解析表达式
    :param value:
    :return: 数组, [0]是在remote上的key  [1]是默认值
    """
    if not value.startswith("${"):
        return tuple("", value)

    import re
    aaa = re.findall(r"\${((?:\w|\.|-)*)(:(\w|/)*)*}", value)
    return aaa[0]


def _convertStr2Other(value: str):
    """
    数据转换,把字符串的结果进行类型转换尝试,转换成为 int float boolean
    :param value:
    :return:
    """

    if value is None:
        return None

    if isinstance(value,bool) or isinstance(value,int) or isinstance(value,float):
        return value

    # 先尝试bool
    if "true" == value.lower():
        return True
    elif "false" == value.lower():
        return False

    try:
        # 尝试转换成为int
        return int(value)
    except ValueError:
        try:
            # 尝试转换成为float
            return float(value)
        except ValueError:
            # 都不是,那么就是字符串
            return value

def deep_search_and_merge(dict1, dict2):
    """
    深度遍历以及合并两个 dict 类型的数据. 要求相同key的值进行合并,如果值是dict,那么递归合并
    :param dict1:
    :param dict2:
    :return:
    """
    if dict2 is None or not isinstance(dict2,dict):
        return

    for key in dict2.keys():
        if key not in dict1.keys():
            dict1[key] = dict2[key]
        else:
            val1 = dict1[key]
            val2 = dict2[key]
            if  val1 is None or val2 is None:
                # 如果两个中有一个是None,那么就不用递归了,直接替换
                dict1[key] = val2
            elif isinstance(val1,dict) and isinstance(val2,dict):
                # 只有两个都是字典类型的情况下,再递归调用
                deep_search_and_merge(dict1[key], dict2[key])
            else:
                # 说明dict1或dict2中某一个相同的key的value是基础类型,那么就直接替换
                dict1[key] = val2

