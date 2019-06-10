# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""To transfer data between various storages.

Supports Azure Blob, Azure Data Lake Store, Azure SQL database and Azure database for PostgreSQL.
"""
from azureml.core.compute import DataFactoryCompute
from azureml.data.data_reference import DataReference
from azureml.pipeline.core import PipelineData, PipelineStep
from azureml.pipeline.core.graph import ParamDef, InputPortBinding
from azureml.pipeline.core.graph import _PipelineIO
from azureml.pipeline.core._module_builder import _InterfaceModuleBuilder

import json


class DataTransferStep(PipelineStep):
    """Add a step to transfer data between various storage options.

     Supports Azure Blob, Azure Data Lake store, Azure SQL database and Azure database for PostgreSQL.

     See example of using this step in notebook https://aka.ms/pl-data-trans

    .. remarks::

        To establish data dependency between steps, use :func:`azureml.pipeline.steps.DataTransferStep.get_output`
        method to get a :class:`azureml.pipeline.core.PipelineData` object that represents the output of this data
        transfer step and can be used as input for later steps in the pipeline.

        .. code-block:: python

            data_transfer_step = DataTransferStep(name="copy data", ...)

            # Use output of data_transfer_step as input of another step in pipeline
            # This will make training_step wait for data_transfer_step to complete
            training_input = data_transfer_step.get_output()
            training_step = PythonScriptStep(script_name="train.py",
                                    arguments=["--model", training_input],
                                    inputs=[training_input],
                                    compute_target=aml_compute,
                                    source_directory=source_directory)

        To create an :class:`azureml.pipeline.core.graph.InputPortBinding` with specific name, you can combine
        `get_output()` call with :func:`azureml.pipeline.core.PipelineData.as_input` or
        :func:`azureml.pipeline.core.PipelineData.as_mount` helper methods.

        .. code-block:: python

            data_transfer_step = DataTransferStep(name="copy data", ...)

            training_input = data_transfer_step.get_output().as_input("my_input_name")


    :param name: Name of the step
    :type name: str
    :param source_data_reference: Input connection that serves as source of data transfer operation
    :type source_data_reference: list[azureml.pipeline.core.graph.InputPortBinding,
                  azureml.data.data_reference.DataReference, azureml.pipeline.core.PortDataReference,
                  azureml.pipeline.core.builder.PipelineData, azureml.core.Dataset,
                  azureml.data.dataset_definition.DatasetDefinition, azureml.pipeline.core.PipelineDataset]
    :param destination_data_reference: Input connection that serves as destination of data transfer operation
    :type destination_data_reference: list[azureml.pipeline.core.graph.InputPortBinding,
                                           azureml.data.data_reference.DataReference]
    :param compute_target: Azure Data Factory to use for transferring data
    :type compute_target: DataFactoryCompute, str
    :param source_reference_type: An optional string specifying the type of source_data_reference. Possible values
                                  include: 'file', 'directory'. When not specified, we use the type of existing path.
                                  Use it to differentiate between a file and directory of the same name.
    :type source_reference_type: str
    :param destination_reference_type: An optional string specifying the type of destination_data_reference. Possible
                                       values include: 'file', 'directory'. When not specified, we use the type of
                                       existing path, source reference, or 'directory', in that order.
    :type destination_reference_type: str
    :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
        Reuse is enabled by default. If step arguments remain unchanged, the output from the previous
        run of this step is reused. When reusing the step, instead of transferring data again, the results from
        the previous run are immediately made available to any subsequent steps.
    :type allow_reuse: bool
    """

    _step_version = 2

    _parameter_definitions = [
        {'name': 'Command', 'default_value': 'DataCopy'},
        {'name': 'CopyOptions', 'is_optional': True},
        {'name': 'Version', 'default_value': _step_version, 'is_metadata_param': True},
        {'name': 'SourceInputName', 'is_metadata_param': True},
        {'name': 'DestinationInputName', 'is_metadata_param': True},
        {'name': 'OutputName', 'is_metadata_param': True},
        {'name': 'ComputeName', 'is_metadata_param': True},
    ]

    _execution_type = 'DataTransferCloud'

    _output_port_name = '_data_transfer_output'

    def __init__(self, name, source_data_reference=None, destination_data_reference=None, compute_target=None,
                 source_reference_type=None, destination_reference_type=None, allow_reuse=True):
        """
        Initialize DataTransferStep.

        :param name: Name of the step
        :type name: str
        :param source_data_reference: Input connection that serves as source of data transfer operation
        :type source_data_reference: list[azureml.pipeline.core.graph.InputPortBinding,
                    azureml.data.data_reference.DataReference, azureml.pipeline.core.PortDataReference,
                    azureml.pipeline.core.builder.PipelineData, azureml.core.Dataset,
                    azureml.data.dataset_definition.DatasetDefinition, azureml.pipeline.core.PipelineDataset]
        :param destination_data_reference: Input connection that serves as destination of data transfer operation
        :type destination_data_reference:
                    list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference]
        :param compute_target: Azure Data Factory to use for transferring data
        :type compute_target: DataFactoryCompute, str
        :param source_reference_type: An optional string specifying the type of source_data_reference. Possible values
                                      include: 'file', 'directory'. When not specified, we use the type of existing
                                      path. Use it to differentiate between a file and directory of the same name.
        :type source_reference_type: str
        :param destination_reference_type: An optional string specifying the type of destination_data_reference.
                                           Possible values include: 'file', 'directory'. When not specified, we use
                                           the type of existing path, source reference, or 'directory', in that order.
        :type destination_reference_type: str
        :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
            Reuse is enabled by default. If step arguments remain unchanged, the output from the previous
            run of this step is reused. When reusing the step, instead of transferring data again, the results from
            the previous run are immediately made available to any subsequent steps.
        :type allow_reuse: bool
        """
        if name is None:
            raise ValueError('name is required')
        if not isinstance(name, str):
            raise ValueError('name must be a string')
        if source_data_reference is None:
            raise ValueError('source_data_reference is required')
        if destination_data_reference is None:
            raise ValueError('destination_data_reference is required')
        if compute_target is None:
            raise ValueError('compute_target is required')

        if isinstance(source_data_reference, tuple):
            source_data_reference = PipelineStep._tuple_to_ioref(source_data_reference)

        if isinstance(destination_data_reference, tuple):
            destination_data_reference = PipelineStep._tuple_to_ioref(destination_data_reference)

        self._compute_target = compute_target
        self._allow_reuse = allow_reuse
        self._source_data_reference = source_data_reference
        self._destination_data_reference = destination_data_reference
        self._source_reference_type = source_reference_type
        self._destination_reference_type = destination_reference_type

        output = DataTransferStep._create_output_from_destination_input(destination_data_reference)
        output._set_producer(self)
        self._output = output

        super(self.__class__, self).__init__(
            name,
            inputs=[source_data_reference, destination_data_reference],
            outputs=[output])

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from this DataTransfer step and add to the given graph.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: The graph context.
        :type context: _GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        param_defs = DataTransferStep._create_param_defs(DataTransferStep._parameter_definitions)
        param_bindings = self._create_param_bindings(context)

        input_bindings, output_bindings = self.create_input_output_bindings(
            self._inputs, self._outputs, default_datastore)

        module_def = self.create_module_def(
            execution_type=DataTransferStep._execution_type,
            input_bindings=input_bindings,
            output_bindings=output_bindings,
            param_defs=param_defs,
            allow_reuse=self._allow_reuse)

        module_builder = _InterfaceModuleBuilder(context=context, module_def=module_def)

        return graph.add_module_node(
            self.name,
            input_bindings=input_bindings,
            output_bindings=output_bindings,
            param_bindings=param_bindings,
            module_builder=module_builder)

    def get_output(self):
        """
        Get the output of the step as PipelineData.

        .. remarks::

            To establish data dependency between steps, use :func:`azureml.pipeline.steps.DataTransferStep.get_output`
            method to get a :class:`azureml.pipeline.core.PipelineData` object that represents the output of this data
            transfer step and can be used as input for later steps in the pipeline.

            .. code-block:: python

                data_transfer_step = DataTransferStep(name="copy data", ...)

                # Use output of data_transfer_step as input of another step in pipeline
                # This will make training_step wait for data_transfer_step to complete
                training_input = data_transfer_step.get_output()
                training_step = PythonScriptStep(script_name="train.py",
                                        arguments=["--model", training_input],
                                        inputs=[training_input],
                                        compute_target=aml_compute,
                                        source_directory=source_directory)

            To create an :class:`azureml.pipeline.core.graph.InputPortBinding` with specific name, you can combine
            `get_output()` call with :func:`azureml.pipeline.core.PipelineData.as_input` or
            :func:`azureml.pipeline.core.PipelineData.as_mount` helper methods.

            .. code-block:: python

                data_transfer_step = DataTransferStep(name="copy data", ...)

                training_input = data_transfer_step.get_output().as_input("my_input_name")

        :return: The output of the step.
        :rtype: azureml.pipeline.core.builder.PipelineData
        """
        return self._output

    def _create_param_bindings(self, context):
        params = {}

        params['SourceInputName'] = PipelineStep._get_input_port_name(self._source_data_reference)
        params['DestinationInputName'] = PipelineStep._get_input_port_name(self._destination_data_reference)
        params['OutputName'] = self._output._output_name

        params['ComputeName'] = DataTransferStep._get_data_factory_compute_name(context, self._compute_target)

        copy_options = DataTransferStep._get_copy_options_param(
            self._source_reference_type, self._destination_reference_type)
        if copy_options is not None:
            params['CopyOptions'] = copy_options

        return params

    @staticmethod
    def _get_copy_options_param(source_reference_type, destination_reference_type):
        if source_reference_type is None and destination_reference_type is None:
            return None

        possible_values = ['file', 'directory']
        possible_values_str = ', '.join(possible_values)

        copy_options = {}

        def get_valid_ref(ref_name, ref_type):
            if not isinstance(ref_type, str):
                raise ValueError('{name} must be a string. Possible values include: {values}.'
                                 .format(name=ref_name, values=possible_values_str))

            ref_type = ref_type.lower()

            if ref_type not in possible_values:
                raise ValueError('Unknown value provided for {name}. Possible values include: {values}.'
                                 .format(name=ref_name, values=possible_values_str))

            return ref_type

        if source_reference_type is not None:
            copy_options['source_reference_type'] = get_valid_ref('source_reference_type', source_reference_type)

        if destination_reference_type is not None:
            copy_options['destination_reference_type'] = get_valid_ref('destination_reference_type',
                                                                       destination_reference_type)
        return json.dumps(copy_options)

    @staticmethod
    def _get_data_factory_compute_name(context, compute_target):
        if isinstance(compute_target, DataFactoryCompute):
            return compute_target.name

        if isinstance(compute_target, str):
            try:
                compute_target = DataFactoryCompute(context._workspace, compute_target)
                return compute_target.name
            except Exception as e:
                raise ValueError('Error in getting data factory compute named `{0}`. Exception: {1}'.format(
                    compute_target, e))

        raise ValueError('compute_target is not specified correctly')

    @staticmethod
    def _create_output_from_destination_input(destination_data_reference):
        data_reference = DataTransferStep._convert_to_data_reference(destination_data_reference)

        return PipelineData(
            name=DataTransferStep._output_port_name,
            datastore=data_reference.datastore,
            output_mode=data_reference.mode,
            output_path_on_compute=data_reference.path_on_compute,
            output_overwrite=data_reference.overwrite)

    @staticmethod
    def _convert_to_data_reference(destination_data_reference):
        if isinstance(destination_data_reference, DataReference):
            return destination_data_reference

        if isinstance(destination_data_reference, InputPortBinding):
            bind_object = destination_data_reference.bind_object
            if isinstance(bind_object, DataReference):
                return bind_object
            else:
                raise ValueError("destination_data_reference has unexpected bind_object type: %s" % type(bind_object))

        if isinstance(destination_data_reference, _PipelineIO):
            return destination_data_reference.as_input()

        raise ValueError("Unexpected destination_data_reference type: %s" % type(destination_data_reference))

    @staticmethod
    def _create_param_defs(items):
        return [
            ParamDef(
                name=item['name'],
                default_value=item.get('default_value'),
                is_metadata_param=item.get('is_metadata_param', False),
                is_optional=item.get('is_optional', False),
                set_env_var=item.get('set_env_var', False),
                env_var_override=item.get('env_var_override'))
            for item in items]
