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
This module contains the Job class and some related classes.
"""

import datetime
import os
import urllib.request
import urllib.error
import urllib.parse
import shutil
from typing import Dict, List, Iterable
from collections import OrderedDict

from enum import Enum

from .. import exceptions, version, resources
from ..abc.serializable import Serializable
from ..core import vfs_plugin as vfs
from ..core.cardinality import create_cardinality
from ..core.samples import SampleId, SampleIndex, SampleItem
from ..core.provenance import Provenance
from ..data import url
from ..datatypes import URLType, DataType, Deferred, types
from ..helpers import log, config
from ..helpers.events import emit_event, EventType
from ..helpers.filesynchelper import FileSyncHelper, filesynchelper_enabled
from ..helpers.iohelpers import load_gpickle, save_gpickle, save_json

try:
    from fastr.execution.environmentmodules import EnvironmentModules
    ENVIRONMENT_MODULES = EnvironmentModules(config.protected_modules)
    ENVIRONMENT_MODULES_LOADED = True
except exceptions.FastrValueError:
    ENVIRONMENT_MODULES_LOADED = False


class JobState(Enum):
    """
    The possible states a Job can be in. An overview of the states and the
    adviced transitions are depicted in the following figure:

    .. graphviz::

       digraph jobstate {
           nonexistent [shape=box];
           created [shape=box];
           queued [shape=box];
           hold [shape=box];
           running [shape=box];
           execution_done [shape=box];
           execution_failed [shape=box];
           processing_callback [shape=box];
           finished [shape=box];
           failed [shape=box];
           cancelled [shape=box];

           nonexistent -> created;
           created -> queued;
           created -> hold;
           hold -> queued;
           queued -> running;
           running -> execution_done;
           running -> execution_failed;
           execution_done -> processing_callback;
           execution_failed -> processing_callback;
           processing_callback -> finished;
           processing_callback -> failed;
           running -> cancelled;
           queued -> cancelled;
           hold -> cancelled;
       }
    """
    nonexistent = ('nonexistent', 'idle', False)
    created = ('created', 'idle', False)
    queued = ('queued', 'idle', False)
    hold = ('hold', 'idle', False)
    running = ('running', 'in_progress', False)
    execution_done = ('execution_done', 'in_progress', False)
    execution_failed = ('execution_failed', 'in_progress', True)
    processing_callback = ('processing_callback', 'in_progress', False)
    finished = ('finished', 'done', False)
    failed = ('failed', 'done', True)
    cancelled = ('cancelled', 'done', True)

    def __init__(self, _, stage, error):
        self.stage = stage
        self.error = error

    @property
    def idle(self):
        return self.stage == 'idle'

    @property
    def done(self):
        return self.stage == 'done'

    @property
    def in_progress(self):
        return self.stage == 'in_progress'


class JobCleanupLevel(Enum):
    """
    The cleanup level for Jobs that are finished.
    """
    all = 'all'
    non_failed = 'non_failed'
    no_cleanup = 'no_cleanup'


class Job(Serializable):

    """Class describing a job.

       Arguments:
       tool_name - the name of the tool (str)
       tool_version - the version of the tool (Version)
       argument - the arguments used when calling the tool (list)
       tmpdir - temporary directory to use to store output data
       hold_jobs - list of jobs that need to finished before this job can run (list)
    """

    # Constants for file names related to jobs
    COMMAND_DUMP = '__fastr_command__.pickle.gz'
    RESULT_DUMP = '__fastr_result__.pickle.gz'
    STDOUT_DUMP = '__fastr_stdout__.txt'
    STDERR_DUMP = '__fastr_stderr__.txt'
    INFO_DUMP = '__fastr_extra_job_info__.json'
    PROV_DUMP = '__fastr_prov__.json'

    def __init__(self,
                 node,
                 sample_id: SampleId,
                 sample_index: SampleIndex,
                 input_arguments: Dict[str, SampleIndex],
                 output_arguments: Dict[str, Dict],
                 hold_jobs: List[str]=None,
                 preferred_types: List=None):
        """
        Create a job

        :param fastr.planning.node.Node node: the node the job is based on
        :param sample_id: the id of the sample
        :param sample_index: the index of the sample
        :param input_arguments: the argument list
        :param output_arguments: the argument list
        :param hold_jobs: the jobs on which this jobs depend
        :param preferred_types: The list of preferred types to use
        :return:
        """
        # Save information about the Job environment in which it was created
        self.network_id = node.parent.long_id
        self.network_version = str(node.parent.network_version)
        self.run_id = node.parent.id
        self.node = node
        self.node_id = node.id
        self.node_global_id = node.global_id
        self.tool_name = node.tool.ns_id
        self.tool_version = str(node.tool.version)
        self.sample_id = sample_id
        self.sample_index = sample_index
        self.network_tmpurl = node.parent.tmpurl

        # Arguments for the command
        self.input_arguments = input_arguments
        self.output_arguments = output_arguments

        # Create tmpdir
        # Determine subfolder name in tmp mount
        self.ensure_tmp_dir()

        self._resources = node.resources
        self.translated_values = {}
        self.preferred_types = preferred_types if preferred_types else {}

        if isinstance(hold_jobs, (set, list, tuple)):
            self.hold_jobs = list(hold_jobs)
        elif isinstance(hold_jobs, str):
            self.hold_jobs = [hold_jobs]
        elif hold_jobs is None:
            self.hold_jobs = []
        else:
            raise exceptions.FastrTypeError('Cannot create jobs: hold_jobs has invalid type!')

        self.timestamp = datetime.datetime.utcnow()

        self.info_store = {
            'id': self.id,
        }

        self.errors = []
        self.input_hash = {}
        self.output_hash = {}

        # The status list contains tuples with (timestamp, status)
        # This is updated via the status property
        self.status_list = []
        self.status = JobState.created

        self.provenance = Provenance()

        # Dictionary where the output data will be stored
        self.output_data = {}

        # Save fastr version for safety
        self.fastr_version = version.full_version

    def __getstate__(self):
        """
        Get the state of the job

        :return: job state
        :rtype: dict
        """
        state = {k: v for k, v in self.__dict__.items()}
        del state['info_store']
        del state['provenance']
        del state['node']

        # Store states by id, not by actual type
        state['preferred_types'] = {
            output_key: [x.id for x in output_types]
            for output_key, output_types in state['preferred_types'].items()
        }
        return state

    def __setstate__(self, state):
        """
        Set the state of the job

        :param dict state:
        """
        preferred_types = {}
        for key, value in state['preferred_types'].items():
            temp = []
            for type_ in value:
                if isinstance(type_, str) and type_ in types:
                    temp.append(types[type_])
                elif isinstance(type_, type) and issubclass(type_, DataType):
                    temp.append(type_)
                else:
                    log.warning('Could not find type {} during unpickling of Job'.format(type_))
            preferred_types[key] = temp

        state['preferred_types'] = preferred_types

        # For backwards compatibility
        if 'status_list' not in state and '_status_list' in state:
            state['status_list'] = state.pop('_status_list')

        self.__dict__.update(state)

        # Cannot transport reference to Node
        if not hasattr(self, 'node'):
            self.node = None

        if not hasattr(self, 'info_store'):
            self.info_store = {
                'id': self.id,
            }

        if not hasattr(self, 'provenance'):
            self.provenance = Provenance()

    def get_result(self):
        """
        Get the result of the job if it is available. Load the output file if
        found and check if the job matches the current object. If so, load and
        return the result.

        :returns: Job after execution or None if not available
        :rtype: Job | None
        """

        if not os.path.exists(self.logfile):
            return None

        log.debug('Found old job result file: {}'.format(self.logfile))

        try:
            result = load_gpickle(self.logfile)
        except (IOError, EOFError):
            # Errors loading pickle or gzip stream
            return None

        log.debug('Loaded old job result file')

        if not isinstance(result, Job):
            log.debug('Result is not valid Job! (found {})'.format(type(result).__name__))
            return None

        if result.status != JobState.execution_done:
            log.debug('Result status is wrong ({})'.format(result.status))
            return None

        if result.id != self.id:
            log.debug('Result job id is wrong ({})'.format(result.id))
            return None

        if result.tool_name != self.tool_name:
            log.debug('Result tool name is wrong ({})'.format(result.tool_name))
            return None

        if result.tool_version != self.tool_version:
            log.debug('Result tool version is wrong ({})'.format(result.tool_version))
            return None

        if result.sample_id != self.sample_id:
            log.debug('Result sample id is wrong ({})'.format(result.sample_id))
            return None

        log.debug('Checking payloads')

        result_payload = result.create_payload()
        if result_payload != self.create_payload():
            log.debug('Result payload is wrong ({})'.format(result_payload))
            return None

        log.debug('Checking sample index')

        if self.sample_index != result.sample_index:
            log.info('Updating sample index from {} to {}'.format(result.sample_index,
                                                                        self.sample_index))
            result.sample_index = self.sample_index

        # Update job run id to current run
        if self.run_id != result.run_id:
            result.run_id = self.run_id
            result.node_global_id = self.node_global_id

        return result

    def __repr__(self):
        """
        String representation of the Job
        """
        return '<Job\n  id={job.id}\n  tool={job.tool_name} {job.tool_version}\n  tmpdir={job.tmpurl}/>'.format(
            job=self
        )

    @property
    def status(self):
        """
        The status of the job
        """
        # The get last status update and only the new status
        return self.status_list[-1][1]

    @status.setter
    def status(self, status):
        """
        Set the status of a job
        :param status: new status
        """
        if not isinstance(status, JobState):
            raise exceptions.FastrTypeError(
                'Job status should be of class JobState, found [{}] {}'.format(type(status).__name__,
                                                                               status)
            )
        if len(self.status_list) == 0 or self.status != status:
            self.status_list.append((datetime.datetime.utcnow(), status))

            # Emit event that this job has been updated
            emit_event(EventType.job_updated, self)

    @property
    def id(self):
        """
        The id of this job
        """
        return '{}___{}___{}'.format(self.network_id,
                                     self.node_id,
                                     self.sample_id)

    @property
    def fullid(self):
        """
        The full id of the job
        """
        return self.id

    @property
    def tmpurl(self):
        """
        The URL of the tmpdir to use
        """
        return url.join(self.network_tmpurl, self.node_id, str(self.sample_id))

    @property
    def commandurl(self):
        """
        The url of the command pickle
        """
        return url.join(self.tmpurl, self.COMMAND_DUMP)

    @property
    def logurl(self):
        """
        The url of the result pickle
        """
        return url.join(self.tmpurl, self.RESULT_DUMP)

    @property
    def stdouturl(self):
        """
        The url where the stdout text is saved
        """
        return url.join(self.tmpurl, self.STDOUT_DUMP)

    @property
    def stderrurl(self):
        """
        The url where the stderr text is saved
        """
        return url.join(self.tmpurl, self.STDERR_DUMP)

    @property
    def provurl(self):
        """
        The url where the prov document is saved
        """
        return url.join(self.tmpurl, self.PROV_DUMP)

    @property
    def extrainfourl(self):
        """
        The url where the extra job info document is saved
        """
        return url.join(self.tmpurl, self.INFO_DUMP)

    @property
    def resources(self):
        """
        The compute resources required for this job
        """
        return self._resources

    def clean(self):
        log.debug('Cleaning {}'.format(self.id))
        cleanup_level = JobCleanupLevel(config.job_cleanup_level)

        if cleanup_level == JobCleanupLevel.no_cleanup:
            return

        if cleanup_level == JobCleanupLevel.all or self.status not in [JobState.failed, JobState.execution_failed]:
            job_tmp_dir = vfs.url_to_path(self.tmpurl)
            if os.path.exists(job_tmp_dir):
                shutil.rmtree(job_tmp_dir)

    def get_deferred(self, output_id, cardinality_nr, sample_id=None):
        """
        Get a deferred pointing to a specific output value in the Job

        :param str output_id: the output to select from
        :param int cardinality_nr: the index of the cardinality
        :param str sample_id: the sample id to select (optional)
        :return: The deferred
        """
        parsed_url = urllib.parse.urlparse(self.logurl)

        query = {
            'outputname': output_id,
            'nr': cardinality_nr,
        }

        if sample_id is not None:
            query['sampleid'] = sample_id

        deffered_url = urllib.parse.urlunparse(
            (
                'val',
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                urllib.parse.urlencode(query),
                ''
            )
        )

        return Deferred(deffered_url)

    @property
    def commandfile(self):
        """
        The path of the command pickle
        """
        return vfs.url_to_path(self.commandurl)

    @property
    def logfile(self):
        """
        The path of the result pickle
        """
        return vfs.url_to_path(self.logurl)

    @property
    def stdoutfile(self):
        """
        The path where the stdout text is saved
        """
        return vfs.url_to_path(self.stdouturl)

    @property
    def stderrfile(self):
        """
        The path where the stderr text is saved
        """
        return vfs.url_to_path(self.stderrurl)

    @property
    def provfile(self):
        """
        The path where the prov document is saved
        """
        return vfs.url_to_path(self.provurl)

    @property
    def extrainfofile(self):
        """
        The path where the extra job info document is saved
        """
        return vfs.url_to_path(self.extrainfourl)

    @property
    def tool(self):
        return resources.tools[self.tool_name, self.tool_version]

    def ensure_tmp_dir(self):
        # Determine absolute location of output dir and create directory
        output_dir = url.get_path_from_url(self.tmpurl)

        # Remove output directory if there is old stuff present
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if not os.path.exists(output_dir):
            log.critical('Could not create output directory {}!'.format(output_dir))

    def create_payload(self):
        """
        Create the payload for this object based on all the input/output
        arguments

        :return: the payload
        :rtype: dict
        """
        tool = self.tool
        payload = {'inputs': {}, 'outputs': {}}

        # Fill the payload with the values to use (these should be translated to paths/strings/int etc
        # Translate all inputs to be in correct form
        for id_, value in self.input_arguments.items():
            argument = tool.inputs[id_]
            argument_datatype = types[argument.datatype]
            if isinstance(value, SampleItem):
                if len(value.data.mapping_part()) == 0:
                    value = value.data.sequence_part()
                elif len(value.data.sequence_part()) == 0:
                    value = value.data.mapping_part()
                else:
                    raise ValueError('Fastr does not (yet) accept mixed sequence/mapping input!')

            if not argument.hidden:
                if isinstance(value, tuple):
                    payload['inputs'][id_] = tuple(self.translate_argument(x) for x in value)
                else:
                    # Should be ordered dict
                    payload['inputs'][id_] = OrderedDict(
                        (k, tuple(self.translate_argument(x) for x in v)) for k, v in value.items()
                    )

            else:
                if issubclass(argument_datatype, URLType):
                    payload['inputs'][id_] = tuple(self.translate_argument(x) for x in value)
                else:
                    payload['inputs'][id_] = value

            if len(payload['inputs'][id_]) == 0 and argument.default is not None:
                payload['inputs'][id_] = (self.cast_to_type(argument.default, (argument_datatype,)),)

        # Create output arguments automatically
        for id_, spec in self.output_arguments.items():
            argument = tool.outputs[id_]

            if not argument.automatic:
                cardinality_spec = create_cardinality(spec['cardinality'], None)
                cardinality = cardinality_spec.calculate_job_cardinality(payload)

                if cardinality is None:
                    raise exceptions.FastrValueError('Cardinality cannot be unknown for non-automatic outputs! '
                                                     'Found {} for {}'.format(cardinality, argument))
            else:
                cardinality = 1

            payload['outputs'][id_] = self.fill_output_argument(tool.outputs[id_],
                                                                cardinality,
                                                                spec['datatype'],
                                                                spec['requested'],
                                                                self.tmpurl)

        return payload

    def execute(self):
        """
        Execute this job

        :returns: The result of the execution
        :rtype: InterFaceResult
        """
        # Check if Fastr version is stored or we use a version that predates
        # this feature
        if not hasattr(self, 'fastr_version'):
            message = (
                'Job was created with an old version of Fastr that did not'
                'track the fastr_version yet, current Fastr version is {}'
            ).format(version.full_version)

            # For default branch (production) this is an error, for development
            # just a warning
            if version.hg_branch == 'default':
                log.critical(message)
                raise exceptions.FastrVersionMismatchError(message)
            else:
                log.warning(message)

        # Check if the fastr version is identical to the version that created
        # the job initially.
        if version.full_version != self.fastr_version:
            message = (
                'Job was created using Fastr version {}, but execution is'
                ' attempted on Fastr version {}'
            ).format(
                self.fastr_version,
                version.full_version
            )

            # For default branch (production) this is an error, for development
            # just a warning
            if version.hg_branch == 'default':
                log.critical(message)
                raise exceptions.FastrVersionMismatchError(message)
            else:
                log.warning(message)

        # Change the working directory to job temp dir
        old_curdir = os.path.abspath(os.curdir)
        job_dir = vfs.url_to_path(self.tmpurl)
        log.info('Set current directory to job output dir {}'.format(job_dir))
        os.chdir(job_dir)

        # Set environment variables
        os.environ['FASTR_SAMPLE_ID'] = str(self.sample_id)
        os.environ['FASTR_SAMPLE_INDEX'] = str(self.sample_index)
        os.environ['FASTR_JOB_ID'] = self.id
        os.environ['FASTR_WORK_DIR'] = job_dir

        tool = self.tool

        # Hash the inputs
        self.hash_inputs()

        # Create the payload
        log.info('Start executing tool')
        start = datetime.datetime.utcnow()
        payload = self.create_payload()
        end = datetime.datetime.utcnow()
        log.info('Finished creating payload in {} seconds'.format((end - start).total_seconds()))

        # Execute the tool
        log.info('Start executing tool')
        start = datetime.datetime.utcnow()
        result = tool.execute(payload)
        end = datetime.datetime.utcnow()
        log.info('Finished executing tool in {} seconds'.format((end - start).total_seconds()))

        # Save the log data
        self.info_store['process'] = result.target_result.as_dict()

        # Check if there were errors in the Interface result
        errors = []
        for error in result.errors:
            if isinstance(error, exceptions.FastrError):
                errors.append(error.excerpt())
            elif isinstance(error, BaseException):
                errors.append((type(error).__name__, error.message, 'unknown', 'uknown'))
            elif isinstance(error, str):
                errors.append(('ErrorInJobExecute', error, 'uknown', 'unknown'))
            elif isinstance(error, (list, tuple)) and len(error) == 4:
                errors.append(error)
            else:
                log.warning('Collected a mal-formatted error: {}'.format(error))
        self.errors.extend(result.errors)

        log.info('Start translating results tool')
        start = datetime.datetime.utcnow()
        self.output_data = self.translate_results(result.result_data)
        end = datetime.datetime.utcnow()
        log.info('Finished translating results in {} seconds'.format((end - start).total_seconds()))

        # Collect the provenance for the node
        self.collect_provenance()

        # Return the working directory to the old state
        log.info('Resetting current directory to {}'.format(old_curdir))
        os.chdir(old_curdir)

        if not self.validate_results(payload):
            raise exceptions.FastrValueError('Output values are not valid!')

        return result

    def collect_provenance(self):
        """
        Collect the provenance for this job.
        """
        self.provenance.collect_provenance(self)

    @classmethod
    def translate_argument(cls, value):
        """
        Translate an argument from a URL to an actual path.

        :param value: value to translate
        :param datatype: the datatype of the value
        :return: the translated value
        """
        return cls.get_value(value=value)

    def get_output_datatype(self, output_id):
        """
        Get the datatype for a specific output

        :param str output_id: the id of the output to get the datatype for
        :return: the requested datatype
        :rtype: tuple
        """
        output = self.tool.outputs[output_id]
        datatype = types[output.datatype]
        preferred_type = datatype
        requested_type = types[self.output_arguments[output_id]['datatype']]

        # If there are preferred types, match with that if possible
        if output_id in self.preferred_types and len(self.preferred_types[output_id]) > 0:
            preferred_type = types.match_types(datatype, preferred=self.preferred_types[output_id])

        datatypes = tuple(x for x in [requested_type, preferred_type, datatype] if x is not None)

        return datatypes

    def translate_results(self, result):
        """
        Translate the results of an interface (using paths etc) to the proper
        form using URI's instead.

        :param dict result: the result data of an interface
        :return: the translated result
        :rtype: dict
        """
        to_remove = []
        for key, value in result.items():
            datatypes = self.get_output_datatype(key)
            try:
                result[key] = self.translate_output_results(value,
                                                            datatypes=datatypes)
            except exceptions.FastrError:
                if self.output_arguments[key]['requested']:
                    raise
                else:
                    log.warning('Encountered problem translating non-requested result for {}, ignoring...'.format(key))
                    to_remove.append(key)

        # Removing keys that were not translated correctly
        for key in to_remove:
            log.info('Dropping non-translated item with key {}'.format(key))
            result.pop(key, None)

        return result

    @staticmethod
    def cast_to_type(value, datatypes: Iterable) -> DataType:
        """
        Try to cast value to one of the given datatypes. Will try all the
        datatypes in order.

        :param tuple datatypes: Possible datatypes to cast to
        :return: casted value
        """
        log.info('Trying to cast {} to one of {}'.format(value, datatypes))
        for datatype in datatypes:
            try:
                item = datatype(str(value))
                if item.valid:
                    log.info('Successfully cast to {!r}'.format(item))
                    return item
                log.info('Could not cast to valid {!r}'.format(item))
            except exceptions.FastrValueError:
                log.info('Could not cast to {!r}'.format(datatype))
        else:
            raise exceptions.FastrValueError('Could not cast "{}" to any of {}'.format(
                value, datatypes
            ))

    @staticmethod
    def translate_output_results(value, datatypes, mountpoint=None):
        """
        Translate the results for on Output

        :param value: the results value for the output
        :param tuple datatypes: tuple of possible datatypes for the output
        :param preferred_type: the preferred datatype of the output
        :return: the update value for the result
        """
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                new_subvalue = []
                for item in subvalue:
                    if not isinstance(item, DataType):
                        item = Job.cast_to_type(item, datatypes)
                    if isinstance(item, URLType):
                        item.value = vfs.path_to_url(item.value)
                        if filesynchelper_enabled():
                            FileSyncHelper().make_file_promise(item.value)
                    new_subvalue.append(item)
                value[subkey] = tuple(new_subvalue)
        else:
            new_value = []
            for item in value:
                if not isinstance(item, DataType):
                    item = Job.cast_to_type(item, datatypes)
                if isinstance(item, URLType):
                    item.value = vfs.path_to_url(item.value, mountpoint=mountpoint)
                    if filesynchelper_enabled():
                        FileSyncHelper().make_file_promise(item.value)
                new_value.append(item)
            value = new_value

        return value

    @classmethod
    def fill_output_argument(cls, output_spec, cardinality, desired_type, requested, tmpurl):
        """
        This is an abstract class method. The method should take the argument_dict
        generated from calling self.get_argument_dict() and turn it into a list
        of commandline arguments that represent this Input/Output.

        :param int cardinality: the cardinality for this output (can be non for automatic outputs)
        :param DataType desired_type: the desired datatype for this output
        :param bool requested: flag to indicate that the output is requested by Fastr
        :return: the values for this output
        :rtype: list
        """
        values = []

        if not output_spec.automatic and requested:
            # For requested non-automatic outputs, fill them here
            datatype = types[desired_type]

            for cardinality_nr in range(cardinality):
                if datatype.extension is not None:
                    output_url = '{}/{}_{}.{}'.format(tmpurl, output_spec.id, cardinality_nr, datatype.extension)
                else:
                    output_url = '{}/{}_{}'.format(tmpurl, output_spec.id, cardinality_nr)

                # Wrap the output url in the correct DataType
                log.debug('Wrapping {} in a {}'.format(output_url, datatype))
                output_value = datatype(output_url)
                log.debug('Got {}'.format(output_value))

                # Translate to a path and use
                values.append(cls.translate_argument(output_value))
        elif output_spec.automatic:
            datatype = types['Boolean']
            values.append(datatype(requested))

        return tuple(values)

    @classmethod
    def get_value(cls, value):
        """
        Get a value

        :param value: the url of the value
        :param datatype: datatype of the value
        :return: the retrieved value
        """
        if isinstance(value, Deferred):
            value = value.target

        # If the value already has valid datatype, use that and don't guess from scratch
        if isinstance(value, URLType):
            datatype = type(value)
            if url.isurl(str(value)):
                if filesynchelper_enabled():
                    # we are using file promises
                    file_sync_helper = FileSyncHelper()
                    # if we have a file promise for this value
                    # we need to wait until the file is available
                    # or until a timeout has occured
                    if file_sync_helper.has_file_promise(value):
                        file_sync_helper.wait_for_vfs_url(value)
                value = vfs.url_to_path(str(value))
            else:
                if filesynchelper_enabled():
                    # we are using file promises
                    file_sync_helper = FileSyncHelper()
                    # if we have a file promise for this value
                    # we need to wait until the file is available
                    # or until a timeout has occured
                    if file_sync_helper.has_file_promise(value):
                        file_sync_helper.wait_for_file(value)
                if not os.path.exists(str(value)):
                    raise exceptions.FastrValueError(
                        'Found a non-url path ({}) of type {} that does not exist!'.format(value, datatype)
                    )
            return datatype(value)
        elif isinstance(value, DataType):
            return value
        else:
            raise exceptions.FastrTypeError('Arguments should be a DataType, found {}'.format(type(value).__name__))

    def hash_inputs(self):
        """
        Create hashes for all input values and store them in the info store
        """
        for key, value in self.input_arguments.items():
            if value.data.is_sequence:
                self.input_hash[key] = [x.checksum() if x.valid else None for x in value.data.sequence_part()]
            else:
                self.input_hash[key] = {}
                for sample_id, input_val in value.data.mapping_part().items():
                    self.input_hash[key][sample_id] = [x.checksum() if x.valid else None for x in input_val]

    def hash_results(self):
        """
        Create hashes of all output values and store them in the info store
        """
        for output in self.output_arguments.values():
            if not output['requested'] and output['id'] not in self.output_data:
                continue

            id_ = output['id']
            output_value = self.output_data[id_]

            if isinstance(output_value, list):
                self.output_hash[id_] = [x.checksum() if x.valid else None for x in output_value]
            elif isinstance(output_value, dict):
                self.output_hash[id_] = {}
                for sample_id, output_val in output_value.items():
                    self.output_hash[id_][sample_id] = [x.checksum() if x.valid else None for x in output_val]

    def validate_results(self, payload):
        """
        Validate the results of the Job

        :return: flag indicating the results are complete and valid
        """

        valid = True
        for output in self.tool.outputs.values():
            id_ = output.id

            if id_ not in self.output_data:
                if id_ in self.output_arguments and self.output_arguments[id_]['requested']:
                    message = 'Could not find result for output {}'.format(id_)
                    self.errors.append(exceptions.FastrOutputValidationError(message).excerpt())
                    log.warning(message)
                    valid = False
                else:
                    log.warning('Could not find non-required output {}'.format(id_))
                continue

            output_value = self.output_data[id_]

            if isinstance(output_value, (list, tuple)):
                if not self._validate_result(output, output_value, payload):
                    message = 'The output "{}" is invalid!'.format(id_)
                    self.errors.append(exceptions.FastrOutputValidationError(message).excerpt())
                    log.warning(message)
                    if self.output_arguments[id_]['requested']:
                        valid = False
                    else:
                        log.warning('Non-required output {} is invalid!'.format(id_))
            elif isinstance(output_value, dict):
                for sample_id, output_val in output_value.items():
                    if self._validate_result(output, output_val, payload):
                        continue

                    message = 'The output "{}" for sample "{}" is invalid!'.format(id_, sample_id)
                    self.errors.append(exceptions.FastrOutputValidationError(message).excerpt())
                    log.warning(message)
                    if self.output_arguments[id_]['requested']:
                        valid = False
                    else:
                        log.warning('Non-required output {} is invalid!'.format(id_))

            else:
                raise exceptions.FastrTypeError('Output data is not of correct type (expected a list/dict)')

        return valid

    def write(self):
        self.provenance.serialize(self.provfile, 'json')
        save_json(self.extrainfofile, self.info_store)
        save_gpickle(self.logfile, self)

    def _validate_result(self, output, output_value, payload):
        """
        Validate the result for a specific output/sample
        :param output: the output for which to check
        :param output_value: the value for the output
        :return: flag indicating if the result is value
        """
        valid = True
        cardinality = create_cardinality(output.cardinality, None)

        if not cardinality.validate(payload, len(output_value)):
            message = 'Cardinality mismatch for {} (found {}, expected {!r})'.format(output.id,
                                                                                     len(output_value),
                                                                                     cardinality)
            self.errors.append(exceptions.FastrOutputValidationError(message).excerpt())
            log.warning(message)
            valid = False

        for value in output_value:
            if not value.valid:
                message = 'Output value [{}] "{}" not valid for datatype "{!r}"'.format(type(value).__name__,
                                                                                        value,
                                                                                        output.datatype)
                self.errors.append(exceptions.FastrOutputValidationError(message).excerpt())
                log.warning(message)
                valid = False

        log.info('Data for output {} is {}'.format(output.id, 'valid' if valid else 'invalid'))

        return valid


class SinkJob(Job):
    """
    Special SinkJob for the Sink
    """
    def __init__(self, node, sample_id, sample_index, input_arguments,
                 output_arguments, hold_jobs=None, substitutions=None,
                 preferred_types=None):

        # This is required!
        self.cardinality = substitutions['cardinality']

        super(SinkJob, self).__init__(node=node,
                                      sample_id=sample_id,
                                      sample_index=sample_index,
                                      input_arguments=input_arguments,
                                      output_arguments=output_arguments,
                                      hold_jobs=hold_jobs,
                                      preferred_types=preferred_types)

        self._substitutions = substitutions if substitutions else {}

    def __repr__(self):
        """
        String representation for the SinkJob
        """
        return '<SinkJob\n  id={job.id}\n  tmpdir={job.tmpurl}/>'.format(job=self)

    @property
    def id(self):
        """
        The id of this job
        """
        return '{}___{}___{}___{}'.format(
            self.network_id,
            self.node_id,
            self.sample_id,
            self.cardinality
        )

    @property
    def tmpurl(self):
        """
        The URL of the tmpdir to use
        """
        return '{}/{}/{}_{}'.format(self.network_tmpurl, self.node_id,
                                    self.sample_id, self.cardinality)

    def get_result(self):
        """
        Get the result of the job if it is available. Load the output file if
        found and check if the job matches the current object. If so, load and
        return the result.

        :returns: Job after execution
        """
        return None

    def validate_results(self, payload):
        """
        Validate the results of the SinkJob

        :return: flag indicating the results are complete and valid
        """
        if self.info_store['process']['stderr'] != '':
            message = 'SinkJob should have an empty stderr, found error messages!\n{}'.format(
                self.info_store['process']['stderr']
            )
            log.warning(message)
            self.errors.append(exceptions.FastrOutputValidationError(message).excerpt())
            return False
        else:
            return True

    def create_payload(self):
        """
        Create the payload for this object based on all the input/output
        arguments

        :return: the payload
        :rtype: dict
        """
        payload = super(SinkJob, self).create_payload()
        log.info('Temp payload: {}'.format(payload))
        log.info('Input data: {}'.format(payload['inputs']['input']))
        log.info('Input arguments: {}'.format(self.input_arguments['input'].data))

        payload['inputs']['output'] = tuple(self.substitute(in_, datatype=type(out)) for in_, out in zip(payload['inputs']['output'],
                                                                                                         payload['inputs']['input']))

        # Add the provenance information into the mix
        extra_inputs = []
        extra_outputs = []
        extra_datatypes = []

        if len(self.input_arguments['input'].data.mapping_part()) > 0:
            raise exceptions.FastrValueError('SinkJob should not have input with mapping_parts!')

        inputs = self.input_arguments['input'].data.sequence_part()
        outputs = payload['inputs']['output']

        for input_, output in zip(inputs, outputs):
            log.info('Checking [{}] {!s} ({!r})'.format(type(input_), input_, input_))
            if isinstance(input_, Deferred):
                parsed_url = urllib.parse.urlparse(input_.raw_value)

                if parsed_url.scheme != 'val':
                    raise exceptions.FastrValueError(
                        'Cannot lookup value {}, wrong url scheme'.format(input_.raw_value)
                    )

                # Find location of the provn file
                datafile = os.path.join(config.mounts[parsed_url.netloc],
                                        os.path.normpath(parsed_url.path[1:]))
                datafile = datafile.replace(self.RESULT_DUMP, self.PROV_DUMP)

                extra_inputs.append(types['JsonFile'](datafile))

                # Update the output_url
                output_url = urllib.parse.urlparse(output)
                output_path = output_url.path
                output_dir, output_file = url.split(output_path)
                output_path = url.join(output_dir, output_file.replace('.', '_')) + '.prov.json'
                output = urllib.parse.urlunparse(output_url._replace(path=output_path))

                extra_outputs.append(output)
                extra_datatypes.append(types['String']('JsonFile'))

        log.info('Extra inputs: {}  Extra outputs: {}'.format(extra_inputs,
                                                                    extra_outputs))

        payload['inputs']['input'] = payload['inputs']['input'] + tuple(extra_inputs)
        payload['inputs']['output'] = payload['inputs']['output'] + tuple(extra_outputs)
        payload['inputs']['datatype'] = payload['inputs']['datatype'] + tuple(extra_datatypes)

        return payload

    def substitute(self, value, datatype=None):
        """
        Substitute the special fields that can be used in a SinkJob.

        :param str value: the value to substitute fields in
        :param BaseDataType datatype: the datatype for the value
        :return: string with substitutions performed
        :rtype: str
        """
        if datatype is None:
            datatype = type(value)

        subs = dict(self._substitutions)
        if isinstance(datatype.extension, tuple):
            subs['ext'] = datatype.dot_extension[0]
            subs['extension'] = datatype.extension[0]
        elif datatype.extension is None:
            subs['ext'] = ''
            subs['extension'] = ''
        else:
            subs['ext'] = datatype.dot_extension
            subs['extension'] = datatype.extension

        return str(value).format(**subs)

    def hash_inputs(self):
        """
        Create hashes for all input values and store them in the info store
        """
        input_data = self.input_arguments['input'].data
        if input_data.is_sequence:
            self.input_hash['input'] = [x.checksum() for x in input_data.sequence_part()]
        else:
            self.input_hash['input'] = {}
            for sample_id, input_val in input_data.mapping_part().items():
                self.input_hash['input'][sample_id] = [x.checksum() for x in input_val]


class SourceJob(Job):
    """
    Special SourceJob for the Source
    """
    def __repr__(self):
        """
        String representation for the SourceJob
        """
        return '<SourceJob\n  id={job.id}\n  tmpdir={job.tmpurl}/>'.format(job=self)

    def validate_results(self, payload):
        """
        Validate the results of the Job

        :return: flag indicating the results are complete and valid
        """
        if self.info_store['process']['stderr'] != '':
            message = 'SourceJob should have an empty stderr, found error messages!'
            log.warning(message)
            self.errors.append(exceptions.FastrOutputValidationError(message).excerpt())
            return False
        else:
            return super(SourceJob, self).validate_results(payload)

    def get_output_datatype(self, output_id):
        """
        Get the datatype for a specific output

        :param str output_id: the id of the output to get the datatype for
        :return: the requested datatype
        :rtype: BaseDataType
        """
        return types[self._datatype],

    def hash_inputs(self):
        """
        Create hashes for all input values and store them in the info store
        """
        inputs = [types['String'](x) for x in self.input_arguments['input']]
        self.input_hash['input'] = [x.checksum() for x in inputs]

    def collect_provenance(self):
        """
        Collect the provenance for this job
        """
        super(SourceJob, self).collect_provenance()


class InlineJob(Job):
    """
    Job that does not actually need to run but is used for consistency in
    data processing and logging.
    """
    def __init__(self, *args, **kwargs):
        super(InlineJob, self).__init__(*args, **kwargs)
        self.collect_provenance()

    def collect_provenance(self):
        """
        Collect the provenance for this job
        ::
        """
        self.provenance.init_provenance(self)
        self.provenance.collect_provenance(self, advanced_flow=True)

    def get_result(self):
        if not os.path.exists(self.logfile):
            return None

        try:
            result = load_gpickle(self.logfile)
        except (IOError, EOFError):
            # Errors loading pickle or gzip stream
            return None

        if not isinstance(result, Job):
            log.debug('Result is not valid Job! (found {})'.format(type(result).__name__))
            return None

        return result
