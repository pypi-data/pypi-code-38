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

"""A module to maintain a tool.

Exported classes:

* Tool -- A class encapsulating a tool.
* ParameterDescription -- The base class containing the shared description of
  a parameter (both input and ouput).
* InputParameterDescription -- A class containing the description of an input
  parameter.
* Output ParameterDescription -- A class containing the description of an
  output parameter.
"""

import itertools
import os
import platform
import re
import shutil
from collections import namedtuple, OrderedDict
from tempfile import mkdtemp

import jsonschema

from . import vfs_plugin
from .cardinality import create_cardinality
from .interface import InterfaceResult
from .version import Version
from .. import exceptions
from ..abc.baseplugin import PluginState
from ..abc.serializable import Serializable
from ..datatypes import types
from ..helpers import log, config
from ..helpers.checksum import hashsum
from ..helpers import iohelpers
from .. import resources


class Tool(Serializable):
    """
    The class encapsulating a tool.
    """

    __dataschemafile__ = 'Tool.schema.json'

    test_spec = namedtuple('TestSpecification', ['input', 'command', 'output'])
    TOOL_REFERENCE_FILE_NAME = '__fastr_tool_ref__.json'
    TOOL_RESULT_FILE_NAME = '__fastr_tool_result.pickle.gz'

    DEFAULT_TARGET_CLASS = {
        'MacroNode': 'MacroTarget'
    }

    def __init__(self, doc=None):
        """
        Create a new Tool
        :param doc: path of toolfile or a dict containing the tool data
        :type doc: str or dict
        """

        # Cache value for target binary
        self._target = None

        if doc is None:
            return

        filename = None
        if not isinstance(doc, dict):
            log.debug('Trying to load file: {}'.format(doc))
            filename = os.path.expanduser(doc)
            filename = os.path.abspath(filename)
            doc = self._loadf(filename)

        # Check if the doc is a valid Tool structure
        try:
            # __unserializer__ is supplied by the serializable meta-class
            # pylint: disable=no-member
            doc = Tool.get_serializer().instantiate(doc)
        except jsonschema.ValidationError:
            log.error('Could not validate Tool data again the schema!')
            raise
        else:
            log.debug('Tool schema validated!')

        # Get attributes from root node
        self.filename = filename

        #: Identifier for the tool
        regex = r'^[A-Z][\w\d_]*$'
        if re.match(regex, doc['id']) is None:
            message = 'A tool id in Fastr should be UpperCamelCase as enforced' \
                      ' by regular expression {} (found {})'.format(regex, doc['id'])
            log.warning(message)

        self._id = doc['id']

        #: The namespace this tools lives in, this will be set by the ToolManager on load
        self.namespace = None

        #: Name of the tool, this should be a descriptive, human readable name.
        self.name = doc.get('name', self._id)

        #: Version of the tool, not of the underlying software
        self.version = Version(str(doc.get('version')))

        #: Class for of the Node to use
        self.node_class = doc.get('class', 'Node')

        if self._id is None or self.name is None or self.version is None:
            raise exceptions.FastrValueError('Tool should contain an id, name and version!')

        #: URL to website where this tool can be downloaded from
        self.url = doc.get('url', '')

        #: Description of the tool and it's functionality
        self.description = doc.get('description', '')

        #: List of authors of the tool. These people wrapped the executable but
        #: are not responsible for executable itself.
        self.authors = doc['authors']

        #: List of tags for this tool
        self.tags = doc.get('tags', [])

        # Parse references field and format them into a dictionary
        #: A list of documents and in depth reading about the methods used in this tool
        self.references = doc.get('references', [])

        #: Requirements for this Tool
        #:
        #: .. warning:: Not yet implemented
        self.requirements = None

        #: Test for this tool. A test should be a collection of inputs, parameters
        #: and outputs to verify the proper functioning of the Tool.
        #:
        #: The format of the tests is a list of namedtuples, that have 3 fields:
        #: - input: a dict of the input data
        #: - command: a list given the expected command-line arguments
        #: - output: a dict of the output data to validate
        #:
        #: .. warning:: Not yet implemented

        self.tests = doc['tests']

        command = doc['command']

        # Find commands
        #: Command is a dictionary contain information about the command which is
        #: called by this Tool:
        #: command['interpreter'] holds the (possible) interpreter to use
        #: command['targets'] holds a per os/arch dictionary of files that should be executed
        #: command['url'] is the webpage of the command to be called
        #: command['version'] is the version of the command used
        #: command['description'] can help a description of the command
        #: command['authors'] lists the original authors of the command
        self.command = {
            'targets': command['targets'],
            'license': command.get('license', ''),
            'url': command.get('url', ''),
            'version': Version(str(command.get('version'))),
            'description': command.get('description', ''),
            'authors': command.get('authors', [])
        }

        if len(self.command['targets']) == 0:
            raise exceptions.FastrValueError("No targets defined in tool description.")

        #: This holds the citation you should use when publishing something based on this Tool
        self.cite = doc['cite']

        #: Man page for the Tool. Here usage and examples can be described in detail
        self.help = doc['help']

        #: Create the Interface based on the class specified in the tool file
        interface_class = resources.interfaces[doc['interface'].get('class', 'FastrInterface')]

        if interface_class.status != PluginState.loaded:
            raise exceptions.FastrPluginNotLoaded(
                'Required InterfacePlugin {} was not loaded properly (status {})'.format(interface_class.id,
                                                                                         interface_class.status)
            )

        self.interface = interface_class(id_='{}_{}_interface'.format(self.id, self.command['version']),
                                         document=doc['interface'])

    @property
    def hash(self):
        return hashsum(self.__getstate__())

    @property
    def id(self):
        return '{}:{}'.format(self._id, self.command['version'])

    @property
    def ns_id(self):
        """
        The namespace and id of the Tool
        """
        if self.namespace is None:
            return self.id
        else:
            return '{}/{}'.format(self.namespace, self.id)

    @property
    def fullid(self):
        """
        The full id of this tool
        """
        return 'fastr:///tools/{}/{}'.format(self.ns_id, self.version)

    @property
    def inputs(self):
        return self.interface.inputs

    @property
    def outputs(self):
        return self.interface.outputs

    @property
    def target(self):
        """
        The OS and arch matched target definition.
        """
        if self._target is not None:
            return self._target

        # Get platform and os
        arch = platform.architecture()[0].lower()
        os_ = platform.system().lower()

        matching_targets = [x for x in self.command['targets'] if x['os'] in [os_, '*'] and x['arch'] in [arch, '*']]

        if len(matching_targets) == 0:
            return None
        elif len(matching_targets) == 1:
            target = matching_targets[0]
        else:
            # This should give the optimal match
            for match in matching_targets:
                match['score'] = 0

                if match['os'] == os_:
                    match['score'] += 2

                if match['arch'] == arch:
                    match['score'] += 1

            matching_targets = sorted(matching_targets, reverse=True, key=lambda x: x['score'])
            log.debug('Sorted matches: {}'.format(matching_targets))
            target = matching_targets[0]

        # Make sure target is a copy
        target = dict(target)
        cls = self.DEFAULT_TARGET_CLASS.get(self.node_class)
        if cls is None:
            cls = target.pop('class', 'LocalBinaryTarget')
        cls = resources.targets[cls]

        # Create target from curdir
        old_curdir = os.path.abspath(os.curdir)
        os.chdir(self.path)

        # Check if the argument binary exists (or use bin as alternative)
        if 'binary' not in target and 'bin' in target:
            target['binary'] = target.pop('bin')

        # Remove needless fields
        target.pop('os', None)
        target.pop('arch', None)

        # Instantiate target
        try:
            self._target = cls(**target)
        except Exception as exception:
            log.error('Could not load tool {} because the following exception was encountered: {}'.format(
                self.ns_id, exception
            ))
            raise

        os.chdir(old_curdir)

        return self._target

    def _prepare_payload(self, payload=None, **kwargs):
        # Allow kwargs to be used instead of payload
        if payload is None:
            payload = {'inputs': {}, 'outputs': {}}
            for key, value in kwargs.items():
                if key in self.inputs and key in self.outputs:
                    raise exceptions.FastrValueError(
                        'Cannot figure out if "{}" is an input or output, please prefix with input_/output_ as needed'
                    )
                elif key in self.inputs:
                    payload['inputs'][key] = value
                elif key in self.outputs:
                    payload['outputs'][key] = value
                elif key.startswith('input_') and key[6:] in self.inputs:
                    payload['inputs'][key[6:]] = value
                elif key.startswith('output_') and key[7:] in self.outputs:
                    payload['outputs'][key[7:]] = value
                else:
                    raise exceptions.FastrValueError('Cannot match key "{}" to any input/output!'.format(key))

        # Make sure all values are wrapped in a tuple (for single values)
        for key, value in payload['inputs'].items():
            if not isinstance(value, (tuple, OrderedDict)):
                payload['inputs'][key] = (value,)
        for key, value in payload['outputs'].items():
            if not isinstance(value, (tuple, OrderedDict)):
                payload['outputs'][key] = (value,)

        return payload

    def _validate_payload(self, payload):
        for input_ in self.inputs.values():
            if input_.id not in payload['inputs']:
                if input_.required:
                    raise exceptions.FastrValueError('Could not find data for required input {}'.format(input_.id))
                else:
                    continue

            value = payload['inputs'][input_.id]

            if not isinstance(value, (tuple, OrderedDict)):
                raise exceptions.FastrTypeError('Value needs to be a tuple or OrderedDict')

            cardinality_spec = create_cardinality(input_.cardinality, None)
            if not (not input_.required and len(value) == 0) and \
                    not cardinality_spec.validate(payload, len(value)):
                raise exceptions.FastrValueError(
                    'Input cardinality mismatch for {}. Cardinality "{}" does not match "{!r}"'.format(
                        input_.id,
                        len(value),
                        cardinality_spec,
                    )
                )

            datatype = types.get(input_.datatype)

            # If the input has named sub-inputs we need to collapse the structure
            # before checking the datatypes
            if isinstance(value, OrderedDict):
                value = (x for y in value.values() for x in y)

            if datatype is not None and not all(datatype.isinstance(x) for x in value):
                raise exceptions.FastrTypeError('Input {} has an incorrect datatype (found {}, expected {})'.format(
                    input_.id,
                    set(type(x) for x in value),
                    datatype
                ))

    def execute(self, payload=None, **kwargs) -> InterfaceResult:
        """
        Execute a Tool given the payload for a single run

        :param payload: the data to execute the Tool with
        :returns: The result of the execution
        :rtype: InterFaceResult
        """
        payload = self._prepare_payload(payload=payload, **kwargs)

        # Make sure hte payload is valid
        self._validate_payload(payload)

        # Set environment variables if not set
        os.environ.setdefault('FASTR_SAMPLE_ID', 'UNKNOWN')
        os.environ.setdefault('FASTR_SAMPLE_INDEX', '0')
        os.environ.setdefault('FASTR_JOB_ID', 'fastr_interactive_0')
        os.environ.setdefault('FASTR_WORK_DIR', 'UNKNOWN')

        target = self.target
        log.info('Target is {}'.format(target))

        if target is None:
            arch = platform.architecture()[0].lower()
            os_ = platform.system().lower()
            raise exceptions.FastrValueError(
                'Cannot find a viable target for {}/{} on {} ({} bit)'.format(self.id, self.version, os_, arch)
            )

        log.info('Using payload: {}'.format(payload))
        with target:
            result = self.interface.execute(target, payload)

        return result

    def __str__(self):
        """
        Get a string version for the Tool

        :return: the string version
        :rtype: str
        """
        return '<Tool: {} version: {}>'.format(self.id, self.version)

    def __repr__(self):
        """
        Get a string representation for the Tool. This will show the inputs
        and output defined in a table-like structure.

        :return: the string representation
        :rtype: str
        """
        if self.name is not None and len(self.name) > 0:
            name_part = ' ({})'.format(self.name)
        else:
            name_part = ''

        return_list = ["Tool {} v{}{}".format(self.id, str(self.command['version']), name_part)]

        # The "+ [8]" guarantees a minimum of 8 width and avoids empty lists
        width_input_keys = max([len(x.id) for x in self.inputs.values()] + [8])
        width_input_types = max([len(x.datatype) for x in self.inputs.values()] + [8]) + 2
        width_output_keys = max([len(x.id) for x in self.outputs.values()] + [8])
        width_output_types = max([len(x.datatype) for x in self.outputs.values()] + [8]) + 2

        return_list.append('{:^{}}  | {:^{}}'.format('Inputs', width_input_types + width_input_keys + 1,
                                                     'Outputs', width_output_types + width_output_keys + 1))
        return_list.append('-' * (width_input_keys + width_input_types + width_output_keys + width_output_types + 7))
        for input_, output in itertools.zip_longest(self.inputs.values(), self.outputs.values()):
            if input_ is None:
                input_id = ''
                input_type = ''
            else:
                input_id = input_.id
                input_type = '({})'.format(input_.datatype)

            if output is None:
                output_id = ''
                output_type = ''
            else:
                output_id = output.id
                output_type = '({})'.format(output.datatype)

            return_list.append('{:{}} {:{}}  |  {:{}} {:{}}'.format(input_id, width_input_keys,
                                                                    input_type, width_input_types,
                                                                    output_id, width_output_keys,
                                                                    output_type, width_output_types))

        return '\n'.join(return_list)

    def __eq__(self, other):
        """Compare two Tool instances with each other.

        :param other: the other instances to compare to
        :type other: Tool
        :returns: True if equal, False otherwise
        """
        if not isinstance(other, Tool):
            return NotImplemented

        dict_self = dict(self.__dict__)
        del dict_self['_target']
        del dict_self['namespace']
        del dict_self['filename']

        dict_other = dict(other.__dict__)
        del dict_other['_target']
        del dict_other['namespace']
        del dict_other['filename']

        return dict_self == dict_other

    def __getstate__(self):
        """
        Retrieve the state of the Tool

        :return: the state of the object
        :rtype dict:
        """
        state = dict(vars(self))
        state['command'] = {k: v for k, v in list(self.command.items())}

        state['class'] = state['node_class']
        state['interface'] = self.interface.__getstate__()
        state['command']['version'] = str(self.command['version'])
        state['version'] = str(self.version)
        state['id'] = self._id
        del state['node_class']
        del state['_target']

        return state

    def _serialize(self):
        """
        Prepare data for serialization, this removes some fields from the state
        that are not needed when serializing to a file
        """
        state = self.__getstate__()

        # Data stub to be ordered
        data = {
            "id": self._id,
            "name": self.name,
            "version": str(self.version),
            "description": self.description,
            "authors": self.authors,
            "class": state['class'],
            "command": state['command'],
            "interface": state['interface'],
        }

        # Set of items to skip
        skip = {'_id', 'namespace', 'filename'}

        for key, value in state.items():
            if key in skip or key in data:
                continue

            data[key] = value

        return data

    def __setstate__(self, state):
        """
        Set the state of the Tool by the given state.

        :param dict state: The state to populate the object with
        """
        if 'filename' not in state:
            state['filename'] = None

        if 'namespace' not in state:
            state['namespace'] = None

        if 'id' in state:
            state['_id'] = state.pop('id')
            
        state['version'] = Version(state['version'])
        state['command']['version'] = Version(str(state['command']['version']))

        state['node_class'] = state['class']
        del state['class']

        interface_class = resources.interfaces[state['interface'].get('class', 'FastrInterface')]
        if 'id' not in state['interface']:
            state['interface']['id'] = '{}_{}_interface'.format(state['_id'], state['command']['version'])

        if interface_class.status != PluginState.loaded:
            raise exceptions.FastrPluginNotLoaded(
                'Required InterfacePlugin {} was not loaded properly (status {})'.format(interface_class.id,
                                                                                         interface_class.status)
            )

        state['interface'] = interface_class.createobj(state['interface'])
        self.__dict__.update(state)
        self._target = None

    @property
    def path(self):
        """
        The path of the directory in which the tool definition file was
        located.
        """
        return os.path.dirname(self.filename)

    @property
    def command_version(self):
        return self.command['version']

    def create_reference(self, input_data, output_directory, mount_name='__ref_tmp__', copy_input=True):
        # Make sure the output directory is absolute for later on
        output_directory = os.path.abspath(os.path.expanduser(output_directory))

        # Create output directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        input_data_dir = os.path.join(output_directory, 'input_data')

        if not os.path.exists(input_data_dir):
            os.mkdir(input_data_dir)

        output_data_dir = os.path.join(output_directory, 'output_data')

        if not os.path.exists(output_data_dir):
            os.mkdir(output_data_dir)

        # Add the temporary mount
        config.read_config_string('mounts["{}"] = "{}"'.format(mount_name, output_directory))

        # If desired, copy input data to data directory in output directory
        if copy_input:
            log.info('Copying input data into reference directory...')
            new_input_data = {}
            stored_input_data = {}
            for input_id, input_value in input_data.items():
                new_input_value = []
                stored_input_value = []

                # Make sure we are working with tuples
                if isinstance(input_value, list):
                    input_value = tuple(input_value)

                if not isinstance(input_value, tuple):
                    input_value = input_value,

                # Datatype for this input
                datatype = types[self.inputs[input_id].datatype]

                # If needed copy the data
                for value in input_value:
                    if isinstance(value, str) and os.path.exists(value):
                        filename = os.path.basename(value)
                        destination = 'vfs://{}/input_data/{}'.format(mount_name, filename)
                        vfs_plugin.push_sink_data(value, destination, datatype=datatype)
                        new_input_value.append(vfs_plugin.url_to_path(destination))
                        stored_input_value.append('$REFDIR/input_data/{}'.format(filename))
                    else:
                        new_input_value.append(value)
                        stored_input_value.append(value)
                new_input_data[input_id] = tuple(new_input_value)
                stored_input_data[input_id] = tuple(stored_input_value)
        else:
            new_input_data = input_data
            stored_input_data = input_data

        test_data = {
            'input_data': stored_input_data,
            'used_input_data': new_input_data,
            'original_input_data': input_data,
            'tool': self.ns_id,
            'version': str(self.command_version),
        }

        # New replace input_data with new input data
        input_data = new_input_data

        # Save the test summary to the reference file
        log.info('Saving basic reference information')
        iohelpers.save_json(
            os.path.join(output_directory, self.TOOL_REFERENCE_FILE_NAME),
            test_data
        )

        # Reference payload as a shortcut
        payload = {'inputs': input_data, 'outputs': {}}

        # Create output arguments automatically
        from fastr.execution.job import Job

        log.info('Determining values for outputs')
        for id_, argument in self.outputs.items():
            # Determine cardinality
            if not argument.automatic:
                cardinality = argument.cardinality.calc_cardinality(payload)
            else:
                cardinality = 1

            # Create output arguments automatically
            payload['outputs'][id_] = Job.fill_output_argument(output_spec=argument,
                                                               cardinality=cardinality,
                                                               desired_type=types[argument.datatype],
                                                               requested=True,
                                                               tmpurl='vfs://{}/output_data'.format(mount_name))

        log.info('Resulting test data: {}'.format(test_data))

        log.info('Executing tool...')
        result = self.execute(payload=payload)
        result.command = result.target_result.command

        # Translate command to avoid hard links to output_directory
        log.info('Processing results for use as reference data')

        # Do no substitute for input data
        pattern = r'^{}'.format(output_data_dir)
        result.reference_command = [re.sub(pattern, '$OUTDIR', x, 1) for x in result.target_result.command]
        result.reference_command = ['$INDIR/{}'.format(os.path.basename(x)) if os.path.exists(x) else x
                                    for x in result.reference_command]

        # Translate results back
        output_data = {}
        for key, value in result.result_data.items():
            datatype = types[self.outputs[key].datatype]
            preferred_type = datatype

            output_data[key] = Job.translate_output_results(value,
                                                            datatype=datatype,
                                                            preferred_type=preferred_type,
                                                            mountpoint=mount_name)

        result.output_data = output_data

        config.read_config_string('del mounts["{}"]'.format(mount_name))

        log.info('Saving results for reference...')
        iohelpers.save_gpickle(
            os.path.join(output_directory, self.TOOL_RESULT_FILE_NAME),
            result
        )
        log.info('Finishing creating reference data for {}/{}'.format(self.ns_id, self.command_version))

    @staticmethod
    def compare_output_data(current_output_data, reference_output_data, validation_result, output):
        log.info('Current output data: {}'.format(current_output_data))
        log.info('Reference output data: {}'.format(reference_output_data))
        for nr, (current_value, reference_value) in enumerate(zip(current_output_data, reference_output_data)):
            if current_value != reference_value:
                validation_result.append('\n'.join((
                    'Value for {}/{} was not equal! (found "{}", expected "{}")'.format(
                        output,
                        nr,
                        current_value,
                        reference_value,
                    ),
                    'Output: [{}] {!r}'.format(type(current_value).__name__,
                                               current_value),
                    'Reference: [{}] {!r}'.format(type(reference_value).__name__,
                                                  reference_value),
                )))

    @classmethod
    def test_tool(cls, reference_data_dir, tool=None, input_data=None):
        """
        Execute the tool with the input data specified and test the results
        against the refence data. This effectively tests the tool execution.

        :param str reference_data_dir: The path or vfs url of reference data to compare with
        :param dict source_data: The source data to use
        """
        if not isinstance(reference_data_dir, str):
            raise exceptions.FastrTypeError('reference_data_dir should be a string!')

        if reference_data_dir.startswith('vfs://'):
            reference_data_dir = vfs_plugin.url_to_path(reference_data_dir)

        if not os.path.isdir(reference_data_dir):
            raise exceptions.FastrTypeError('The reference_data_dir should be pointing to an existing directory!'
                                            ' {} does not exist'.format(reference_data_dir))

        test_data = iohelpers.load_json(
            os.path.join(reference_data_dir, cls.TOOL_REFERENCE_FILE_NAME)
        )

        if tool is None:
            tool = resources.tools[test_data['tool'], test_data['version']]

        log.info('Testing tool {}/{} against {}'.format(
            tool.ns_id,
            tool.command_version,
            reference_data_dir,
        ))

        if input_data is None:
            input_data = {}

            for key, value in test_data['input_data'].items():
                if not isinstance(value, (tuple, list)):
                    value = value,

                # Set the $REFDIR correctly (the avoid problems with moving the reference dir)
                value = tuple(x.replace('$REFDIR', reference_data_dir) if isinstance(x, str) else x for x in value)
                input_data[key] = value

        temp_results_dir = None
        reference_result = iohelpers.load_gpickle(os.path.join(reference_data_dir, cls.TOOL_RESULT_FILE_NAME))

        validation_result = []
        try:
            # Create temporary output directory
            temp_results_dir = os.path.normpath(mkdtemp(
                prefix='fastr_tool_test_{}_'.format(tool.id), dir=config.mounts['tmp']
            ))

            # Create a new reference for comparison
            log.info('Running tool and creating new reference data for comparison...')
            try:
                tool.create_reference(input_data,
                                      temp_results_dir,
                                      mount_name='__test_tmp__',
                                      copy_input=False)
            except Exception as exception:
                log.warning('Encountered exception when trying to run the {}/{} tool!'.format(
                    tool.ns_id, tool.command_version)
                )
                log.warning('Exception: [{}] {}'.format(type(exception).__name__, exception))
                validation_result.append('Encountered {}: {}'.format(type(exception).__name__, exception))
                return validation_result

            current_result = iohelpers.load_gpickle(os.path.join(temp_results_dir, cls.TOOL_RESULT_FILE_NAME))

            log.info('Comparing current run against reference run...')

            # First check the command and return code
            if current_result.reference_command != reference_result.reference_command:
                validation_result.append('\n'.join((
                    'Different command used for execution of tool "{}/{}"'.format(tool.ns_id, tool.command_version),
                    'Current command: {}'.format(current_result.reference_command),
                    'Reference command {}'.format(reference_result.reference_command),
                )))

            if current_result.target_result.returncode != reference_result.target_result.return_code:
                validation_result.append('\n'.join((
                    'Different returncode used for execution of tool "{}/{}"'.format(tool.ns_id,
                                                                                     tool.returncode_version),
                    'Current returncode: {}'.format(current_result.target_result.returncode),
                    'Reference returncode {}'.format(reference_result.target_result.returncode),
                )))

            # Check if the outputs are the same
            current_outputs = sorted(reference_result.output_data.keys())
            reference_outputs = sorted(current_result.output_data.keys())
            if current_outputs != reference_outputs:
                validation_result.append('\n'.join((
                    'Different outputs found in tool "{}/{}"'.format(tool.ns_id, tool.command_version),
                    'Current outputs: {}'.format(current_outputs),
                    'Reference outputs {}'.format(reference_outputs),
                )))

            # Add the mounts need to find the data
            config.read_config_string('mounts["__test_tmp__"] = "{}"'.format(temp_results_dir))
            config.read_config_string('mounts["__ref_tmp__"] = "{}"'.format(reference_data_dir))

            # Check if values for all outputs match
            for output in reference_outputs:
                current_output_data = current_result.output_data[output]
                reference_output_data = reference_result.output_data[output]
                if not isinstance(current_output_data, type(reference_output_data)):
                    validation_result.append('\n'.join((
                        'Different type for output {} found in tool "{}/{}"'.format(tool.ns_id, tool.command_version),
                        'Current type: {}'.format(type(current_output_data)),
                        'Reference type {}'.format(type(reference_output_data)),
                    )))

                if isinstance(current_output_data, dict):
                    raise exceptions.FastrNotImplementedError(
                        'Output comparison of dict structures is not supported yet!'
                    )
                else:
                    cls.compare_output_data(
                        current_output_data,
                        reference_output_data,
                        validation_result,
                        output
                    )

            # Remove the temporary mounts again
            config.read_config_string('del mounts["__test_tmp__"]')
            config.read_config_string('del mounts["__ref_tmp__"]')

            if len(validation_result) == 0:
                log.info('Run and reference were equal! Test passed!')
            else:
                log.info('Found difference with reference data! Test failed!')
                for line in validation_result:
                    log.info(line)
            return validation_result
        finally:
            # Clean up
            log.info('Removing temp result directory {}'.format(temp_results_dir))
            if temp_results_dir is not None and os.path.isdir(temp_results_dir):
                shutil.rmtree(temp_results_dir, ignore_errors=True)

    def test(self, reference=None):
        """
        Run the tests for this tool
        """
        if reference is None:
            result = []
            tool_dir = os.path.dirname(self.filename)
            for test in self.tests:
                reference_dir = os.path.abspath(os.path.join(tool_dir, test))
                try:
                    result.extend(self.test_tool(reference_data_dir=reference_dir, tool=self))
                except exceptions.FastrTypeError:
                    message = 'Reference data in {} is not valid!'.format(reference_dir)
                    log.warning(message)
                    result.append(message)
        else:
            result = self.test_tool(reference_data_dir=reference, tool=self)

        return result
