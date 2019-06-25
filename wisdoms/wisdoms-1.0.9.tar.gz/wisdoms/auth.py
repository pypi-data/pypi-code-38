# Install nameko before use

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

from nameko.standalone.rpc import ClusterRpcProxy
from functools import wraps


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

            with ClusterRpcProxy(host) as r:
                res = r.baseUserApp.verify({'service': service, 'func': func, 'token': token})
            if res:
                args[1]['user'] = res
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

            with ClusterRpcProxy(host) as r:
                res = r.baseUserApp.get_uid({'token': token})
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

            with ClusterRpcProxy(host) as r:
                res = r.baseUserApp.get_user({'token': token})
            if res:
                args[1]['user'] = res
                return f(*args, **kwargs)

            raise Exception('verified failed')

        return inner

    return wrapper
