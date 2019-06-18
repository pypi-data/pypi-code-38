# coding: utf-8

"""This is the core for managing extensions and plugings for the
:class:`~deployv.base.commandv.CommandV` class.

All of the events handlers must inherit from
:class:`~deployv.base.extensions_core.EventListenerBase`.
"""

from functools import wraps
import abc
import glob
import imp
import inspect
import logging
import os
import six
import extend_me


logger = logging.getLogger(__name__)  # pylint: disable=C0103
EVENTLISTENER_META = extend_me.ExtensibleByHashType._('EventListener', hashattr='name')


def load_extensions():
    """This module just loads all the extensions from the corresponding path.

    :returns: Loaded modules.
    :rtype: dict
    """
    modules = {}
    path = os.path.dirname(os.path.realpath(__file__))
    for path in glob.glob(os.path.join(path, '..', 'extensions/[!_]*.py')):
        name, ext = os.path.splitext(os.path.basename(path))
        modules[name] = imp.load_source(name, path)
    return modules


@six.add_metaclass(EVENTLISTENER_META)
class EventListenerBase(object):
    """This is the base class for all the events listener that will be developed in the base
    commands and new ones.

    All inherited classes must have a class Meta with the required information.

    There is a small example in :class:`~deployv.base.extensions_core.TestListener` with the basic
    information configured.
    """

    def __repr__(self):
        try:
            name = self.Meta.name
        except AttributeError:
            name = None

        if name is not None:
            return 'EventListener:%s' % name
        return super(EventListenerBase, self).__repr__()

    @property
    def event(self):

        try:
            event_name = self.Meta.event
        except AttributeError:
            event_name = None
        return event_name

    @property
    def name(self):

        try:
            _name = self.Meta.name
        except AttributeError:
            _name = None
        return _name

    @abc.abstractmethod
    def execute(self, *args, **kwargs):
        """The code that will be executed when the event is *fired* by the
        :class:`~deployv.base.extensions_core.EventManager` according to the event that the class
        registered using the *event* property of the Meta class.

        Check the example :class:`~deployv.base.extensions_core.TestListener` class for more info.

        :returns: The execution result.
        :rtype: dict
        """
        return


class TestListener(EventListenerBase):
    """Just an example plugin to test if plugin logic works.

    Must inherit from :class:`~deployv.base.extensions_core.EventListenerBase`.
    """

    class Meta:  # pylint: disable=C1001
        """This is a test event and the information associated with it.

        The event name and the event listener name that you want to associate with the object (very
        useful for logging and debugging).

        The event name **must** be in the format "before.method.event" or "after.method.event",
        otherwise it won't be executed at all.
        """
        name = 'ListenerName'
        event = 'before.test.event'

    def execute(self, obj):
        logger.debug("Running the event %s", self.Meta.event)


class Singleton(type):

    def __init__(cls, name, bases, p_dict):
        super(Singleton, cls).__init__(name, bases, p_dict)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            cls.instance = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance


@six.add_metaclass(Singleton)
class EventManager(object):

    def __init__(self):
        self.__listeners = {}

    def __getitem__(self, name):
        listener = self.__listeners.get(name, False)
        if listener is False:
            try:
                event_cls = type(EventListenerBase).get_class(name)
            except ValueError as error:
                raise KeyError(str(error))

            listener = event_cls()  # pylint: disable=E1102
            self.__listeners[name] = listener
        return listener

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __contains__(self, name):
        return name in self.registered_listeners

    def __dir__(self):
        res = dir(super(EventManager, self))
        res.extend(self.registered_listeners)
        return res

    def fire_event(self, event_name, obj, returned_value=None):
        logger.debug('Firing event %s', event_name)
        res = list()
        for listener in self.registered_listeners:
            if self[listener].event == event_name:
                listener_instance = self[listener]
                logger.debug('Event handler %s', listener_instance.name)
                if event_name.startswith('after.'):
                    lres = listener_instance.execute(obj, returned_value)
                else:
                    lres = listener_instance.execute(obj)
                res.append({listener_instance.name: lres})
        return res

    @property
    def registered_listeners(self):
        return type(EventListenerBase).get_registered_names()

    def refresh(self):
        self.__listeners = {}
        return self


def events(function):
    event_manager = EventManager()

    @wraps(function)
    def process_events(*args, **kwargs):
        args_map = {}
        if args or kwargs:
            args_map = inspect.getcallargs(function, *args, **kwargs)
        if 'self' in args_map:
            obj = args_map['self']
        logger.debug('Executing before.events for %s ', function.__name__)
        pre_event = event_manager.fire_event(
            'before.{}.event'.format(function.__name__), obj)
        res = function(*args, **kwargs)
        logger.debug('Executing after.events for %s ', function.__name__)
        post_event = event_manager.fire_event(
            'after.{}.event'.format(function.__name__), obj, res)
        if pre_event:
            res.update({'before': pre_event})
        if post_event:
            res.update({'after': post_event})
        return res
    return process_events
