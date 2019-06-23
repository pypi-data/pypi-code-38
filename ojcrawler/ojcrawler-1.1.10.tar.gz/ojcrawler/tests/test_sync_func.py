import inspect


def sample_sync_func(status, *args, **kwargs):
    pass


class Controller(object):
    # 一次性根据配置的账号数量，初始化对应oj对应数量的Controller
    # 在外部做负载均衡

    def __init__(self, oj_name: str, sync_func=sample_sync_func):
        self.oj = oj_name
        print(inspect.getfullargspec(sync_func))
        args = inspect.getfullargspec(sync_func)[0]
        if len(args) < 1 or args[0] != 'status':
            raise ValueError(
                'sync_func的第一个参数必须为status而不是{}, sample: sync_func(status, *args, **kwargs)'.format(args[0]))
        self.func = sync_func

    def run(self, *args, **kwargs):
        self.func('test', *args, **kwargs)


def sync_fun(status, ip, port):
    print('status:', status)
    print('ip:', ip)
    print('port:', port)


if __name__ == '__main__':
    c = Controller('x')
    c.run()
