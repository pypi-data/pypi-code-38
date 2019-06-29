from functools import wraps


class Stub():
    def __init__(self, func):
        self.func = func
        self.level = 0

    def __call__(self, *args, **kwargs):
        raise RuntimeError('Stubs are not to be called!')

    @classmethod
    def wraps(cls, func):
        if isinstance(func, cls):
            func.level += 1
            return func
        return wraps(func)(cls(func))


class Wrapper():
    def __init__(self, func, no_arg=False):
        assert callable(func), '{}'.format(func)
        self.func = func
        self.no_arg = no_arg
        wraps(func)(self)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class DecoratorDelegator():
    def __init__(self, namespace):
        self.namespace = namespace
        self.todo = []

    def __call__(self, decorator):
        if isinstance(decorator, bool) and decorator:
            # if take no (other) arg
            def func(decorator):
                return Wrapper(decorator, True)
            return func
        if not callable(decorator):
            msg = ('@cls applies to methods. If you have more decorators, for '
                   'example, @property and @classmethod, please consider '
                   'different order.')
            raise RuntimeError(msg)
        return Wrapper(decorator)

    def __getattr__(self, decorator_name):
        def collect_args(*args, **kwargs):
            def delay(func):
                stub = Stub.wraps(func)
                self.todo.append((decorator_name, args, kwargs, stub))
                return stub
            if len(args) == 1 and callable(args[0]):
                return delay(args[0])
            return delay
        return collect_args

    def realize(self, cls_):
        for decorator_name, args, kwargs, stub in self.todo:
            decorator = getattr(cls_, decorator_name)
            if decorator.no_arg:
                wrapped = decorator(cls_)(stub.func)
            else:
                wrapped = decorator(cls_, *args, **kwargs)(stub.func)
            if stub.level > 0:
                stub.level -= 1
                stub.func = wrapped
            else:
                self.namespace[stub.__name__] = wrapped
                setattr(cls_, stub.__name__, wrapped)


# Steps constructing class:
# 0. Resolving MRO entries
# 1. Determining the appropriate metaclass
class ClsMeta(type):
    # 2. Preparing the class namespace
    def __prepare__(name, bases, **kwds):
        namespace = type.__prepare__(name, bases, **kwds)
        namespace['cls'] = DecoratorDelegator(namespace)
        return namespace

    # 3. Executing the class body
    # 4. Creating the class object
    # def __call__(name, bases, namespace, **kwds):
    #     def __new__(meta, name, bases, namespace, **kwds):
        #     4.1.0 colloct descriptors
        #     4.1.1 for each descriptor call __set_name__(self, owner, name)
        #     4.1.2 init cls
    def __init__(cls, name, bases, namespace):
        delegator = namespace.pop('cls')
        delegator.realize(cls)
        cls = type.__init__(cls, name, bases, namespace)
        return cls

    # 5. Nothing more, ready to go
