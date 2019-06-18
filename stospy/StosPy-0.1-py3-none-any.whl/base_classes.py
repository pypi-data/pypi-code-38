from logging import getLogger

from .runtime import runtime


logger = getLogger(__name__)

IGNORE_ATTRIBUTE_LIST = {
    "__class__",
}


class SwappableMetaClass(type):
    def __init__(cls, name, bases, namespace):
        if name == "SwappableObject":
            # Purely virtual
            super().__init__(name, bases, namespace)
            return

        runtime.backend.register_new_class(name, cls)
        super().__init__(name, bases, namespace)

    def __call__(cls, *args, **kwargs):
        """Perform the two-stage (__new__ + __init__) explicit initialization."""
        new_instance = cls.__new__(cls, *args, **kwargs)
        runtime.backend.register_new_instance(new_instance)

        # Typically, we want the __init__ **after** registering the instance,
        # given that the __init__ may use setters and/or getters
        new_instance.__init__(*args, **kwargs)
        return new_instance


class SwappableObject(metaclass=SwappableMetaClass):
    def __getattribute__(self, item):
        if item in IGNORE_ATTRIBUTE_LIST:
            return super().__getattribute__(item)
        logger.debug("Getter for attribute `%s` on object %r", item, self)
        return runtime.backend.get_attribute_for_instance(self, item)

    def __setattr__(self, item, value):
        if item in IGNORE_ATTRIBUTE_LIST:
            super().__setattr__(item, value)
            return
        logger.debug("Setter for attribute `%s` on object %r", item, self)
        runtime.backend.set_attr_for_instance(self, item, value)

    def __del__(self):
        logger.debug("Deleting object %r", self)
        runtime.backend.free_instance(self)
