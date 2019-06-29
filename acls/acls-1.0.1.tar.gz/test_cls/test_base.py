from functools import wraps
import cls


class Base(metaclass=cls.ClsMeta):
    @cls
    def decor1(cls, decor_arg):
        def wrap(func):
            @wraps(func)
            def wrapper(self, arg):
                pre = 'cdp({})'.format(cls.__name__)
                retval = func(self, arg)
                sub = 'cds({})'.format(decor_arg)
                return '.'.join((pre, retval, sub))
            return wrapper
        return wrap

    @cls(True)
    def decor2(cls):
        def wrap(func):
            @wraps(func)
            def wrapper(self, arg):
                pre = 'cdp2({})'.format(cls.__name__)
                retval = func(self, arg)
                sub = 'cds2()'.format()
                return '|'.join((pre, retval, sub))
            return wrapper
        return wrap


def plain_decor(func):
    pre = 'pdb'
    sub = 'pds'
    return lambda x: '|'.join((pre, func(x,), sub))


class Extended(Base):
    @cls
    def decor3(cls, decor_arg='decor3 arg'):
        def wrap(func):
            @wraps(func)
            def wrapper(self, arg):
                pre = 'cdp3({})'.format(cls.__name__)
                retval = func(self, arg)
                sub = 'cds3({})'.format(decor_arg)
                return '|'.join((pre, retval, sub))
            return wrapper
        return wrap

    @cls.decor3()
    @cls.decor1('decor1 arg')
    @cls.decor2
    def func(self, func_arg):
        return func_arg


def test_cls():
    obj = Extended()
    retval = obj.func('function arg')
    print(retval)
    assert retval == 'cdp3(Extended)|cdp(Extended).cdp2(Extended)|function arg|cds2().cds(decor1 arg)|cds3(decor3 arg)'


if __name__ == '__main__':
    test_cls()
