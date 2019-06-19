from __future__ import print_function

from pprint import pformat

from attr import attrs, attrib
from collections import defaultdict
from twisted.internet.defer import Deferred, inlineCallbacks, returnValue

from .clock import withTimeout


ORIGINAL_IS_DECODER = object()


@attrs(slots=True)
class Call(object):
    protocol = attrib(repr=False)
    args = attrib()
    kw = attrib()
    result = attrib()
    consumed = attrib(repr=False, default=False)


class HookState(object):

    def __init__(self, once):
        self.once = once
        self.instanceDeferreds = defaultdict(Deferred)
        self.instanceQueues = defaultdict(list)

    def handleCall(self, call):
        instance = call.protocol
        for target in None, instance:
            self.instanceQueues[target].append(call)
            deferred = self.instanceDeferreds[target]
            if target is None or not self.once:
                del self.instanceDeferreds[target]
            deferred.callback(call)

    @inlineCallbacks
    def expectCallback(self, instance, timeout):
        queue = self.instanceQueues[instance]
        if not queue:
            deferred = self.instanceDeferreds[instance]
            yield withTimeout(deferred, timeout)
        if self.once:
            call = queue[0]
        else:
            call = queue.pop(0)
        call.consumed = True
        returnValue(call)

    def cleanup(self):
        allUnconsumed = {}
        for instance, queue in self.instanceQueues.items():
            if instance is None:
                continue
            unconsumed = tuple(r for r in queue if not r.consumed)
            if unconsumed:
                allUnconsumed[instance] = unconsumed
            queue[:] = []
        return allUnconsumed


@inlineCallbacks
def called(self, decoder, timeout, instance):
    call = yield self.state.expectCallback(instance, timeout)
    decoder = decoder or self.decoder
    if decoder is None:
        returnValue(call)
    if decoder is ORIGINAL_IS_DECODER:
        returnValue(call.result)
    returnValue(decoder(*call.args, **call.kw))


class BoundHook(object):

    def __init__(self, state, original, instance, decoder):
        self.state = state
        self.original = original
        self.instance = instance
        self.decoder = decoder

    def __call__(self, *args, **kw):
        result = self.original(self.instance, *args, **kw)
        self.state.handleCall(Call(self.instance, args, kw, result))
        if self.decoder is not ORIGINAL_IS_DECODER:
            return result

    def called(self, decoder=None, timeout=None):
        return called(self, decoder, timeout, self.instance)


class UnconsumedCalls(AssertionError):

    def __init__(self, unconsumed):
        self.unconsumed = unconsumed

    def __str__(self):
        return '\n'+pformat(self.unconsumed)


class HookedCall(object):

    all = {}
    registeredClasses = set()

    def __init__(self, class_, name, decoder=None, once=False):
        self.original = getattr(class_, name)
        self.class_ = class_
        self.name = name
        self.state = HookState(once)
        self.decoder = decoder
        self.once = once
        setattr(class_, name, self)
        self.all[class_, name] = self

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return BoundHook(self.state, self.original, instance, self.decoder)

    @inlineCallbacks
    def protocol(self, timeout=None):
        call = yield self.state.expectCallback(None, timeout)
        returnValue(call.protocol)

    def called(self, decoder=None, timeout=None):
        return called(self, decoder, timeout, instance=None)

    @classmethod
    def hook(cls, class_, name, decoder=None, once=False):
        """
        Hook a method on a hooked class such that tests can wait on it being called
        on a particular instance.

        :param class_:
          The class on which to hook the named method.

        :param name:
          The name of the method to hook.

        :param decoder:
          A callable that will be used to decode the result of the method being called.
          It should take the same arguments and parameters as the method being hooked and should
          return whatever is required by the test that is going to wait on calls to this method.

        :param once:
          Only expect one call on this method. Multiple waits in a test will all end up
          waiting on the same call. This is most useful when hooking connections going away,
          where the test may want to explicitly wait for this, while the tear down of the test
          will also need to wait on it.
        """
        # opportunistic register:
        cls.register(class_)
        method = getattr(class_, name)
        if not isinstance(method, HookedCall):
            method = HookedCall(class_, name, decoder, once)
        return method

    def unHook(self):
        setattr(self.class_, self.name, self.original)

    @classmethod
    def register(cls, class_):
        if class_ not in cls.registeredClasses:
            cls.registeredClasses.add(class_)
            for name, obj in vars(class_).items():
                if getattr(obj, '__carly__decoder__', False):
                    cls.hook(class_, name, decoder=ORIGINAL_IS_DECODER)

    @classmethod
    def cleanup(cls):
        allUnconsumed = {}
        for key, hook in cls.all.items():
            setattr(hook.class_, hook.name, hook.original)
            unconsumed = hook.state.cleanup()
            if unconsumed:
                allUnconsumed[key] = unconsumed
            hook.unHook()
        cls.registeredClasses = set()
        cls.all = {}
        if allUnconsumed:
            raise UnconsumedCalls(allUnconsumed)



hook = HookedCall.hook
cleanup = HookedCall.cleanup
register = HookedCall.register


def decoder(method):
    """
    Mark a method as decoder when it is hooked.
    """
    method.__carly__decoder__ = True
    return method
