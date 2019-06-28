import argparse
import inspect
from ruamel import yaml
import os
import sys
import six

from distutils import util

support_types = ('str', 'int', 'bool', 'float')

from cpbox.tool import datatypes

def append_cli(container, cli):
    cli_map = {}
    if hasattr(container, '__cli_map__'):
        cli_map = container.__cli_map__
    for key, attr in cli.__class__.__dict__.items():
        if key[0:1] != '_' and callable(attr):
            cli_map[key] = cli
            setattr(container, key, attr.__get__(cli))

def merge_class(*proxy_cls_list):
    def real_decorator(cls):
        cls.__proxy_src_cls__ = cls
        cls.__proxy_cls_list__ = list(proxy_cls_list)
        return cls
    return real_decorator

def keep_class(cls):
    cls.keep_class_for_cli = True
    return cls

def keep_method(f):
    f.keep_method_for_cli = True
    return f

class AppSepc(object):

    def __init__(self, app, log_level, common_args_option=None):

        self.common_args_option = common_args_option

        self.app = app
        self.get_app_public_methods(app)
        self.method_spec_map = self._get_app_method_spec()
        self.num_to_name_map = {str(index): name for index, name in enumerate(self.public_methods)}

        self.method_will_call = None

    def get_app_public_methods_for_proxy_class(self, app):
        proxy_src_cls = app.__dict__['__proxy_src_cls__']
        proxy_cls_list = app.__dict__['__proxy_cls_list__']

        method_names = []
        method_map = {}

        src_cls_methods = get_cls_cli_methods(proxy_src_cls, True)
        method_names.extend(src_cls_methods.keys())
        method_map.update(src_cls_methods)

        for cls in proxy_cls_list:
            cls_methods = get_cls_cli_methods(cls, False)
            method_names.extend(cls_methods.keys())
            method_map.update(cls_methods)

        self.public_methods = method_names
        self.method_map = method_map

    def get_app_public_methods_for_simple_class(self, app):
        cls_methods = get_cls_cli_methods(app, True)
        self.public_methods = cls_methods.keys()
        self.method_map = cls_methods

    def get_app_public_methods(self, app):
        if '__proxy_cls_list__' in app.__dict__:
            self.get_app_public_methods_for_proxy_class(app)
        else:
            self.get_app_public_methods_for_simple_class(app)

    def find_method_name(self, num_or_name):
        if num_or_name in self.num_to_name_map:
            return self.num_to_name_map[num_or_name]
        if num_or_name in self.method_spec_map:
            return num_or_name
        return None

    def fix_terminal_columns(self):
        if sys.stdin.isatty() and sys.stdout.isatty():
            rows, columns = os.popen('stty size', 'r').read().split()
            os.environ['COLUMNS'] = columns

    def resolve(self, default_method=None, enable_method_index=False):
        self.fix_terminal_columns()

        method_will_call = None
        if len(sys.argv) > 1:
            method_will_call = sys.argv[1].lstrip('-')
            method_will_call = method_will_call.replace('-', '_')
        if method_will_call is None and default_method is not None:
            method_will_call =  default_method
        method_will_call = self.find_method_name(method_will_call)

        if not method_will_call:
            self.show_help_then_exit(enable_method_index)

        self.method_will_call = method_will_call
        self._parse_args()

    def _parse_args(self):
        method_will_call = self.method_will_call
        method_spec = self.method_spec_map[method_will_call]
        kwargs = build_argparser_for_func(method_will_call, method_spec)

        self.common_kwargs = {}
        if self.common_args_option:
            common_args_keys = set(self.common_args_option.get('args'))
            methods_args_keys = set(method_spec['method_args'])
            method_kwargs = {}
            for key, value in kwargs.items():
                if key in common_args_keys:
                    self.common_kwargs[key] = value
                if key in methods_args_keys:
                    method_kwargs[key] = value
            self.kwargs = method_kwargs
        else:
            self.kwargs = kwargs

    def run(self):
        kwargs = self.kwargs
        _app = self.app(**self.common_kwargs)
        func = getattr(_app, self.method_will_call)
        func(**kwargs)

    def _get_app_method_spec(self):
        method_spec_map = {}
        for method_name in self.public_methods:
            method_spec_map[method_name] = self.get_method_spec(method_name)
        return method_spec_map

    def get_method_spec(self, method_name):
        method_attr = self.method_map[method_name]
        method_arg_spec = inspect.getargspec(method_attr)
        default_values = None
        if method_arg_spec.defaults:
            default_values = dict(zip(method_arg_spec.args[-len(method_arg_spec.defaults):], method_arg_spec.defaults))
        args = list(filter(lambda x: x != 'self', method_arg_spec.args))

        method_spec = {}
        method_spec['method_args'] = list(args)
        if self.common_args_option != None:
            args.extend(self.common_args_option.get('args', []))
            args = list(set(args))
            default_values_from_common_args = self.common_args_option.get('default_values', [])
            if default_values is None:
                default_values = default_values_from_common_args
            else:
                default_values.update(default_values_from_common_args)

        method_spec['args'] = args
        method_spec['default_values'] = default_values
        method_spec['parameters'] = _check_parameters_spec(method_name, args, default_values)
        return method_spec

    def show_help_then_exit(self, enable_method_index):
        parser = argparse.ArgumentParser(add_help=False)
        parser.allow_abbrev = False
        parser.add_argument('-h', '--help', action='store_true', help='show this help message and exit')
        for index, method_name in enumerate(self.public_methods):
            if enable_method_index:
                parser.add_argument('-' + str(index), '--' + method_name, action='store_true')
            else:
                parser.add_argument('--' + method_name, action='store_true')
        parser.print_help()

        method_will_call = self.method_will_call
        if method_will_call and (method_will_call == 'h' or method_will_call == 'help'):
            sys.exit(0)
        else:
            sys.exit(1)

def _get_func_comments(method_attr):
    comments = inspect.getdoc(method_attr)
    if comments is None:
        return None
    else:
        return yaml.load(comments)

def _is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def _check_parameter_item_default_value(arg_name, parameter_item, default_values):
    if default_values is None or arg_name not in default_values:
        return parameter_item

    value = default_values[arg_name]
    type = _determine_type(value)

    if type is None:
        raise Error('Can not determine type for parameter: %s, parameter_item: %s' %s (arg_name, parameter_item))

    parameter_item['type'] = type
    parameter_item['des'] = 'type: %s, default value is: %s' % (type, value)
    return parameter_item

def _determine_type(value):
    type = None
    if value is None:
        type = 'str'
    elif isinstance(value, bool):
        type = 'bool'
    elif isinstance(value, six.integer_types):
        type = 'int'
    elif isinstance(value, six.string_types):
        type = 'str'
    elif _is_float(value):
        type = 'float'
    return type

def _convert_value_for_type(value, type):
    if value is None:
        return value
    elif type == 'bool':
        if isinstance(value, six.string_types):
            try:
                return bool(util.strtobool(value))
            except:
                return False
        return bool(value)
    elif type == 'int':
        return int(value)
    elif type == 'str':
        return str(value)
    elif type == 'float':
        return float(value)
    return value

def _check_parameters_spec(method_name, args, default_values):
    parameters = {}
    for arg_name in args:
        parameter_item = {}
        if isinstance(parameter_item, six.string_types):
            parameter_item = {
                    'type': 'str',
                    'des': parameter_item
                    }
        parameter_item = _check_parameter_item_default_value(arg_name, parameter_item, default_values)
        if 'type' not in parameter_item:
            parameter_item['type'] = 'str'
        if 'des' not in parameter_item:
            parameter_item['des'] = arg_name

        parameters[arg_name] = parameter_item
        _check_parameter_item(arg_name, parameter_item)

    return parameters

def _check_parameter_item(arg_name, parameter_item):
    if 'type' not in parameter_item:
        print('Missing type in parameter item: %s' % parameter_item)
    if parameter_item['type'] not in support_types:
        print('The type: %s is not in support types: %s' % (parameter_item['type'], support_types))
    if not parameter_item['des']:
        print('Missing parameter descripion(`des`): %s' % parameter_item)

def get_cls_cli_methods(cls, exclude_parent=True):
    methods = get_cls_public_methods(cls)
    if exclude_parent:
        parenet_cls_methods = get_cls_parent_methods_for_exclude(cls)
        return {key: value for key, value in methods.items() if key not in parenet_cls_methods}
    else:
        return methods

def get_cls_public_methods(cls):
    list = inspect.getmembers(cls, predicate=lambda x: inspect.isfunction(x) or inspect.ismethod(x))
    methods = {item[0]: item[1] for item in list if item[0][0:1] != '_'}
    return methods

def get_cls_parent_methods_for_exclude(cls):
    methods = {}
    for parent_cls in cls.__bases__:
        if parent_cls.__dict__.get('keep_class_for_cli', False):
            continue
        parent_methods = get_cls_public_methods(parent_cls)
        parent_methods = {key: val for key, val in parent_methods.items() if not val.__dict__.get('keep_method_for_cli', False)}
        methods.update(parent_methods)
    return methods

def build_argparser_for_func(method_name, method_spec):

    args = method_spec['args']
    default_values = method_spec['default_values']

    parser = argparse.ArgumentParser()
    parser.add_argument('--' + method_name, action='store_true')

    parameters = method_spec.get('parameters', {})
    for arg_name in args:
        parameter = parameters.get(arg_name)
        help = parameter.get('des', '')
        metavar = ''

        if default_values is not None and arg_name in default_values:
            if len(arg_name) == 1:
                parser.add_argument('-' + arg_name, metavar=metavar, help=help, default=default_values[arg_name], nargs=1, required=False)
            else:
                parser.add_argument('--' + arg_name, metavar=metavar, help=help, default=default_values[arg_name], nargs=1, required=False)
        else:
            if len(arg_name) == 1:
                parser.add_argument('-' + arg_name, metavar=metavar, help=help, nargs=1, required=True)
            else:
                parser.add_argument('--' + arg_name, metavar=metavar, help=help, nargs=1, required=True)
    args_input, _ = parser.parse_known_args()
    kwargs = {}
    for arg_name in args:
        parameter = parameters.get(arg_name)
        attr = getattr(args_input, arg_name)
        if default_values is not None and arg_name in default_values and attr == default_values[arg_name]:
            kwargs[arg_name] = attr
        else:
            kwargs[arg_name] = _convert_value_for_type(
                    _get_first_from_list_or_item_self(attr), parameter['type'])
    return kwargs

def _get_first_from_list_or_item_self(attr):
    try:
        return next(iter(attr), None)
    except TypeError:
        return attr

def _check_args_has(args, option):
    ret = getattr(args, option)
    return ret

def run_app(app, log_level='critical', default_method=None, common_args_option=None, common_args_option_basic=None):
    common_args_option = common_args_option if common_args_option else {}
    if common_args_option_basic:
        common_args_option = datatypes.merge(common_args_option_basic, common_args_option, 'merge')
    app_spec = AppSepc(app, log_level, common_args_option)
    app_spec.resolve(default_method)
    app_spec.run()