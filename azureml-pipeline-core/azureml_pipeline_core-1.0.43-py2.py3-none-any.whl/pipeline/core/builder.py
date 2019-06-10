# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""builder.py, module for building a pipeline graph."""
from abc import abstractmethod, ABCMeta
from azureml.pipeline.core.graph import Graph, Node, InputPortBinding, OutputPortBinding, \
    _PipelineIO, PipelineDataset, DataSource
from azureml.pipeline.core.graph import PortDataReference, DataSourceDef, PipelineParameter
from azureml.pipeline.core.graph import Edge, _DataReferenceEdgeBuilder, _PipelineDataEdgeBuilder, \
    _PipelineIOEdgeBuilder, _DatasetEdgeBuilder
from azureml.data.data_reference import DataReference
from azureml.pipeline.core._datasource_builder import _DataReferenceDatasourceBuilder
from azureml.pipeline.core._module_parameter_provider import _ModuleParameterProvider
from msrest.exceptions import HttpOperationError
from .module import Module

import os


class PipelineStep(object):
    """
    PipelineStep represents an execution step in a pipeline.

    A PipelineStep can have named inputs, outputs, and parameters. This is the base step class which the supported
    step types inherit from.

    .. remarks::

        See the following pages for information on the various Step types supported:

        *  :class:`azureml.pipeline.steps.PythonScriptStep`
        *  :class:`azureml.pipeline.steps.AdlaStep`
        *  :class:`azureml.pipeline.steps.DatabricksStep`
        *  :class:`azureml.pipeline.steps.DataTransferStep`
        *  :class:`azureml.pipeline.steps.EstimatorStep`
        *  :class:`azureml.pipeline.steps.MpiStep`
        *  :class:`azureml.pipeline.steps.HyperDriveStep`
        *  :class:`azureml.pipeline.steps.AzureBatchStep`
        *  :class:`azureml.train.automl.AutoMLStep`

        See the following link for an overview on constructing a Pipeline: `https://aka.ms/pl-first-pipeline`


    :param name: The name of the pipeline step.
    :type name: str
    :param inputs: The list of step inputs.
    :type inputs: :class:`list`
    :param outputs: The list of step outputs.
    :type outputs: :class:`list`
    :param arguments: The list of step arguments.
    :type arguments: :class:`list`
    :param fix_port_name_collisions: If true and an input and output have the same name, the input is prefixed with
        'INPUT'
    :type fix_port_name_collisions: bool
    :param resource_inputs: The list of inputs to be used as resources. Resources are downloaded to the script folder
        and provide a way to change the behavior of script at run-time.
    :type resource_inputs: :class:`list`
    """

    __metaclass__ = ABCMeta

    def __init__(self, name, inputs, outputs, arguments=None, fix_port_name_collisions=False, resource_inputs=None):
        """
        Initialize PipelineStep.

        :param name: The name of the pipeline step.
        :type name: str
        :param inputs: The list of step inputs.
        :type inputs: :class:`list`
        :param outputs: The list of step outputs.
        :type outputs: :class:`list`
        :param arguments: The list of step arguments.
        :type arguments: :class:`list`
        :param fix_port_name_collisions: If true and an input and output have the same name, the input is prefixed with
            "INPUT_".
        :type fix_port_name_collisions: bool
        :param resource_inputs: The list of inputs to be used as resources. Resources are downloaded to the script
            folder and provide a way to change the behavior of script at run-time.
        :type resource_inputs: :class:`list`
        """
        self.name = name
        self.run_after_steps = []

        if inputs is None:
            inputs = []
        if outputs is None:
            outputs = []
        if resource_inputs is None:
            resource_inputs = []
        if arguments is None:
            arguments = []

        PipelineStep._validate_io_types(inputs, outputs, resource_inputs)

        input_port_names = [PipelineStep._get_input_port_name(input) for input in inputs]
        resource_input_port_names = [PipelineStep._get_input_port_name(input) for input in resource_inputs]
        output_port_names = [output._output_name for output in outputs]

        PipelineStep._assert_valid_port_names(input_port_names + resource_input_port_names,
                                              output_port_names, fix_port_name_collisions)

        self._inputs = inputs
        self._resource_inputs = resource_inputs
        self._arguments = arguments

        self._outputs = outputs
        for output in self._outputs:
            output._set_producer(self)

        if fix_port_name_collisions:
            # Fix port name collisions not supported for resources
            step_inputs = {PipelineStep._get_input_port_name(input): input for input in inputs}
            self._fix_port_name_collisions(input_port_names, output_port_names, step_inputs, arguments)

        self._update_input_with_pipeline_parameters()
        PipelineStep.validate_arguments(self._arguments, self._inputs, self._outputs)

    @staticmethod
    def _assert_valid_port_names(input_port_names, output_port_names, fix_port_name_collisions):
        import re
        invalid_name_exp = re.compile('\\W')

        def assert_valid_port_names(port_names, port_type):
            for port_name in port_names:
                if invalid_name_exp.search(port_name):
                    raise ValueError("[{port_name}] is not a valid {port_type} name as it may contain only letters, "
                                     "digits, and underscores.".format(port_name=port_name, port_type=port_type))

        def assert_unique_port_names(port_names, port_type, seen=None):
            if seen is None:
                seen = set()
            for port_name in port_names:
                if port_name in seen:
                    raise ValueError("[{port_name}] is repeated. {port_type} port names must be unique."
                                     .format(port_name=port_name, port_type=port_type.capitalize()))
                seen.add(port_name)

        if input_port_names is not None:
            assert_valid_port_names(input_port_names, 'input')
            assert_unique_port_names(input_port_names, 'input')

        if output_port_names is not None:
            assert_valid_port_names(output_port_names, 'output')
            assert_unique_port_names(output_port_names, 'output')

        if not fix_port_name_collisions:
            if input_port_names is not None and output_port_names is not None:
                assert_unique_port_names(input_port_names, 'Input and Output', set(output_port_names))

    @staticmethod
    def _validate_io_types(inputs, outputs, resource_inputs):
        def validate_input_type(input):
            if not isinstance(input, PipelineData) and not isinstance(input, InputPortBinding) \
                    and not isinstance(input, DataReference) and not isinstance(input, PortDataReference) \
                    and not isinstance(input, _PipelineIO) and not PipelineDataset.is_dataset(input) \
                    and not isinstance(input, PipelineDataset):
                raise ValueError("Unexpected input type: %s" % type(input))

            if PipelineDataset.is_dataset(input) or isinstance(input, PipelineDataset):
                PipelineDataset.validate_dataset(input)

        def validate_output_type(output):
            if not isinstance(output, PipelineData) and not isinstance(output, OutputPortBinding):
                raise ValueError("Unexpected output type: %s" % type(output))

        if inputs is not None:
            for input in inputs:
                validate_input_type(input)

        if outputs is not None:
            for output in outputs:
                validate_output_type(output)

        if resource_inputs is not None:
            for resource_input in resource_inputs:
                validate_input_type(resource_input)

    @staticmethod
    def _get_input_port_name(input):
        if isinstance(input, DataReference) or isinstance(input, PortDataReference):
            return input.data_reference_name
        if PipelineDataset.is_dataset(input):
            return PipelineDataset.default_name(input)
        else:
            return input.name

    def _fix_port_name_collisions(self, input_port_names, output_port_names, step_inputs, step_arguments):
        output_seen = set(output_port_names)
        new_inputs = []
        changed_inputs = {}
        for port_name in input_port_names:
            # check if any input port names are also output port names, if so append 'INPUT_'
            # prefix to data ref name
            step_input = step_inputs[port_name]
            if port_name in output_seen:
                new_name = "INPUT_{0}".format(port_name)
                if isinstance(step_input, DataReference):
                    new_bind_object = self._create_input_bind_object(step_input, new_name)

                    new_input = InputPortBinding(name=new_name,
                                                 bind_object=new_bind_object,
                                                 bind_mode=step_input.mode,
                                                 path_on_compute=step_input.path_on_compute,
                                                 overwrite=step_input.overwrite)

                    changed_inputs[step_input] = new_bind_object
                elif isinstance(step_input, PipelineData) or isinstance(step_input, PortDataReference):
                    new_bind_object = self._create_input_bind_object(step_input, new_name)
                    if isinstance(step_input, PipelineData):
                        new_bind_object._set_producer(step_input._producer)

                    new_input = InputPortBinding(name=new_name, bind_object=new_bind_object)

                    changed_inputs[step_input] = new_bind_object
                elif PipelineDataset.is_dataset(step_input):
                    new_bind_object = self._create_input_bind_object(step_input, new_name)
                    new_input = InputPortBinding(name=new_name)
                    changed_inputs[step_input] = new_bind_object
                elif isinstance(step_input, PipelineDataset):
                    new_bind_object = self._create_input_bind_object(step_input, new_name)
                    new_input = InputPortBinding(name=new_name, bind_object=new_bind_object,
                                                 bind_mode=new_bind_object.bind_mode,
                                                 path_on_compute=new_bind_object.path_on_compute,
                                                 overwrite=new_bind_object.overwrite)
                    changed_inputs[step_input] = new_bind_object
                elif isinstance(step_input, _PipelineIO):
                    new_input = self._create_input_bind_object(step_input, new_name)
                    changed_inputs[step_input] = new_input
                else:
                    new_bind_object = self._create_input_bind_object(step_input.bind_object, new_name)

                    if isinstance(new_bind_object, PipelineData) or isinstance(new_bind_object, OutputPortBinding):
                        new_bind_object._set_producer(step_input.bind_object._producer)
                    new_input = InputPortBinding(name=new_name,
                                                 bind_object=new_bind_object,
                                                 bind_mode=step_input.bind_mode,
                                                 path_on_compute=step_input.path_on_compute,
                                                 overwrite=step_input.overwrite)
                    changed_inputs[step_input.bind_object] = new_bind_object
                    changed_inputs[step_input] = new_input
                new_inputs.append(new_input)
            elif isinstance(step_input, InputPortBinding):
                bind_object_name = step_input.get_bind_object_name()

                if bind_object_name in output_seen:
                    new_name = "INPUT_{0}".format(bind_object_name)
                    new_bind_object = self._create_input_bind_object(step_input.bind_object, new_name)
                    if isinstance(new_bind_object, PipelineData) or isinstance(new_bind_object, OutputPortBinding):
                        new_bind_object._set_producer(step_input.bind_object._producer)
                    new_input = InputPortBinding(name=new_name,
                                                 bind_object=new_bind_object,
                                                 bind_mode=step_input.bind_mode,
                                                 path_on_compute=step_input.path_on_compute,
                                                 overwrite=step_input.overwrite)

                    changed_inputs[step_input] = new_input
                    changed_inputs[step_input.bind_object] = new_bind_object
                    new_inputs.append(new_input)
                else:
                    new_inputs.append(step_input)
            else:
                new_inputs.append(step_input)

        new_arguments = []
        for argument in step_arguments:
            if argument in changed_inputs.keys():
                new_arguments.append(changed_inputs[argument])
            else:
                new_arguments.append(argument)

        self._inputs = new_inputs
        self._arguments = new_arguments

    def run_after(self, step):
        """
        Append this step after the provided step.

        :param step: The pipeline step to run before this step.
        :type step: azureml.pipeline.core.PipelineStep
        """
        self.run_after_steps.append(step)

    @abstractmethod
    def create_node(self, graph, default_datastore, context):
        """
        Create a node for the pipeline graph based on this step.

        :param graph: The graph to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: The graph context object.
        :type context: _GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        pass

    @staticmethod
    def _process_pipeline_io(arguments, inputs, outputs):
        io_ref_dict = {}
        # replace tuple representation with _PipelineIO objects
        for entity_list in [arguments, inputs, outputs]:
            PipelineStep._replace_ioref(entity_list, io_ref_dict)

    @staticmethod
    def _validate_params(params, runconfig_pipeline_params):
        if params and runconfig_pipeline_params:
            for param_name, param_value in params.items():
                if param_name in runconfig_pipeline_params:
                    raise ValueError('Duplicate parameter {0} in params and runconfig_pipeline_params '
                                     'parameters'.format(param_name))

        import re
        invalid_name_exp = re.compile('\\W')
        for param_name in params:
            if invalid_name_exp.search(param_name):
                raise ValueError(
                    "[{param_name}] is not a valid parameter name as it may contain only letters, "
                    "digits, and underscores.".format(param_name=param_name))

    @staticmethod
    def _replace_ioref(entity_list, io_ref_dict):
        if entity_list:
            for index in range(0, len(entity_list)):
                # replace tuples only
                if isinstance(entity_list[index], tuple):
                    tuple_val = entity_list[index]
                    entity_list[index] = PipelineStep._tuple_to_ioref(tuple_val, io_ref_dict)

    @staticmethod
    def _tuple_to_ioref(tuple_val, io_ref_dict=None):
        # verify structure of the tuple and types of items in the tuple
        _PipelineIO._validate(tuple_val)

        # if a tuple is already replaced, get _PipelineIO object created for the tuple
        # this is needed because a tuple used in arguments will be used in inputs or outputs as well
        if io_ref_dict is not None and tuple_val in io_ref_dict:
            io_ref = io_ref_dict[tuple_val]
        else:
            io_ref = _PipelineIO.create(tuple_val)
            if io_ref_dict is not None:
                io_ref_dict[tuple_val] = io_ref
        return io_ref

    @staticmethod
    def _check_for_duplicates(pipeline_params_in_step_params, pipeline_params_implicit, pipeline_params_runconfig):
        if pipeline_params_runconfig:
            for param in pipeline_params_runconfig.values():
                if pipeline_params_in_step_params and param.name in pipeline_params_in_step_params:
                    dvalue1 = pipeline_params_in_step_params[param.name].default_value
                    dvalue2 = param.default_value
                    PipelineStep._raise_defaultvalue_error(dvalue1, dvalue2, param.name)

                if pipeline_params_implicit and param.name in pipeline_params_implicit:
                    dvalue1 = pipeline_params_implicit[param.name].default_value
                    dvalue2 = param.default_value
                    PipelineStep._raise_defaultvalue_error(dvalue1, dvalue2, param.name)

    @staticmethod
    def _raise_defaultvalue_error(dvalue1, dvalue2, param_name):
        if dvalue1 != dvalue2:
            raise Exception('Pipeline parameters with same name {0} '
                            'but different values {1}, {2} used'
                            .format(param_name, dvalue1, dvalue2))

    @staticmethod
    def _configure_pipeline_parameters(graph, node, pipeline_params_in_step_params=None,
                                       pipeline_params_implicit=None, pipeline_params_runconfig=None):
        PipelineStep._check_for_duplicates(pipeline_params_in_step_params, pipeline_params_implicit,
                                           pipeline_params_runconfig)
        if pipeline_params_in_step_params is not None:
            graph._add_pipeline_params(list(pipeline_params_in_step_params.values()))
        if pipeline_params_implicit is not None:
            graph._add_pipeline_params(list(pipeline_params_implicit.values()))
        if pipeline_params_runconfig is not None:
            graph._add_pipeline_params(list(pipeline_params_runconfig.values()))
        node._attach_pipeline_parameters(pipeline_params_implicit, pipeline_params_in_step_params,
                                         pipeline_params_runconfig)

    @staticmethod
    def _get_pipeline_parameters_implicit(arguments=None):
        pipeline_params = {}
        if arguments is not None:
            PipelineStep._process_pipeline_parameters(arguments, pipeline_params)
        return pipeline_params

    @staticmethod
    def _get_pipeline_parameters_step_params(params):
        pipeline_params = {}
        if params is not None:
            for param_name, param_value in params.items():
                if isinstance(param_value, PipelineParameter):
                    if param_name not in pipeline_params:
                        pipeline_params[param_name] = param_value
                    else:
                        if pipeline_params[param_name].default_value != param_value.default_value:
                            raise Exception('Pipeline parameters with same name {0} '
                                            'but different values {1}, {2} used'
                                            .format(param_name,
                                                    pipeline_params[param_name].default_value,
                                                    param_value.default_value))
        return pipeline_params

    @staticmethod
    def _get_pipeline_parameters_runconfig(runconfig_pipeline_params):
        pipeline_params = {}
        if runconfig_pipeline_params is not None:
            for param_name, param_value in runconfig_pipeline_params.items():
                if isinstance(param_value, PipelineParameter):
                    if param_name not in pipeline_params:
                        pipeline_params[param_name] = param_value
                    else:
                        if pipeline_params[param_name].default_value != param_value.default_value:
                            raise Exception('Pipeline parameters with same name {0} '
                                            'but different values {1}, {2} used'
                                            .format(param_name,
                                                    pipeline_params[param_name].default_value,
                                                    param_value.default_value))
                else:
                    typename = type(param_value).__name__
                    raise ValueError('Invalid type ({0}) for parameter {1}. '
                                     'Expected type is PipelineParameter'.format(typename, param_name))

        return pipeline_params

    @staticmethod
    def _validate_runconfig_pipeline_params(runconfig_pipeline_params, param_defs):
        if runconfig_pipeline_params:
            for param_name, param_value in runconfig_pipeline_params.items():
                matches = list(filter(lambda param_def: param_def.name == param_name, param_defs))
                if len(matches) == 0 or len(matches) > 1:
                    raise ValueError('Runconfig property name {0} is not valid'.format(param_name))
                else:
                    if param_name not in _ModuleParameterProvider._get_parameterizable_runconfig_properties():
                        raise ValueError('Runconfig property {0} is not parameterizable'.format(param_name))

    @staticmethod
    def _process_pipeline_parameters(parameterizable_list, pipeline_params):
        if parameterizable_list is not None:
            for item in parameterizable_list:
                if isinstance(item, PipelineParameter):
                    if item.name not in pipeline_params:
                        pipeline_params[item.name] = item
                    else:
                        if pipeline_params[item.name].default_value != item.default_value:
                            raise Exception('Pipeline parameters with same name {0} '
                                            'but different values {1}, {2} used'
                                            .format(item.name,
                                                    pipeline_params[item.name].default_value,
                                                    item.default_value))

    @staticmethod
    def _create_input_bind_object(step_input, new_name):
        """
        Create input bind object with the new given name.

        :param step_input: The step input object to recreate.
        :type step_input: PipelineData, DataReference, PortDataReference
        :param new_name: The new name for the input.
        :type new_name: str

        :return: The new step input.
        :rtype: DataReference or PortDataReference or PipelineData or OutputPortBinding
        """
        if isinstance(step_input, DataReference):
            return DataReference(datastore=step_input.datastore,
                                 data_reference_name=new_name,
                                 path_on_datastore=step_input.path_on_datastore,
                                 mode=step_input.mode,
                                 path_on_compute=step_input.path_on_compute,
                                 overwrite=step_input.overwrite)
        elif isinstance(step_input, PortDataReference):
            new_data_ref = DataReference(datastore=step_input._data_reference.datastore,
                                         data_reference_name=new_name,
                                         path_on_datastore=step_input.path_on_datastore,
                                         mode=step_input._data_reference.mode,
                                         path_on_compute=step_input._data_reference.path_on_compute,
                                         overwrite=step_input._data_reference.overwrite)

            return PortDataReference(context=step_input._context,
                                     pipeline_run_id=step_input.pipeline_run_id,
                                     data_reference=new_data_ref)
        elif PipelineDataset.is_dataset(step_input):
            return PipelineDataset(step_input, new_name)
        elif isinstance(step_input, PipelineDataset):
            return PipelineDataset(step_input.dataset, new_name, bind_mode=step_input.bind_mode,
                                   path_on_compute=step_input.path_on_compute, overwrite=step_input.overwrite,
                                   parameter_name=step_input.parameter_name)
        elif isinstance(step_input, PipelineData):
            return PipelineData(name=new_name,
                                datastore=step_input.datastore,
                                output_mode=step_input._output_mode,
                                output_path_on_compute=step_input._output_path_on_compute,
                                output_overwrite=step_input._output_overwrite,
                                output_name=step_input._output_name)
        elif isinstance(step_input, OutputPortBinding):
            return OutputPortBinding(name=new_name,
                                     datastore=step_input.datastore,
                                     output_name=step_input._output_name,
                                     bind_mode=step_input.bind_mode,
                                     path_on_compute=step_input.path_on_compute,
                                     overwrite=step_input.overwrite,
                                     pipeline_output_name=step_input.pipeline_output_name)
        elif isinstance(step_input, _PipelineIO):
            return _PipelineIO(datapath=step_input._datapath,
                               datapath_param=step_input._datapath_param,
                               datapath_compute_binding=step_input._datapath_compute_binding,
                               name=new_name)

    def _sub_params_in_script(self, script_path, pattern, repl):
        """
        Substitute parameters in a given script with the replacement.

        :param script_path: Script path for the substitution.
        :type script_path: str
        :param pattern: Pattern in the script to replace
        :type pattern: Pattern
        :param repl: Replacement can be a string or function.
                     If it is a function, it is called for every non-overlapping occurrence of pattern.
                     The function takes a single match object argument, and returns the replacement string.
        :type repl: str or function
        """
        if not os.path.isfile(script_path):
            abs_path = os.path.abspath(script_path)
            raise ValueError('script not found at:', abs_path)

        import re
        with open(script_path, 'r') as in_file:
            buf = in_file.readlines()
        with open(script_path, 'w') as out_file:
            for line in buf:
                match = pattern.search(line)
                if match:
                    line = re.sub(pattern, repl, line)
                out_file.write(line)

    @staticmethod
    def validate_arguments(arguments, inputs, outputs):
        """
        Validate the step inputs and outputs in the arguments list are in the input and output lists.

        :param arguments: List of step arguments.
        :type arguments: :class:`list`
        :param inputs: List of step inputs.
        :type inputs: :class:`list`
        :param outputs: List of step outputs.
        :type outputs: :class:`list`
        """
        if arguments is not None:
            for argument in arguments:
                valid = False
                if isinstance(argument, InputPortBinding):
                    for input in inputs:
                        if input == argument or argument.bind_object == input:
                            valid = True
                            break
                    if not valid:
                        raise ValueError(
                            "Input %s appears in arguments list but is not in the input list" % (
                                argument.name))
                elif isinstance(argument, PipelineData):
                    for output in outputs:
                        if output == argument:
                            valid = True
                            break
                    if not valid:
                        for input in inputs:
                            if argument == input or isinstance(input, InputPortBinding) and \
                                    input.bind_object == argument:
                                valid = True
                                break
                    if not valid:
                        raise ValueError(
                            "Input/Output %s appears in arguments list but is not in the input/output lists" % (
                                argument.name))
                elif isinstance(argument, _PipelineIO):
                    if argument not in inputs:
                        raise ValueError('Parameterized datapath {0} is not in input list'.format(argument.name))
                elif isinstance(argument, DataReference) or PipelineDataset.is_dataset(argument):
                    for input in inputs:
                        if input == argument or (isinstance(input, InputPortBinding) and
                                                 input.bind_object == argument):
                            valid = True
                            break
                    if not valid:
                        name = PipelineDataset.default_name(argument) if PipelineDataset.is_dataset(argument) \
                            else argument.data_reference_name
                        raise ValueError("Input %s appears in arguments list but is not in the input list" % (name))
                elif isinstance(argument, PipelineDataset):
                    for input in inputs:
                        if input == argument or (isinstance(input, InputPortBinding) and
                                                 input.bind_object == argument):
                            valid = True
                            break
                    if not valid:
                        raise ValueError("Input {} appears in arguments list but is not in the input list"
                                         .format(argument.name))
                elif isinstance(argument, PortDataReference):
                    for input in inputs:
                        if input == argument or (isinstance(input, InputPortBinding) and
                                                 input.bind_object == argument):
                            valid = True
                            break
                    if not valid:
                        raise ValueError(
                            "Input %s appears in arguments list but is not in the input list" % (
                                argument.data_reference_name))
                elif isinstance(argument, OutputPortBinding):
                    for output in outputs:
                        if output == argument:
                            valid = True
                            break
                    if not valid:
                        raise ValueError(
                            "Output %s appears in arguments list but is not in the output list" % (
                                argument.name))

    def _update_input_with_pipeline_parameters(self):
        for arg in self._arguments:
            if isinstance(arg, PipelineParameter):
                if PipelineDataset.is_dataset(arg.default_value):
                    self._inputs.append(PipelineDataset(dataset=arg.default_value,
                                                        name=PipelineDataset.default_name(arg.default_value),
                                                        parameter_name=arg.name))
                elif isinstance(arg.default_value, PipelineDataset):
                    plds = arg.default_value
                    self._inputs.append(PipelineDataset(dataset=plds.dataset, name=plds.name, parameter_name=arg.name,
                                                        bind_mode=plds.bind_mode, path_on_compute=plds.path_on_compute,
                                                        overwrite=plds.overwrite))

    @staticmethod
    def resolve_input_arguments(arguments, inputs, outputs, params):
        """
        Match inputs and outputs to arguments so argument string is produced correctly.

        :param arguments: List of step arguments.
        :type arguments: :class:`list`
        :param inputs: List of step inputs.
        :type inputs: :class:`list`
        :param outputs: List of step outputs.
        :type outputs: :class:`list`
        :param params: List of step parameters.
        :type params: :class:`list`

        :return: The resolved arguments list.
        :rtype: :class:`list`
        """
        resolved_arguments = []
        for argument in arguments:
            if isinstance(argument, InputPortBinding):
                for input in inputs:
                    if input == argument:
                        resolved_arguments.append(input)
                        break
                    elif argument.bind_object == input:
                        resolved_arguments.append(input)
                        break
            elif isinstance(argument, PipelineData):
                found_input = False
                for input in inputs:
                    if input == argument:
                        resolved_arguments.append(input)
                        found_input = True
                        break
                    elif isinstance(input, InputPortBinding) and argument == input.bind_object:
                        resolved_arguments.append(input)
                        found_input = True
                        break
                if not found_input:
                    for output in outputs:
                        if output == argument:
                            resolved_arguments.append(output)
            elif isinstance(argument, PortDataReference):
                for input in inputs:
                    if input == argument:
                        resolved_arguments.append(input)
                        break
                    elif isinstance(input, InputPortBinding) and argument == input.bind_object:
                        resolved_arguments.append(input)
                        break
            elif isinstance(argument, DataReference):
                for input in inputs:
                    if input == argument:
                        resolved_arguments.append(input)
                        break
                    elif isinstance(input, InputPortBinding) and argument == input.bind_object:
                        resolved_arguments.append(input)
                        break
            elif isinstance(argument, PipelineDataset):
                for input in inputs:
                    if input == argument:
                        resolved_arguments.append(input)
                        break
                    elif isinstance(input, InputPortBinding) and argument == input.bind_object:
                        resolved_arguments.append(input)
                        break
            elif PipelineDataset.is_dataset(argument):
                for input in inputs:
                    if input == argument:
                        resolved_arguments.append(PipelineDataset(input, name=PipelineDataset.default_name(input)))
                    elif isinstance(input, InputPortBinding) and argument == input.bind_object:
                        pl_ds = PipelineDataset(input.bind_object, PipelineDataset.default_name(input.bind_object))
                        resolved_arguments.append(pl_ds)
            elif isinstance(argument, _PipelineIO):
                for input in inputs:
                    if input == argument:
                        resolved_arguments.append(input)
                        break
                    elif isinstance(input, InputPortBinding) and argument == input.bind_object:
                        resolved_arguments.append(input)
                        break
            elif isinstance(argument, PipelineParameter):
                resolved_arguments.append("$AML_PARAMETER_{0}".format(argument.name))
            elif isinstance(argument, str):
                found = False
                for param_name in params:
                    if param_name == argument:
                        resolved_arguments.append("$AML_PARAMETER_{0}".format(argument))
                        found = True
                if not found:
                    resolved_arguments.append(argument)
            else:
                resolved_arguments.append(argument)

        return resolved_arguments

    def create_module_def(self, execution_type, input_bindings, output_bindings, param_defs=None,
                          create_sequencing_ports=True, allow_reuse=True, version=None):
        """
        Create the module definition object that describes the step.

        :param execution_type: The execution type of the module.
        :type execution_type: str
        :param input_bindings: The step input bindings.
        :type input_bindings: :class:`list`
        :param output_bindings: The step output bindings.
        :type output_bindings: :class:`list`
        :param param_defs: The step param definitions.
        :type param_defs: :class:`list`
        :param create_sequencing_ports: If true sequencing ports will be created for the module.
        :type create_sequencing_ports: bool
        :param allow_reuse: If true the module will be available to be reused in future Pipelines.
        :type allow_reuse: bool
        :param version: The version of the module.
        :type version: str

        :return: The module def object.
        :rtype: azureml.pipeline.core.graph.ModuleDef
        """
        return Module.module_def_builder(self.name, self.name, execution_type, input_bindings,
                                         output_bindings, param_defs,
                                         create_sequencing_ports, allow_reuse, version)

    def create_input_output_bindings(self, inputs, outputs, default_datastore, resource_inputs=None):
        """
        Create input and output bindings from the step inputs and outputs.

        :param inputs: The list of step inputs.
        :type inputs: :class:`list`
        :param outputs: The list of step outputs.
        :type outputs: :class:`list`
        :param default_datastore: The default datastore.
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param resource_inputs: The list of inputs to be used as resources. Resources are downloaded to the script
            folder and provide a way to change the behavior of script at run-time.
        :type resource_inputs: :class:`list`

        :return: Tuple of the input bindings and output bindings.
        :rtype: :class:`list`, :class:`list`
        """
        def create_input_binding(step_input):
            if isinstance(step_input, InputPortBinding):
                return step_input
            if isinstance(step_input, DataReference):
                return InputPortBinding(name=step_input.data_reference_name,
                                        bind_object=step_input,
                                        bind_mode=step_input.mode,
                                        path_on_compute=step_input.path_on_compute,
                                        overwrite=step_input.overwrite)
            if isinstance(step_input, _PipelineIO):
                return step_input.as_input_port_binding()
            if PipelineDataset.is_dataset(step_input) or isinstance(step_input, PipelineDataset):
                if PipelineDataset.is_dataset(step_input):
                    step_input = PipelineDataset(dataset=step_input, name=PipelineDataset.default_name(step_input))
                return InputPortBinding(name=step_input.name,
                                        bind_object=step_input,
                                        bind_mode=step_input.bind_mode,
                                        path_on_compute=step_input.path_on_compute,
                                        overwrite=step_input.overwrite)
            return step_input.create_input_binding()

        input_bindings = [create_input_binding(step_input) for step_input in inputs]

        if resource_inputs is not None:
            input_bindings += [create_input_binding(input).as_resource() for input in resource_inputs]

        output_bindings = []
        for step_output in outputs:
            output_binding = step_output
            if step_output._producer != self:
                raise ValueError("Step output %s can not be used as an output for step %s, as it is already an "
                                 "output of step %s." % (step_output.name, self.name, step_output._producer.name))
            if isinstance(step_output, PipelineData):
                output_binding = OutputPortBinding(name=step_output.name,
                                                   datastore=step_output.datastore,
                                                   output_name=step_output._output_name,
                                                   bind_mode=step_output._output_mode,
                                                   path_on_compute=step_output._output_path_on_compute,
                                                   overwrite=step_output._output_overwrite,
                                                   data_type=step_output._data_type,
                                                   is_directory=step_output._is_directory,
                                                   pipeline_output_name=step_output._pipeline_output_name,
                                                   training_output=step_output._training_output)

            if output_binding.datastore is None:
                output_binding.datastore = default_datastore
                if default_datastore is None:
                    raise ValueError("DataStore not provided for output: %s" % step_output.name)
            output_bindings.append(output_binding)

        return input_bindings, output_bindings

    def get_source_directory_and_hash_paths(self, context, source_directory, script_name, hash_paths):
        """
        Get source directory and hash paths for the step.

        :param context: The graph context object.
        :type context: _GraphContext
        :param source_directory: The source directory for the step.
        :type source_directory: str
        :param script_name: The script name for the step.
        :type script_name: str
        :param hash_paths: The hash paths to use when determining the module fingerprint.
        :type hash_paths: :class:`list`

        :return: The source directory and hash paths.
        :rtype: str, :class:`list`
        """
        source_directory = source_directory
        if source_directory is None:
            source_directory = context.default_source_directory

        script_path = os.path.join(source_directory, script_name)
        if not os.path.isfile(script_path):
            abs_path = os.path.abspath(script_path)
            raise ValueError("Step [%s]: script not found at: %s. Make sure to specify an appropriate "
                             "source_directory on the Step or default_source_directory on the Pipeline."
                             % (self.name, abs_path))

        fq_hash_paths = []
        for hash_path in hash_paths:
            if not os.path.isabs(hash_path):
                hash_path = os.path.join(source_directory, hash_path)
                fq_hash_paths.append(hash_path)
                if not os.path.isfile(hash_path) and not os.path.isdir(hash_path):
                    raise ValueError("step [%s]: hash_path does not exist: %s" % (self.name, hash_path))

        return source_directory, fq_hash_paths


class PipelineData(object):
    """
    PipelineData represents a piece of intermediate data in a pipeline.

    PipelineData can be produced by one step and consumed in another step by providing the PipelineData object as an
    output of one step and the input of one or more steps.

    .. remarks::

        PipelineData represent outputs a step will produce when it is run. Use PipelineData when creating steps
        to describe the files or directories which will be generated by the step. These outputs will be added to
        the specified Datastore and can be retrieved/viewed later.

        For example the following step produces one output, named "model":

        .. code-block:: python

            from azureml.pipeline.core import PipelineData
            from azureml.pipeline.steps import PythonScriptStep

            datastore = ws.get_default_datastore()
            step_output = PipelineData("model", datastore=datastore)
            step = PythonScriptStep(script_name="train.py",
                                    arguments=["--model", step_output],
                                    outputs=[step_output],
                                    compute_target=aml_compute,
                                    source_directory=source_directory)

        In this case, the train.py script will write the model it produces to the location which is provided to the
        script through the --model argument.

        PipelineData objects are also used when constructing Pipelines to describe step dependencies. To specify that
        a step requires the output of another step as input, use a PipelineData object in the constructor of both
        steps.

        For example the train step in this Pipeline depends on the processed_data output of the process step:

        .. code-block:: python

            from azureml.pipeline.core import Pipeline, PipelineData
            from azureml.pipeline.steps import PythonScriptStep

            datastore = ws.get_default_datastore()
            process_step_output = PipelineData("processed_data", datastore=datastore)
            process_step = PythonScriptStep(script_name="process.py",
                                            arguments=["--model", process_step_output],
                                            outputs=[process_step_output],
                                            compute_target=aml_compute,
                                            source_directory=source_directory)
            train_step = PythonScriptStep(script_name="train.py",
                                          arguments=["--data", process_step_output],
                                          inputs=[process_step_output],
                                          compute_target=aml_compute,
                                          source_directory=source_directory)

            pipeline = Pipeline(workspace=ws, steps=[process_step, train_step])

        This will create a Pipeline with two steps. The process step will be executed first, then after it has
        completed, the train step will be executed. The orchestrator will provide the output produced by the process
        step to the train step.

        See this page for further examples of using PipelineData to construct a Pipeline: https://aka.ms/pl-data-dep

        For supported compute types, PipelineData can also be used to specify how the data will be produced and
        consumed by the run. There are two supported methods:

        * Mount (default): The input or output data is mounted to local storage on the compute
          node, and an environment variable is set which points to the path of this data ($AZUREML_DATAREFERENCE_name).
          For convenience, you can pass the PipelineData object in as one of the arguments to your script, and
          this will resolve to the path of that data. For outputs, your compute script should create a file
          or directory at this output path.

        * Upload: Specify an output_path_on_compute corresponding to a file or directory
          name that your script will generate. (Environment variables are not used in this case.)


    :param name: Name of the PipelineData object. Can only contain letters, digits, and underscores.
    :type name: str
    :param datastore: Datastore the PipelineData will reside on.  If unspecified, the default datastore is used
    :type datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
    :param output_name: Name of the output, if None name is used.
    :type output_name: str
    :param output_mode: Specifies whether the producing step will use "upload" or "mount" method to access the data.
    :type output_mode: str
    :param output_path_on_compute: For "upload" mode, the path the module writes the output to.
    :type output_path_on_compute: str
    :param output_overwrite: For "upload" mode, whether to overwrite existing data.
    :type output_overwrite: bool
    :param data_type: Optional. Data type can be used to specify the expected type of the output and to detail how
                      consuming steps should use the data. Can be any user-defined string.
    :type data_type: str
    :param is_directory: Whether the data is a directory or single file. This is only used to determine the data type
                         if the data_type parameter is not provided.
    :type is_directory: bool
    :param pipeline_output_name: If provided this output will be available by using
        PipelineRun.get_pipeline_output(). Pipeline output names must be unique in the pipeline.
    :param training_output: Defines output for training result. This is needed only for specific trainings which
                            result in different kinds of outputs such as Metrics and Model.
                            For example, :class:`azureml.train.automl.AutoMLStep` results in metrics and model.
                            You can also define specific training iteration or metric used to get best model.
    :type training_output: azureml.pipeline.core.TrainingOutput, optional
    """

    def __init__(self, name, datastore=None, output_name=None, output_mode="mount", output_path_on_compute=None,
                 output_overwrite=None, data_type=None, is_directory=None, pipeline_output_name=None,
                 training_output=None):
        """
        Initialize PipelineData.

        :param name: Name of the PipelineData object. Can only contain letters, digits, and underscores.
        :type name: str
        :param datastore: Datastore the PipelineData will reside on.  If unspecified, the default datastore is used
        :type datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param output_name: Name of the output, if None name is used.
        :type output_name: str
        :param output_mode: Specifies whether the producing step will use "upload" or "mount"
            method to access the data.
        :type output_mode: str
        :param output_path_on_compute: For "upload" mode, the path the module writes the output to.
        :type output_path_on_compute: str
        :param output_overwrite: For "upload" mode, whether to overwrite existing data.
        :type output_overwrite: bool
        :param data_type: Optional. Data type can be used to specify the expected type of the output and to detail how
                          consuming steps should use the data. Can be any user-defined string.
        :type data_type: str
        :param is_directory: Whether the data is a directory or single file.
        :type is_directory: bool
        :param pipeline_output_name: If provided this output will be available by using
            PipelineRun.get_pipeline_output(). Pipeline output names must be unique in the pipeline.
        :type pipeline_output_name: str
        :param training_output: Defines output for training result. This is needed only for specific trainings which
                                result in different kinds of outputs such as Metrics and Model.
                                For example, :class:`azureml.train.automl.AutoMLStep` results in metrics and model.
                                You can also define specific training iteration or metric used to get best model.
        :type training_output: azureml.pipeline.core.TrainingOutput, optional
        """
        import re
        invalid_name_exp = re.compile('\\W')
        if invalid_name_exp.search(name):
            raise ValueError("PipelineData name: [{name}] is not a valid, as it may contain only letters, "
                             "digits, and underscores.".format(name=name))
        self._name = name

        if output_name is None:
            output_name = name
        self._output_name = output_name

        import re
        invalid_name_exp = re.compile('\\W')
        if invalid_name_exp.search(output_name):
            raise ValueError("PipelineData output_name: [{name}] is not a valid, as it may contain only letters, "
                             "digits, and underscores.".format(name=output_name))

        self._datastore = datastore
        self._producer = None
        self._output_mode = output_mode
        self._output_path_on_compute = output_path_on_compute
        self._output_overwrite = output_overwrite
        self._data_type = data_type
        self._is_directory = is_directory
        self._pipeline_output_name = pipeline_output_name

        if self._output_mode not in ["mount", "upload"]:
            raise ValueError("Invalid output mode [%s]" % self._output_mode)

        self._training_output = training_output

    def _set_producer(self, step):
        self._producer = step

    def as_download(self, input_name=None, path_on_compute=None, overwrite=None):
        """
        Consume the PipelineData as download.

        :param input_name: Use to specify a name for this input.
        :type input_name: str
        :param path_on_compute: The path on the compute to download to.
        :type path_on_compute: str
        :param overwrite: Use to indicate whether to overwrite existing data.
        :type overwrite: bool

        :return: The InputPortBinding with this PipelineData as the source.
        :rtype: azureml.pipeline.core.graph.InputPortBinding
        """
        return self.create_input_binding(input_name=input_name, mode="download", path_on_compute=path_on_compute,
                                         overwrite=overwrite)

    def as_mount(self, input_name=None):
        """
        Consume the PipelineData as mount.

        :param input_name: Use to specify a name for this input.
        :type input_name: str

        :return: The InputPortBinding with this PipelineData as the source.
        :rtype: azureml.pipeline.core.graph.InputPortBinding
        """
        return self.create_input_binding(input_name=input_name, mode="mount")

    def as_input(self, input_name):
        """
        Create an InputPortBinding and specify an input name (but use default mode).

        :param input_name: Use to specify a name for this input.
        :type input_name: str

        :return: The InputPortBinding with this PipelineData as the source.
        :rtype: azureml.pipeline.core.graph.InputPortBinding
        """
        return self.create_input_binding(input_name=input_name)

    def create_input_binding(self, input_name=None, mode=None, path_on_compute=None, overwrite=None):
        """
        Create input binding.

        :param input_name: The name of the input.
        :type input_name: str
        :param mode: The mode to access the PipelineData ("mount" or "download").
        :type mode: str
        :param path_on_compute: For "download" mode, the path on the compute the data will reside.
        :type path_on_compute: str
        :param overwrite: For "download" mode, whether to overwrite existing data.
        :type overwrite: bool

        :return: The InputPortBinding with this PipelineData as the source.
        :rtype: azureml.pipeline.core.graph.InputPortBinding
        """
        if input_name is None:
            input_name = self._name

        # TODO: currently defaulting to mount, but what if the compute doesnt support it?
        # should be getting default value from somewhere else? should default be passthrough??
        if mode is None:
            mode = "mount"

        if mode not in ["mount", "download"]:
            raise ValueError("Input [%s] has an invalid mode [%s]" % (input_name, mode))

        input_binding = InputPortBinding(
            name=input_name,
            bind_object=self,
            bind_mode=mode,
            path_on_compute=path_on_compute,
            overwrite=overwrite,
        )

        return input_binding

    def get_env_variable_name(self):
        """
        Return the name of the environment variable for this PipelineData.

        :return: The environment variable name.
        :rtype: str
        """
        return self.__str__()

    @property
    def name(self):
        """
        Name of the PipelineData object.

        :return: Name.
        :rtype: str
        """
        return self._name

    @property
    def datastore(self):
        """
        Datastore the PipelineData will reside on.

        :return: The Datastore object.
        :rtype: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        """
        return self._datastore

    @property
    def data_type(self):
        """
        Type of data which will be produced.

        :return: The data type name.
        :rtype: str
        """
        return self._data_type

    def __str__(self):
        """
        __str__ override.

        :return: str representation of the PipelineData
        :rtype: str
        """
        return "$AZUREML_DATAREFERENCE_{0}".format(self.name)

    def __repr__(self):
        """
        Return __str__.

        :return: str representation of the PipelineData
        :rtype: str
        """
        return self.__str__()


class _PipelineGraphBuilder(object):
    """_PipelineGraphBuilder."""

    _registered_builders = {}

    @staticmethod
    def register(collection_name, builder):
        """
        Register builders.

        :param collection_name: collection name
        :type collection_name: str
        :param builder: builder
        :type builder: _SequentialPipelineGraphBuilder, _ParallelPipelineGraphBuilder
        """
        _PipelineGraphBuilder._registered_builders[collection_name] = builder

    def __init__(self, builders=None, resolve_closure=True, default_datastore=None, context=None):
        """
        Initialize _PipelineGraphBuilder.

        :param builders: builders
        :type builders: dict
        :param resolve_closure: whether to resolve closure
        :type resolve_closure: bool
        :param default_datastore: default datastore
        :type default_datastore: str
        :param context: graph context object
        :type context: _GraphContext
        """
        if context is None:
            raise ValueError("a valid graph context is required")

        self._context = context
        self._default_datastore = default_datastore

        if builders is None:
            builders = _PipelineGraphBuilder._registered_builders

        self._builders = builders
        self._resolve_closure = resolve_closure

    def build(self, name, steps, finalize=True, regenerate_outputs=False):
        """
        Build a graph that executes the required pipeline steps and produces any required pipeline data.

        :param name: a friendly name for the graph, this is useful for tracking
        :type name: str
        :param steps: pipeline steps and/or data that the graph is required to include
        :type steps: Union[PipelineData, PipelineStep, list]
        :param finalize: call finalize on the graph after construction
        :type finalize: bool
        :param regenerate_outputs: set True to force a new run during finalization (disallows module/datasource reuse)
        :type regenerate_outputs: bool

        :return: the constructed graph
        :rtype: Graph
        """
        if (self._default_datastore is None and self._context._workspace is not None):
            try:
                # Attempt to find the default datastore of the workspace if the user has not specified one
                default_datastore = self._context._workspace.get_default_datastore()
                if default_datastore is not None:
                    self._default_datastore = default_datastore
            except HttpOperationError:
                # If the workspace does not have a default datastore, keep default_datastore unset
                pass

        graph = self.construct(name, steps)
        if finalize:
            graph.finalize(regenerate_outputs=regenerate_outputs)
        return graph

    def construct(self, name, steps):
        """
        Construct a graph but does not upload modules.

        :param name: a friendly name for the graph, this is useful for tracking
        :type name: str
        :param steps: pipeline steps and/or data that the graph is required to include
        :type steps: Union[PipelineData, PipelineStep, list]

        :return: the constructed graph
        :rtype: Graph
        """
        self._builderStack = []
        self._nodeStack = []
        self._step2node = {}
        self._graph = Graph(name, self._context)
        self._nodeStack.append([])
        self.process_collection(steps)
        for builder in self._builderStack[::-1]:
            builder.apply_rules()

        return self._graph

    def validate(self):
        """Validate inputs."""
        # check for dangling inputs
        pass

    def process_collection(self, collection):
        """
        Process collection.

        :param collection: collection
        :type collection: list

        :return: list of added nodes.
        :rtype: :class:`list`
        """
        # for outputs, just include the producer step?
        if isinstance(collection, PipelineData):
            if collection._producer is None:
                raise ValueError("Cannot build graph as step output [%s] does not have a producer. "
                                 "Please add to the outputs list of the step that produces it" % collection._name)
            collection = collection._producer

        # just a step?
        if isinstance(collection, PipelineStep):
            return self.process_step(collection)

        # delegate to correct builder
        builder = self.create_builder(collection)
        self._nodeStack.append([])
        self._builderStack.append(builder)
        builder.process_collection(collection)
        added_nodes = self._nodeStack.pop()
        self._nodeStack[-1].extend(added_nodes)
        return added_nodes

    def assert_node_valid(self, step, graph, node):
        """
        Raise an assert when node is invalid.

        :param step: step
        :type step: pipeline step
        :param graph: graph
        :type graph: Graph
        :param node: node
        :type node: Node
        """
        if node is None:
            raise ValueError("step %s type %s: create_node needs to return a valid Node (got None)"
                             % (step.name, type(step)))
        if not isinstance(node, Node):
            raise ValueError("step %s type %s: create_node needs to return a valid Node (got %s)"
                             % (step.name, type(step), type(node)))
        # TODO: validate node is on correct graph
        # TODO: do deeper node validation e.g. ports etc

    def process_step(self, step):
        """
        Process a step.

        :param step: step
        :type step: PipelineStep

        :return: list of added steps.
        :rtype: :class:`list`
        """
        if step in self._step2node:
            return self._step2node[step]

        node = step.create_node(self._graph, self._default_datastore, self._context)
        self.assert_node_valid(step, self._graph, node)

        self._step2node[step] = node
        self._nodeStack[-1].append(node)

        resolved_nodes = self.resolve_references([node])

        # resolve run_after's
        for predecessor_step in step.run_after_steps:
            if predecessor_step in self._step2node:
                predecessor_node = self._step2node[predecessor_step]
                node.run_after(predecessor_node)
            elif self._resolve_closure:
                resolved_nodes.append(self.process_step(predecessor_step))
                node.run_after(self._step2node[predecessor_step])
            else:
                raise ValueError

        return resolved_nodes

    def create_builder(self, collection):
        """
        Create a builder.

        :param collection: collection
        :type collection: list

        :return: Builder for the collection.
        :rtype: _PipelineGraphBuilder
        """
        key = type(collection).__name__
        if key not in self._builders:
            raise NotImplementedError(key)
        return self._builders[key](self)

    def resolve_references(self, node_list):
        """
        Resolve node references.

        :param node_list: node_list
        :type node_list: list

        :return: list of resolved nodes.
        :rtype: :class:`list`
        """
        added_nodes = []
        for node in node_list:
            for input_port in node.inputs:
                edge = input_port.incoming_edge
                if edge is not None and not isinstance(edge, Edge) and edge.source is not None:
                    resolved_node = None
                    if isinstance(edge, _PipelineDataEdgeBuilder):
                        peer = edge.source._producer

                        if not isinstance(peer, PipelineStep):
                            input_text = 'Input ' + input_port.name + ' on step ' + node.name
                            if peer is None:
                                raise ValueError(input_text + ' is not connected to any previous step')
                            else:
                                raise ValueError(input_text + ' is connected to an invalid item: ' + peer)

                        if peer not in self._step2node:
                            if self._resolve_closure:
                                added_nodes.extend(self.process_step(peer))
                            else:
                                raise ValueError

                        resolved_node = self._step2node[peer]

                    elif isinstance(edge, _DataReferenceEdgeBuilder):
                        peer = edge.source
                        datasource_def = DataSourceDef.create_from_data_reference(peer)

                        datasource_builder = _DataReferenceDatasourceBuilder(context=self._context,
                                                                             datasource_def=datasource_def)

                        resolved_node = self._graph.add_datasource_node(name=peer.data_reference_name,
                                                                        datasource_builder=datasource_builder)

                    elif isinstance(edge, _DatasetEdgeBuilder):
                        peer = edge.source
                        datasource_def = DataSourceDef(peer.name, pipeline_dataset=peer)
                        datasource = DataSource(None, datasource_def)
                        resolved_node = self._graph.add_datasource_node(name=peer.name,
                                                                        datasource=datasource)

                    elif isinstance(edge, _PipelineIOEdgeBuilder):
                        peer = edge.source

                        if not isinstance(peer, _PipelineIO):
                            raise AssertionError('Edge source should be of type _PipelineIO')

                        input_data_reference = peer.as_input()
                        datasource_def = DataSourceDef.create_from_data_reference(input_data_reference)

                        datasource_builder = _DataReferenceDatasourceBuilder(context=self._context,
                                                                             datasource_def=datasource_def)

                        resolved_node = self._graph.add_datasource_node(name=peer.name,
                                                                        datasource_builder=datasource_builder,
                                                                        datapath_param_name=peer.datapath_param_name)

                        pipeline_parameter = peer.as_pipeline_parameter()
                        if pipeline_parameter:
                            self._graph._add_datapath_parameter(pipeline_parameter)

                    edge.create_edge(resolved_node)

        if len(added_nodes) > 0:
            node_list.extend(self.resolve_references(added_nodes))

        return node_list


class _SequentialPipelineGraphBuilder(object):
    """_SequentialPipelineGraphBuilder."""

    def __init__(self, base_builder):
        """
        Initialize _SequentialPipelineGraphBuilder.

        :param base_builder: base builder
        :type base_builder: _PipelineGraphBuilder
        """
        self._base_builder = base_builder
        self._nodes = []

    def process_collection(self, collection):
        """
        Process list of nodes.

        :param collection: collection
        :type collection: list
        """
        for item in collection:
            nodes = self._base_builder.process_collection(item)
            self._nodes.append(nodes)

    def apply_rules(self):
        """Apply sequential rules."""
        if len(self._nodes) < 2:
            return
        predecessors = []
        for successors in self._nodes:
            if not isinstance(successors, list):
                successors = [successors]
            for successor in successors:
                for predecessor in predecessors:
                    successor.run_after(predecessor)
            predecessors = successors


class _ParallelPipelineGraphBuilder(object):
    """_ParallelPipelineGraphBuilder."""

    def __init__(self, base_builder):
        """
        Initialize _ParallelPipelineGraphBuilder.

        :param base_builder: base builder
        :type base_builder: _PipelineGraphBuilder
        """
        self._base_builder = base_builder

    def process_collection(self, collection):
        """
        Process collection.

        :param collection: collection
        :type collection: list
        """
        for item in collection:
            self._base_builder.process_collection(item)

    def apply_rules(self):
        """Apply rules."""
        pass


class StepSequence(object):
    """
    Creates a list of steps in a :class:`azureml.pipeline.core.Pipeline` which will be executed in order.

    Use a StepSequence when initializing a Pipeline to create a workflow that contains the steps in the StepSequence.
    The steps will be executed in the order they appear in the list.

    .. remarks::

        A StepSequence can be used to easily run steps in a specific order, without needing to specify data
        dependencies through the use of :class:`azureml.pipeline.core.PipelineData`.

        An example to build a Pipeline using StepSequence is as follows:

        .. code-block:: python

            from azureml.pipeline.core import Pipeline, StepSequence
            from azureml.pipeline.steps import PythonScriptStep

            prepare_step = PythonScriptStep(
                name='prepare data step',
                script_name="prepare_data.py",
                compute_target=compute
            )

            train_step = PythonScriptStep(
                name='train step',
                script_name="train.py",
                compute_target=compute
            )

            step_sequence = StepSequence(steps=[prepare_step, train_step])
            pipeline = Pipeline(workspace=ws, steps=step_sequence)

        In this example train_step will only run after prepare_step has successfully completed execution.


    :param steps: steps for StepSequence.
    :type steps: :class:`list`
    """

    def __init__(self, steps=None):
        """
        Initialize StepSequence.

        :param steps: steps for StepSequence.
        :type steps: :class:`list`
        """
        if steps is None:
            steps = []

        self._steps = steps

    def __iter__(self):
        """
        Iterate over the steps.

        :return: iterator.
        :rtype: iter
        """
        return self._steps.__iter__()


_PipelineGraphBuilder.register(StepSequence.__name__, _SequentialPipelineGraphBuilder)
_PipelineGraphBuilder.register(list.__name__, _ParallelPipelineGraphBuilder)
