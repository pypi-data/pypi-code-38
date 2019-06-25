from enum import Enum, unique


@unique
class OperationEnum(Enum):
    INSERT = 0
    UPDATE = 1
    UPSERT = 2
    CLEAN = 3
    DELETE = 4


class OutputWrapper:
    """
    数据操作包装类
    """
    __index = 0

    __content = None

    __operation: OperationEnum = None

    def __init__(self, content, operation, index):
        self.__content = content
        self.__operation = operation
        self.__index = index

    def content(self):
        return self.__content

    def operation(self):
        return self.__operation

    def index(self):
        return self.__index


def INSERT(content, index=0):
    """
    插入操作一个内容
    :param content: 被操作的内容
    :param index: 操作层级,一般不管
    :return: OutputWrapper对象
    """
    return OutputWrapper(content, OperationEnum.INSERT, index)


def UPDATE(content, index=0):
    """
    更新操作一个内容
    :param content: 被操作的内容
    :param index: 操作层级,一般不管
    :return: OutputWrapper对象
    """
    return OutputWrapper(content, OperationEnum.UPDATE, index)


def UPSERT(content, index=0):
    """
    saveOrUpdate操作一个内容
    :param content: 被操作的内容
    :param index: 操作层级,一般不管
    :return: OutputWrapper对象
    """
    return OutputWrapper(content, OperationEnum.UPSERT, index)


def DELETE(query, index=0):
    """
    删除操作一个内容
    :param query: 被删除的查询条件
    :param index: 操作层级,一般不管
    :return: OutputWrapper对象
    """
    return OutputWrapper(query, OperationEnum.DELETE, index)


def CLEAN(index=0):
    """
    清除操作
    :param index: 操作层级,一般不管
    :return: OutputWrapper对象
    """
    return OutputWrapper(None, OperationEnum.CLEAN, index)
