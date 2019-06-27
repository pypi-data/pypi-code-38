import collections
import copy
import functools
import typing


AccessorType = typing.Callable[[typing.Any], typing.Any]


class Recorder:
    # TODO: make changes resilient... what happens if underlying object changes and recorder can't be applied?
    # TODO: thread safety

    def __init__(self, object, accessor_fn: AccessorType=None, logger=None):
        self.__object = object
        self.__accessor_fn = accessor_fn if accessor_fn else lambda x: x  # type: AccessorType
        self.__logger = logger if logger is not None else list()
        self.__property_changed_event_listener = object.property_changed_event.listen(self.__property_changed)
        self.__item_set_event_listener = object.item_set_event.listen(self.__item_set)
        self.__item_cleared_event_listener = object.item_cleared_event.listen(self.__item_cleared)
        self.__item_inserted_event_listener = object.item_inserted_event.listen(self.__item_inserted)
        self.__item_removed_event_listener = object.item_removed_event.listen(self.__item_removed)
        self.__item_recorders = dict()
        self.__relationship_recorders = collections.defaultdict(list)
        for key in object.item_names:
            item = getattr(object, key)
            if item:
                def item_accessor(key, x):
                    return getattr(self.__accessor_fn(x), key)
                self.__item_recorders[key] = Recorder(item, functools.partial(item_accessor, key), self.__logger)
        for key in object.relationship_names:
            items = getattr(object, key)
            for index, item in enumerate(items):
                def item_accessor(key, index, x):
                    return getattr(self.__accessor_fn(x), key)[index]
                self.__relationship_recorders[key].append(Recorder(item, functools.partial(item_accessor, key, index), self.__logger))

    def close(self):
        self.__property_changed_event_listener.close()
        self.__property_changed_event_listener = None
        self.__item_set_event_listener.close()
        self.__item_set_event_listener = None
        self.__item_cleared_event_listener.close()
        self.__item_cleared_event_listener = None
        self.__item_inserted_event_listener.close()
        self.__item_inserted_event_listener = None
        self.__item_removed_event_listener.close()
        self.__item_removed_event_listener = None
        for key, item_recorder in self.__item_recorders.items():
            item_recorder.close()
        self.__item_recorders = None
        for key, relationship_recorder_list in self.__relationship_recorders.items():
            for relationship_recorder in self.__relationship_recorders[key]:
                relationship_recorder.close()
        self.__relationship_recorders = None

    def apply(self, object):
        for logger_item in self.__logger:
            logger_item(object)

    @property
    def _accessor_fn(self) -> AccessorType:
        return self._accessor_fn

    @_accessor_fn.setter
    def _accessor_fn(self, value: AccessorType) -> None:
        self._accessor_fn = value

    def __property_changed(self, key):
        if self.__object._is_persistent_property_recordable(key):
            def property_setter(x):
                setattr(self.__accessor_fn(x), key, getattr(self.__object, key))
            # print("set property {} {}".format(key, value))
            self.__logger.append(property_setter)

    def __item_set(self, key, item):
        item_recorder = self.__item_recorders.pop(key)
        if item_recorder:
            item_recorder.close()
        item = getattr(self.__accessor_fn(), key)
        if item:
            self.__item_recorders[key] = Recorder(item, lambda x: getattr(self.__accessor_fn(x), key), self.__logger)
        # print("set {} {}".format(key, item))
        self.__logger.append(lambda x: setattr(self.__accessor_fn(x), key, item))

    def __item_cleared(self, key):
        self.__item_set(key, None)

    def __item_inserted(self, key, value, before_index):
        for index, relationship_recorder in enumerate(self.__relationship_recorders[key]):
            if index >= before_index:
                relationship_recorder._accessor_fn = lambda x: getattr(self.__accessor_fn(x), key)[index + 1]
        self.__relationship_recorders[key].insert(before_index, Recorder(value, lambda x: getattr(self.__accessor_fn(x), key)[before_index], self.__logger))
        # print("append {} {} {}".format(key, value, before_index))
        self.__logger.append(lambda x: self.__accessor_fn(x).insert_item(key, before_index, copy.deepcopy(value)))

    def __item_removed(self, key, value, item_index):
        for index, relationship_recorder in enumerate(self.__relationship_recorders[key]):
            if index > item_index:
                relationship_recorder._accessor_fn = lambda x: getattr(self.__accessor_fn(x), key)[index - 1]
        self.__relationship_recorders[key].pop(item_index).close()
        # print("remove {} {} {}".format(key, value, item_index))
        self.__logger.append(lambda x: self.__accessor_fn(x).remove_item(key, getattr(self.__accessor_fn(x), key)[item_index]))
