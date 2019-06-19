# -*- coding: utf-8 -*-
from missinglink.resource_manager.docker.config.configuration_instance import ConfigurationInstance


class WindowsConfigurationInstance(ConfigurationInstance):

    SHELL_IMAGE = 'python:3.7'
    GIT_IMAGE = 'missinglinkai/git-lfs:windows-server-0.1'
    ML_IMAGE = 'missinglinkai/missinglink:windows-server-0.1'
