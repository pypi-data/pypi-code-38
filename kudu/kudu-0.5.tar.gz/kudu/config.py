from os.path import expanduser

import click
import yaml


def write_config(data, path='.kudu.yml'):
    with open(path, 'w+') as stream:
        yaml.safe_dump(data, stream, default_flow_style=False, allow_unicode=True)


def read_config(path='.kudu.yml'):
    try:
        with open(path, 'r+') as stream:
            try:
                from yaml import CLoader as Loader, CDumper as Dumper
            except ImportError:
                from yaml import Loader, Dumper

            config = yaml.load(stream.read(), Loader=Loader)
    except IOError:
        config = {}

    return config


def merge_config(self, other):
    if isinstance(other, dict):
        for key, value in other.items():
            self[key] = value


def load_config():
    config = {}

    for path in (expanduser('~/.kudu.yml'), '.kudu.yml'):
        merge_config(config, read_config(path))

    return config


class ConfigOption(click.Option):
    data = None

    def __init__(self, param_decls=None, config_name=None, **attrs):
        click.Option.__init__(self, param_decls, **attrs)
        self.config_name = config_name if config_name else self.name

    def consume_value(self, ctx, opts):
        value = super(ConfigOption, self).consume_value(ctx, opts)
        if value is None:
            value = load_config().get(self.config_name)
        return value
