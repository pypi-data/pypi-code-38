from types import TupleType

class Serializer(object):
    """
    Usage:
        attrs = ['attr_or_function', ('attr_or_function', [args], {kwargs}),]
        Serializer(obj).get_dict(attrs)
    """

    def __init__(self, obj):
        self.obj = obj

    def get_dict(self, attrs):
        data_dict = {}

        for attr in attrs:
            args = []
            kwargs = {}

            # get args or kwargs
            if type(attr) == TupleType:
                try:
                    args = attr[1]
                except IndexError:
                    pass

                try:
                    kwargs = attr[2]
                except IndexError:
                    pass

                attr = attr[0]

            # get serializer
            method_name = "get_%s" % attr
            if hasattr(self, method_name):
                value = getattr(self, method_name)
                value = value(*args, **kwargs)

            else:
                value = getattr(self.obj, attr)

                # call methods
                if callable(value):
                    value = value(*args, **kwargs)

            data_dict[attr] = value

        return data_dict
