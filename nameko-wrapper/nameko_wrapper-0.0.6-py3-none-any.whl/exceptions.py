"""
Service Exception

Service Exception 由rpc调用处理
"""


class ServiceBaseException(Exception):
    """Service Exception Base Class"""
    pass


class ServiceErrorException(ServiceBaseException):
    """Service Error Exception （RPC响应不进行捕捉异常，用于提示服务报错）"""
    pass


class IllegalResponseException(ServiceErrorException):
    """Illegal Response Exception"""
    msg = '非法的响应'
    code = 500


class ServiceException(ServiceBaseException):
    """Service Exception （RPC响应捕捉可处理异常，常用于服务的退出控制）"""
    msg = '请求异常'
    code = 400

    def __init__(self, msg=None, code=None, *args, obj=None, **kwargs):
        self.set_attr_value('msg', msg)
        self.set_attr_value('code', code)

    def set_attr_value(self, attr_name, value):
        """
        根据不同的场景设置期望值

        当类初始化设置值时，类初始化输入值优先级最高，其次期望类自身属性，最后为默认值
        Args:
            attr_name: 属性名
            value: 属性值

        Returns:

        """
        if value:
            setattr(self, attr_name, value)


class DBException(ServiceException):
    msg = '数据库异常'
    code = 500


class NotFound(ServiceException):
    """Not Found"""
    msg = 'not found'
    code = 404


class ObjectAlreadyExist(ServiceException):
    """Object Already Exist"""
    msg = '对象已存在'
    code = 400
    

class ObjectDoesNotExist(ServiceException):
    """Object Doesn't Exist"""
    msg = '对象不存在'
    code = 400
    

#  ************************ Permission Exception ************************
class PermissionBase(ServiceException):
    """权限异常基类"""
    msg = '权限不足'
    code = 400


class PermissionDenied(PermissionBase):
    """Permission Denied"""
    msg = '权限不足'
    code = 400


class InconsistentUser(PermissionBase):
    """不一致的用户身份"""
    msg = '用户身份不一致'
    code = 400


class InformationLoss(ServiceException):
    """服务端信息缺失"""
    msg = '服务端信息不完整'
    code = 500


class IncorrectContent(ServiceException):
    """服务端内容异常"""
    msg = '服务端内容保存不正确'
    code = 500


class ParameterException(ServiceException):
    """参数异常"""
    msg = '参数异常'
    code = 400


