#!/usr/bin/env python

from j5basic import Decorators, DictUtils
import threading
import time
import inspect
from j5test.Utils import method_raises, raises

class TestDecoratorDecorator(object):

    @staticmethod
    def f(self, x=1, y=2, *args, **kw):
        """sample function for testing signatures etc"""
        pass

    @staticmethod
    def chatty(f, *args, **kw):
        """sample decorator that logs calls on f.calls"""
        if not hasattr(f, "calls"):
            f.calls = []
        f.calls.append("Calling %r" % f.__name__)
        return f(*args, **kw)

    @staticmethod
    def extdec(f, x, y, z):
        """decorator extending underlying function"""
        if not hasattr(f, "calls"):
            f.calls = []
        f.calls.append("Called with x=%r, y=%r, z=%r" % (x, y, z))
        return f(x + y * z)

    @staticmethod
    def callfdec(f, x, y, z, calling_frame):
        """decorator extending underlying function and getting calling_frame"""
        if not hasattr(f, "call_frames"):
            f.call_frames = []
        f.call_frames.append(calling_frame)
        return f(x + y * z)

    @staticmethod
    def callfdec2(f, x, calling_frame):
        """decorator extending underlying function, and passing calling_frame into it"""
        if not hasattr(f, "call_frames"):
            f.call_frames = []
        f.call_frames.append(calling_frame)
        return f(x, calling_frame)

    @staticmethod
    def override_x(f, *args, **kw):
        args, kw = Decorators.override_arg("x", 50, args, kw, inspect.getargspec(f))
        return f(*args, **kw)

    @staticmethod
    def g(x):
        """returns x plus 25"""
        return x + 25

    @staticmethod
    def extdec2(f, *args, **kw):
        """decorator extending underlying function, and using args and kwargs"""
        if not hasattr(f, "calls"):
            f.calls = []
        args = list(args)
        def poparg(argname):
            if argname in kw:
                return kw.pop(argname)
            else:
                return args.pop()
        y = poparg("y")
        z = poparg("z")
        x = poparg("x")
        f.calls.append("Called with x=%r, y=%r, z=%r" % (x, y, z))
        return f(x + y * z, z)

    @staticmethod
    def g2(x, z=4):
        """returns x plus z plus 25"""
        return x + z + 25

    @staticmethod
    def g3(y, x=0):
        return y + x + 25

    def test_getinfo(self):
        """tests that the getinfo function returns the correct information about a function signature"""
        info = Decorators.decorator_helpers.getinfo(self.f)
        assert info["name"] == 'f'
        assert info["argnames"] == ['self', 'x', 'y', 'args', 'kw']
        assert info["defarg"] == (1, 2)
        assert info["shortsign"] == 'self, x, y, *args, **kw'
        assert info["fullsign"] == 'self, x=defarg[0], y=defarg[1], *args, **kw'
        assert (info["arg0"], info["arg1"], info["arg2"], info["arg3"], info["arg4"]) == ('self', 'x', 'y', 'args', 'kw')

    def test_decorator(self):
        """test that a decorator is called, and properly calls the underlying function"""
        chatty_decorator = Decorators.decorator(self.chatty)
        chatty_g = chatty_decorator(self.g)
        result = chatty_g(3)
        assert result == 28
        assert self.g.calls[-1] == "Calling 'g'"

    def test_decorator_lambda(self):
        """test that a decorator is called, and properly calls the underlying function"""
        l = lambda x: x + 21
        assert l(3) == 24
        chatty_decorator = Decorators.decorator(self.chatty)
        chatty_l = chatty_decorator(l)
        assert chatty_l(3) == 24

    def test_decorator_signature(self):
        """tests that a decorated function retains the signature of the underlying function"""
        chatty_decorator = Decorators.decorator(self.chatty)
        chatty_f = chatty_decorator(self.f)
        info = Decorators.decorator_helpers.getinfo(self.f)
        chatty_info = Decorators.decorator_helpers.getinfo(chatty_f)
        assert info == chatty_info
        assert info.__doc__ == chatty_info.__doc__

    def test_extend_decorator(self):
        """tests that a decorated function can extend the underlying function"""
        ext_decorator = Decorators.decorator(self.extdec, ['y', ('z', 3)])
        ext_g = ext_decorator(self.g)
        assert ext_g(100, 4) == 100 + 12 + 25
        assert self.g.calls[-1] == "Called with x=100, y=4, z=3"

    def test_decorator_calling_frame_arg(self):
        """tests that a decorated function can get the frame of the calling function"""
        frames_so_far = len(getattr(self.g, "call_frames", []))
        callf_decorator = Decorators.decorator(self.callfdec, ['y', ('z', 3)], calling_frame_arg="calling_frame")
        callf_g = callf_decorator(self.g)
        assert callf_g(100, 4) == 100 + 12 + 25
        assert len(self.g.call_frames) == frames_so_far + 1
        call_frame = self.g.call_frames[-1]
        assert call_frame
        assert call_frame.f_code.co_name == "test_decorator_calling_frame_arg"
        # check that calling_frame can't be overridden
        some_frame = Decorators.inspect.currentframe()
        raises(TypeError, callf_g, 100, 4, calling_frame=some_frame)
        raises(TypeError, callf_g, 100, 4, some_frame)

    def test_decorator_calling_frame_extendedarg(self):
        """tests that a decorated function can get the frame of the calling function and pass it as an extended argument"""
        frames_so_far = len(getattr(self.g, "call_frames", []))
        callf_decorator = Decorators.decorator(self.callfdec, ['y', ('z', 3), ("calling_frame", None)], calling_frame_arg="calling_frame")
        callf_g = callf_decorator(self.g)
        assert callf_g(100, 4) == 100 + 12 + 25
        assert len(self.g.call_frames) == frames_so_far + 1
        call_frame = self.g.call_frames[-1]
        assert call_frame
        assert call_frame.f_code.co_name == "test_decorator_calling_frame_extendedarg"
        # check that calling_frame can be overridden, but the result is still correct
        some_frame = Decorators.inspect.currentframe().f_back
        assert callf_g(100, 4, calling_frame=some_frame) == 100 + 12 + 25
        assert len(self.g.call_frames) == frames_so_far + 2
        assert self.g.call_frames[-1] != some_frame
        assert callf_g(100, 4, 5, some_frame) == 100 + 20 + 25
        assert len(self.g.call_frames) == frames_so_far + 3
        assert self.g.call_frames[-1] != some_frame

    def test_decorator_lambda_calling_frame_arg(self):
        """tests that a decorated function can get the frame of the calling function when a lambda is being decorated"""
        l = lambda x: x + 21
        frames_so_far = len(getattr(l, "call_frames", []))
        callf_decorator = Decorators.decorator(self.callfdec, ['y', ('z', 3)], calling_frame_arg="calling_frame")
        callf_l = callf_decorator(l)
        assert callf_l(100, 4) == 100 + 12 + 21
        assert len(l.call_frames) == frames_so_far + 1
        call_frame = l.call_frames[-1]
        assert call_frame
        assert call_frame.f_code.co_name == "test_decorator_lambda_calling_frame_arg"
        # check that calling_frame can't be overridden
        some_frame = Decorators.inspect.currentframe()
        raises(TypeError, callf_l, 100, 4, calling_frame=some_frame)
        raises(TypeError, callf_l, 100, 4, some_frame)

    def test_decorator_lambda_calling_frame_extendedarg(self):
        """tests that a decorated function can get the frame of the calling function when a lambda is being decorated, and pass it as an extended argument"""
        l = lambda x, calling_frame: x + 21
        frames_so_far = len(getattr(l, "call_frames", []))
        callf_decorator = Decorators.decorator(self.callfdec2, [("calling_frame", None)], calling_frame_arg="calling_frame")
        callf_l = callf_decorator(l)
        assert callf_l(100, "nonsense") == 100 + 21
        assert len(l.call_frames) == frames_so_far + 1
        call_frame = l.call_frames[-1]
        assert call_frame
        # check that the argument given for calling frame is overridden
        assert call_frame != "nonsense"
        assert call_frame.f_code.co_name == "test_decorator_lambda_calling_frame_extendedarg"

    def test_extend_decorator_signature(self):
        """tests that a decorated function can extend the signature of the underlying function"""
        ext_decorator = Decorators.decorator(self.extdec, ['y', ('z', 3)])
        ext_g = ext_decorator(self.g)
        info = Decorators.decorator_helpers.getinfo(self.g)
        ext_info = Decorators.decorator_helpers.getinfo(ext_g)
        assert ext_info.__doc__ == info.__doc__
        assert ext_info["name"] == info["name"]
        assert ext_info["argnames"] == ['x', 'y', 'z']
        assert ext_info["defarg"] == (3,)
        assert ext_info["shortsign"] == 'x, y, z'
        assert ext_info["fullsign"] == 'x, y, z=defarg[0]'
        assert ext_info["arg0"] == 'x'
        assert ext_info["arg1"] == 'y'
        assert ext_info["arg2"] == 'z'

    def test_extend_decorator_existing(self):
        """tests that a decorated function can extend the underlying function, handling existing arguments right"""
        ext_decorator = Decorators.decorator(self.extdec2, [('y', 5), ('z', 3), ('x', 0)])
        ext_g = ext_decorator(self.g2)
        info = Decorators.decorator_helpers.getinfo(self.g2)
        ext_info = Decorators.decorator_helpers.getinfo(ext_g)
        assert ext_info.__doc__ == info.__doc__
        assert ext_info["name"] == info["name"]
        assert ext_info["argnames"] == ['x', 'z', 'y']
        assert ext_info["defarg"] == (0, 3, 5)
        assert ext_info["shortsign"] == 'x, z, y'
        assert ext_info["fullsign"] == 'x=defarg[0], z=defarg[1], y=defarg[2]'
        assert ext_info["arg0"] == 'x'
        assert ext_info["arg1"] == 'z'
        assert ext_info["arg2"] == 'y'
        result = ext_g()
        assert result == (0 + 3*5) + 3 + 25
        assert self.g2.calls[-1] == "Called with x=0, y=5, z=3"

    def test_override_arg(self):
        override_decorator = Decorators.decorator(self.override_x)
        override_g = override_decorator(self.g)
        assert override_g(0) == 75

        override_g3 = override_decorator(self.g3)
        assert override_g3(25, 0) == 100

class TestSelfLocking(object):

    def test_runwithlock(self):
        THREADS = 4

        class Foo(object):
            lock = threading.Lock()
            res = []

            @Decorators.SelfLocking.runwithlock
            def haslock(self,i):
                self.res.append(i)
                time.sleep(0.1)
                self.res.append(i)

        threads = []
        for i in range(THREADS):
            threads.append(threading.Thread(target=Foo().haslock,args=[i]))

        for thrd in threads:
            thrd.start()

        for thrd in threads:
            thrd.join()

        assert len(Foo.res) == 2*THREADS
        for i in range(THREADS):
            assert Foo.res[2*i] == Foo.res[2*i+1]


    def test_runwithnamedlock(self):
        THREADS = 4

        class Foo(object):
            other_lock = threading.Lock()
            res = []

            @Decorators.SelfLocking.runwithnamedlock('other_lock')
            def hasotherlock(self,i):
                self.res.append(i)
                time.sleep(0.1)
                self.res.append(i)

        threads = []
        for i in range(THREADS):
            threads.append(threading.Thread(target=Foo().hasotherlock,args=[i]))

        for thrd in threads:
            thrd.start()

        for thrd in threads:
            thrd.join()

        assert len(Foo.res) == 2*THREADS
        for i in range(THREADS):
            assert Foo.res[2*i] == Foo.res[2*i+1]

class TestNotImplemented(object):

    @method_raises(NotImplementedError)
    def test_noimp(self):
        @Decorators.notimplemented
        def f(x,y):
            """Should be overridden elsewhere."""
            pass

        f(1,2)

def test_chain_decorators():
    @Decorators.decorator
    def increase_result(f, *args, **kwargs):
        return f(*args, **kwargs) + 1
    @Decorators.decorator
    def double_result(f, *args, **kwargs):
        return f(*args, **kwargs)*2
    @Decorators.chain_decorators(increase_result, double_result)
    def underlying(x):
        return x * 6

    assert underlying(3) == ((3*6)*2) + 1

def test_get_right_args():
    def my_arg_function(foo, bar, jim=3):
        pass

    rightargs = Decorators.getrightargs(my_arg_function, {'foo': 1, 'bar': 2, 'bob': 3, 'mary': 4, 'jim': 5})
    DictUtils.assert_dicts_equal(rightargs, {'foo': 1, 'bar': 2, 'jim': 5})
    rightargs = Decorators.getrightargs(my_arg_function, {'foo': 1, 'bar': 2, 'bob': 3, 'mary': 4})
    DictUtils.assert_dicts_equal(rightargs, {'foo': 1, 'bar': 2})

    class my_arg_class(object):
        def __init__(self, foo, filip):
            pass

    rightargs = Decorators.getrightargs(my_arg_class, {'foo': 1, 'bar': 2, 'bob': 3, 'mary': 4})
    DictUtils.assert_dicts_equal(rightargs, {'foo': 1, 'filip': None})

    rightargs, rightkw = Decorators.conform_to_argspec((1, 2), {'billybob': 5, 'jim': 3}, inspect.getargspec(my_arg_function))
    assert rightargs == [1, 2, 3]
    assert not rightkw

def test_get_or_pop_arg():
    def my_arg_function(foo, bar, jim=3):
        pass

    args = (1, 2)
    kw = {'jim': 3}

    assert Decorators.get_or_pop_arg('bar', args, kw, inspect.getargspec(my_arg_function)) == 2
    assert args == (1, 2)
    DictUtils.assert_dicts_equal(kw, {'jim': 3})
    assert Decorators.get_or_pop_arg('jim', args, kw, inspect.getargspec(my_arg_function)) == 3
    assert args == (1, 2)
    DictUtils.assert_dicts_equal(kw, {'jim': 3})

    kw['billybob'] = 4
    assert Decorators.get_or_pop_arg('billybob', args, kw, inspect.getargspec(my_arg_function)) == 4
    assert args == (1, 2)
    DictUtils.assert_dicts_equal(kw, {'jim': 3})

