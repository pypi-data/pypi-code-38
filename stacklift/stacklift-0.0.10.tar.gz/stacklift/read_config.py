#!/usr/bin/env python3

import yaml
from collections import OrderedDict

def yaml_ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


class ConfigReader:
    def __init__(self, filename):
        self.config_path = filename
        with open(filename) as f:
            self.config = yaml_ordered_load(f)
        self.sections = {}

        common = self.config.get("Common") or {}
        for section_name in self.config["Stacks"]:
            section = OrderedDict()
            section.update(common)
            section.update(self.config["Stacks"][section_name])
            self.sections[section_name] = section

    def assert_value_string(self, v):
        if not isinstance(v, str):
            raise RuntimeError("Value '%s' is not a string" % v)
        return v

    def get_value_or_default(self, section_name, key, default_value=None):
        section = self.sections[section_name]
        if key in section:
            return self.assert_value_string(section[key])
        return default_value

    def get_value(self, section_name, key):
        value = self.get_value_or_default(section_name, key, None)
        if value is None:
            raise RuntimeError("Key {} is not found in {}".format(key, section_name))
        return value

    def get_section_names(self):
        return list(self.sections.keys())

    def get_section_parameters(self, section_name):
        return self.sections[section_name].get("Parameters") or {}

    def get_parameter_or_default(self, section_name, parameter_name, default_value=None):
        section = self.get_section_parameters(section_name)
        if parameter_name in section:
            return self.assert_value_string(section[parameter_name])
        return default_value

    def get_parameter(self, section_name, parameter_name):
        value = self.get_parameter_or_default(section_name, parameter_name, None)
        if value is None:
            raise RuntimeError("Parameter {} is not found in {}".format(parameter_name, section_name))
        return value

    def get_parameters(self, section_name, parameter_names):
        key_values = [(x, self.get_parameter_or_default(section_name, x)) for x in parameter_names]
        return { key: value for key, value in key_values if value is not None }

    def get_global_value(self, key):
        return self.config["Global"][key]


class ReadConfigOptions:
    def __init__(self):
        self.file = None
        self.section = None
        self.default = None
        self.parameter = False
        self.key = None


def read_config(opts: ReadConfigOptions):
    config_reader = ConfigReader(opts.file)

    key = opts.key
    if opts.parameter:
        if opts.default is not None:
            print(config_reader.get_parameter_or_default(opts.section, key, opts.default))
        else:
            print(config_reader.get_parameter(opts.section, key))
        return

    if opts.default is not None:
        print(config_reader.get_value_or_default(opts.section, key, opts.default))
    else:
        print(config_reader.get_value(opts.section, key))
