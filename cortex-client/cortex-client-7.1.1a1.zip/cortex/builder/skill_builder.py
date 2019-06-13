"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from cortex.skill import Skill
from cortex_client import CatalogClient
from cortex.action import Action


class InputBuilder:
    """
    Builds an input to a skill.
    """
    def __init__(self, name: str, parent, camel='1.0.0'):
        self._name = name
        self._title = None
        self._description = None
        self._parent = parent
        self._routing = None
        self._routing_config = {}
        self._parameters = {}
        self._is_schema_ref = False

    def title(self, title: str):
        """
        Sets the title property of the skill input.

        :param title: The human-readable name of the skill input
        :return: The builder instance
        """
        self._title = title
        return self

    def description(self, description: str):
        """
        Sets the description property of the skill input.

        :param description: the human-readable long description of the skill input
        :return: the builder instance
        """
        self._description = description
        return self

    def all_routing(self, action, output: str):
        self._routing = 'all'
        if isinstance(action, Action):
            self._routing_config['action'] = action.name
        else:
            self._routing_config['action'] = str(action)

        self._routing_config['output'] = output

        return self

    def parameter(self, name: str, type: str, format: str=None, title=None, description=None, required=True):
        """
        Adds an input message parameter/field.

        :param name: the name of an input message parameter
        :param type: the CAMEL schema type of the input message parameter
        :param format: the specific format for some schema types like `datetime`
        :param title: the human-readable name of the input message parameter
        :param description: the human-readable description of the input message parameter
        :param required: boolean flag that determines if the input parameter is required
        :return: the builder instance
        """
        if self._is_schema_ref:
            raise Exception('Schema ref already used, parameters not allowed')

        param = {'name': name, 'type': type, 'required': required}

        if title:
            param['title'] = title

        if description:
            param['description'] = description

        if format:
            param['format'] = format

        self._parameters[name] = param

        return self

    def use_schema(self, name):
        """
        Use a schema reference to define the Input Message parameters.

        :param name: the name of an input message parameter
        :return: the builder instance
        """
        self._parameters['$ref'] = {'$ref': name}
        self._is_schema_ref = True
        return self

    def build(self):
        routing = {self._routing: self._routing_config}

        params = list(self._parameters.values())
        if len(params) == 1:
            if '$ref' in params[0]:
                params = params[0]

        skill_input = {
            'name': self._name,
            'title': self._title or self._name,
            'parameters': params,
            'routing': routing
        }

        if self._description:
            skill_input['description'] = self._description

        self._parent._inputs[self._name] = skill_input

        return self._parent


class OutputBuilder:
    """
    Builds the output of a skill.
    """
    def __init__(self, name: str, parent, camel='1.0.0'):
        self._name = name
        self._title = None
        self._description = None
        self._parent = parent
        self._parameters = {}
        self._is_schema_ref = False

    def title(self, title: str):
        """
        Sets the title property of the skill output.

        :param title: The human-readable name of the skill output
        :return: the builder instance
        """
        self._title = title
        return self

    def description(self, description: str):
        """
        Sets the description property of the skill output.

        :param description: The human-readable long description of the skill output
        :return: the builder instance
        """
        self._description = description
        return self

    def parameter(self, name: str, type: str, format: str=None, title=None, description=None, required=True):
        """
        Adds an output message parameter/field.

        :param name: the name of an output message parameter
        :param type: the CAMEL schema type of the output message parameter
        :param format: the specific format for some schema types like `datetime`
        :param title: the human-readable name of the output message parameter
        :param description: the human-readable description of the output message parameter
        :param required: boolean flag that determines if the output parameter is required
        :return: the builder instance
        """
        if self._is_schema_ref:
            raise Exception('Schema ref already used, parameters not allowed')

        self._parameters[name] = {'name': name, 'type': type, 'required': required}

        if title:
            self._parameters[name]['title'] = title

        if description:
            self._parameters[name]['description'] = description

        if format:
            self._parameters[name]['format'] = format

        return self

    def use_schema(self, name):
        """
        Use a schema reference to define the output message parameters.

        :param description: The human-readable schema reference
        :return: the builder instance.
        """
        self._parameters['$ref'] = {'$ref': name}
        self._is_schema_ref = True
        return self

    def build(self):
        params = list(self._parameters.values())
        if len(params) == 1:
            if '$ref' in params[0]:
                params = params[0]

        skill_output = {
            'name': self._name,
            'title': self._title or self._name,
            'parameters': params
        }

        if self._description:
            skill_output['description'] = self._description

        self._parent._outputs[self._name] = skill_output

        return self._parent


class DatasetRefBuilder:
    """
    Builds dataset references for a skill.
    """
    def __init__(self, name: str, parent, camel='1.0.0'):
        self._name = name
        self._parent = parent
        self._parameters = {}


    def parameter(self, ref: str):
        """
        Adds a dataset reference parameter

        :param ref: the identifier of the reference dataset
        """
        param = {'$ref': ref}

        self._parameters[ref] = param

        return self


    def build(self):

        params = list(self._parameters.values())

        skill_datasetrefs = {
            'name': self._name,
            'parameters': params,
        }
        self._parent._datasetrefs[self._name] = skill_datasetrefs
        return self._parent



class SkillBuilder:

    """
    Creates a Cortex skill; not meant to be directly instantiated byclients.
    """

    def __init__(self, name: str, client: CatalogClient, camel='1.0.0'):
        self._camel = camel
        self._name = name
        self._title = None
        self._description = None
        self._client = client
        self._inputs = {}
        self._outputs = {}
        self._properties = {}
        self._datasetrefs = {}

    def title(self, title: str):
        """
        Sets the title property of the Skill.

        :param title: the human friendly name of the Skill
        :return: the builder instance
        """
        self._title = title
        return self

    def description(self, description: str):
        """
        Sets the description property of the Skill.

        :param description: the human friendly long description of the Skill
        :return: the builder instance
        """
        self._description = description
        return self

    def property(self, name: str, data_type: str, title: str=None, description: str=None, required: bool=True, secure=False, default_val: str=None, valid_values=None):
        """
        Adds a skill property, which can be configured on a per instance basis and are passed down to actions for use.

        :param name: the property name
        :param data_type: the CAMEL schema data type of the skill property
        :param title: the human-readable name of the skill property
        :param description: the human-readable description of the skill property
        :param required: boolean flag that identifies if the skill property is required
        :param secure: boolean flag that identifies if the skill property requires a secure variable assignment
        :param default_val: the default value of the propery
        :param valid_values: additional valid values for the property that may be selected
        :return: the builder instance
        """
        prop ={
            'name': name,
            'type': data_type,
            'required': required,
            'secure': secure
        }

        if title:
            prop['title'] = title

        if description:
            prop['description'] = description

        if default_val:
            prop['defaultValue'] = default_val

        if valid_values:
            prop['validValues'] = valid_values

        self._properties[name] = prop

        return self

    def input(self, name: str):
        """
        Adds a skill input.

        :param name: the name of a skill input parameter
        :return: the builder instance
        """
        return InputBuilder(name, self, self._camel)

    def output(self, name: str):
        """
        Adds a skill output.

        :param name: the name of a skill output parameter
        :return: the builder instance
        """
        return OutputBuilder(name, self, self._camel)

    def dataset(self, name: str):
        """
        Adds a skill dataset reference.

        :param name: the name of a dataset reference for a skill
        :return: the builder instance
        """
        return DatasetRefBuilder(name, self, self._camel)

    def to_camel(self):
        skill = {
            'camel': self._camel,
            'name': self._name,
            'title': self._title or self._name,
            'inputs': list(self._inputs.values()),
            'outputs': list(self._outputs.values())

        }


        if len(self._properties) > 0:
            skill['properties'] = list(self._properties.values())

        if len(self._datasetrefs) > 0:
            skill['datasets'] = list(self._datasetrefs.values())

        if self._description:
            skill['description'] = self._description

        return skill

    def build(self) -> Skill:
        """
        Builds and replaces a skill using the properties configured on the builder.

        :return: the resulting skill
        """
        skill = self.to_camel()
        self._client.save_skill(skill)

        return Skill.get_skill(self._name, self._client._serviceconnector)
