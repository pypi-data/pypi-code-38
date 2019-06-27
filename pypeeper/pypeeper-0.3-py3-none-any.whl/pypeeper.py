import re


def _get_property_getter(attribute_name):
    def property_getter(self):
        return getattr(self, attribute_name)

    return property_getter


def _get_property_setter(attribute_name, notify_objects):

    def property_setter(self, value):
        if getattr(self, attribute_name) is not value:
            for notify_object in notify_objects:
                notify_object(
                    self,
                    id(self),
                    attribute_name.strip('__'),
                    getattr(self, attribute_name),
                    value
                )
            setattr(self, attribute_name, value)

    return property_setter


def _create_properties(instance, cls, notify_objects):

    for attr_name in filter(
            lambda x: re.match(instance.pattern, x), instance.__dict__
    ):
        getter = property(_get_property_getter('__' + attr_name))
        setattr(cls, attr_name, getter)
        setter = getter.setter(
            _get_property_setter('__' + attr_name, notify_objects)
        )
        setattr(cls, attr_name, setter)


def _get_setattr_method(cls):

    def set_attr_method(self, key, value):

        if key not in self._modifiers and re.match(self.pattern, key):
            super(cls, self).__setattr__('__' + key, value)
            self._modifiers.add(key)
            self._modifiers.add('__' + key)
        else:
            super(cls, self).__setattr__(key, value)

    return set_attr_method


def _get_class_copy(cls):
    return type(cls.__name__, cls.__bases__, dict(cls.__dict__))


class ObservablesFactory(type):
    _notify_methods = []

    def __call__(cls, *args, **kwargs):

        if issubclass(cls, Observable):
            cls_clone = _get_class_copy(cls)
            cls_clone._modifiers = set()
            instance = super(ObservablesFactory, cls).__call__(*args, **kwargs)
            _create_properties(instance, cls_clone, cls._notify_methods)
            cls_clone.__setattr__ = _get_setattr_method(cls_clone)
            new_instance = super(ObservablesFactory, cls_clone).__call__(
                *args, **kwargs
            )

            return new_instance

        else:
            instance = super(ObservablesFactory, cls).__call__(*args, **kwargs)
            cls._notify_methods.append(instance.notify)
            return instance


class Observable(metaclass=ObservablesFactory):
    pattern = r'.*'


class Observer(metaclass=ObservablesFactory):

    def notify(self, class_name, object_id, attribute_name, old, new):
        pass
