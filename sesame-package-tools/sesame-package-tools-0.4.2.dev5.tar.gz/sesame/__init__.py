# -*- coding: utf-8 -*-

import os

_ROOT = os.path.abspath(os.path.dirname(__file__))

def get_template_path(name):
    return os.path.join(_ROOT, 'templates', name)

def get_conan_settings_path():
    return os.path.join(_ROOT, 'conan_settings')

def get_conan_settings_yml_path():
    return os.path.join(get_conan_settings_path(), 'settings.yml')

def get_conan_profiles_path(name):
    return os.path.join(get_conan_settings_path(), 'profiles', name)

def get_setup_path():
    return os.path.abspath(os.path.join(_ROOT, os.pardir))
