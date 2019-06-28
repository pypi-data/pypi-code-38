import sys
import inspect
import codecs
import configparser
from . import AError


def _transform_ip(s):
    ip = ''
    vec = s.split('.')
    if len(vec) != 4:
        return None
    for index, item in enumerate(vec):
        try:
            seg = int(item)
        except:
            return None
        if not (0 <= seg <= 255):
            return None
        ip += str(seg)
        if index != 3:
            ip += '.'
    return ip


def _transform_port(s):
    try:
        port = int(s)
    except:
        return None
    if not 0 <= port <= 65535:
        return None
    return port


class INI_Error(AError.Error):
    pass


class Field:
    def __init__(self, default=None):
        self.default = default

    def to_python_value(self, value):
        return self.coerce(value)


class BoolField(Field):
    coerce = bool


class IntField(Field):
    coerce = int


class FloatField(Field):
    coerce = float


class StringField(Field):
    def __init__(self, allow_empty=False):
        self.allow_empty = allow_empty

    def coerce(self, value):
        if (not self.allow_empty) and (not value):
            raise ValueError('empty string not allowed')
        return value


class IPField(Field):
    def coerce(self, value):
        ip = _transform_ip(value)
        if ip is None:
            raise ValueError('ip must be <n>.<n>.<n>.<n> n between 0~255')
        return ip


class IPPortField(Field):
    def coerce(self, value):
        if ':' not in value:
            raise ValueError('format must be <ip>:<port>')

        vec = value.split(':')
        if len(vec) != 2:
            raise ValueError('format must be <ip>:<port>')

        ip = _transform_ip(vec[0])
        if ip is None:
            raise ValueError('ip must be <n>.<n>.<n>.<n> n between 0~255')

        port = _transform_port(vec[1])
        if port is None:
            raise ValueError('port must be a number between 0~65535')

        return (ip, port)


class ListField(Field):
    def __init__(self, element_field, default=None):
        Field.__init__(self, default)
        self.element_field = element_field

    def coerce(self, value):
        ret = []
        for index, item in enumerate(value.split(',')):
            item = item.strip()
            try:
                item_value = self.element_field.to_python_value(item)
            except Exception as e:
                raise ValueError("element #%d '%s' is not a valid value of '%s': %s" % (
                    index, item,
                    self.element_field.__class__.__name__,
                    str(e)
                ))
            ret.append(item_value)
        return ret


class ChoiceField(Field):
    def __init__(self, element_field, choices, default=None):
        Field.__init__(self, default)
        self.element_field = element_field
        self.choices = choices
        for choice in self.choices:
            try:
                element_field.to_python_value(choice)
            except Exception as e:
                raise ValueError("choice '%s' is not a valid value of '%s': %s" % (
                    choice,
                    self.element_field.__class__.__name__,
                    str(e)
                ))

    def coerce(self, value):
        if value not in self.choices:
            raise ValueError("'%s' is not a valid choice in %s" % (value, self.choices))
        return self.element_field.to_python_value(value)


class Section:
    pass


class INI:
    @classmethod
    def load(cls, file_path, encoding='UTF-8'):
        conf = configparser.ConfigParser()

        try:
            fp = codecs.open(file_path, 'r', encoding)
            configparser.ConfigParser.read_file(conf, fp)
        except Exception as e:
            raise INI_Error(str(e))

        ret = cls()
        for section_name, section_cls in cls.__dict__.items():
            if not (inspect.isclass(section_cls) and issubclass(section_cls, Section)):
                continue

            section = section_cls()
            setattr(ret, section_name, section)

            for field_name, field in section_cls.__dict__.items():
                if not isinstance(field, Field):
                    continue

                try:
                    origin_value = conf.get(section_name, field_name)
                except (configparser.NoSectionError, configparser.NoOptionError) as e:
                    if field.default is None:
                        raise INI_Error(str(e))
                    else:
                        setattr(section, field_name, field.default)
                        continue

                try:
                    value = field.to_python_value(origin_value)
                except Exception as e:
                    raise INI_Error("[%s] %s: '%s' is not a valid value of '%s': %s" % (
                        section_name, field_name, origin_value, field.__class__.__name__,
                        str(e)
                    ))

                setattr(section, field_name, value)

        return ret

"""
Examples
--------

example.ini::
	
    [Section1]
    bool_field = True
    int_field = 123
    #int_default_field = 567
    float_field = 456.7
    string_field = hello, world

    [Section2]
    ip_field = 127.0.0.1
    ipport_field = 127.0.0.1:12345
    ipport_list_field = 127.0.0.1:12345, 127.0.0.2:12346
	
	[Section3]
	choice_field = release

example.py::

    from AINI import *
    import sys

    class MyConfig(INI):
        class Section1(Section):
            bool_field = BoolField()
            int_field = IntField()
            int_default_field = IntField(default='default value 6')
            float_field = FloatField()
            string_field = StringField()
        class Section2(Section):
            ip_field = IPField()
            ipport_field = IPPortField()
            ipport_list_field = ListField(IPPortField())
        class Section3(Section):
			choice_field = ChoiceField(StringField(), ['debug', 'release'], 'debug')

    try:
        config = MyConfig.load('example.ini')
    except Error as e:
        print('Failed to load file: %s' % str(e))
        sys.exit(1)

    print(config.Section1.bool_field)
    print(config.Section1.int_field)
    print(config.Section1.int_default_field)
    print(config.Section1.float_field)
    print(config.Section1.string_field)
    print(config.Section2.ip_field)
    print(config.Section2.ipport_field)
    print(config.Section2.ipport_list_field)
	print(config.Section3.choice_field)

output::

    True
    123
    default value 6
    456.7
    hello, world
    127.0.0.1
    ('127.0.0.1', 12345)
    [('127.0.0.1', 12345), ('127.0.0.2', 12346)]
	release

"""