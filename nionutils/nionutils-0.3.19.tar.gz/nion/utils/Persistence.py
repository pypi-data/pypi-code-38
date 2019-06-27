"""
A collection of persistence classes.
"""

# standard libraries
import copy
import datetime
import logging
import re
import uuid
import weakref


# third party libraries
# None

# local libraries
from nion.utils import Event


class PersistentProperty:

    """
        Represents a persistent property.

        converter converts from value to json value
    """

    def __init__(self, name, value=None, make=None, read_only=False, hidden=False, recordable=True, validate=None, converter=None, changed=None, key=None, reader=None, writer=None):
        super(PersistentProperty, self).__init__()
        self.name = name
        self.key = key if key else name
        self.value = value
        self.make = make
        self.read_only = read_only
        self.hidden = hidden
        self.recordable = recordable
        self.validate = validate
        self.converter = converter
        self.reader = reader
        self.writer = writer
        self.convert_get_fn = converter.convert if converter else copy.deepcopy  # optimization
        self.convert_set_fn = converter.convert_back if converter else lambda value: value  # optimization
        self.changed = changed

    def set_value(self, value):
        if self.validate:
            value = self.validate(value)
        else:
            value = copy.deepcopy(value)
        self.value = value
        if self.changed:
            self.changed(self.name, value)

    @property
    def json_value(self):
        return self.convert_get_fn(self.value)

    @json_value.setter
    def json_value(self, json_value):
        self.set_value(self.convert_set_fn(json_value))

    def read_from_dict(self, properties):
        if self.reader:
            value = self.reader(self, properties)
            if value is not None:
                self.set_value(value)
        else:
            if self.key in properties:
                if self.make:
                    value = self.make()
                    value.read_dict(properties[self.key])
                    self.set_value(value)
                else:
                    self.json_value = properties[self.key]

    def write_to_dict(self, properties):
        if self.writer:
            self.writer(self, properties, self.value)
        else:
            if self.make:
                value = self.value
                if value is not None:
                    value_dict = value.write_dict()
                    properties[self.key] = value_dict
                else:
                    properties.pop(self.key, None)  # remove key
            else:
                value = self.json_value
                if value is not None:
                    properties[self.key] = value
                else:
                    properties.pop(self.key, None)  # remove key


class PersistentPropertySpecial(PersistentProperty):

    def __init__(self, name, value=None, make=None, read_only=False, hidden=False, recordable=True, validate=None, converter=None, changed=None, key=None, reader=None, writer=None):
        super().__init__(name, value, make, read_only, hidden, recordable, validate, converter, changed, key, reader, writer)
        self.__value = value

    @property
    def value(self):
        return copy.deepcopy(self.__value)

    @value.setter
    def value(self, value):
        self.__value = value


class PersistentItem:

    def __init__(self, name, factory, item_changed=None, hidden=False):
        super(PersistentItem, self).__init__()
        self.name = name
        self.factory = factory
        self.item_changed = item_changed
        self.hidden = hidden
        self.value = None


class PersistentRelationship:

    def __init__(self, name, factory, insert=None, remove=None, key=None):
        super().__init__()
        self.name = name
        self.factory = factory
        self.insert = insert
        self.remove = remove
        self.key = key
        self.values = list()

    @property
    def storage_key(self):
        return self.key if self.key else self.name


class PersistentObjectContext:
    """Manages a collection of persistent objects.

    When a subclass makes a change which it wants to make persistent, it calls one of the following methods to
    facilitate the persistence:

        item_inserted(self, parent, name, before_index, item)
        item_removed(self, parent, name, item_index, item)
        item_set(self, parent, name, item)
        property_changed(self, object, name, value)
        clear_property(self, object, name)

    Each top level persistent object must be associated with persistent storage handler. Objects that are added to
    the context as an item or as part of a relationship will inherit the persistent storage handler of their parent.

    The persistent storage handler must implement the persistent storage interface:

        properties
        set_property(object, name value)
        clear_property(object, name)
        insert_item(parent, name, before_index, item)
        remove_item(parent, name, item_index, item)
        set_item(parent, name, item)
        set_value(object, name, value)

    Subclasses of this class may have additional requirements for persistent storage.

    All objects participating in the document model should register and unregister themselves with this context.
    This occurs automatically for PersistentObjects when setting the persistent_object_context property.

    Other objects can then subscribe and unsubscribe to know when a particular object (identified by uuid) becomes
    available or unavailable. This facilitates lazy connections between objects.
    """

    def __init__(self):
        self.__subscriptions = dict()
        self.__objects = dict()
        self.__persistent_storages = dict()
        self.registration_event = Event.Event()

    def register(self, object):
        """
            Register an object with the persistent object context.

            :param object: an object with a uuid property
        """
        object_uuid = object.uuid
        weak_object = weakref.ref(object)
        self.__objects[object_uuid] = weak_object
        for registered, unregistered in self.__subscriptions.get(object_uuid, list()):
            if registered:
                registered(object)
        self.registration_event.fire(object, None)

    def unregister(self, object):
        """
            Unregister an object with the persistent object context.

            :param object: an object with a uuid property
        """
        object_uuid = object.uuid
        weak_object = self.__objects.get(object_uuid)
        object = weak_object() if weak_object else None
        for registered, unregistered in self.__subscriptions.get(object_uuid, list()):
            if unregistered:
                unregistered(object)
        self.registration_event.fire(None, object)
        del self.__objects[object_uuid]
        self.__subscriptions.pop(object_uuid, None)  # delete if it exists

    def get_registered_object(self, object_uuid):
        weak_object = self.__objects.get(object_uuid)
        return weak_object and weak_object()

    def subscribe(self, object_uuid, registered, unregistered):
        """
            Subscribe to a particular object being registered or unregistered.

            :param object_uuid: the uuid of the object to subscribe to
            :param registered: a function taking one parameter (the object) to be called when the object gets registered
            :param unregistered: a function taking one parameter (the object) to be called when the object gets unregistered

            If the object is already registered, registered will be invoked immediately.
        """
        self.__subscriptions.setdefault(object_uuid, list()).append((registered, unregistered))
        weak_object = self.__objects.get(object_uuid)
        object = weak_object and weak_object()
        if object is not None:
            registered(object)

    def _set_persistent_storage_for_object(self, object, persistent_storage):
        """ Set the persistent storage object associated with the object. """
        if persistent_storage:
            def remove_object(weak_object):
                del self.__persistent_storages[weak_object]
            weak_object = weakref.ref(object, remove_object)
            self.__persistent_storages[weak_object] = persistent_storage
        else:
            weak_object = weakref.ref(object)
            del self.__persistent_storages[weak_object]

    def _get_persistent_storage_for_object(self, object):
        """ Return the persistent storage object associated with the object. """
        weak_object = weakref.ref(object)
        if weak_object in self.__persistent_storages:
            return self.__persistent_storages[weak_object]
        persistent_object_parent = object.persistent_object_parent
        if persistent_object_parent:
            return self._get_persistent_storage_for_object(persistent_object_parent.parent)
        return None

    def get_properties(self, object):
        """ Return a copy of the properties for the object as a dict. """
        persistent_storage = self._get_persistent_storage_for_object(object)
        # TODO: future versions will only support get_properties
        return copy.deepcopy(persistent_storage.get_properties(object) if hasattr(persistent_storage, "get_properties") else persistent_storage.properties)

    def item_inserted(self, parent, name, before_index, item):
        """ Call this to notify this context that the item before before_index has just been inserted into the parent in
        the relationship with the given name. """
        persistent_storage = self._get_persistent_storage_for_object(parent)
        persistent_storage.insert_item(parent, name, before_index, item)

    def item_removed(self, parent, name, item_index, item):
        """ Call this to notify this context that the item at item_index has been removed from the parent in the
        relationship with the given name. """
        persistent_storage = self._get_persistent_storage_for_object(parent)
        persistent_storage.remove_item(parent, name, item_index, item)

    def item_set(self, parent, name, item):
        """ Call this to notify this context that an item with name has been set on the parent. """
        persistent_storage = self._get_persistent_storage_for_object(parent)
        persistent_storage.set_item(parent, name, item)

    def property_changed(self, object, name, value):
        """ Call this to notify this context that a property with name has changed to value on object. """
        persistent_storage = self._get_persistent_storage_for_object(object)
        persistent_storage.set_property(object, name, value)

    def clear_property(self, object, name):
        """ Call this to notify this context that a property with name has been removed on object. """
        persistent_storage = self._get_persistent_storage_for_object(object)
        persistent_storage.clear_property(object, name)

    def read_external_data(self, item, name):
        """ Call this to notify read external data with name from an item in persistent storage. """
        persistent_storage = self._get_persistent_storage_for_object(item)
        return persistent_storage.read_external_data(item, name)

    def write_external_data(self, item, name, value) -> None:
        """ Call this to notify write external data value with name to an item in persistent storage. """
        persistent_storage = self._get_persistent_storage_for_object(item)
        persistent_storage.write_external_data(item, name, value)

    def enter_write_delay(self, object) -> None:
        """ Call this to notify this context that the object should be write delayed. """
        persistent_storage = self._get_persistent_storage_for_object(object)
        persistent_storage.enter_write_delay(object)

    def exit_write_delay(self, object) -> None:
        """ Call this to notify this context that the object should no longer be write delayed. """
        persistent_storage = self._get_persistent_storage_for_object(object)
        persistent_storage.exit_write_delay(object)

    def is_write_delayed(self, object) -> bool:
        """ Call this to notify determine if the object is currently write delayed. """
        persistent_storage = self._get_persistent_storage_for_object(object)
        return persistent_storage.is_write_delayed(object)

    def rewrite_item(self, item) -> None:
        """ Call this to write an item that was write delayed. """
        persistent_storage = self._get_persistent_storage_for_object(item)
        persistent_storage.rewrite_item(item)

    def get_storage_property(self, item, name):
        """ Call this to get a storage property with name of the item. """
        persistent_storage = self._get_persistent_storage_for_object(item)
        return persistent_storage.get_storage_property(item, name)


class PersistentObjectParent:
    """ Track the parent of a persistent object. """

    def __init__(self, parent, relationship_name=None, item_name=None):
        self.__weak_parent = weakref.ref(parent)
        self.relationship_name = relationship_name
        self.item_name = item_name

    @property
    def parent(self):
        return self.__weak_parent()


class PersistentObject:
    """
        Base class for objects being stored in a PersistentObjectContext.

        Subclasses can define properties, items, and relationships. Changes to those items will
        be persisted to the PersistentObjectContext.

        Keeps track of modified field automatically.

        Properties are single values, items are a one-to-one between objects, relationships are
        one-to-many between objects.

        Properties can have validators, converters, change notifications, and more.
        They are created using the define_property method.

        Items have set notifications and more. They are created using the
        define_item method.

        Relationships have change notifications and more. They are created using
        the define_relationship method.

        Subclasses can set the uuid after init. It should not be changed at other times.

        The persistent_object_context property must be set explicitly for top level objects of the
        PersistentObjectContext. Objects contained in the items and relationships will be have their
        persistent_object_context managed when they are inserted into or removed from another persistent object.

        It is an error to add an object as an item or relationship more than once. Items can be
        removed and added again, though.

        Objects must be able to read from and write themselves to a dict.

        The persistent_object_context property will be valid after (but not during) reading.

        After reading, an object may immediately update itself to a newer version using the persistent object
        context.
    """

    def __init__(self):
        super(PersistentObject, self).__init__()
        self.__type = None
        self.__properties = dict()
        self.__items = dict()
        self.__relationships = dict()
        self._is_reading = False
        self.__persistent_object_context = None
        # uuid as a property is too slow, so make it direct
        self.uuid = uuid.uuid4()
        self.__modified_count = 0
        self.modified_state = 0
        self.__modified = datetime.datetime.utcnow()
        self.persistent_object_parent = None

    def __deepcopy__(self, memo):
        deepcopy = self.__class__()
        deepcopy.deepcopy_from(self, memo)
        memo[id(self)] = deepcopy
        return deepcopy

    def deepcopy_from(self, item, memo):
        for key in self.__properties.keys():
            value = item._get_persistent_property_value(key)
            new_value = copy.deepcopy(value)
            self._set_persistent_property_value(key, new_value)
        for key in self.__items.keys():
            self.set_item(key, copy.deepcopy(getattr(item, key)))
        for key in self.__relationships.keys():
            for child_item in getattr(item, key):
                self.append_item(key, copy.deepcopy(child_item, memo))

    def persistent_object_context_changed(self):
        """ Subclasses can override this to be notified when the persistent object context changes. """
        pass

    @property
    def persistent_object_context(self):
        """ Return the persistent object context. """
        return self.__persistent_object_context

    @persistent_object_context.setter
    def persistent_object_context(self, persistent_object_context):
        """ Set the persistent object context and propagate it to contained objects. """
        assert self.__persistent_object_context is None or persistent_object_context is None  # make sure persistent object context is handled cleanly
        old_persistent_object_context = self.__persistent_object_context
        self.__persistent_object_context = persistent_object_context
        for item_name in self.__items.keys():
            item_value = self.__items[item_name].value
            if item_value:
                item_value.persistent_object_context = persistent_object_context
        for relationship_name in self.__relationships.keys():
            for item in self.__relationships[relationship_name].values:
                item.persistent_object_context = persistent_object_context
        if old_persistent_object_context:
            old_persistent_object_context.unregister(self)
        if persistent_object_context:
            persistent_object_context.register(self)
        self.persistent_object_context_changed()

    def get_accessor_in_parent(self):
        persistent_object_parent = self.persistent_object_parent
        assert persistent_object_parent
        if persistent_object_parent.item_name:
            return lambda storage_dict: storage_dict.get(persistent_object_parent.item_name, dict())
        if persistent_object_parent.relationship_name:
            index = getattr(persistent_object_parent.parent, persistent_object_parent.relationship_name).index(self)
            return lambda storage_dict: storage_dict[persistent_object_parent.relationship_name][index]
        return None

    def define_type(self, type):
        self.__type = type

    def define_property(self, name: str, value=None, make=None, read_only: bool=False, hidden: bool=False, recordable: bool=True, copy_on_read: bool=False, validate=None, converter=None, changed=None, key=None, reader=None, writer=None):
        """ key is what is stored on disk; name is what is used when accessing the property from code. """
        if copy_on_read:
            self.__properties[name] = PersistentPropertySpecial(name, value, make, read_only, hidden, recordable, validate, converter, changed, key, reader, writer)
        else:
            self.__properties[name] = PersistentProperty(name, value, make, read_only, hidden, recordable, validate, converter, changed, key, reader, writer)

    def define_item(self, name, factory, item_changed=None, hidden=False):
        self.__items[name] = PersistentItem(name, factory, item_changed, hidden)

    def define_relationship(self, name, factory, insert=None, remove=None, key=None):
        self.__relationships[name] = PersistentRelationship(name, factory, insert, remove, key)

    def undefine_properties(self):
        self.__properties.clear()

    def undefine_items(self):
        self.__items.clear()

    def undefine_relationships(self):
        self.__relationships.clear()

    @property
    def property_names(self):
        return list(self.__properties.keys())

    @property
    def key_names(self):
        return [property.key for property in self.__properties.values()]

    @property
    def type(self):
        return self.__type

    @property
    def modified(self):
        return self.__modified

    @property
    def modified_count(self):
        return self.__modified_count

    def _set_modified(self, modified):
        # for testing
        self.__update_modified(modified)
        if self.persistent_object_context:
            self.persistent_object_context.property_changed(self, "uuid", str(self.uuid))  # dummy write

    @property
    def item_names(self):
        return list(self.__items.keys())

    @property
    def relationship_names(self):
        return list(self.__relationships.keys())

    def begin_reading(self):
        self._is_reading = True

    def read_from_dict(self, properties):
        """ Read from a dict. """
        # uuid is handled specially for performance reasons
        if "uuid" in properties:
            self.uuid = uuid.UUID(properties["uuid"])
            if self.persistent_object_context:
                self.persistent_object_context.register(self)
        if "modified" in properties:
            self.__modified = datetime.datetime(*list(map(int, re.split('[^\d]', properties["modified"]))))
        # iterate the defined properties
        for key in self.__properties.keys():
            property = self.__properties[key]
            property.read_from_dict(properties)
        for key in self.__items.keys():
            item_dict = properties.get(key)
            if item_dict:
                factory = self.__items[key].factory
                # the object has not been constructed yet, but we needs its
                # type or id to construct it. so we need to look it up by key/index/name.
                # to minimize the interface to the factory methods, just pass a closure
                # which looks up by name.
                def lookup_id(name, default=None):
                    return item_dict.get(name, default)
                item = factory(lookup_id)
                if item is None:
                    logging.debug("Unable to read %s", key)
                assert item is not None
                # read the item from the dict
                item.begin_reading()
                item.read_from_dict(item_dict)
                self.__set_item(key, item)
        for key in self.__relationships.keys():
            storage_key = self.__relationships[key].storage_key
            for item_dict in properties.get(storage_key, list()):
                factory = self.__relationships[key].factory
                # the object has not been constructed yet, but we needs its
                # type or id to construct it. so we need to look it up by key/index/name.
                # to minimize the interface to the factory methods, just pass a closure
                # which looks up by name.
                def lookup_id(name, default=None):
                    return item_dict.get(name, default)
                item = factory(lookup_id)
                if item is None:
                    logging.debug("Unable to read %s", key)
                assert item is not None
                # read the item from the dict
                item.begin_reading()
                item.read_from_dict(item_dict)
                # insert it into the relationship dict
                self.__insert_item(key, len(self.__relationships[key].values), item)

    def finish_reading(self):
        for key in self.__items.keys():
            item = self.__items[key].value
            if item:
                item.finish_reading()
        for key in self.__relationships.keys():
            for item in self.__relationships[key].values:
                item.finish_reading()
        self._is_reading = False

    def write_to_dict(self):
        """ Write the object to a dict and return it. """
        properties = dict()
        if self.__type:
            properties["type"] = self.__type
        properties["uuid"] = str(self.uuid)
        for key in self.__properties.keys():
            property = self.__properties[key]
            property.write_to_dict(properties)
        for key in self.__items.keys():
            item = self.__items[key].value
            if item:
                properties[key] = item.write_to_dict()
        for key in self.__relationships.keys():
            storage_key = self.__relationships[key].storage_key
            items_list = properties.setdefault(storage_key, list())
            for item in self.__relationships[key].values:
                items_list.append(item.write_to_dict())
        return properties

    def _update_persistent_object_context_property(self, name):
        """
            Update the property given by name in the persistent object context.

            Subclasses can override this to provide custom writing behavior, such
            as delaying write until an appropriate time for performance reasons.
        """
        property = self.__properties[name]
        if self.persistent_object_context:
            properties = dict()
            property.write_to_dict(properties)
            if properties:
                for property_key in properties:
                    self.persistent_object_context.property_changed(self, property_key, properties[property_key])
            else:
                self.persistent_object_context.clear_property(self, name)

    def __update_modified(self, modified):
        self.__modified_count += 1
        self.modified_state += 1
        self.__modified = modified
        parent = self.persistent_object_parent.parent if self.persistent_object_parent else None
        if parent:
            parent.__update_modified(modified)

    def _get_persistent_property(self, name):
        """ Subclasses can call this to get a property descriptor. """
        return self.__properties[name]

    def _get_persistent_property_value(self, name, default=None):
        """ Subclasses can call this to get a hidden property. """
        property = self.__properties.get(name)
        return property.value if property else default

    def _set_persistent_property_value(self, name, value):
        """ Subclasses can call this to set a hidden property. """
        property = self.__properties[name]
        property.set_value(value)
        self.__update_modified(datetime.datetime.utcnow())
        self._update_persistent_object_context_property(name)

    def _update_persistent_property(self, name: str, value) -> None:
        """ Subclasses can call this to notify that a custom property was updated. """
        self.__update_modified(datetime.datetime.utcnow())
        if self.persistent_object_context:
            self.persistent_object_context.property_changed(self, name, value)

    def _is_persistent_property_recordable(self, name) -> bool:
        property = self.__properties.get(name)
        return (property.recordable and not property.read_only) if (property is not None) else False

    def __getattr__(self, name):
        # Handle property objects that are not hidden.
        property = self.__properties.get(name)
        if property and not property.hidden:
            return property.value
        if name in self.__items and not self.__items[name].hidden:
            return self.__items[name].value
        if name in self.__relationships:
            return copy.copy(self.__relationships[name].values)
        raise AttributeError("%r object has no attribute %r" % (self.__class__, name))

    def __setattr__(self, name, value):
        # Check for private properties of this class
        if name.startswith("_PersistentObject__"):
            super(PersistentObject, self).__setattr__(name, value)
        # Otherwise check for defined properties.
        else:
            property = self.__properties.get(name)
            # if the property is hidden, fall through and give regular style property a chance to handle it
            if property and not property.hidden:
                # if the property is not hidden and it is read only, throw an exception
                if not property.read_only:
                    property.set_value(value)
                    self.__update_modified(datetime.datetime.utcnow())
                    self._update_persistent_object_context_property(name)
                else:
                    raise AttributeError()
            else:
                super(PersistentObject, self).__setattr__(name, value)

    def __set_item(self, name, value):
        """ Set item into item storage and notify. Does not set into persistent storage or update modified. Item can be None. """
        item = self.__items[name]
        old_value = item.value
        item.value = value
        if value:
            value.persistent_object_parent = PersistentObjectParent(self, item_name=name)
            value.persistent_object_context = self.persistent_object_context
        if item.item_changed:
            item.item_changed(name, old_value, value)

    def get_item(self, name):
        """ Get item from persistent storage. """
        item = self.__items[name]
        return item.value

    def set_item(self, name, value):
        """ Set item into persistent storage and then into item storage and notify. """
        item = self.__items[name]
        old_value = item.value
        item.value = value
        self.__update_modified(datetime.datetime.utcnow())
        if value:
            value.persistent_object_parent = PersistentObjectParent(self, item_name=name)
        # the persistent_object_parent and item need to be established before
        # calling item_changed.
        if self.persistent_object_context:
            self.persistent_object_context.item_set(self, name, value)  # this will also update item's persistent_object_context
        if item.item_changed:
            item.item_changed(name, old_value, value)

    def __insert_item(self, name, before_index, item):
        """ Insert item into relationship storage and notify. Does not insert in persistent storage or update modified. """
        relationship = self.__relationships[name]
        relationship.values.insert(before_index, item)
        item.persistent_object_parent = PersistentObjectParent(self, relationship_name=name)
        item.persistent_object_context = self.persistent_object_context
        if relationship.insert:
            relationship.insert(name, before_index, item)

    def insert_item(self, name, before_index, item):
        """ Insert item in persistent storage and then into relationship storage and notify. """
        relationship = self.__relationships[name]
        relationship.values.insert(before_index, item)
        self.__update_modified(datetime.datetime.utcnow())
        item.persistent_object_parent = PersistentObjectParent(self, relationship_name=name)
        # the persistent_object_parent and relationship need to be established before
        # calling item_inserted.
        if self.persistent_object_context:
            self.persistent_object_context.item_inserted(self, name, before_index, item)  # this will also update item's persistent_object_context
        if relationship.insert:
            relationship.insert(name, before_index, item)

    def append_item(self, name, item):
        """ Append item and append to persistent storage. """
        self.insert_item(name, len(self.__relationships[name].values), item)

    def remove_item(self, name, item):
        """ Remove item and remove from persistent storage. """
        relationship = self.__relationships[name]
        item_index = relationship.values.index(item)
        relationship.values.remove(item)
        self.__update_modified(datetime.datetime.utcnow())
        if relationship.remove:
            relationship.remove(name, item_index, item)
        item.persistent_object_context = None
        if self.persistent_object_context:
            self.persistent_object_context.item_removed(self, name, item_index, item)  # this will also update item's persistent_object_context
        item.persistent_object_parent = None

    def extend_items(self, name, items):
        """ Append multiple items and add to persistent storage. """
        for item in items:
            self.append_item(name, item)

    def item_count(self, name: str) -> int:
        """Return the count of items in the relationship specified by name."""
        relationship = self.__relationships[name]
        return len(relationship.values)

    def item_index(self, name: str, item: object) -> int:
        """Return the index of item within the relationship specified by name."""
        relationship = self.__relationships[name]
        return relationship.values.index(item)
