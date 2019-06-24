import os
import ruamel.yaml as yaml
import glob
import json
from typing import Any, Optional
from enum import Enum


class ComponentType(Enum):
    connection = "connection"
    action = "action"
    trigger = "trigger"


class IO(object):
    """
    An Input or Output on a Connection, Action, Trigger
    """

    def __init__(self,
                 identifier: str,
                 title: Optional[str],
                 description: Optional[str],
                 type: str,
                 required: bool,
                 default: Optional[Any],
                 enum: Optional[list] = None,
                 raw_parameters: set = {}
                 ):
        """
        Initializer for an input or output belonging to a component
        :param identifier: Identifier for an IO (optional)
        :param title: Title of an IO (optional)
        :param description: Description of an IO (optional)
        :param type: Type of an IO (eg. string, integer, number, boolean, etc)
        :param required: Boolean indicator of requiredness
        :param default: Default value for the IO (optional)
        :param enum: Enum values (optional)
        :param raw_parameters: All properties belonging to the IO as a set of strings

        """
        self.identifier = identifier
        self.title = title
        self.description = description
        self.type = type
        self.required = required
        self.default = default
        self.enum = enum
        self.raw_parameters = raw_parameters

    @classmethod
    def from_dict(cls, raw: {str: Any}):
        # Get the first and only key from the dict anonymously and assign that to an identifier
        identifier = list(raw.keys())[0]

        return cls(identifier=identifier,
                   title=raw[identifier].get("title"),
                   description=raw[identifier].get("description"),
                   type=raw[identifier].get("type"),
                   required=raw[identifier].get("required"),
                   default=raw[identifier].get("default"),
                   enum=raw[identifier].get("enum"),
                   raw_parameters=set(raw[identifier].keys()))


class PluginComponent(object):
    """
    A Connection, Action, or Trigger
    """

    def __init__(self,
                 component_type: ComponentType,
                 identifier: str = None,
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 inputs: [IO] = None,
                 outputs: [IO] = None,
                 raw_parameters: set = {}):
        """
        Initializer for a PluginComponent
        :param component_type: Type of the component
        :param title: Title of the component. Not present on a Connection component
        :param description: Description of the component. Not present on a Connection component
        :param inputs: List of component inputs (optional)
        :param outputs: List of component outputs (never present on a Connection component) (optional)
        :param raw_parameters: All top-level properties (input/output/etc) belonging to the component as a set of strings
        """
        self.component_type = component_type
        self.identifier = identifier
        self.title = title
        self.description = description
        self.inputs = inputs
        self.outputs = outputs
        self.raw_parameters = raw_parameters

    @classmethod
    def new_action(cls, raw: dict):
        # Get the first and only key from the dict anonymously and assign that to an identifier
        identifier: str = list(raw.keys())[0]
        raw_parameters: {str} = set(raw[identifier].keys())

        input_, output = raw[identifier].get("input"), raw[identifier].get("output")

        inputs: [IO] = [IO.from_dict(raw={k: v}) for k, v in input_.items()] if input_ else []
        outputs: [IO] = [IO.from_dict(raw={k: v}) for k, v in output.items()] if output else []

        return cls(component_type=ComponentType.action,
                   identifier=identifier,
                   title=raw[identifier].get("title"),
                   description=raw[identifier].get("description"),
                   inputs=inputs,
                   outputs=outputs,
                   raw_parameters=raw_parameters)

    @classmethod
    def new_trigger(cls, raw: dict):
        # Get the first and only key from the dict anonymously and assign that to an identifier
        identifier: str = list(raw.keys())[0]
        raw_parameters: {str} = set(raw[identifier].keys())

        input_, output = raw[identifier].get("input"), raw[identifier].get("output")

        inputs: [IO] = [IO.from_dict(raw={k: v}) for k, v in input_.items()] if input_ else []
        outputs: [IO] = [IO.from_dict(raw={k: v}) for k, v in output.items()] if output else []

        return cls(component_type=ComponentType.trigger,
                   identifier=identifier,
                   title=raw[identifier].get("title"),
                   description=raw[identifier].get("description"),
                   inputs=inputs,
                   outputs=outputs,
                   raw_parameters=raw_parameters)

    @classmethod
    def new_connection(cls, raw: dict):
        # Create a list of IO objects from the raw inputs dict
        inputs: [IO] = [IO.from_dict(raw={k: v}) for k, v in raw.items()] if raw else []
        return cls(component_type=ComponentType.connection,
                   identifier="connection",
                   inputs=inputs)


class KomandPluginSpec:
    """
    Class for accessing a Komand plugin's spec.
    """

    def __init__(self, directory, spec_file_name='plugin.spec.yaml'):
        """
        Creates an object from a given plugin directory.
        :param directory: The directory of the Komand plugin.
        :raises Exception if the directory does not exist or if the plugin.spec.yaml is missing or invalid.
        """
        self.directory = os.path.abspath(directory)
        self.spec_file_name = spec_file_name

        self._plugin_name = None
        self._plugin_vendor = None
        self._plugin_version = None
        self._raw_dockerfile = None
        self._dockerfile = None
        self._spec_dictionary = None
        self._spec_json = None
        self._market_json = None
        self._raw_spec = None
        self._raw_makefile = None
        self._raw_help = None
        self._raw_action_files = None
        self._raw_trigger_files = None
        self._raw_connection_file = None
        self._raw_util_files = None

    def spec_dictionary(self):
        """
        Returns the plugin spec as a dictionary.
        :return: plugin spec as a dictionary
        """

        if not self._spec_dictionary:
            self._spec_dictionary = yaml.safe_load(self.raw_spec())

        return self._spec_dictionary

    def json(self):
        """
        Returns the plugin spec as a JSON string.
        :return: plugin spec as a JSON string
        """
        if not self._spec_json:
            spec_dic = self.spec_dictionary()
            self._spec_json = json.dumps(spec_dic)

        return self._spec_json

    def market_json(self):
        """
        Returns the plugin spec as market uploadable JSON
        :return: market uploadable JSON
        """
        if not self._market_json:
            plugin_spec_file_name = os.path.join(self.directory, self.spec_file_name)
            if not os.path.exists(plugin_spec_file_name):
                raise Exception(
                    'No plugin spec file "%s" file in directory "%s"' % (self.spec_file_name, self.directory))

            try:
                with open(plugin_spec_file_name, 'r') as spec_file:
                    spec_contents = spec_file.read()
                    formatted_spec = {'spec': spec_contents}

                    self._market_json = json.loads(json.dumps(formatted_spec))

            except Exception as e:
                raise Exception('Unable to read plugin.spec.yaml', e)

        return self._market_json

    def raw_spec(self):
        """
        Returns the plugin spec as a single string.
        :return: plugin spec as a string
        """
        if not self._raw_spec:

            plugin_spec_file_name = os.path.join(self.directory, self.spec_file_name)
            if not os.path.exists(plugin_spec_file_name):
                raise Exception(
                    'No plugin spec file "%s" file in directory "%s"' % (self.spec_file_name, self.directory))

            try:
                with open(plugin_spec_file_name) as f:
                    self._raw_spec = f.read()
            except Exception as e:
                raise Exception('Unable to read plugin.spec.yaml', e)

            if not self._raw_spec:
                raise Exception('plugin.spec.yaml was empty')

        return self._raw_spec

    def plugin_name(self):
        if not self._plugin_name:
            self._plugin_name = self.spec_dictionary()['name']
        return self._plugin_name

    def plugin_vendor(self):
        if not self._plugin_vendor:
            self._plugin_vendor = self.spec_dictionary()['vendor']
        return self._plugin_vendor

    def plugin_version(self):
        if not self._plugin_version:
            self._plugin_version = self.spec_dictionary()['version']
        return self._plugin_version

    def raw_dockerfile(self):
        if not self._raw_dockerfile:
            with open(os.path.join(self.directory, 'Dockerfile')) as f:
                self._raw_dockerfile = f.readlines()
        return self._raw_dockerfile

    def raw_makefile(self):
        if not self._raw_makefile:
            with open(os.path.join(self.directory, 'Makefile')) as f:
                self._raw_makefile = f.read()
        return self._raw_makefile

    def raw_help(self):
        if not self._raw_help:
            with open(os.path.join(self.directory, 'help.md')) as f:
                self._raw_help = f.read()
        return self._raw_help

    @staticmethod
    def _dir_check(directory, plugin_name, operation_dir):
        komand_inner_dir = 'komand_' + plugin_name
        icon_inner_dir = "icon_" + plugin_name

        if os.path.isdir(os.path.join(directory, komand_inner_dir)):
            return os.path.join(directory, komand_inner_dir, operation_dir)

        if os.path.isdir(os.path.join(directory, icon_inner_dir)):
            return os.path.join(directory, icon_inner_dir, operation_dir)
        else:
            raise Exception("Unable to find plugin directory")

    # TODO: Handle Go plugins
    def raw_action_files(self):
        plugin_name = self.plugin_name()
        if not self._raw_action_files:
            self._raw_action_files = []
            full_inner_dir = self._dir_check(self.directory, plugin_name, "actions")
            action_dirs = [action[0] for action in os.walk(full_inner_dir)]
            for action in action_dirs[1:]:
                try:
                    with open(os.path.join(full_inner_dir, action, 'action.py')) as f:
                        self._raw_action_files.append(f.read())
                except FileNotFoundError:
                    pass
        return self._raw_action_files

    # TODO: Handle Go plugins
    def raw_trigger_files(self):
        plugin_name = self.plugin_name()
        if not self._raw_trigger_files:
            self._raw_trigger_files = []
            full_inner_dir = self._dir_check(self.directory, plugin_name,
                                             "triggers")
            trigger_dirs = [trigger[0] for trigger in os.walk(full_inner_dir)]
            for trigger in trigger_dirs[1:]:
                try:
                    with open(os.path.join(full_inner_dir, trigger, 'trigger.py')) as f:
                        self._raw_trigger_files.append(f.read())
                except FileNotFoundError:
                    pass
        return self._raw_trigger_files

    # TODO: Handle Go plugins
    def raw_connection_file(self):
        plugin_name = self.plugin_name()
        if not self._raw_connection_file:
            full_inner_dir = self._dir_check(self.directory, plugin_name,
                                             "connection")
            with open(os.path.join(full_inner_dir, 'connection.py')) as f:
                self._raw_connection_file = f.read()
        return self._raw_connection_file

    # TODO: Handle Go plugins
    def raw_util_files(self):
        plugin_name = self.plugin_name()
        if not self._raw_util_files:
            self._raw_util_files = []
            full_inner_dir = self._dir_check(self.directory, plugin_name,
                                             "util")
            util_files = glob.glob(full_inner_dir + '/*.py')
            for util in util_files:
                with open(util) as f:
                    self._raw_util_files.append(f.read())
        return self._raw_util_files

    def dockerfile(self):
        raise Exception('Not implemented yet')

    def types(self):
        spec = self.spec_dictionary()
        if not spec or 'types' not in spec or not spec['types']:
            return

        for k, v in spec['types'].items():
            yield k, v

    def actions(self):
        spec = self.spec_dictionary()
        if not spec or 'actions' not in spec or not spec['actions']:
            return

        return spec['actions']

    def triggers(self):
        spec = self.spec_dictionary()
        if not spec or 'triggers' not in spec or not spec['triggers']:
            return

        return spec['triggers']

    def connection(self):
        spec = self.spec_dictionary()
        if not spec or 'connection' not in spec or not spec['connection']:
            return

        return spec['connection']

    @staticmethod
    def action_input_items(action_dict):
        if not action_dict or 'input' not in action_dict or not action_dict['input']:
            return

        for k, v in action_dict['input'].items():
            yield k, v

    @staticmethod
    def action_output_items(action_dict):
        if not action_dict or 'output' not in action_dict or not action_dict['output']:
            return

        for k, v in action_dict['output'].items():
            yield k, v

    @staticmethod
    def type_items(type):
        for k, v in type.items():
            yield k, v
