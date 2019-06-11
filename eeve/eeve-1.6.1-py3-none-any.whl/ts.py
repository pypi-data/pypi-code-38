import json_tricks, inspect


def test_sampler_decorator(func):
    def test_sampler(*args, **kwargs):
        #t = kwargs['trigger']
        #c = t.__class__
        try:
            #ti = t.__new__(c)
            dmp = json_tricks.dumps([args, kwargs])
            c = get_class_that_defined_method(func)
            #print(inspect.getmodule(func).__name__, c, func.__name__, dmp)
            pass

        except Exception as ex:
            #print('-' * 15, ex)
            pass

        return func(*args, **kwargs)

    return test_sampler


def get_class_that_defined_method(meth):
    if inspect.ismethod(meth):
        print('this is a method')
        for cls in inspect.getmro(meth.__self__.__class__):
            if cls.__dict__.get(meth.__name__) is meth:
                return cls
    if inspect.isfunction(meth):
        print('this is a function')
        return getattr(inspect.getmodule(meth), meth.__qualname__.split('.<locals>', 1)[0].rsplit('.', 1)[0])
    print('this is neither a function nor a method')
    return None  # not required since None would have been implicitly returned anyway