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

from abc import abstractmethod
from collections import OrderedDict, namedtuple
from collections.abc import Mapping, Iterable
import json
import os
import sys
import re

import fastr
from fastr import exceptions
from fastr.abc.baseplugin import Plugin
from fastr.abc.serializable import Serializable
from fastr.core.interface import Interface, InterfaceResult, InputSpec, OutputSpec
from fastr.datatypes import EnumType, TypeGroup, URLType
from fastr.plugins.managers.pluginmanager import PluginSubManager


class PathDescription(object):
    def __init__(self, path):
        """
        Create a path description that allows access to parts

        :param str path: the path to describe
        """
        if not isinstance(path, str):
            path = str(path)

        self.path = path

    def __repr__(self):
        return '<PathSpec: {}>'.format(self.path)

    def __str__(self):
        return self.path

    def __getitem__(self, item):
        """
        Forward the getitem to the path string

        :param int,slice item: the part of the path the retrieve
        :return: substring
        """
        return self.path[item]

    @property
    def directory(self):
        """
        The directory name of the path
        """
        return os.path.dirname(self.path)

    @property
    def filename(self):
        """
        The entire filename of the path
        """
        return os.path.basename(self.path)

    @property
    def basename(self):
        """
        The basename of the filename of the path
        """
        return self.filename.split('.', 1)[0]

    @property
    def extension(self):
        """
        The extension of the path
        """
        if '.' not in self.path:
            return ''
        else:
            return self.path.split('.', 1)[1]


class CollectorPlugin(Plugin):
    """
    :py:class:`CollectorPlugins <fastr.resources.plugins.interfaceplugins.fasterinterface.CollectorPlugin>`
    are used for finding and collecting the output data of outputs part of a
    :py:class:`FastrInterface <fastr.resources.plugins.interfaceplugins.fasterinterface.FasterInterface>`
    """

    # Signal managers that this plugin should be stored instantiated
    _instantiate = True

    def __init__(self):
        """
        Constructor
        """
        super(CollectorPlugin, self).__init__()
        self.job = None

    @property
    def fullid(self):
        """
        The full id of the plugin
        """
        if self.job is not None:
            return 'fastr://plugins/collectorplugins/{}/{}'.format(self.id, self.job.id)
        else:
            return 'fastr://plugins/collectorplugins/{}'.format(self.id)

    def collect_results(self, interface, output, result):
        """
        Start the collection of the results. This method calls the actual
        implementation from the subclass (_collect_results) and wraps it
        with some convience functionality.

        :param interface: Job to collect data for
        :param output: Output to collect data for
        """
        self._collect_results(interface, output, result)

    @abstractmethod
    def _collect_results(self, job, output, result):
        """
        Placeholder method for the actual collection of the results. This
        method should implemented by subclasses.

        :param job: Job to collect data for
        :param output: Output to collect data for
        """
        pass

    def _regexp_path(self, path):
        """
        Helper function that searches for a regular expression in a path. There
        can be wildcards in any level of the path.

        :param path: path with regular expressions
        :return: list of paths that match the path pattern
        """
        # Get a clean, absolute path to work with
        path = os.path.expanduser(path)
        path = os.path.abspath(path)

        subpaths = self._full_split(path)
        if subpaths[0] != os.path.sep and not re.match(r'[a-zA-Z]:[/\\]', subpaths[0]):
            raise ValueError('path should always contain an absolute path (subpaths: {})'.format(subpaths))

        basepath = subpaths[0]

        pathlist = [basepath]
        fastr.log.debug('Basepath: {}'.format(basepath))
        for subpath in subpaths[1:]:
            subpath = '^' + subpath + '$'
            # Test the regexp and give a more understandable error if it fails
            try:
                re.compile(subpath)
            except Exception as detail:
                raise ValueError('Error parsing regexp "{}": {}'.format(subpath, detail))

            # Scan new level for matches
            newpathlist = []
            for curpath in pathlist:
                contents = os.listdir(curpath)
                for option in contents:
                    if re.match(subpath, option):
                        newpathlist.append(os.path.join(curpath, option))

            pathlist = newpathlist

        return pathlist

    @staticmethod
    def _full_split(urlpath):
        """
        Split an urls path completely into parts

        :param urlpath: path part of the url
        :return: a list of parts
        """
        parts = []
        while True:
            newpath, tail = os.path.split(urlpath)
            if newpath == urlpath:
                assert not tail
                if urlpath:
                    parts.append(urlpath)
                break
            parts.append(tail)
            urlpath = newpath
        parts.reverse()
        return parts


class CollectorPluginManager(PluginSubManager):
    """
    Container holding all the CollectorPlugins
    """

    def __init__(self):
        """
        Create the Coll
        :param path:
        :param recursive:
        :return:
        """
        super(CollectorPluginManager, self).__init__(parent=fastr.plugin_manager,
                                                     plugin_class=CollectorPlugin)
        self._key_map = {}

    @property
    def _instantiate(self):
        """
        Indicate that the plugins should instantiated before stored
        """
        return True

    def __keytransform__(self, key):
        try:
            return self._key_map[key]
        except KeyError:
            self._key_map.clear()
            for id_, value in self.data.items():
                self._key_map[value.id] = id_
            return self._key_map[key]

    def __iter__(self):
        for value in self.data.values():
            yield value.id


class HiddenFieldMap(Mapping):
    def __init__(self, *args, **kwargs):
        self._data = OrderedDict(*args, **kwargs)

    def __getitem__(self, item):
        return self._data[item]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for key, value in self._data.items():
            if not (hasattr(value, 'hidden') and value.hidden):
                yield key


class FastrInterface(Interface):
    """
    The default Interface for fastr. For the command-line Tools as used by
    fastr. It build a commandline call based on the input/output specification.

    The fields that can be set in the interface:

    +-------------------------------------------------+--------------------------------------------------------------------------------+
    | Attribute                                       | Description                                                                    |
    +=================================================+================================================================================+
    | ``id``                                          | The id of this Tool (used internally in fastr)                                 |
    +---------------+---------------------------------+--------------------------------------------------------------------------------+
    | ``inputs[]``  |                                 | List of Inputs that can are accepted by the Tool                               |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``id``                          | ID of the Input                                                                |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``name``                        | Longer name of the Input (more human readable)                                 |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``datatype``                    | The ID of the DataType of the Input [#f1]_                                     |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``enum[]``                      | List of possible values for an EnumType (created on the fly by fastr) [#f1]_   |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``prefix``                      | Commandline prefix of the Input (e.g. --in, -i)                                |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``cardinality``                 | Cardinality of the Input                                                       |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``repeat_prefix``               | Flag indicating if for every value of the Input the prefix is repeated         |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``required``                    | Flag indicating if the input is required                                       |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``nospace``                     | Flag indicating if there is no space between prefix and value (e.g. --in=val)  |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``format``                      | For DataTypes that have multiple representations, indicate which one to use    |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``default``                     | Default value for the Input                                                    |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``description``                 | Long description for an input                                                  |
    +---------------+---------------------------------+--------------------------------------------------------------------------------+
    | ``outputs[]`` |                                 | List of Outputs that are generated by the Tool (and accessible to fastr)       |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``id``                          | ID of the Output                                                               |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``name``                        | Longer name of the Output (more human readable)                                |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``datatype``                    | The ID of the DataType of the Output [#f1]_                                    |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``enum[]``                      | List of possible values for an EnumType (created on the fly by fastr) [#f1]_   |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``prefix``                      | Commandline prefix of the Output (e.g. --out, -o)                              |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``cardinality``                 | Cardinality of the Output                                                      |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``repeat_prefix``               | Flag indicating if for every value of the Output the prefix is repeated        |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``required``                    | Flag indicating if the input is required                                       |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``nospace``                     | Flag indicating if there is no space between prefix and value (e.g. --out=val) |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``format``                      | For DataTypes that have multiple representations, indicate which one to use    |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``description``                 | Long description for an input                                                  |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``action``                      | Special action (defined per DataType) that needs to be performed before        |
    |               |                                 | creating output value (e.g. 'ensure' will make sure an output directory exists)|
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``automatic``                   | Indicate that output doesn't require commandline argument, but is created      |
    |               |                                 | automatically by a Tool [#f2]_                                                 |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``method``                      | The collector plugin to use for the gathering automatic output, see the        |
    |               |                                 | :ref:`Collector plugins <collectorplugin-ref>`                                 |
    |               +---------------------------------+--------------------------------------------------------------------------------+
    |               | ``location``                    | Definition where to an automatically, usage depends on the ``method`` [#f2]_   |
    +---------------+---------------------------------+--------------------------------------------------------------------------------+

    .. rubric:: Footnotes

    .. [#f1] ``datatype`` and ``enum`` are conflicting entries, if both specified ``datatype`` has presedence
    .. [#f2] More details on defining automatica output are given in [TODO]

    """

    __dataschemafile__ = 'FastrInterface.schema.json'

    collectors = CollectorPluginManager()
    collector_plugin_type = CollectorPlugin

    def __init__(self, id_, document):
        super(FastrInterface, self).__init__()

        # Load from file if it is not a dict
        if not isinstance(document, dict):
            fastr.log.debug('Trying to load file: {}'.format(document))
            filename = os.path.expanduser(document)
            filename = os.path.abspath(filename)
            document = self._loadf(filename)
        else:
            document = self.get_serializer().instantiate(document)

        #: The ID of the interface
        self.id = id_

        #: List of input parameter descriptions
        self.input_map = OrderedDict()

        #: List of output parameter descriptions
        self.output_map = OrderedDict()

        # Parse input and output fields into parameter_description objects
        for n_order, input_ in enumerate(document['inputs']):
            self.input_map[input_['id']] = InputParameterDescription(self, input_, n_order)
        n_inputs = len(self.input_map)

        for n_order, output in enumerate(document['outputs']):
            self.output_map[output['id']] = OutputParameterDescription(self, output, n_order + n_inputs)

        # Create the inputs/outputs spec to expose to the rest of the system
        self._inputs = HiddenFieldMap((k, InputSpec(id_=v.id,
                                                    cardinality=v.cardinality,
                                                    datatype=v.datatype,
                                                    required=v.required,
                                                    description=v.description,
                                                    default=v.default,
                                                    hidden=v.hidden)) for k, v in self.input_map.items())

        self._outputs = HiddenFieldMap((k, OutputSpec(id_=v.id,
                                                      cardinality=v.cardinality,
                                                      datatype=v.datatype,
                                                      automatic=v.automatic,
                                                      required=v.required,
                                                      description=v.description,
                                                      hidden=v.hidden)) for k, v in self.output_map.items())

    def __eq__(self, other):
        if not isinstance(other, FastrInterface):
            return NotImplemented

        return vars(self) == vars(other)

    def __getstate__(self):
        """
        Get the state of the FastrInterface object.

        :return: state of interface
        :rtype: dict
        """
        state = {
            'id': self.id,
            'class': type(self).__name__,
            'inputs': [x.__getstate__() for x in self.input_map.values()],
            'outputs': [x.__getstate__() for x in self.output_map.values()],
        }

        return state

    def __setstate__(self, state):
        """
        Set the state of the Interface
        """
        self.id = state['id']

        self.input_map = OrderedDict()
        self.output_map = OrderedDict()

        state['inputs'] = state['inputs'] or {}
        for order, x in enumerate(state['inputs']):
            self.input_map[x['id']] = InputParameterDescription(self, x, order)
        n_inputs = len(self.input_map)
        state['outputs'] = state['outputs'] or {}
        for order, x in enumerate(state['outputs']):
            self.output_map[x['id']] = OutputParameterDescription(self, x, order + n_inputs)

        # Create the inputs/outputs spec to expose to the rest of the system
        self._inputs = HiddenFieldMap((k, InputSpec(id_=v.id,
                                                    cardinality=v.cardinality,
                                                    datatype=v.datatype,
                                                    required=v.required,
                                                    description=v.description,
                                                    default=v.default,
                                                    hidden=v.hidden)) for k, v in self.input_map.items())

        self._outputs = HiddenFieldMap((k, OutputSpec(id_=v.id,
                                                      cardinality=v.cardinality,
                                                      datatype=v.datatype,
                                                      automatic=v.automatic,
                                                      required=v.required,
                                                      description=v.description,
                                                      hidden=v.hidden)) for k, v in self.output_map.items())

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def expanding(self):
        return 0

    def get_command(self, target, payload):
        return [target.binary] + self.get_arguments(payload)

    def execute(self, target, payload):
        """
        Execute the interface using a specific target and payload (containing
        a set of values for the arguments)

        :param target: the target to use
        :type target: :py:class:`SampleId <fastr.core.target.Target>`
        :param dict payload: the values for the arguments
        :return: result of the execution
        :rtype: InterfaceResult
        """
        fastr.log.info('Execution payload: {}'.format(payload))
        command = self.get_command(target=target, payload=payload)
        target_result = target.run_command(command)

        result = InterfaceResult(result_data={}, target_result=target_result, payload=payload, errors=None)

        # TODO: add the collection of results and log store here
        fastr.log.info('Collecting results')
        for output in self.outputs.values():
            if not output.automatic:
                if output.id in payload['outputs']:
                    result.result_data[output.id] = payload['outputs'][output.id]
                elif output.required:
                    raise exceptions.FastrValueError('Required output {} not in payload!'.format(output.id))

        self.collect_errors(result)
        self.collect_results(result)

        return result

    def check_input_id(self, id_):
        """
        Check if an id for an object is valid and unused in the Tool. The
        method will always returns True if it does not raise an exception.

        :param str id_: the id to check
        :return: True
        :raises FastrValueError: if the id is not correctly formatted
        :raises FastrValueError: if the id is already in use
        """

        regex = r'^\w[\w\d_]*$'
        if re.match(regex, id_) is None:
            raise exceptions.FastrValueError('An id in Fastr should follow'
                                             ' the following pattern {}'
                                             ' (found {})'.format(regex, id_))

        if id_ in self.input_map:
            raise exceptions.FastrValueError('The id {} is already in use in {}!'.format(id_, self.id))

        return True

    def check_output_id(self, id_):
        """
        Check if an id for an object is valid and unused in the Tool. The
        method will always returns True if it does not raise an exception.

        :param str id_: the id to check
        :return: True
        :raises FastrValueError: if the id is not correctly formatted
        :raises FastrValueError: if the id is already in use
        """

        regex = r'^\w[\w\d_]*$'
        if re.match(regex, id_) is None:
            raise exceptions.FastrValueError('An id in Fastr should follow'
                                             ' the following pattern {}'
                                             ' (found {})'.format(regex, id_))

        if id_ in self.output_map:
            raise exceptions.FastrValueError('The id {} is already in use in {}!'.format(id_, self.id))

        return True

    def get_arguments(self, values):
        """
        Get the argument list for this interface

        :return: return list of arguments
        """
        # Get the argument list
        arguments = list(self.input_map.values()) + list(self.output_map.values())
        arguments = sorted(arguments, key=lambda x: x.order if x.order >= 0 else sys.maxsize - x.order)

        argument_list = []

        for argument in arguments:
            id_ = argument.id

            try:
                if isinstance(argument, InputParameterDescription):
                    value = values['inputs'][id_]
                else:
                    value = values['outputs'][id_]

            except KeyError:
                if argument.default is not None:
                    if isinstance(argument.default, list):
                        value = tuple(argument.default)
                    else:
                        value = (argument.default,)
                elif argument.required and not (isinstance(argument, OutputParameterDescription) and argument.automatic):
                    raise exceptions.FastrValueError('Required argument "{}" has no value!'.format(argument.id))
                else:
                    value = None

            if value is not None:
                fastr.log.info('Adding {} to argument list based on {}'.format(value, argument))
                if argument.environ is not None:
                    argument.set_environ(value)
                else:
                    argument_list.extend(argument.get_commandline_argument(value))

        return argument_list

    def collect_results(self, result):
        """
        Collect all results of the interface
        """
        for output in self.output_map.values():
            if output.automatic:
                collector = self.collectors[output.method]

                # Do the try/except here so one failed output collection
                # does not stop the rest
                try:
                    collector.collect_results(self, output, result)

                    fastr.log.info('Collected automatic result for {}'.format(output.id))
                    fastr.log.info(result.result_data[output.id])
                except exceptions.FastrError as exception:
                    if output.required:
                        fastr.log.error('Encountered an error when collecting the results')
                        result.errors.append(exception.excerpt())
                    else:
                        fastr.log.info(('Non-required output {} did not yield'
                                        ' results due to collection error: {}').format(output.id,
                                                                                       exception))
                except BaseException as exception:
                    fastr.log.critical('Encountered unhandled exception: [{}] {}'.format(type(exception).__name__,
                                                                                         exception))
                    raise

    @staticmethod
    def collect_errors(result: InterfaceResult):
        """
        Special error collection for fastr interfaces
        """
        errors = []
        match = re.search('^__FASTR_ERRORS__ = (?P<value>.*)$',
                          result.target_result.stdout,
                          re.MULTILINE)

        if match is not None:
            value = match.group('value')
            try:
                value = json.loads(value)
            except ValueError:
                value = []

            if isinstance(value, list):
                errors.extend(value)
            else:
                message = "The errors should be a list, found a {}".format(
                    type(value).__name__
                )
                fastr.log.warning(message)

        match = re.search('^__FASTR_ERRORS__ = (?P<value>.*)$',
                          result.target_result.stderr,
                          re.MULTILINE)

        if match is not None:
            value = match.group('value')
            try:
                value = json.loads(value)
            except ValueError:
                value = []

            if isinstance(value, list):
                errors.extend(value)
            else:
                message = "The errors should be a list, found a {}".format(
                    type(value).__name__
                )
                fastr.log.warning(message)

        for error in errors:
            if isinstance(error, str):
                error = ('FromSubprocess', error, "unknown", "unknown")

            fastr.log.error('Got error from subprocess: {}'.format(
                error
            ))
            result.errors.append(error)

    def get_specials(self, payload, output, cardinality_nr):
        """
        Get special attributes. Returns tuples for specials, inputs and outputs
        that are used for formatting substitutions.

        :param output: Output for which to get the specials
        :param int cardinality_nr: the cardinality number
        """
        if output is not None:
            datatype = fastr.types[output.datatype]
            # Get extension match
            extensions = set()
            # Collect possible extensions we can encounter
            if issubclass(datatype, URLType):
                if isinstance(datatype.extension, str):
                    extensions.add(datatype.extension)
                elif isinstance(datatype.extension, Iterable):
                    extensions.update(datatype.extension)
                else:
                    extensions.add('')
            elif issubclass(datatype, TypeGroup):
                for member in datatype.members:
                    if isinstance(member.extension, str):
                        extensions.add(member.extension)
                    elif isinstance(member.extension, Iterable):
                        extensions.update(member.extension)
                    else:
                        extensions.add('')
            else:
                extensions.add('')

            # Format the extension set into a proper string
            if len(extensions) > 1:
                # This is a regexp where each extension is allowed
                extension = '({})'.format('|'.join(extensions))
            elif len(extensions) == 1:
                # This is just a single extension as a string
                extension = extensions.pop()
            else:
                extension = ''
        else:
            extension = ''

        specials_tuple_type = namedtuple('Specials', ['cardinality', 'extension', 'workdir'])
        specials = specials_tuple_type(cardinality_nr, extension, os.path.abspath(os.curdir))

        if len(self.input_map) > 0:
            # Gather the data
            input_data = OrderedDict()
            for input_id, input_ in self.input_map.items():
                temp_data = payload['inputs'][input_id] if input_id in payload['inputs'] else [input_.default]
                input_data[input_id] = [PathDescription(x) for x in temp_data]

            # Create a named tuple
            inputs_tuple_type = namedtuple('Inputs', list(input_data.keys()))
            inputs = inputs_tuple_type(*list(input_data.values()))
        else:
            inputs = ()

        output_arguments = [x for x in self.output_map.values() if not x.automatic]
        if len(output_arguments) > 0:
            # Gather the data
            output_data = OrderedDict()
            for output_id, ouput in self.output_map.items():
                temp_data = payload['outputs'][output_id] if output_id in payload['outputs'] else [output.default]
                output_data[output_id] = [PathDescription(x) for x in temp_data]

            # Create a named tuple
            outputs_tuple_type = namedtuple('Outputs', [x.id for x in self.output_map.values()])
            outputs = outputs_tuple_type(*list(output_data.values()))
        else:
            outputs = ()

        return specials, inputs, outputs


class ParameterDescription(Serializable):
    """
    Description of an input or output parameter used by a Tool. This is the
    super class for both input and output, containing the shared parts.
    """
    _IS_INPUT = False

    def __init__(self, parent, element, order=0):
        """
        Instantiate a ParameterDescription

        :param Tool parent: parent tool
        :param dict element: description of the parameter
        :param order: the order in which the parameter was defined in the file
        """
        self.parent = parent

        if isinstance(element, dict):
            self.id = element['id']
            self.name = element['name']

            if 'datatype' in element:
                self.datatype = element['datatype']
            elif 'enum' in element:
                element['enum'] = [str(x) for x in element['enum']]
                self.datatype = '__{}__{}__Enum__'.format(parent.id, self.id)
                fastr.types.create_enumtype(self.datatype, tuple(element['enum']), self.datatype)
            else:
                raise exceptions.FastrValueError('No valid datatype defined for {}'.format(self.id))

            self.prefix = element.get('prefix', None)
            self.repeat_prefix = element.get('repeat_prefix', False)
            self.cardinality = element.get('cardinality', 1)
            self.nospace = element.get('nospace', False)
            self.format = element.get('format', None)
            self.required = element.get('required', True)
            self.default = element.get('default', None)
            self.description = element.get('description', '')
            self.order = element.get('order', order)
            self.hidden = element.get('hidden', False)
            self.join = element.get('join', None)
            self.environ = element.get('environ', None)
        else:
            raise exceptions.FastrTypeError('element should be a dict')

    def __eq__(self, other):
        """
        Compare two ParameterDescription instance with eachother. This
        function helps ignores the parent, but once tests the values for
        equality

        :param other: the other instances to compare to

        :returns: True if equal, False otherwise
        """
        if not isinstance(other, ParameterDescription):
            return NotImplemented

        dict_self = dict(vars(self))
        del dict_self['parent']

        dict_other = dict(vars(self))
        del dict_other['parent']

        return dict_self == dict_other

    def __getstate__(self):
        """
        Retrieve the state of the ParameterDescription

        :return: the state of the object
        :rtype dict:
        """
        state = dict(vars(self))
        state['parent'] = self.parent.id

        datatype = fastr.types[self.datatype]
        if issubclass(datatype, EnumType):
            del state['datatype']
            state['enum'] = list(datatype.options)

        return state

    def __setstate__(self, state):
        """
        Set the state of the ParameterDescription by the given state.

        :param dict state: The state to populate the object with
        """
        if 'datatype' not in state:
            if 'enum' in state:
                typename = '__{}__{}__Enum__'.format(state['parent'], state['id'])
                state['datatype'] = typename
                fastr.types.create_enumtype(typename, tuple(state['enum']), typename)
            else:
                raise exceptions.FastrValueError('No valid datatype defined for {} in {}'.format(state['id'], state))

        self.__dict__.update(state)

    def get_commandline_argument(self, value):
        """
        Get the commandline argument for this Parameter given the values
        assigned to it.

        :param value: the value(s) for this input
        :return: commandline arguments
        :rtype: list
        """
        argument = []
        if isinstance(value, tuple):
            if self.join is not None:
                datatype = fastr.types[self.datatype]
                value = self.join.join(str(x if datatype.isinstance(x) else datatype(x)) for x in value),

            for cardinality_nr, value_item in enumerate(value):
                if self.join is None:
                    value_item = self.format_argument_value(value_item)

                argument.extend(self.format_prefix(value_item, cardinality_nr))

        elif isinstance(value, OrderedDict):
            sep = self.join or ','
            for cardinality_nr, (key, value_item) in enumerate(value.items()):
                value_item = sep.join(self.format_argument_value(x) for x in value_item if x is not None)
                argument.extend(self.format_prefix('{}={}'.format(key, value_item), cardinality_nr))
        else:
            raise exceptions.FastrTypeError('Argument should be tuple or OrderedDict!')

        return argument

    def set_environ(self, value):
        """
        Set environment variable for argument if needed
        :param value: value to set
        """
        if self.environ is None:
            return

        if isinstance(value, tuple):
            sep = self.join or ','
            datatype = fastr.types[self.datatype]
            value = sep.join(str(x if datatype.isinstance(x) else datatype(x)) for x in value)
        elif isinstance(value, OrderedDict):
            value = json.dumps(value)

        os.environ[self.environ] = value

    def format_prefix(self, value, cardinality_nr):
        extra_argument = []

        # Build the prefix
        prefix = self.prefix
        if prefix is not None:
            if prefix.strip() == '':
                prefix = None
            elif cardinality_nr == 0 or self.repeat_prefix:
                prefix = self.prefix.replace('#', str(cardinality_nr))
            else:
                prefix = None

        # Handle special case for boolean flags
        if value.startswith('__FASTR_FLAG__'):
            if value == '__FASTR_FLAG__FALSE__':
                return []
            else:
                if prefix is None:
                    raise exceptions.FastrValueError('Found non-prefixed arguments with type'
                                                     ' Boolean (flag). This is not possible,'
                                                     ' a flag should always have a proper prefix!')
                return [self.prefix.replace('#', str(cardinality_nr))]

        # Handle the normal cases
        if self.nospace:
            if prefix is None:
                raise exceptions.FastrValueError('Found a nospace without a valid prefix! When'
                                                 ' nospace is true a valid prefix should be'
                                                 ' specified (and repeat prefix should be used)!')
            extra_argument.append('{}{}'.format(self.prefix, value))
        else:
            if prefix is not None:
                extra_argument.append(prefix)
            if value is not None:
                extra_argument.append(value)

        return extra_argument

    def format_argument_value(self, value, datatype=None):
        if datatype is None:
            datatype = fastr.types[self.datatype]

        if not datatype.isinstance(value):
            fastr.log.debug('CREATING DATATYPE {!r} for {!r}!'.format(datatype, value))
            value = datatype(value)

        # Format (and validate if required) the input value
        value.format = self.format
        if self._IS_INPUT and not value.valid:
            fastr.log.debug('SELF TYPE: {}, ID {}'.format(type(self).__name__, self.id))
            raise exceptions.FastrDataTypeValueError('Value for input {} not a valid instance of type {} (value: {} ({} / {!r}) -> {})'.format(self.id, datatype.id, value, type(value).__name__, value.value, value.valid))

        value = str(value)

        # Filter out boolean flags
        return value


class InputParameterDescription(ParameterDescription):
    """
    Description of an input parameter used by a Tool.
    """
    _IS_INPUT = True

    def __init__(self, parent, element, order=0):
        """
        Instantiate an InputParameterDescription

        :param Tool parent: parent tool
        :param dict element: description of the parameter
        :param order: the order in which the parameter was defined in the file
        """
        if isinstance(element, dict):
            super(InputParameterDescription, self).__init__(parent, element, order)
            self.parent.check_input_id(element['id'])
        else:
            raise exceptions.FastrTypeError('element should be a dict')


class OutputParameterDescription(ParameterDescription):
    """
    Description of a output parameter used by a Tool.
    """
    def __init__(self, parent, element, order=0):
        """
        Instantiate an OutputParameterDescription

        :param Tool parent: parent tool
        :param dict element: description of the parameter
        :param order: the order in which the parameter was defined in the file
        """
        if isinstance(element, dict):
            super(OutputParameterDescription, self).__init__(parent, element, order)
            self.parent.check_output_id(element['id'])
            self.automatic = element.get('automatic', False)
            if self.automatic:
                # Automatic outputs with a prefix are not required by default
                self.required = element.get('required', False)
            self.action = element.get('action', None)
            self.location = element.get('location', None)
            self.separator = element.get('separator', None)
            if self.automatic:
                self.method = element.get('method', 'path')
            else:
                self.method = element.get('method', None)
            self.negate = element.get('negate', False)
        else:
            raise exceptions.FastrTypeError('element should be a dict')

    def __setstate__(self, state):
        """
        Set the state of the OutputParameterDescription by the given state.

        :param dict state: The state to populate the object with
        """
        if 'location' not in state:
            state['location'] = None

        if 'separator' not in state:
            state['separator'] = None

        if 'method' not in state:
            if 'automatic' not in state or not state['automatic']:
                state['method'] = None
            else:
                state['method'] = 'path'

        if 'action' not in state:
            state['action'] = None

        if 'negate' not in state:
            state['negate'] = False

        super(OutputParameterDescription, self).__setstate__(state)

    def get_commandline_argument(self, values):
        """
        Get the commandline argument for this Parameter given the values
        assigned to it.

        :param value: the value(s) for this input
        :return: commandline arguments
        :rtype: list
        """
        if self.action is not None:
            if self.action in self.ACTIONS:
                action_func = self.ACTIONS[self.action]
                for value in values:
                    fastr.log.info('Calling action {} for {}'.format(action_func, value))
                    action_func(self, value)
            else:
                fastr.log.warning('Encountered unknown action {}, only know: {}'.format(self.action,
                                                                                        list(self.ACTIONS.keys())))

        if not self.automatic or self.prefix is not None:
            if self.automatic and self.prefix and self.negate:
                fastr.log.info('Negating value for automatic prefixed output: {}'.format(self.id))
                fastr.log.info('Values before: {}'.format(values))
                if isinstance(values, tuple):
                    values = tuple(fastr.datatypes.Boolean(not x.value) for x in values)
                elif isinstance(value, OrderedDict):
                    for key, value in values.items():
                        values[key] = tuple(fastr.datatypes.Boolean(not x.value) for x in value)
                else:
                    raise exceptions.FastrTypeError('Argument should be tuple or OrderedDict!')
                fastr.log.info('Values after: {}'.format(values))

            return super(OutputParameterDescription, self).get_commandline_argument(values)
        else:
            return []

    def format_argument_value(self, value):
        # For the non-automatic case, nothing special happens
        if self.automatic:
            datatype = fastr.types['Boolean']
            return super(OutputParameterDescription, self).format_argument_value(value,
                                                                                 datatype=datatype)
        else:
            return super(OutputParameterDescription, self).format_argument_value(value)

    def mkdirs(self, value):
        """
        Create the directory if it does not yet exist

        :param URLType value: the directory to create
        """
        value = str(value)
        if not os.path.exists(value):
            os.makedirs(value)

    ACTIONS = {'ensure': mkdirs,
               'mkdir': mkdirs}
