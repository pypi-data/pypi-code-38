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
VM_ABNORMAL_STATE = -13

SUCCESS = 1

WARNING = 100

code2name = {

    ERROR: 'ERROR',
    MS_ERROR: 'MS_ERROR',
    DATABASE_ERROR: 'DATABASE_ERROR',
    NOT_AUTHORIZED: 'NOT_AUTHORIZED',
    DATA_FORMAT_ERROR: 'DATA_FORMAT_ERROR',
    TIMEOUT: 'TIMEOUT',
    UNKNOWN_ERROR: 'UNKNOWN_ERROR',
    THIRD_PARTY_ERROR: 'THIRD_PARTY_ERROR',
    PARAM_ERROR: 'PARAM_ERROR',
    GET_WAY_ERROR: 'GET_WAY_ERROR',
    CONNECTION_TIMEOUT: 'CONNECTION_TIMEOUT',
    ES_SERVER_ERROR: 'ES_SERVER_ERROR',
    VM_ABNORMAL_STATE: 'VM_ABNORMAL_STATE',

    SUCCESS: 'SUCCESS',

    WARNING: 'WARNING'
}

code_desc = {
    ERROR: '错误',
    MS_ERROR: '微服务错误',
    DATABASE_ERROR: '数据库错误',
    NOT_AUTHORIZED: '未授权，拒绝访问',
    DATA_FORMAT_ERROR: '数据格式错误',
    TIMEOUT: '超时',
    UNKNOWN_ERROR: '未知错误',
    THIRD_PARTY_ERROR: '第三方服务错误',
    PARAM_ERROR: '参数错误',
    GET_WAY_ERROR: 'api 网关服务器错误',
    ES_SERVER_ERROR: 'elastic search 服务器错误',
    CONNECTION_TIMEOUT: '连接超时',
    VM_ABNORMAL_STATE: '虚机非正常状态',

    SUCCESS: '成功',

    WARNING: '警告'
}

name2code = {
    'ERROR': ERROR,
    'MS_ERROR': MS_ERROR,
    'DATABASE_ERROR': DATABASE_ERROR,
    'NOT_AUTHORIZED': NOT_AUTHORIZED,
    'DATA_FORMAT_ERROR': DATA_FORMAT_ERROR,
    'TIMEOUT': TIMEOUT,
    'UNKNOWN_ERROR': UNKNOWN_ERROR,
    'THIRD_PARTY_ERROR': THIRD_PARTY_ERROR,
    'PARAM_ERROR': PARAM_ERROR,
    'GET_WAY_ERROR': GET_WAY_ERROR,
    'CONNECTION_TIMEOUT': CONNECTION_TIMEOUT,
    'ES_SERVER_ERROR': ES_SERVER_ERROR,
    'VM_ABNORMAL_STATE': VM_ABNORMAL_STATE,

    'SUCCESS': SUCCESS,

    'WARNING': WARNING
}

name_desc = {
    'ERROR': '错误',
    'MS_ERROR': '微服务错误',
    'DATABASE_ERROR': '数据库错误',
    'NOT_AUTHORIZED': '未授权，拒绝访问',
    'DATA_FORMAT_ERROR': '数据格式错误',
    'TIMEOUT': '超时',
    'UNKNOWN_ERROR': '未知错误',
    'THIRD_PARTY_ERROR': '第三方服务错误',
    'PARAM_ERROR': '参数错误',
    'GET_WAY_ERROR': 'api 网关服务器错误',
    'CONNECTION_TIMEOUT': '连接超时',
    'ES_SERVER_ERROR': 'elastic search 服务器错误',
    'VM_ABNORMAL_STATE': '虚机非正常状态',

    'SUCCESS': '成功',

    'WARNING': '警告'
}


def revert(code1, data=None, desc=None):
    """
    公共返回方法

    :param code1: 状态码
    :param data: 返回数据
    :param desc: 描述
    :return: dict
    """

    try:
        msg = code2name[code1]

        if not desc:
            desc = code_desc[code1]
    except KeyError as e:
        return revert(-9, e, '调用公共返回方法出错，未找到状态码，请检查状态码是否匹配')

    if data is not None:
        return {'code': code1, 'msg': msg, 'desc': desc, 'data': data}
    else:
        return {'code': code1, 'msg': msg, 'desc': desc}
