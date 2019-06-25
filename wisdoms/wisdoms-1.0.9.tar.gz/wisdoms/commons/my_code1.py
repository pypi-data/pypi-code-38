# Created by Q-ays.
# whosqays@gmail.com


"""
    状态码

    Notice::
        大于0，顺利执行
        小于0，执行出错
        大于100，执行成功，出现警告

    Example::
        from wisdoms.commons import revert, codes

        def foo():
            # return revert(1)
            return revert(codes.SUCCESS)


"""

from enum import Enum, unique


@unique
class Code(Enum):
    ERROR = -1
    MS_ERROR = -2
    DATABASE_ERROR = -3
    NOT_AUTHORIZED = -4
    DATA_FORMAT_ERROR = -5
    TIMEOUT = -6
    UNKNOWN_ERROR = -7
    THIRD_PARTY_ERROR = -8
    PARAM_ERROR = -9
    GET_WAY_ERROR = -10
    CONNECTION_TIMEOUT = -11
    ES_SERVER_ERROR = -12

    SUCCESS = 1

    WARNING = 100


@unique
class CodeDesc(Enum):
    ERROR = '错误'
    MS_ERROR = '微服务错误'
    DATABASE_ERROR = '数据库错误'
    NOT_AUTHORIZED = '未授权，拒绝访问'
    DATA_FORMAT_ERROR = '数据格式错误'
    TIMEOUT = '超时'
    UNKNOWN_ERROR = '未知错误'
    THIRD_PARTY_ERROR = '第三方服务错误'
    PARAM_ERROR = '参数错误'
    GET_WAY_ERROR = 'api 网关服务器错误'
    ES_SERVER_ERROR = 'elastic search 服务器错误'
    CONNECTION_TIMEOUT = '连接超时'

    SUCCESS = '成功'

    WARNING = '警告'
