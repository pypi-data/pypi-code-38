import os
import sys
from os.path import abspath
from yamlreader import yaml_load

VALID_PLUGIN_NAMES = [
    'actions',
    'config',
    'editor_wrappers',
    'filters',
    'functions',
    'templates'
]

def resolve_plugin_path(plugin_name, config_path):
    validate_plugin_name(plugin_name)
    start_path = get_start_path(plugin_name, config_path)
    if os.path.isdir(start_path):
        return abspath(start_path)
    if start_path:
        plugin_path = get_plugin_path(start_path, config_path)
        if os.path.isdir(plugin_path):
            return abspath(plugin_path)

def validate_plugin_name(plugin_name):
    if plugin_name not in VALID_PLUGIN_NAMES:
        raise RuntimeError("error: plugin name: " + plugin_name + " is invalid")

def get_start_path(plugin_name, config_path):
    plugin_settings = plugin_name + "_path"
    config_object = yaml_load(config_path)
    if config_object.get("settings", "") and config_object["settings"].get("plugins", "") and config_object["settings"]["plugins"].get(plugin_settings, ""):
        return config_object["settings"]["plugins"][plugin_settings]
    return ''

def get_plugin_path(start_path, config_path):
    default_path = os.path.join(config_path, start_path)
    if os.path.isdir(default_path):
        return default_path
    config_path_no_file = os.path.dirname(config_path)
    trimmed_path = os.path.join(config_path_no_file, start_path)
    if os.path.isdir(trimmed_path):
        return trimmed_path
    raise RuntimeError("error: unable to get plugin path for: " + str(config_path) + " and: " + str(start_path))

def get_tide_base_path():
    join_paths = get_python_scripts_base_path(), "..", ".."
    return os.path.join(*join_paths)

def get_python_scripts_base_path():
    return os.path.dirname(os.path.realpath(__file__))

def get_paths_for_plugin(plugin_name):
    import config_source as Cs
    validate_plugin_name(plugin_name)
    plugin_paths = []
    for config_path in Cs.CONFIG_LOCATION_ARRAY:
        resolved_path = resolve_plugin_path(plugin_name, config_path)
        if resolved_path:
            plugin_paths.append(resolved_path)
    return plugin_paths
