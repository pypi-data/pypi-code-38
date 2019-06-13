from functools import wraps, partial, update_wrapper
from collections import Callable, OrderedDict
from kwrepr import kwrepr, default_kw, need_args


def iscallable(x):
    return isinstance(x, Callable)


class xargs:
    def __new__(cls, func, expect_args=(), expect_kw=()):
        self = super(xargs, cls).__new__(cls)
        self.func = func
        self.expect_args = expect_args
        self.expect_kw = expect_kw
        return update_wrapper(self, func)

    def copy(self, **kw):
        return self.__new__(type(self), partial(self.func, **kw),
                            self.expect_args, self.expect_kw)

    def __call__(self, src, key):
        return self.func(*(src[k] for k in self.expect_args),
                         **{k: src[k] for k in self.expect_kw})

    def __kwrepr__(self):
        kwr = dict(__class__ = ":".join((self.__class__.__module__,
                                         self.__class__.__name__)),
                   func = kwrepr(self.func))
        if self.expect_args:
            kwr['expect_args'] = self.expect_args
        if self.expect_kw:
            kwr['expect_kw'] = self.expect_kw
        return kwr

    def __repr__(self):
        kw = self.__kwrepr__()
        klass = kw.pop('__class__')
        return "{}({})".format(klass, kw)


class xlazy(xargs):
    def __new__(cls, func):
        return update_wrapper(super(xlazy, cls).__new__(cls, func), func)

    def copy(self, **kw):
        return self.__new__(type(self), partial(self.func, **kw))

    def __call__(self, src, key):
        return self.func(src)

    def __kwrepr__(self):
        return dict(__class__ = ":".join((self.__class__.__module__,
                                          self.__class__.__name__)),
                    func = kwrepr(self.func))


class xmem(xargs):
    def __new__(cls, func, expect_args=(), expect_kw=()):
        self = super(xmem, cls).__new__(cls, func)
        self.expect_args = expect_args
        self.expect_kw = expect_kw
        return update_wrapper(self, func)

    def copy(self, **kw):
        return self.__new__(type(self), partial(self.func, **kw),
                            self.expect_args, self.expect_kw)

    def __call__(self, src, key):
        return src.cache_set_default(
            (key, tuple(src[k] for k in (list(self.expect_args) +
                                         list(self.expect_kw)))),
            partial(self.func,
                    *(src[k] for k in self.expect_args),
                    **{k: src[k] for k in self.expect_kw}))


def iff(cond, ontrue, onfalse):
    return ontrue() if cond() else onfalse()


def loop(init, step, end):
    state = init()
    while not end(state):
        step(state)
    return state


class EvalAttr:
    def __init__(self, defaults):
        self._defaults = defaults
        self._dct = defaults.copy()
        self._cache = dict()

    def update_dct(self, *args):
        for a in args:
            self._dct.update(a)

    def cache_set_default(self, k, default_fn):
        d = self._cache
        return d[k] if k in d else d.setdefault(k, default_fn())

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        v = self._dct[key]
        return (v(self, key)
                if isinstance(v, xargs)
                else v)


def kwplus(func, evaldictclass=EvalAttr):
    def_kw = default_kw(func)
    need_a = need_args(func)
    ekw = evaldictclass(def_kw)

    @wraps(func)
    def wrapper(*a, **kw):
        a2kw = dict(zip(need_a[:len(a)], a))
        ekw.update_dct(a2kw, kw)
        kwevaled = {k: ekw[k] for k in need_a}
        return func(**kwevaled)

    return wrapper


def clone_partial(func, **kw):
    return (func.copy(**kw)
            if isinstance(func, xargs)
            else partial(func, **kw))


def _recpartial(func, reckey, val, sep="."):
    reckeys = reckey.split(sep)
    next_val = (val
                if len(reckeys) == 1
                else
                recpartial(default_kw(func)[reckeys[0]],
                           sep.join(reckeys[1:]), val))
    return clone_partial(func, **{reckeys[0]: next_val})


def recpartial(func, keywords, sep="."):
    """
    recpartial(func, {'a.b.c': 10})

    is a short form for

    partial(func, a=partial(b=partial(c=10))

    As expected a and b need to be callables and b must accept c as a keyword
    argument.
    """
    # Separate head keywords from tail keywords.
    # We will apply partial with head keywords.
    # Tail keywords will be passed on recursively, but they need to be grouped
    # first to minimize calls to the recpartial.
    assert iscallable(func)
    head_keywords = dict()
    tail_keywords = OrderedDict()  # respect keywords order
    for reckey, val in keywords.items():
        reckeys = reckey.split(sep)
        if len(reckeys) > 1:
            tail_keywords.setdefault(
                reckeys[0], {})[sep.join(reckeys[1:])] = val
        else:
            head_keywords[reckeys[0]] = val

    for headkey, t_keywords in tail_keywords.items():
        tail_func = head_keywords.get(headkey, default_kw(func)[headkey])
        head_keywords[headkey] = recpartial(tail_func, t_keywords, sep=sep)
    return clone_partial(func, **head_keywords)
