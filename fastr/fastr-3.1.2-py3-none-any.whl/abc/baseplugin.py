# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The base class for all Plugins in the fastr system
"""

from abc import ABCMeta
from enum import Enum
import gzip
import io

from colorama import Fore, Back, Style

from .. import exceptions
from ..helpers import config, log
from ..helpers.classproperty import classproperty


class PluginState(Enum):
    """ Plugin status Enum. """
    uninitialized = Back.CYAN + 'UnInitialized' + Style.RESET_ALL
    preload = Back.LIGHTGREEN_EX + 'PreLoad' + Style.RESET_ALL
    unloaded = Back.CYAN + 'UnLoaded' + Style.RESET_ALL
    failed = Fore.WHITE + Back.RED + Style.BRIGHT + 'Failed' + Style.RESET_ALL
    loaded = Fore.WHITE + Back.GREEN + Style.BRIGHT + 'Loaded' + Style.RESET_ALL


class PluginMeta(ABCMeta):
    """ Meta class for the BasePlugin. """
    def __repr__(self):
        return '<{}: {} class [{}]>'.format(self.__bases__[0].__name__, self.id, getattr(self.status, 'value', 'NA'))


class BasePlugin(metaclass=PluginMeta):
    """
    Base class for Plugins in the fastr system.
    """

    #: The status of the plugin
    _status = (PluginState.uninitialized, 'Plugin object created', None)
    _source_code = None
    module = None
    _instantiate = False

    def __init__(self):
        """
        The BasePlugin constructor.

        :return: the created plugin
        :rtype: BasePlugin
        :raises FastrPluginNotLoaded: if the plugin did not load correctly
        """

        if self.status not in (PluginState.preload, PluginState.loaded):
            raise exceptions.FastrPluginNotLoaded('Plugin was not properly loaded: [{}] {}'.format(
                self._status[0], self._status[1])
            )

    def __str__(self):
        """
        Creare string representation of the plugin.

        :return: string represenation
        :rtype: str
        """
        return '<Plugin: {}>'.format(self.__class__.__name__)

    def __repr__(self):
        return '<{}: {} object [{}]>'.format(
            type(self).__bases__[0].__name__, self.id, getattr(self.status, 'value', 'NA')
        )

    @classproperty
    def id(cls):
        """
        The id of this plugin
        """
        return cls.__name__

    @classproperty
    def configuration_fields(cls):
        """
        Plugins can register the fields they need from the configuration
        by adding them here. The format of the data structure is::

            {
                "var_name": (type, default, description),
            }

        So for example::

            {
                "some_string": (str, "spam", "some string used for demonstration purposes"),
                "some_int": (str, 42, "the answer to life etc"),
            }
        """
        return {}

    @classmethod
    def register_configuration(cls):
        """
        Register and test the configuation fields of the plugin
        """
        # Register fields
        config.register_fields(cls.configuration_fields)

        # Validate that current values are correct
        for field_name, field_spec in cls.configuration_fields.items():
            log.debug('Tested config value: {}'.format(getattr(config, field_name)))

    @classproperty
    def fullid(cls):
        """
        The full id of this plugin
        """
        return 'fastr://plugins/{}'.format(cls.id)

    @classproperty
    def source_code(cls):
        """
        The source code of this plugin
        """
        code_gzip = io.StringIO(cls._source_code)
        with gzip.GzipFile(fileobj=code_gzip, mode='rb') as gzip_stream:
            return gzip_stream.read()

    @classproperty
    def status(cls):
        """
        The status of the plugin.
        """
        return cls._status[0]

    @classproperty
    def instantiate(cls):
        """
        Flag if the plugin should be instantiated
        """
        return cls._instantiate

    @classproperty
    def status_message(cls):
        """
        The message explaining the status of the plugin.
        """
        return cls._status[1]

    @classproperty
    def status_details(cls):
        """
        The status details (e.g. stacktrace in case of errors)
        """
        return cls._status[2]

    @classmethod
    def print_status(cls):
        if cls.status != PluginState.loaded:
            log.error('Cannot use plugin {}'.format(cls))
            log.error(cls.status_message)
            log.error('Detailed error report: {}'.format(cls.status_details))

    @classmethod
    def set_status(cls, status, message, exception=None):
        """
        Update the status of the plugin

        :param str status: the new status
        :param str message: message explaining the status change
        :param str exception: stacktrace of the exception causing the failed load
        """
        if not isinstance(status, PluginState):
            raise exceptions.FastrTypeError('Plugin status should be of type PluginState')

        if not isinstance(message, str):
            raise exceptions.FastrTypeError('Plugin status message should be a string')

        cls._status = (status, message, exception)

    @classmethod
    def set_code(cls, source_code):
        """
        Set the filename and source code of the plugin

        :param str source_code: the source code of the plugin
        """
        cls._source_code = source_code

    def cleanup(self):
        """
        Perform any cleanup action needed when the plugin use ended. This can
        be closing files/streams etc.
        """
        pass

    @classmethod
    def test(cls):
        """
        Test the plugin, default behaviour is just to instantiate the plugin
        """
        obj = cls()
        obj.cleanup()
        del obj


class Plugin(BasePlugin):
    pass
