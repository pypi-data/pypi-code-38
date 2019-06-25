# Used for micro-service which developed by nameko
# install nameko before use
"""
    Example::

        from wisdoms.auth import permit

        host = {'AMQP_URI': "amqp://guest:guest@localhost"}

        auth = permit(host)

        class A:
            @auth
            def func():
                pass
"""
from nameko.rpc import rpc

from nameko.standalone.rpc import ClusterRpcProxy
from nameko.standalone.rpc import ServiceRpcProxy

from nameko.exceptions import RpcTimeout, MethodNotFound

from functools import wraps
from operator import methodcaller
from wisdoms.utils import xpt_func


def rpc_with_timeout(host, service, func, data=None, timeout=8):
    try:
        with ServiceRpcProxy(service, host, timeout=timeout) as proxy:
            if data is not None:
                res = methodcaller(func, data)(proxy)
            else:
                res = methodcaller(func)(proxy)
            return res
    except RpcTimeout as e:
        print(service, ' ~~连接超时 %s sec......，检查是否启动......' % e)
    except MethodNotFound as e:
        print('function of this server not found,未找到方法 %s ' % e)


def ms_base(ms_host, **extra):
    """
    返回父类，闭包，传参数ms host
    :param ms_host:
    :param extra: 额外信息
    :return:
    """

    class MsBase:
        name = 'ms-base'

        @rpc
        # @exception()
        def export_info2db(self):
            """
            export information of this service to database

            :param timeout 超时设置
            :return:
            """
            clazz = type(self)
            service = clazz.name
            functions = list(clazz.__dict__.keys())

            origin = dict()
            origin['service'] = service
            origin['functions'] = functions
            origin['roles'] = extra.get('roles')
            origin['name'] = extra.get('name')
            origin['types'] = extra.get('types', 'free')
            origin['entrance'] = extra.get('entrance')
            origin['entrance4app'] = extra.get('entrance4app')
            origin['entrance4back'] = extra.get('entrance4back')

            rpc_with_timeout(ms_host, 'baseUserApp', 'app2db', origin)

    return MsBase


def permit(host):
    """ 调用微服务功能之前，进入基础微服务进行权限验证

    :param: host: micro service host
    """

    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            service = args[0].name
            func = f.__name__
            token = args[1].get('token')

            res = rpc_with_timeout(host, 'baseUserApp', 'verify', {'service': service, 'func': func, 'token': token})

            if res:
                del res['password_hash']
                del res['partner']
                args[1]['user'] = res
                args[1]['uid'] = res.get('id')
                return f(*args, **kwargs)

            raise Exception('verified failed')

        return inner

    return wrapper


def add_uid(host):
    """
    用户token 返回用户id
    :param host:
    :return:
    """

    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            token = args[1].get('token')

            res = rpc_with_timeout(host, 'baseUserApp', 'get_uid', {'token': token})

            if res:
                args[1]['uid'] = res
                return f(*args, **kwargs)

            raise Exception('verified failed')

        return inner

    return wrapper


def add_user(host):
    """
    用户token 返回用户信息
    :param host:
    :return:
    """

    def wrapper(f):
        @wraps(f)
        def inner(*args, **kwargs):
            token = args[1].get('token')

            res = rpc_with_timeout(host, 'baseUserApp', 'get_user', {'token': token})
            if res:
                del res['password_hash']
                del res['partner']
                args[1]['user'] = res
                return f(*args, **kwargs)

            raise Exception('verified failed')

        return inner

    return wrapper


def assemble(rpc, service, function1, param1='', *params):
    str1 = rpc + '.' + service + '.' + function1
    str2 = '(' + param1
    for param in params:
        str2 += ',' + param
    str2 += ')'
    return str1 + str2


def crf_closure(ms_host):
    def crf(service, function1, data):
        with ClusterRpcProxy(ms_host) as rpc:
            result = eval(assemble('rpc', service, function1, 'data'))
        return result

    return crf


def config_server(host, service='configServerFunc', func='import_config', timeout=10):
    try:
        with ServiceRpcProxy(service, host, timeout=timeout) as proxy:
            res = methodcaller(func)(proxy)
            print(res)
            return res
    except RpcTimeout as e:
        return {'code': -30, 'desc': '配置中心微服务连接超时，或未启动, 时长:%s' % e, 'data': None}
