# -*- coding: utf-8 -*-
import sys
from .validator import validator
from .schema_generator import schema_generator
from .api_info_generator import ApiInfoGenerator
from ..lib.CommonLogger import debug, info, warn, error


class Api(object):

    def __init__(self, **kwargs):
        debug("api 参数:{}".format(kwargs))
        the_api_args = self._get_api_args(**kwargs)
        debug("api 默认值后参数:{}".format(the_api_args))
        self.api_args = the_api_args
        self.api_info = None

    def _get_api_args(self, is_cli=True, public=True, **kwargs):
        """
        这里只是设置一些默认值
        :param is_cli:
        :param public:
        :param kwargs:
        :return:
        """
        kwargs['is_cli'] = is_cli
        kwargs['public'] = public
        return kwargs

    @staticmethod
    def check_api_func_type(api_func):
        if sys.version_info < (3, 0):
            if 'self' == api_func.func_code.co_varnames[0]:
                debug("api 是一个实例函数")
                return 'self'
            if 'cls' in api_func.func_code.co_varnames[0]:
                debug("api 是一个类函数")
                return 'cls'
        else:
            if 'self' == api_func.__code__.co_varnames[0]:
                debug("api 是一个实例函数")
                return 'self'
            if 'cls' in api_func.__code__.co_varnames[0]:
                debug("api 是一个类函数")
                return 'cls'
        return 'static'

    def _cfg_api_info(self):
        if self.api_args.get('url'):
            if self.api_info.get('url'):
                debug("注释内写了url,所以就用注释内的")
            else:
                debug("注释内没有写url,就用装饰器内的 {}".format(self.api_args.get('url')))
                self.api_info['url'] = self.api_args.get('url')
        else:
            if self.api_info.get('url') is None:
                error("完全没有设置URL ::{}".format(self.api_info))
        api_validator = schema_generator.generate_schema(self.api_info.get('params'))
        debug("获得的 api {} validator => {} ".format(self.api_info.get('url'), api_validator))
        self.api_info['validator'] = api_validator

    def wrap_api(self, *args, **kwargs):
        """
        自动适应地对各种类型的API （静态方法，类实例方法，类方法） 来进行包装
        :param args:    需要包装的api函数，默认是放在args[0]
        :param kwargs:  暂时没用的
        :return:    包装好的包装函数
        """
        debug("来了参数:{} {}".format(args, kwargs))
        self.api_info = ApiInfoGenerator.generate_api_info(self.api_args.get('url'), args[0])
        if self.api_info is None:
            warn("函数:{} 注释无法解析出api_info".format(args[0]))
            return args[0]
        api_wrapper = self._get_api_wrapper(args[0])
        self._cfg_api_info()
        if self.api_args.get('is_cli'):
            debug("{} 是命令行api".format(self.api_args))
            if self.api_args.get('public'):
                debug("{} 是public api".format(self.api_args))
                api_router = self.api_args.get('router')
                if api_router is None:
                    debug("默认路由添加 cli")
                    from ..cli.router import router
                    api_router = router
                api_router.add_route(self.api_info.uniq_url, api_wrapper, self.api_info)
        else:
            debug("不是cli命令行,无需处理 {}".format(self.api_info.uniq_url))

        return api_wrapper

    def _get_api_wrapper(self, api_func):
        api_type = self.check_api_func_type(api_func)
        if api_type == 'static':
            debug("静态方法:{}".format(api_func))

            def api_wrapper(*api_args, **api_kwargs):
                debug("run api[{}] with args :{}".format(self.api_info, api_kwargs))
                # if self.api_info.is_cli():
                #     debug("api 是cli:{}".format(self.api_info))
                # else:
                #     debug("api 不是cli:{}".format(self.api_info))
                ret = self.api_call(*api_args, **api_kwargs)
                return ret

        elif api_type == 'self':
            debug("类实例方法:{}".format(api_func))
            api_cls = self.api_args.get('cls')

            def api_wrapper(*api_args, **api_kwargs):
                debug("run api[{}] with args :{}".format(self.api_info, api_kwargs))
                if len(api_args) == 0:
                    if api_cls is not None:
                        api_self = api_cls()
                    else:
                        warn('直接用api来做self调 api 会产生逻辑异常')
                        api_self = self
                    ret = self.api_call(api_self, *api_args, **api_kwargs)
                else:
                    ret = self.api_call(*api_args, **api_kwargs)
                return ret

        elif api_type == 'cls':
            debug("类方法:{}".format(api_func))
            api_cls = self.api_args.get('cls')

            def api_wrapper(*api_args, **api_kwargs):
                debug("run api[{}] with args :{}".format(self.api_info, api_kwargs))
                if len(api_args) == 0:
                    if api_cls is not None:
                        api_class = api_cls
                    else:
                        warn('直接用api来做self调 api 会产生逻辑异常')
                        api_class = self
                    ret = self.api_call(api_class, *api_args, **api_kwargs)
                else:
                    ret = self.api_call(*api_args, **api_kwargs)
                return ret
        else:
            error("这是什么鬼函数:{}".format(api_func))
            raise Exception("这是什么鬼函数:{}".format(api_func))
        api_wrapper.__doc__ = api_func.__doc__
        return api_wrapper

    def api_call(self, *args, **kwargs):
        debug('com to call :{}'.format(kwargs))
        valid_args = validator.validate(self.api_info.get('validator'), kwargs)
        return self.api_info.call_api(*args, **valid_args)

    def __call__(self, *args, **kwargs):
        return self.wrap_api(*args, **kwargs)
