import os
import six
import json


class ConfigurationSchemeMetaClass(type):
    def __init__(cls, name, bases, dct):
        super(ConfigurationSchemeMetaClass, cls).__init__(name, bases, dct)

    def __setattr__(self, key, value):
        if key not in type.__getattribute__(self, '__dict__'):
            raise AttributeError("Attribute does not exists in scheme!", key)
        else :
            type.__setattr__(self, key, value)


@six.add_metaclass(ConfigurationSchemeMetaClass)
class ConfigurationScheme(object):
    pass


class ConfigurationValues(object):
    pass


class ConfigManager(object):

    def __init__(self, container):
        self.container = container

    def load_dictionary(self, dictionary):
        self._load_dictionary_recursive(self.container, dictionary)

    def load_config_class(self, cls, by_name=None):
        self._load_object_recursive(self.container.__dict__[by_name or cls.__name__], cls)

    def load_json_file(self, path, namespace=None):
        with open(path, "r") as f:
            contents = json.load(f)

        if isinstance(contents, list):
            for obj in contents:
                self.load_dictionary(obj)
        elif isinstance(contents, dict):
            self.load_dictionary(contents)
        else:
            raise ValueError("Unknown JSON object type")

    # TODO - test this method
    def safe_load_json_file(self, path, namespace=None):
        try:
            if os.path.exists(path):
                self.load_json_file(path, namespace)
        except Exception:
            import logging
            logging.exception("Failed to load configuration json file- %s", path)

    def load_module(self, module):
        for key, value in six.iteritems(module.__dict__):
            if isinstance(value, type) and issubclass(value, ConfigurationValues) and value is not ConfigurationValues:
                self._load_object_recursive(self.container.__dict__[key], value)

    def dump_json_file(self, names, path):
        configuration = {}

        for name in names:
            configuration[name] = ConfigManager._dump_object_recursive(self.container.__dict__[name])

        with open(path, "w") as f:
            json.dump(configuration, f)

    def dump_json_file_all(self, path):
        configuration = {}

        for key, value in six.iteritems(self.container.__dict__):
            if isinstance(value, ConfigurationSchemeMetaClass):
                configuration[key] = ConfigManager._dump_object_recursive(value)

        with open(path, "w") as f:
            json.dump(configuration, f)

    def _load_dictionary_recursive(self, node, dictionary):
        for key, value in six.iteritems(dictionary):
            if isinstance(value, dict):
                self._load_dictionary_recursive(node.__dict__[key], value)
            else:
                setattr(node, key, value)

    def _load_object_recursive(self, node, obj):
        for key, value in six.iteritems(obj.__dict__):
            if isinstance(value, type) and issubclass(value, ConfigurationValues):
                self._load_object_recursive(node.__dict__[key], value)
            else:
                setattr(node, key, value)

    @staticmethod
    def _dump_object_recursive(obj):
        dictionary = {}

        for key, value in six.iteritems(obj.__dict__):
            if not ConfigManager._is_key_built_in(key):
                if isinstance(value, ConfigurationScheme):
                    dictionary[key] = ConfigManager._dump_object_recursive(value)
                else:
                    dictionary[key] = value

        return dictionary

    @staticmethod
    def _is_key_built_in(key):
        return key in ('__builtins__', '__file__', '__package__', '__name__', '__doc__', '__dict__', '__weakref__',
                       '__module__', '__spec__', '__loader__', '__cached__', '_initialized')
