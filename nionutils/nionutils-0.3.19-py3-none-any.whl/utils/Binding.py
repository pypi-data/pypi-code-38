"""
    Binding classes.
"""

# standard libraries
# none

# types
from typing import Any, Callable, Sequence

# third party libraries
# none

# local libraries
# none


class Binding:
    """Binding between two objects.

    Binds two objects, a source and target, together. Typically, the model object would
    be the source and the UI object would be the target. Also facilitates a converter
    object between the source and target to convert between value types. Observes the
    source object for changes.

    Bindings can be one way (from source to target) or two way (from source to target
    and back). The converter object, if used, must always supply a convert method. If
    this binding is two way, then it must also supply a convert_back method. The validator,
    if used, must supply a validate method (on the converted value and return a value).

    This class is not intended to be used directly. Instead, subclasses will implement
    specific source bindings by configuring the source_setter and source_getter methods
    and by using update_target appropriately.

    Clients of this class will set target_setter to directly connect the target, typically
    a UI element.

    The owner should call close on this object.

    Bindings are not sharable. They are meant to be used to bind one ui element to one
    value. However, conversions and binding sources can be shared between bindings in most
    cases.
    """

    def __init__(self, source, *, converter=None, validator=None, fallback=None):
        super().__init__()
        self.__source = None
        self.__converter = converter
        self.__validator = validator
        self.fallback = fallback
        self.source_getter = None
        self.source_setter = None
        self.target_setter = None
        self.__source = source
        self._closed = False

    # not thread safe
    def close(self):
        """Close the binding.

        Closes the binding. Subclasses can use this to perform any shutdown
        related actions. Not thread safe.
        """
        self.__source = None
        self._closed = True

    @property
    def source(self):
        """Return the source of the binding. Thread safe."""
        return self.__source

    @property
    def converter(self):
        """Return the converter (from source to target). Thread safe."""
        return self.__converter

    @property
    def validator(self):
        """Return the validator (of converted value). Thread safe."""
        return self.__validator

    # thread safe
    def __back_converted_value(self, target_value):
        """Return the back converted value (from target to source). Thread safe."""
        return self.__converter.convert_back(target_value) if self.__converter else target_value

    # thread safe
    def __converted_value(self, source_value):
        """Return the converted value (from source to target). Thread safe."""
        return self.__converter.convert(source_value) if self.__converter else source_value

    # thread safe
    def __validated_value(self, source_value):
        """Return the converted value (from source to target). Thread safe."""
        return self.__validator.validate(source_value) if self.__validator else source_value

    # public methods. subclasses must make sure these methods work as expected.

    # thread safe
    def update_source(self, target_value):
        """Update source with back converted target value.

        Update the source from the target value. The target value will be back converted.
        This is typically called by a target (UI element) to update the source (model).

        This method is required for two-way binding.

        Thread safe.
        """
        if self.source_setter:
            converted_value = self.__validated_value(self.__back_converted_value(target_value))
            self.source_setter(converted_value)

    # not thread safe
    def update_target(self, source_value):
        """Update target with converted source value.

        Call the target setter with the unconverted value from the source.
        This is typically called by subclasses to update the target (UI element)
        when the source (model) changes.

        Required for both one-way and two-way bindings. It uses update_target_direct
        to call the target setter.

        Not thread safe.
        """
        self.update_target_direct(self.__converted_value(source_value))

    # not thread safe
    def update_target_direct(self, converted_value):
        """Update target directly with converted value.

        Call the target setter with the already converted value.
        This is typically called by subclasses to handle target setting
        when the conversion is already done, for instance for implementing
        a fallback, default, or placeholder value.

        Required for both one-way and two-way bindings.

        Not thread safe.
        """
        if self.target_setter:
            self.target_setter(converted_value)

    # thread safe
    def get_target_value(self):
        """Return target value by converting source.

        Get the value from the source that will be set on the target.
        This is typically used by the target object to initialize its value.

        Required for both one-way and two-way bindings.

        Thread safe.
        """
        if self.source_getter:
            source = self.source_getter()
            if source is not None:
                return self.__converted_value(source)
        return self.fallback


class ListBinding(Binding):
    """One way binding from a source list to a target.

    Observes item inserted and item removed events on a source and if the event
    matches the key, calls the functions assigned to inserter and remover fields.

    Source list must support item_inserted_event and item_removed_event with the
    signatures:
        item_inserted(key: str, item: Any, before_index: int) -> None
        item_removed(key: str, item: Any, index: int) -> None

    Client should set the inserter and remover functions to callables with the
    signatures:
        inserter(item: Any, before_index: int) -> None
        remover(index: int) -> None.

    The owner should call close on this object.
    """

    def __init__(self, source, key: str):
        super().__init__(source)
        self.__key = key
        self.inserter = None  # type: Callable[[Any, int], None]
        self.remover = None  # type: Callable[[int], None]

        # thread safe
        def item_inserted(key_: str, item: Any, before_index: int) -> None:
            if key_ == self.__key and callable(self.inserter):
                self.inserter(item, before_index)

        # thread safe
        def item_removed(key_: str, item: Any, index: int) -> None:
            if key_ == self.__key and callable(self.remover):
                self.remover(index)

        self.__item_inserted_listener = source.item_inserted_event.listen(item_inserted)
        self.__item_removed_listener = source.item_removed_event.listen(item_removed)

    def close(self):
        self.__item_inserted_listener.close()
        self.__item_inserted_listener = None
        self.__item_removed_listener.close()
        self.__item_removed_listener = None
        super().close()

    @property
    def items(self) -> Sequence[Any]:
        """ Return the items of the list. Thread safe. """
        return getattr(self.source, self.__key)


class PropertyBinding(Binding):
    """Two way binding from a source property to a target.

    Observes property changed event on a source and if the event matches the
    property name, calls the functions assigned to target_setter field.

    Source must support property_changed_event with the signature:
        property_changed(property_name: str) -> None

    Source must also support get/set attribute for the given property_name.

    Client should set the target_setter function to a callable with the signature:
        target_setter(value: Any) -> None

    The owner should call close on this object.
    """

    # TODO: generalize to 'getter binding'
    # TODO: generalize to 'two way getter connection'

    def __init__(self, source, property_name: str, *, converter=None, validator=None, fallback=None):
        super().__init__(source, converter=converter, validator=validator, fallback=fallback)
        self.__property_name = property_name

        # thread safe
        def property_changed(property_name_: str) -> None:
            assert not self._closed
            if property_name_ == self.__property_name:
                value = getattr(source, property_name)
                if value is not None:
                    self.update_target(value)
                else:
                    self.update_target_direct(self.fallback)

        self.__property_changed_listener = source.property_changed_event.listen(property_changed)
        self.source_setter = lambda value: setattr(self.source, self.__property_name, value)
        self.source_getter = lambda: getattr(self.source, self.__property_name)

    def close(self):
        self.__property_changed_listener.close()
        self.__property_changed_listener = None
        super().close()


class PropertyAttributeBinding(Binding):
    """Two way binding from an attribute within a source property object to a target.

    Observes property changed event on a source and if the event matches the
    property name, calls the functions assigned to target_setter field.

    Source must support property_changed_event with the signature:
        property_changed(property_name: str) -> None

    Source must also support get/set attribute for the given property_name and it
    must return/take an object with an attribute matching attribute_name.

    Client should set the target_setter function to a callable with the signature:
        target_setter(value: Any) -> None

    The owner should call close on this object.
    """

    def __init__(self, source, property_name: str, attribute_name: str, converter=None, fallback=None, update_attribute_fn=None):
        super().__init__(source, converter=converter, fallback=fallback)
        self.__property_name = property_name
        self.__attribute_name = attribute_name

        # thread safe
        def property_changed(property_name_: str):
            if property_name_ == self.__property_name:
                # perform on the main thread
                value = getattr(source, property_name)
                if value is not None and hasattr(value, self.__attribute_name):
                    self.update_target(getattr(value, self.__attribute_name))
                else:
                    self.update_target_direct(self.fallback)

        self.__property_changed_listener = source.property_changed_event.listen(property_changed)

        def source_setter(value):  # pylint: disable=missing-docstring
            source_value = getattr(self.source, self.__property_name)
            if callable(update_attribute_fn):
                source_value = update_attribute_fn(source_value, self.__attribute_name, value)
            else:
                setattr(source_value, self.__attribute_name, value)
            setattr(self.source, self.__property_name, source_value)

        def source_getter():  # pylint: disable=missing-docstring
            source_value = getattr(self.source, self.__property_name)
            return getattr(source_value, self.__attribute_name) if source_value is not None and hasattr(source_value, self.__attribute_name) else None

        self.source_setter = source_setter
        self.source_getter = source_getter

    def close(self):
        self.__property_changed_listener.close()
        self.__property_changed_listener = None
        super().close()


class TuplePropertyBinding(Binding):
    """Two way binding from an element within a source property tuple to a target.

    Observes property changed event on a source and if the event matches the
    property name, calls the functions assigned to target_setter field.

    Source must support property_changed_event with the signature:
        property_changed(property_name: str) -> None

    Source must also support get/set attribute for the given property_name and it
    must return/take a tuple.

    Client should set the target_setter function to a callable with the signature:
        target_setter(value: Any) -> None

    The owner should call close on this object.
    """

    def __init__(self, source, property_name: str, tuple_index: int, converter=None, fallback=None):
        super().__init__(source, converter=converter, fallback=fallback)
        self.__property_name = property_name
        self.__tuple_index = tuple_index

        # thread safe
        def property_changed(property_name_: str):
            if property_name_ == self.__property_name:
                # perform on the main thread
                value = getattr(source, property_name)
                if value is not None and self.__tuple_index < len(value):
                    self.update_target(value[self.__tuple_index])
                else:
                    self.update_target_direct(self.fallback)

        self.__property_changed_listener = source.property_changed_event.listen(property_changed)

        def source_setter(value):  # pylint: disable=missing-docstring
            source_tuple = getattr(self.source, self.__property_name)
            tuple_as_list = list(source_tuple) if source_tuple is not None else list()
            while len(tuple_as_list) <= self.__tuple_index:
                tuple_as_list.append(None)
            tuple_as_list[self.__tuple_index] = value
            setattr(self.source, self.__property_name, tuple(tuple_as_list))

        def source_getter():  # pylint: disable=missing-docstring
            tuple_value = getattr(self.source, self.__property_name)
            return tuple_value[self.__tuple_index] if tuple_value is not None and self.__tuple_index < len(tuple_value) else None

        self.source_setter = source_setter
        self.source_getter = source_getter

    def close(self):
        self.__property_changed_listener.close()
        self.__property_changed_listener = None
        super().close()
