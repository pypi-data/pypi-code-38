import inspect

from dictutils import OrderedAttrDict


class Registry(OrderedAttrDict):
    def register_decorator(self, **kwargs):
        name = kwargs.get("name")

        def decorator(decorated):
            self.register_func(data=decorated, name=name)
            return decorated

        return decorator

    def register(self, data=None, name=None, **kwargs):
        if data is None:
            return self.register_decorator(data=data, name=name, **kwargs)
        else:
            self.register_func(data=data, name=name, **kwargs)
            return data

    def get_object_name(self, data):
        """
            Return a name from an element (object, class, function...)
        """
        if callable(data):
            return data.__name__

        elif inspect.isclass(data):
            return data.__class__.__name__

        else:
            raise ValueError(
                "Cannot deduce name from given object ({}). Please user registry.register() with a 'name' argument.".format(
                    data
                )
            )

    def validate(self, data):
        """
            Called before registering a new value into the registry
            Override this method if you want to restrict what type of data cna be registered
        """
        return True

    def register_func(self, data, name=None, **kwargs):
        """
            Register abritrary data into the registry
        """
        if self.validate(data):
            name = name or self.get_object_name(data)
            self[name] = data
        else:
            raise ValueError(
                "{0} (type: {0.__class__}) is not a valid value for {1} registry".format(
                    data, self.__class__
                )
            )
