# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""graph.py, module for defining a module, datasource, input, output, node, parameters and pipeline run graph."""
from abc import ABCMeta
import hashlib
import uuid
import re
import logging
from enum import Enum
from collections import OrderedDict
from azureml._html.utilities import to_html, make_link
from azureml.core._portal import HasPipelinePortal
from azureml.core import Dataset
from azureml.data.dataset_definition import DatasetDefinition
from azureml.data.data_reference import DataReference
from azureml.data.datapath import DataPath, DataPathComputeBinding
from azureml.data.sql_data_reference import SqlDataReference
from azureml.pipeline.core.run import PipelineRun
from azureml.core._experiment_method import experiment_method


module_logger = logging.getLogger(__name__)


class ModuleDef(object):
    """
    Definition of a module including execution and port definitions.

    :param name: Name of the module.
    :type name: str
    :param description: Description of the module.
    :type description: str
    :param input_port_defs: List of the module input port definitions.
    :type input_port_defs: :class:`list`
    :param output_port_defs: List of the module output port definitions.
    :type output_port_defs: :class:`list`
    :param param_defs: List of parameter definitions.
    :type param_defs: :class:`list`
    :param module_execution_type: The module execution type.
    :type module_execution_type: str
    :param create_sequencing_ports: Whether to create sequencing ports or not.
    :type create_sequencing_ports: bool
    :param allow_reuse: Whether to allow reuse.
    :type allow_reuse: bool
    :param version: The module version.
    :type version: str
    """

    def __init__(self, name, description=None, input_port_defs=None, output_port_defs=None, param_defs=None,
                 module_execution_type=None, create_sequencing_ports=True, allow_reuse=True, version=None):
        """
        Initialize ModuleDef.

        :param name: Name of the module.
        :type name: str
        :param description: Description of the module.
        :type description: str
        :param input_port_defs: List of the module input port definitions.
        :type input_port_defs: :class:`list`
        :param output_port_defs: List of the module output port definitions.
        :type output_port_defs: :class:`list`
        :param param_defs: List of parameter definitions.
        :type param_defs: :class:`list`
        :param module_execution_type: The module execution type.
        :type module_execution_type: str
        :param create_sequencing_ports: Whether to create sequencing ports or not.
        :type create_sequencing_ports: bool
        :param allow_reuse: Whether to allow reuse.
        :type allow_reuse: bool
        :param version: The module version.
        :type version: str
        """
        if input_port_defs is None:
            input_port_defs = []
        if output_port_defs is None:
            output_port_defs = []
        if param_defs is None:
            param_defs = []

        self._name = name
        self._description = description
        self._input_port_defs = input_port_defs
        self._output_port_defs = output_port_defs
        self._param_defs = param_defs
        self._module_execution_type = module_execution_type
        self._create_sequencing_ports = create_sequencing_ports
        self._allow_reuse = allow_reuse
        self._version = version

        self._init_fake_sequencing_ports()
        self._cleanup_param_defs()

    def calculate_hash(self):
        """
        Calculate the module hash.

        :return: The hexdigest hash.
        :rtype: str
        """
        names = []
        names.append("name_" + self._name)
        for i in self._input_port_defs:
            input_signature = "input_" + i.name
            if i.default_datastore_mode is not None:
                input_signature += ",ds_mode_" + i._default_datastore_mode
            if i._default_path_on_compute is not None:
                input_signature += ",ds_path_" + i._default_path_on_compute
            if i.data_types is not None:
                input_signature += ",datatypes_" + ','.join(i._data_types)
            names.append(input_signature)
        for o in self._output_port_defs:
            output_signature = "output_" + o.name
            if o._default_datastore_name is not None:
                output_signature += ",ds_name_" + o._default_datastore_name
            if o._default_datastore_mode is not None:
                output_signature += ",ds_mode_" + o._default_datastore_mode
            if o._default_path_on_compute is not None:
                output_signature += ",ds_path_" + o._default_path_on_compute
            if o._data_type is not None:
                output_signature += ",datatype_" + o._data_type
            names.append(output_signature)
        for p in self._param_defs:
            param_signature = "param_" + p.name
            if p.default_value is not None:
                param_signature += ",val_" + str(p.default_value)
            names.append(param_signature)
        names.append("deterministic_" + str(self.allow_reuse))
        if self._module_execution_type is not None:
            names.append("execution_" + self._module_execution_type)
        if self._version is not None:
            names.append("version_" + self._version)

        names.sort()

        m = hashlib.md5()
        m.update('_'.join(names).encode('utf-8'))
        return m.hexdigest()

    fake_output_name = "_run_after_output"
    fake_input_prefix = "_run_after_input_"

    def _init_fake_sequencing_ports(self):
        """Create fake input and output for sequencing."""
        if self._input_port_defs is None:
            self._input_port_defs = []

        if self._output_port_defs is None:
            self._output_port_defs = []

        if self._create_sequencing_ports:
            if not ModuleDef._contains(self._output_port_defs, lambda x: x.name == ModuleDef.fake_output_name):
                self._output_port_defs.append(OutputPortDef(ModuleDef.fake_output_name, data_type="AnyFile"))

        fake_inputs = [fa for fa in self._input_port_defs if fa.name.startswith(ModuleDef.fake_input_prefix)]
        self._fake_input_index = 0
        for fake_await in fake_inputs:
            curr_index = int(fake_await.name[len(ModuleDef.fake_input_prefix):])
            if curr_index >= self._fake_input_index:
                self._fake_input_index = curr_index + 1

    def _cleanup_param_defs(self):
        updated_param_defs = []
        for param in self._param_defs:
            dv = param.default_value
            if isinstance(dv, PipelineParameter) and (isinstance(dv.default_value, PipelineDataset) or
                                                      PipelineDataset.is_dataset(dv.default_value)):
                continue
            updated_param_defs.append(param)
        self._param_defs = updated_param_defs

    def add_fake_sequencing_input_port(self):
        """
        Add fake input ports for sequencing.

        :return: The fake input port.
        :rtype: azureml.pipeline.core.graph.InputPortDef
        """
        if not self._create_sequencing_ports:
            raise RuntimeError('sequencing ports not supported by this module')
        port_name = "%s%d" % (ModuleDef.fake_input_prefix, self._fake_input_index)
        fake_port = InputPortDef(port_name, ["AnyFile"], is_optional=True)
        self._input_port_defs.append(fake_port)
        self._fake_input_index = self._fake_input_index + 1
        return fake_port

    @staticmethod
    def _contains(list, filter):
        """
        Return True if the given list contains an object according to the given filter.

        :param list: List of objects to filter.
        :type list: :class:`list`
        :param filter: Filter to apply to the objects in the list.
        :type filter: lambda

        :return: If the list contains the object.
        :rtype: bool
        """
        for x in list:
            if filter(x):
                return True
        return False

    @property
    def name(self):
        """
        Name of the Module.

        :return: The name.
        :rtype: str
        """
        return self._name

    @property
    def description(self):
        """
        Get the description of the Module.

        :return: The description string.
        :rtype: str
        """
        return self._description

    @property
    def input_port_defs(self):
        """
        Get the input port definitions of the Module.

        :return: The list of InputPortDefs.
        :rtype: :class:`list`
        """
        return self._input_port_defs

    @property
    def output_port_defs(self):
        """
        Get the output port definitions of the Module.

        :return: The list of OutputPortDefs.
        :rtype: :class:`list`
        """
        return self._output_port_defs

    @property
    def param_defs(self):
        """
        Get the parameter definitions of the Module.

        :return: The list of ParamDefs.
        :rtype: :class:`list`
        """
        return self._param_defs

    @property
    def module_execution_type(self):
        """
        Get the module execution type.

        :return: The module execution type.
        :rtype: str
        """
        return self._module_execution_type

    @property
    def allow_reuse(self):
        """
        Whether to allow module reuse.

        :return: The allow reuse property.
        :rtype: bool
        """
        return self._allow_reuse


class DataSourceDef(object):
    """
    Definition of a datasource.

    :param name: Name of the datasource.
    :type name: str
    :param description: Description of the datasource.
    :type description: str
    :param data_type_id: The data type id of the datasource.
    :type data_type_id: str
    :param datastore_name: The datastore name the datasource resides on.
    :type datastore_name: str
    :param path_on_datastore: The path on the datastore that corresponds to the datasource.
    :type path_on_datastore: str
    :param sql_table: The name of the table in SQL database
    :type sql_table: str, optional
    :param sql_query: The sql query when using an SQL database
    :type sql_query: str, optional
    :param sql_stored_procedure: The name of the stored procedure when using an SQL database
    :type sql_stored_procedure: str, optional
    :param sql_stored_procedure_params: The optional list of parameters to pass to stored procedure.
    :type sql_stored_procedure_params: [azureml.pipeline.core.graph.StoredProcedureParameter]
    :param pipeline_dataset: The PipelineDataset containing the AzureML Dataset that will be used.
    :type pipeline_dataset: :class:`azureml.pipeline.core.PipelineDataset`
    """

    def __init__(self, name, description=None, data_type_id=None, datastore_name=None, path_on_datastore=None,
                 sql_table=None, sql_query=None, sql_stored_procedure=None, sql_stored_procedure_params=None,
                 pipeline_dataset=None):
        """
        Initialize DataSourceDef.

        :param name: Name of the datasource.
        :type name: str
        :param description: Description of the datasource.
        :type description: str
        :param data_type_id: The data type id of the datasource.
        :type data_type_id: str
        :param datastore_name: The datastore name the datasource resides on.
        :type datastore_name: str
        :param path_on_datastore: The path on the datastore that corresponds to the datasource.
        :type path_on_datastore: str
        :param sql_table: the name of the table in SQL database
        :type sql_table: str, optional
        :param sql_query: the sql query when using an SQL database
        :type sql_query: str, optional
        :param sql_stored_procedure: the name of the stored procedure when using an SQL database
        :type sql_stored_procedure: str, optional
        :param sql_stored_procedure_params: the optional list of parameters to pass to stored procedure.
        :type sql_stored_procedure_params: [azureml.pipeline.core.graph.StoredProcedureParameter]
        :param pipeline_dataset: The PipelineDataset containing the AzureML Dataset that will be used.
        :type pipeline_dataset: :class:`azureml.pipeline.core.PipelineDataset`
        """
        self._name = name
        self._description = description
        self._data_type_id = data_type_id
        self.datastore_name = datastore_name
        # If the path is unspecified, use a default of empty string, which maps to the root of the datastore
        self.path_on_datastore = path_on_datastore or ""
        self.sql_table = sql_table
        self.sql_query = sql_query
        self.sql_stored_procedure = sql_stored_procedure
        self.sql_stored_procedure_params = sql_stored_procedure_params
        # datasources have one output port
        self._output_port_def = OutputPortDef(name=DataSource.DATASOURCE_PORT_NAME)
        self._pipeline_dataset = pipeline_dataset

    @property
    def name(self):
        """
        Get the name of the datasource.

        :return: The name of the datasource.
        :rtype: str
        """
        return self._name

    @property
    def description(self):
        """
        Get the description of the datasource.

        :return: The description of the datasource.
        :rtype: str
        """
        return self._description

    @property
    def data_type_id(self):
        """
        Get the data type id of the datasource.

        :return: The data type id of the datasource.
        :rtype: str
        """
        return self._data_type_id

    @property
    def output_port_def(self):
        """
        Get the output port definition.

        :return: The output port definition.
        :rtype: azureml.pipeline.core.graph.OutputPortDef
        """
        return self._output_port_def

    def calculate_hash(self):
        """
        Calculate hash of the datasource.

        :return: The hexdigest hash.
        :rtype: str
        """
        if self._name is None:
            raise ValueError("DataReference inputs must have a name specified")
        if self.datastore_name is None and self._pipeline_dataset is None:
            raise ValueError("DataReference inputs must have a datastore name or pipeline dataset specified")
        values = [self._name]
        if self._pipeline_dataset is None:
            values.extend((self.datastore_name, self.path_on_datastore))
        else:
            values.extend(self._pipeline_dataset._hashable_content)
        if self.data_type_id is not None:
            values.append(self.data_type_id)
        m = hashlib.md5()
        m.update('_'.join(values).encode('utf-8'))
        return m.hexdigest()

    @staticmethod
    def create_from_data_reference(data_reference):
        """
        Create a DataSourceDef using a DataReference.

        :param data_reference: data reference object
        :type data_reference: azureml.data.DataReference
        :return: DataSourceDef object
        :rtype: DataSourceDef
        """
        if isinstance(data_reference, SqlDataReference):
            sp_params = data_reference.sql_stored_procedure_params
            if sp_params is not None:
                sp_params = [StoredProcedureParameter(name=p.name, value=p.value,
                                                      type=StoredProcedureParameterType(p.type.value))
                             for p in sp_params]

            return DataSourceDef(data_reference.data_reference_name, description=None,
                                 data_type_id=None,
                                 datastore_name=data_reference.datastore.name,
                                 sql_table=data_reference.sql_table,
                                 sql_query=data_reference.sql_query,
                                 sql_stored_procedure=data_reference.sql_stored_procedure,
                                 sql_stored_procedure_params=sp_params)
        else:
            return DataSourceDef(data_reference.data_reference_name, description=None,
                                 data_type_id=None,
                                 datastore_name=data_reference.datastore.name,
                                 path_on_datastore=data_reference.path_on_datastore)


class InputPortDef(object):
    """Definition of an input port.

    :param name: Name of the input port.
    :type name: str
    :param data_types: List of datatypes to allow as input.
    :type data_types: :class:`list`
    :param default_datastore_mode: Default mode to access the data store data ("mount" or "download").
    :type default_datastore_mode: str
    :param default_path_on_compute: For "download" mode, the path to which the module reads from during execution.
    :type default_path_on_compute: str
    :param is_optional: Set to true if the input is optional.
    :type is_optional: bool
    :param default_overwrite: For "download" mode, indicate whether to overwrite existing data.
    :type default_overwrite: bool
    :param default_data_reference_name: Default name of the data reference.
    :type default_data_reference_name: str
    :param is_resource: Indicate whether input is a resource. Resources are downloaded to the script folder and
        provide a way to change the behavior of script at run-time.
    :type is_resource: bool
    """

    def __init__(self, name, data_types, default_datastore_mode=None, default_path_on_compute=None, is_optional=False,
                 default_overwrite=None, default_data_reference_name=None, is_resource=False):
        """
        Create an input port.

        :param name: Name of the input port.
        :type name: str
        :param data_types: List of data types to allow as input.
        :type data_types: :class:`list`
        :param default_datastore_mode: Default mode to access the data store data ("mount" or "download").
        :type default_datastore_mode: str
        :param default_path_on_compute: For "download" mode, the path to which the module reads from during execution.
        :type default_path_on_compute: str
        :param is_optional: Set to true if the input is optional.
        :type is_optional: bool
        :param default_overwrite: For "download" mode, indicate whether to overwrite existing data.
        :type default_overwrite: bool
        :param default_data_reference_name: Default name of the data reference.
        :type default_data_reference_name: str
        :param is_resource: Indicate whether input is a resource. Resources are downloaded to the script folder and
            provide a way to change the behavior of script at run-time.
        :type is_resource: bool
        """
        self._name = name
        self._data_types = data_types
        self._default_path_on_compute = default_path_on_compute
        self._is_optional = is_optional
        self._default_datastore_mode = default_datastore_mode
        self._default_overwrite = default_overwrite
        self._default_data_reference_name = default_data_reference_name
        self._is_resource = is_resource

    @property
    def name(self):
        """
        Get the name of the input port.

        :return: The name of the input port.
        :rtype: str
        """
        return self._name

    @property
    def data_types(self):
        """
        Get the list of DataTypes allowed as input.

        :return: The list of DataTypes.
        :rtype: :class:`list`
        """
        return self._data_types

    @property
    def default_path_on_compute(self):
        """
        For "download" mode, the path to which the module writes this output during execution.

        :return: The default path on compute.
        :rtype: str
        """
        return self._default_path_on_compute

    @property
    def is_optional(self):
        """
        Indicate whether to the input port is optional.

        :return: The is_optional property of the InputPortDef.
        :rtype: bool
        """
        return self._is_optional

    @property
    def default_datastore_mode(self):
        """
        Get the default mode for producing output.

        Either "mount" (mounted drive) or "download" (download the data to a local path).

        :return: The default datastore mode.
        :rtype: str
        """
        return self._default_datastore_mode

    @property
    def default_overwrite(self):
        """
        Indicate whether to overwrite existing data.

        :return: The default overwrite value.
        :rtype: bool
        """
        return self._default_overwrite

    @property
    def default_data_reference_name(self):
        """
        Get the default name of the data reference.

        :return: The default data reference name.
        :rtype: str
        """
        return self._default_data_reference_name

    @property
    def is_resource(self):
        """
        Get whether input is a resource.

        :return: Is input a resource.
        :rtype: bool
        """
        return self._is_resource


class OutputPortDef(object):
    """
    Definition of an output port.

    :param name: Name of the output port.
    :type name: str
    :param default_datastore_name: Default data store to write this output to.
    :type default_datastore_name: str
    :param default_datastore_mode: Default mode for producing output, either "mount" or "upload".
    :type default_datastore_mode: str
    :param default_path_on_compute: For "upload" mode, the path to which the module writes to during execution.
    :type default_path_on_compute: str
    :param is_directory: True if the output is a directory of files, False for a single file (default: False).
    :type is_directory: bool
    :param data_type: Datatype to apply to this output.  If unspecified, use a default based on is_directory.
    :type data_type: str
    :param default_overwrite: For "upload" mode, indicate whether to overwrite existing data.
    :type default_overwrite: bool
    :param training_output: Defines output for training result. This is needed only for specific trainings which
                            result in different kinds of outputs such as Metrics and Model.
                            For example, :class:`azureml.train.automl.AutoMLStep` results in metrics and model.
                            You can also define specific training iteration or metric used to get best model.
    :type training_output: azureml.pipeline.core.TrainingOutput, optional
    """

    def __init__(self, name, default_datastore_name=None, default_datastore_mode=None, default_path_on_compute=None,
                 is_directory=False, data_type=None, default_overwrite=None, training_output=None):
        """
        Create an output port.

        :param name: Name of the output port.
        :type name: str
        :param default_datastore_name: Default data store to write this output to.
        :type default_datastore_name: str
        :param default_datastore_mode: Default mode for producing output, either "mount" or "upload".
        :type default_datastore_mode: str
        :param default_path_on_compute: For "upload" mode, the path to which the module writes to during execution.
        :type default_path_on_compute: str
        :param is_directory: True if the output is a directory of files, False for a single file (default: False).
        :type is_directory: bool
        :param data_type: Datatype to apply to this output.  If unspecified, use a default based on is_directory.
        :type data_type: str
        :param default_overwrite: For "upload" mode, indicate whether to overwrite existing data.
        :type default_overwrite: bool
        :param training_output: Defines output for training result. This is needed only for specific trainings which
                                result in different kinds of outputs such as Metrics and Model.
                                For example, :class:`azureml.train.automl.AutoMLStep` results in metrics and model.
                                You can also define specific training iteration or metric used to get best model.
        :type training_output: azureml.pipeline.core.TrainingOutput, optional
        """
        self._name = name
        self._default_datastore_name = default_datastore_name
        self._default_datastore_mode = default_datastore_mode
        self._default_path_on_compute = default_path_on_compute
        self._is_directory = is_directory
        self._default_overwrite = default_overwrite
        self._training_output = training_output

        if data_type is None:
            if self._is_directory:
                self._data_type = "AnyDirectory"
            else:
                self._data_type = "AnyFile"
        else:
            self._data_type = data_type

    @property
    def name(self):
        """
        Get the name of the output port.

        :return: The name of the output port.
        :rtype: str
        """
        return self._name

    @property
    def default_datastore_name(self):
        """
        Get the default data store to write this output to.

        :return: The default datastore name.
        :rtype: str
        """
        return self._default_datastore_name

    @property
    def default_datastore_mode(self):
        """
        Get the default mode for producing output, either "mount" or "upload" (local file which is uploaded).

        :return: The default datastore mode.
        :rtype: str
        """
        return self._default_datastore_mode

    @property
    def default_path_on_compute(self):
        """
        For "upload" mode, the path to which the module writes this output during execution.

        :return: The default path on compute.
        :rtype: str
        """
        return self._default_path_on_compute

    @property
    def is_directory(self):
        """
        Return True if the output is a directory of files, False for a single file (default: False).

        :return: The is_directory property of the OutputPortDef.
        :rtype: bool
        """
        return self._is_directory

    @property
    def data_type(self):
        """
        Datatype to apply to this output.  If unspecified, use a default based on is_directory.

        :return: The datatype.
        :rtype: str
        """
        return self._data_type

    @property
    def default_overwrite(self):
        """
        For "upload" mode, indicate whether to overwrite existing data.

        :return: The default_overwrite property of the OutputPortDef.
        :rtype: bool
        """
        return self._default_overwrite

    @property
    def training_output(self):
        """
        Get training output.

        :return: Training output
        :rtype: azureml.pipeline.core.TrainingOutput
        """
        return self._training_output


class ParamDef(object):
    """
    Definition of an execution parameter.

    :param name: Name of the ParamDef object.
    :type name: str
    :param default_value: Default value of the parameter.
    :type default_value: str
    :param is_metadata_param: Whether the parameter is a metadata param or not.
    :type is_metadata_param: bool
    :param is_optional: Whether the parameter is optional or not.
    :type is_optional: bool
    :param set_env_var: Whether to set an environment variable or not.
    :type set_env_var: bool
    :param env_var_override: The environment variable override value.
    :type env_var_override: str
    """

    def __init__(self, name, default_value=None, is_metadata_param=False, is_optional=False, set_env_var=False,
                 env_var_override=None):
        """
        Initialize ParamDef.

        :param name: Name of the ParamDef object.
        :type name: str
        :param default_value: Default value of the parameter.
        :type default_value: str
        :param is_metadata_param: Whether the parameter is a metadata param or not.
        :type is_metadata_param: bool
        :param is_optional: Whether the parameter is optional or not.
        :type is_optional: bool
        :param set_env_var: Whether to set an environment variable or not.
        :type set_env_var: bool
        :param env_var_override: The environment variable override value.
        :type env_var_override: str
        """
        self.name = name
        self.default_value = default_value
        self.env_var_override = env_var_override
        self.is_metadata_param = is_metadata_param
        self.is_optional = is_optional
        self.set_env_var = set_env_var


class Module(object):
    """
    A runnable module that can be used in a graph.

    :param module_id: The module id.
    :type module_id: str
    :param module_def: The module definition object.
    :type module_def: azureml.pipeline.core.graph.ModuleDef
    :param module_version: The module version to use while constructing the graph.
    :type module_version: azureml.pipeline.core.ModuleVersion
    :param default_version: The default version to use in case a module_version resolution is needed.
    :type default_version: str
    """

    def __init__(self, module_id, module_def=None, module_version=None, default_version=None):
        """
        Initialize Module.

        :param module_id: The module id.
        :type module_id: str
        :param module_def: The module definition object.
        :type module_def: azureml.pipeline.core.graph.ModuleDef
        """
        self.id = module_id
        self.module_def = module_def
        self.module_version = module_version
        self._default_version = default_version


class DataSource(object):
    """
    A datasource that can be used in a graph.

    :param datasource_id: The datasource id.
    :type datasource_id: str
    :param datasource_def: The datasource definition object.
    :type datasource_def: azureml.pipeline.core.graph.DataSourceDef
    """

    def __init__(self, datasource_id, datasource_def):
        """
        Initialize DataSource.

        :param datasource_id: The datasource id.
        :type datasource_id: str
        :param datasource_def: The datasource definition object.
        :type datasource_def: azureml.pipeline.core.graph.DataSourceDef
        """
        self.id = datasource_id
        self.datasource_def = datasource_def

    DATASOURCE_PORT_NAME = 'data'


#########################################
# Classes that represent a nodes and edges in the graph
class Node(object):
    """
    Represents a basic unit in a graph, e.g it could be any datasource or step.

    :param graph: The graph this node belongs to.
    :type graph: azureml.pipeline.core.graph.Graph
    :param node_id: The id of the node.
    :type node_id: str
    :param name: The name of the graph.
    :type name: str
    :param module: The module associated with the Node.
    :type module: azureml.pipeline.core.graph.Module
    :param module_builder: The module builder associated with the Node.
    :type module_builder: _ModuleBuilder
    :param datasource: The datasource associated with the Node.
    :type datasource: azureml.pipeline.core.graph.DataSource
    :param datasource_builder: The datasource builder associated with the Node.
    :type datasource_builder: _DatasourceBuilder
    :param module_wiring: mapping between the node's inputs/outputs and the module inputs/outputs. Holds
                          two keys,inputs and outputs, each mapped to a dict whose keys are the module's
                          inputs/outputs names, and the values are the node's ports
    :type module_wiring: {}
    """

    __metaclass__ = ABCMeta

    def __init__(self, graph, node_id, name=None, module=None, module_builder=None, datasource=None,
                 datasource_builder=None, module_wiring=None):
        """
        Initialize Node.

        :param graph: The graph this node belongs to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param node_id: The id of the node.
        :type node_id: str
        :param name: The name of the node.
        :type name: str
        :param module: The module associated with the Node.
        :type module: azureml.pipeline.core.graph.Module
        :param module_builder: The module builder associated with the Node.
        :type module_builder: _ModuleBuilder
        :param datasource: The datasource associated with the Node.
        :type datasource: azureml.pipeline.core.graph.DataSource
        :param datasource_builder: The datasource builder associated with the Node.
        :type datasource_builder: _DatasourceBuilder
        """
        if module is None and module_builder is None and datasource is None and datasource_builder is None:
            raise ValueError("Require either module or module_builder or datasource or datasource_builder")

        if name is None:
            name = node_id
        self._name = name
        self._graph = graph
        self._node_id = node_id
        self._outputs = {}
        self._inputs = {}
        self._params = {}

        self._module = module
        self._module_builder = module_builder

        self._datasource = datasource
        self._datasource_builder = datasource_builder
        self._module_wiring = module_wiring

        if self.module_def is not None:
            # construct input_ports, outputs_ports and params based on defs in module
            for input_port_def in self.module_def.input_port_defs:
                self._inputs[input_port_def.name] = InputPort(self, input_port_def)

            for output_port_def in self.module_def.output_port_defs:
                self._outputs[output_port_def.name] = OutputPort(self, output_port_def)

            for param_def in self.module_def.param_defs:
                self._params[param_def.name] = Param(param_def)

        elif self.datasource_def is not None:
            output_port_def = self.datasource_def.output_port_def
            self._outputs[output_port_def.name] = OutputPort(self, output_port_def)
        elif self._module is not None and self._module.module_version is not None:
            for output in self._module.module_version.interface.outputs:
                self._outputs[output.name] = OutputPort(self,
                                                        OutputPortDef(
                                                            name=output.name,
                                                            default_datastore_name=output.data_store_name,
                                                            default_datastore_mode=output.data_store_mode,
                                                            default_path_on_compute=output.path_on_compute,
                                                            default_overwrite=output.overwrite))
            for input in self._module.module_version.interface.inputs:
                self._inputs[input.name] = InputPort(self,
                                                     InputPortDef(
                                                         name=input.name,
                                                         default_datastore_mode=input.data_store_mode,
                                                         default_path_on_compute=input.path_on_compute,
                                                         default_overwrite=input.overwrite,
                                                         default_data_reference_name=input.data_reference_name,
                                                         data_types=input.data_type_ids_list,
                                                         is_optional=input.is_optional,
                                                         is_resource=input.is_resource))
            for param in self._module.module_version.interface.parameters:
                self._params[param.name] = Param(ParamDef(name=param.name, default_value=param.default_value,
                                                          is_metadata_param=False, is_optional=param.is_optional,
                                                          set_env_var=param.set_environment_variable,
                                                          env_var_override=param.environment_variable_override))
            for param in self._module.module_version.interface.metadata_parameters:
                self._params[param.name] = Param(ParamDef(name=param.name, default_value=param.default_value,
                                                          is_metadata_param=True, is_optional=param.is_optional,
                                                          set_env_var=param.set_environment_variable,
                                                          env_var_override=param.environment_variable_override))

    @property
    def module_def(self):
        """
        Get the module definition.

        :return: The module definition object.
        :rtype: azureml.pipeline.core.graph.ModuleDef
        """
        if self._module is not None:
            return self._module.module_def

        if self._module_builder is not None:
            return self._module_builder.module_def

        return None

    @property
    def datasource_def(self):
        """
        Get the datasource definition.

        :return: The datasource definition object.
        :rtype: azureml.pipeline.core.graph.DataSourceDef
        """
        if self._datasource is not None:
            return self._datasource.datasource_def

        if self._datasource_builder is not None:
            return self._datasource_builder.datasource_def

        return None

    @property
    def name(self):
        """
        Get the name of this node.

        :return: The name.
        :rtype: str
        """
        return self._name

    @property
    def node_id(self):
        """
        Get the node ID for this node.

        :return: The node ID.
        :rtype: str
        """
        return self._node_id

    def get_input(self, name):
        """
        Return an InputPort by name.

        :param name: Name of the input port.
        :type name: str

        :return: The input port with the matching name.
        :rtype: azureml.pipeline.core.graph.InputPort
        """
        if name in self._inputs:
            return self._inputs[name]
        if self._module_wiring is not None:
            input_wiring = self._module_wiring["inputs"]
            target = next((v for v in input_wiring.values() if v.name == name), None)
            real_name = next((k for k in input_wiring.keys() if input_wiring[k] is target))
            return self._inputs[real_name]

    @property
    def input_dict(self):
        """
        Get a dictionary containing all inputs.

        :return: Dictionary of {input name, :class:`azureml.pipeline.core.graph.InputPort`}
        :rtype: dict
        """
        return self._inputs

    @property
    def inputs(self):
        """
        Get a list containing all inputs.

        :return: List of :class:`azureml.pipeline.core.graph.InputPort`
        :rtype: :class:`list`
        """
        return self._inputs.values()

    def get_output(self, name):
        """
        Return an OutputPort by name.

        :param name: Name of the output port
        :type name: str

        :return: The output port
        :rtype: azureml.pipeline.core.graph.OutputPort
        """
        if name in self._outputs:
            return self._outputs[name]
        elif self._module_wiring is not None:
            output_wiring = self._module_wiring["outputs"]
            target = next((v for v in output_wiring.values() if v.name == name), None)
            real_name = next((k for k in output_wiring.keys() if output_wiring[k] is target))
            return self._outputs[real_name]

    @property
    def output_dict(self):
        """
        Get a dictionary containing all outputs.

        :return: Dictionary of {output name, :class:`azureml.pipeline.core.graph.OutputPort`}
        :rtype: dict
        """
        return self._outputs

    @property
    def outputs(self):
        """
        Get a list containing all outputs.

        :return: List of OutputPort
        :rtype: :class:`list`
        """
        return self._outputs.values()

    def get_param(self, name):
        """
        Return a parameter by name.

        :param name: Name of the parameter.
        :type name: str

        :return: The parameter.
        :rtype: azureml.pipeline.core.graph.Param
        """
        return self._params[name]

    @property
    def params(self):
        """
        Get a dictionary containing all parameters.

        :return: Dictionary of {parameter name, :class:`azureml.pipeline.core.graph.Param`}
        :rtype: dict
        """
        return self._params

    def _attach_pipeline_parameters_from_dict(self, pipeline_params_dict):
        if pipeline_params_dict is not None:
            for pipeline_param_name, pipeline_param in pipeline_params_dict.items():
                dv = pipeline_param.default_value
                if isinstance(dv, PipelineDataset) or PipelineDataset.is_dataset(dv):
                    continue
                self.get_param(pipeline_param_name).set_value(pipeline_params_dict[pipeline_param_name])

    def _attach_pipeline_parameters(self, pipeline_params_implicit, pipeline_params_in_step_params,
                                    pipeline_params_runconfig):
        self._attach_pipeline_parameters_from_dict(pipeline_params_in_step_params)
        self._attach_pipeline_parameters_from_dict(pipeline_params_implicit)
        self._attach_pipeline_parameters_from_dict(pipeline_params_runconfig)

    def run_after(self, node):
        """
        Run this node after the given node.

        :param node: The node to run before this node.
        :type node: azureml.pipeline.core.graph.Node
        """
        if self._module is not None:
            raise ValueError("cannot add depenencies after module is created")

        fake_input_def = self.module_def.add_fake_sequencing_input_port()
        fake_await = InputPort(self, fake_input_def)
        self._inputs[fake_input_def.name] = fake_await
        fake_completion = node.get_output(ModuleDef.fake_output_name)
        fake_await.connect(fake_completion)

    def sequence(self, nodes):
        """
        Configure a list of nodes to run in sequence after this node.

        :param nodes: The list of nodes.
        :type nodes: :class:`list`
        """
        if nodes is None:
            return

        node = self
        for follower in nodes:
            follower.run_after(node)
            node = follower


class ModuleNode(Node):
    """
    Represents a module in a graph.

    :param graph: The graph this node belongs to.
    :type graph: azureml.pipeline.core.graph.Graph
    :param node_id: The id of the node.
    :type node_id: str
    :param name: The name of the graph.
    :type name: str
    :param module: The module associated with the Node.
    :type module: azureml.pipeline.core.graph.Module
    :param module_builder: The module builder associated with the Node.
    :type module_builder: _ModuleBuilder
    """

    def __init__(self, graph, node_id, name=None, module=None, module_builder=None,
                 module_wiring=None):
        """
        Initialize module node.

        :param graph: The graph this node belongs to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param node_id: The id of the node.
        :type node_id: str
        :param name: The name of the graph.
        :type name: str
        :param module: The module associated with the Node.
        :type module: azureml.pipeline.core.graph.Module
        :param module_builder: The module builder associated with the Node.
        :type module_builder: _ModuleBuilder
        """
        super(self.__class__, self).__init__(graph=graph, node_id=node_id, name=name,
                                             module=module, module_builder=module_builder,
                                             module_wiring=module_wiring)


class DataSourceNode(Node):
    """
    Represents a datasource in a graph.

    :param graph: The graph this node belongs to.
    :type graph: azureml.pipeline.core.graph.Graph
    :param node_id: The id of the node.
    :type node_id: str
    :param name: The name of the graph.
    :type name: str
    :param datasource: The datasource associated with the Node.
    :type datasource: azureml.pipeline.core.graph.DataSource
    :param datasource_builder: The datasource builder associated with the Node.
    :type datasource_builder: _DatasourceBuilder
    """

    def __init__(self, graph, node_id, name=None, datasource=None, datasource_builder=None, datapath_param_name=None):
        """
        Initialize datasource node.

        :param graph: The graph this node belongs to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param node_id: The id of the node.
        :type node_id: str
        :param name: The name of the graph.
        :type name: str
        :param datasource: The datasource associated with the Node.
        :type datasource: azureml.pipeline.core.graph.DataSource
        :param datasource_builder: The datasource builder associated with the Node.
        :type datasource_builder: _DatasourceBuilder
        """
        self.datapath_param_name = datapath_param_name
        super(self.__class__, self).__init__(graph=graph, node_id=node_id, name=name,
                                             datasource=datasource, datasource_builder=datasource_builder)


class InputPort(object):
    """
    Instance of an input port on a node, which can be connected to an output port.

    :param node: Node which contains this input.
    :type node: azureml.pipeline.core.graph.Node
    :param input_port_def: Definition of the module input port.
    :type input_port_def: azureml.pipeline.core.graph.InputPortDef
    """

    def __init__(self, node, input_port_def):
        """
        Initialize InputPort.

        :param node: Node which contains this input.
        :type node: azureml.pipeline.core.graph.Node
        :param input_port_def: Definition of the module input port.
        :type input_port_def: azureml.pipeline.core.graph.InputPortDef
        """
        self._node = node
        self._input_port_def = input_port_def
        self._incoming_edge = None
        self._bind_mode = input_port_def.default_datastore_mode
        self._path_on_compute = input_port_def.default_path_on_compute
        self._overwrite = input_port_def.default_overwrite
        self._data_reference_name = input_port_def.default_data_reference_name

    def connect(self, source_port):
        """
        Connect this port to a source.

        :param source_port: The source of the connection.
        :type source_port: azureml.pipeline.core.graph.OutputPort
            azureml.pipeline.core.PortDataReference,
            azureml.data.data_reference.DataReference,
            azureml.pipeline.core.PipelineData,
            azureml.pipeline.core.OutputPortBinding,
            azureml.core.Dataset,
            azureml.data.dataset_definition.DatasetDefinition,
            azureml.pipeline.core.PipelineDataset

        :return: edge
        :rtype: azureml.pipeline.core.graph.Edge
        """
        if self._incoming_edge is not None:
            raise ValueError("Cannot connect the same input to multiple sources")

        from azureml.pipeline.core.builder import PipelineData

        if isinstance(source_port, PortDataReference) or isinstance(source_port, DataReference):
            self._incoming_edge = _DataReferenceEdgeBuilder(source_port, self)
        elif isinstance(source_port, PipelineData) or isinstance(source_port, OutputPortBinding):
            self._incoming_edge = _PipelineDataEdgeBuilder(source_port, self)
        elif isinstance(source_port, _PipelineIO):
            self._incoming_edge = _PipelineIOEdgeBuilder(source_port, self)
        elif isinstance(source_port, PipelineDataset):
            self._incoming_edge = _DatasetEdgeBuilder(source_port, self)
        elif PipelineDataset.is_dataset(source_port):
            pipeline_dset = PipelineDataset(source_port, PipelineDataset.default_name(source_port))
            self._incoming_edge = _DatasetEdgeBuilder(pipeline_dset, self)
        else:
            self._incoming_edge = Edge(source_port, self)

        return self._incoming_edge

    def disconnect(self):
        """Disconnect this InputPort."""
        self._incoming_edge = None

    @property
    def name(self):
        """
        Name of the Input port.

        :return: The name.
        :rtype: str
        """
        return self._input_port_def.name

    @property
    def data_types(self):
        """
        Get the Data types list for the Input port.

        :return: List of data type names.
        :rtype: :class:`list`
        """
        return self._input_port_def.data_types

    @property
    def node(self):
        """
        Return the node where the input port is part of.

        :return: node
        :rtype: azureml.pipeline.core.graph.Node
        """
        return self._node

    @property
    def input_port_def(self):
        """
        Get the Input port definition of this InputPort.

        :return: input_port_def: Definition of the module input port.
        :rtype: azureml.pipeline.core.graph.InputPortDef
        """
        return self._input_port_def

    @property
    def bind_mode(self):
        """
        How this input will be consumed by the step ("mount" or "download").

        :return: The bind mode ("mount" or "download").
        :rtype: str
        """
        return self._bind_mode

    @bind_mode.setter
    def bind_mode(self, value):
        # TODO: rationalize these!
        if value is not "mount" and value is not "download":
            raise ValueError("invalid bind_mode " + value)
        self._bind_mode = value

    @property
    def path_on_compute(self):
        """
        For "download" mode, the path on the compute the data will reside.

        :return: The path on the compute.
        :rtype: str
        """
        return self._path_on_compute

    @path_on_compute.setter
    def path_on_compute(self, value):
        self._path_on_compute = value

    @property
    def overwrite(self):
        """
        For "download" mode, whether to overwrite existing data.

        :return: The overwrite property.
        :rtype: bool
        """
        return self._overwrite

    @overwrite.setter
    def overwrite(self, value):
        """
        Set the overwrite property which indicates whether to overwrite existing data for "download" mode.

        :param value: New value for overwrite property.
        :type value: bool
        """
        self._overwrite = value

    @property
    def data_reference_name(self):
        """
        Get the name of data reference associated with the input.

        :return: The data reference name.
        :rtype: str
        """
        return self._data_reference_name

    @data_reference_name.setter
    def data_reference_name(self, value):
        self._data_reference_name = value

    @property
    def incoming_edge(self):
        """
        Incoming edge.

        :return: _incoming_edge
        :rtype: azureml.pipeline.core.graph.Edge
        """
        return self._incoming_edge


class OutputPort(object):
    """
    Instance of an output port on a node, which can be connected to an input port.

    :param node: Node which contains this output
    :type node: azureml.pipeline.core.graph.Node
    :param output_port_def: Definition of the module output port
    :type output_port_def: azureml.pipeline.core.graph.OutputPortDef
    """

    def __init__(self, node, output_port_def):
        """
        Initialize OutputPort.

        :param node: Node which contains this output
        :type node: azureml.pipeline.core.graph.Node
        :param output_port_def: Definition of the module output port
        :type output_port_def: azureml.pipeline.core.graph.OutputPortDef
        """
        self._node = node
        self._output_port_def = output_port_def
        self._pipeline_output_name = None
        if output_port_def is not None:
            self._datastore_name = output_port_def.default_datastore_name
            self._bind_mode = output_port_def.default_datastore_mode
            self._path_on_compute = output_port_def.default_path_on_compute
            self._overwrite = output_port_def.default_overwrite

    def connect(self, dest_port):
        """
        Connect this port to a source.

        :param dest_port: Input port from the node that is the destination of the connection.
        :type dest_port: azureml.pipeline.core.graph.InputPort

        :return: The created edge.
        :rtype: azureml.pipeline.core.graph.Edge
        """
        return dest_port.connect(self)

    @property
    def name(self):
        """
        Get the name of the Output port.

        :return: The name.
        :rtype: str
        """
        return self._output_port_def.name

    @property
    def node(self):
        """
        Return the node where the Output port is part of.

        :return: node
        :rtype: azureml.pipeline.core.graph.Node
        """
        return self._node

    @property
    def datastore_name(self):
        """
        Get the name of the datastore to write this output to.

        :return: The datastore name.
        :rtype: str
        """
        return self._datastore_name

    @datastore_name.setter
    def datastore_name(self, value):
        self._datastore_name = value

    @property
    def bind_mode(self):
        """
        Get the mode for producing output, either "mount" or "upload" (local file which is uploaded).

        :return: The datastore mode.
        :rtype: str
        """
        return self._bind_mode

    @bind_mode.setter
    def bind_mode(self, value):
        # TODO: rationalize these!
        if value is not "mount" and value is not "upload":
            raise ValueError("invalid bind_mode " + value)
        self._bind_mode = value

    @property
    def path_on_compute(self):
        """
        For "upload" mode, the path to which the module writes this output during execution.

        :return: The path on compute.
        :rtype: str
        """
        return self._path_on_compute

    @path_on_compute.setter
    def path_on_compute(self, value):
        self._path_on_compute = value

    @property
    def overwrite(self):
        """
        For "upload" mode, indicate whether to overwrite existing data.

        :return: _overwrite
        :rtype: str
        """
        return self._overwrite

    @overwrite.setter
    def overwrite(self, value):
        self._overwrite = value

    @property
    def data_type(self):
        """
        Get the type of the data.

        :return: _data_type
        :rtype: str
        """
        return self._output_port_def.data_type

    @property
    def pipeline_output_name(self):
        """
        Get the name of the pipeline output corresponding to this OutputPort.

        :return: The pipeline output name.
        :rtype: str
        """
        return self._pipeline_output_name

    @pipeline_output_name.setter
    def pipeline_output_name(self, value):
        self._pipeline_output_name = value


class TrainingOutput(object):
    """
    TrainingOutput defines a specialized output of a :class:`azureml.train.automl.AutoMLStep`.

    TrainingOutput enables an AutoML metric or model to be made available as a step output to be consumed
    by another step in a Pipeline.

    .. remarks::

        TrainingOutput is used with :class:`azureml.pipeline.core.PipelineData` when constructing a
        :class:`azureml.pipeline.core.Pipeline` to enable other steps to consume the metrics or models generated
        by an AutoMLStep.

        Use TrainingOutput when defining an AutoMLStep as follows:

        .. code-block:: python

            from azureml.pipeline.core import PipelineData, TrainingOutput

            metirics_data = PipelineData(name='metrics_data', datastore=ds,
                                         pipeline_output_name='metrics_output',
                                         training_output=TrainingOutput(type='Metrics'))
            model_data = PipelineData(name='model_data', datastore=ds,
                                      pipeline_output_name='best_model_output',
                                      training_output=TrainingOutput(type='Model'))
            automl_step = AutoMLStep(name='automl_step',
                                     automl_config=automl_config,
                                     inputs=[input_data],
                                     outputs=[metirics_data, model_data])


        See an example of using TrainingOutput and an AutoMlStep step in notebook https://aka.ms/pl-automl

    :param type: Type of training output. Possible values include: 'Metrics', 'Model'
    :type type: str
    :param iteration: The iteration number of the correspond training model.
                      This iteration number can be provided only with type 'Model'.
                      Note that iteration cannot be provide with metric.
    :type iteration: int
    :param metric: The metric to use to return the best training model.
                   The metric can be provided only with type 'Model'.
                   Note that metric cannot be provide with iteration.
    :type metric: str
    """

    def __init__(self, type, iteration=None, metric=None):
        """
        Initialize TrainingOutput.

        :param type: Type of training output. Possible values include: 'Metrics', 'Model'.
        :type type: str
        :param iteration: The iteration number of the correspond training model.
                          This iteration number can be provided only with type 'Model'.
                          Note that iteration cannot be provide with metric.
        :type iteration: int
        :param metric: The metric to use to return the best training model.
                       The metric can be provided only with type 'Model'.
                       Note that metric cannot be provide with iteration.
        :type metric: str
        """
        if type.lower() == 'metrics':
            if iteration or metric:
                raise ValueError("Iteration and metric shouldn't be provided for output type: Metrics")
        elif type.lower() == 'model':
            if iteration and metric:
                raise ValueError("Both iteration and metric cannot be provided for output type: Model")
        else:
            raise ValueError('Unknown training output type has been provided:', type)

        self._type = type
        self._iteration = iteration
        self._metric = metric

    @property
    def type(self):
        """
        Get the type of training output.

        :return: Type of training output. Possible values include: 'Metrics', 'Model'.
        :rtype: str
        """
        return self._type

    @property
    def iteration(self):
        """
        Get iteration number of the correspond training model.

        :return: iteration number for training model.
        :rtype: int
        """
        return self._iteration

    @property
    def metric(self):
        """
        Get metric for best training model.

        :return: metric name for bets training model.
        :rtype: str
        """
        return self._metric


class PipelineParameter(object):
    """
    Parameter to pipeline execution.

    Use PipelineParameters to construct versatile Pipelines which can be resubmitted later with varying
    parameter values.

    .. remarks::

        PipelineParameters can be added to any step when constructing a Pipeline. When the Pipeline is submitted,
        the values of these parameters can be specified.

        An example of adding a PipelineParameter to a step is as follows:

        .. code-block:: python

            from azureml.pipeline.steps import PythonScriptStep
            from azureml.pipeline.core import PipelineParameter

            pipeline_param = PipelineParameter(name="pipeline_arg", default_value="default_val")
            train_step = PythonScriptStep(script_name="train.py",
                                          arguments=["--param1", pipeline_param],
                                          target=compute_target,
                                          source_directory=project_folder)

        In this example a PipelineParameter with the name "pipeline_arg" was added to the arguments of a
        PythonScriptStep. When the python script is run, the value of the PipelineParameter will be provided through
        the command line arguments.
        This PipelineParameter can also be added to other steps in the Pipeline. This can be useful to provide
        common values to multiple steps in the Pipeline. Pipelines can have multiple PipelineParameters specified.

        To submit this Pipeline and specify the value for the "pipeline_arg" PipelineParameter use:

        .. code-block:: python

            from azureml.pipeline.core import Pipeline

            pipeline = Pipeline(workspace=ws, steps=[train_step])
            pipeline_run = experiment.submit(pipeline,
                                             pipeline_params={"pipeline_arg": "new_value"})

        Note: if "pipeline_arg" was not specified in the pipeline_params dictionary, the default value of the
        PipelineParameter provided when the Pipeline was constructed would be used (in this case the
        default value provided was "default_val").

        PipelineParameters can also be used with :class:`azureml.data.datapath.DataPath` and
        :class:`azureml.data.datapath.DataPathComputeBinding` to specify step inputs.
        This enables a Pipeline to be run with varying input data.

        An example of using DataPath with PipelineParameters is as follows:

        .. code-block:: python

            from azureml.core.datastore import Datastore
            from azureml.data.datapath import DataPath, DataPathComputeBinding
            from azureml.pipeline.steps import PythonScriptStep
            from azureml.pipeline.core import PipelineParameter

            datastore = Datastore(workspace=workspace, name="workspaceblobstore")
            datapath = DataPath(datastore=datastore, path_on_datastore='input_data')
            data_path_pipeline_param = (PipelineParameter(name="input_data", default_value=datapath),
                                        DataPathComputeBinding(mode='mount'))

            train_step = PythonScriptStep(script_name="train.py",
                                          arguments=["--input", data_path_pipeline_param],
                                          inputs=[data_path_pipeline_param],
                                          target=compute_target,
                                          source_directory=project_folder)

        In this case the default value of the "input_data" parameter references a file on the "workspaceblobstore"
        named "input_data". If the Pipeline is submitted without specifying a value for this PipelineParameter,
        the default value will be used.
        To submit this Pipeline and specify the value for the "input_data" PipelineParameter use:

        .. code-block:: python

            from azureml.pipeline.core import Pipeline
            from azureml.data.datapath import DataPath

            pipeline = Pipeline(workspace=ws, steps=[train_step])
            new_data_path = DataPath(datastore=datastore, path_on_datastore='new_input_data')
            pipeline_run = experiment.submit(pipeline,
                                             pipeline_params={"input_data": new_data_path})


    :param name: name of the pipeline parameter
    :type name: str
    :param default_value: default value of the pipeline parameter
    :type default_value: literal values or data references as JSON
    """

    def __init__(self, name, default_value):
        """
        Initialize parameters to pipeline execution.

        :param name: name of the pipeline parameter
        :type name: str
        :param default_value: default value of the pipeline parameter
        :type default_value: literal values or data references
        """
        self.name = name
        self.default_value = default_value

        if not isinstance(default_value, int) and not isinstance(default_value, str) and \
            not isinstance(default_value, bool) and not isinstance(default_value, float) \
                and not isinstance(default_value, DataPath) and not PipelineDataset.is_dataset(default_value) \
                and not isinstance(default_value, PipelineDataset):
            raise ValueError('Default value is of unsupported type: {0}'.format(type(default_value).__name__))

    def __str__(self):
        """
        __str__ override.

        :return: str representation of the PipelineParameter
        :rtype: str
        """
        return "PipelineParameter_Name:{0}_Default:{1}".format(self.name, self.default_value)


class Param(object):
    """
    Instance of an parameter on a node.

    :param param_def: The param definition object.
    :type param_def: azureml.pipeline.core.graph.ParamDef
    """

    def __init__(self, param_def):
        """
        Initialize Param.

        :param param_def: The param definition object.
        :type param_def: azureml.pipeline.core.graph.ParamDef
        """
        self.param_def = param_def
        self.name = param_def.name
        self.value = param_def.default_value
        self.set_var = param_def.env_var_override

    def set_value(self, param_value):
        """
        Set the parameter value.

        :param param_value: The parameter value.
        :type param_value: str
        """
        self.value = param_value

    def get_value(self):
        """
        Get the parameter value.

        :return: The parameter value.
        :rtype: str
        """
        return self.value


class Edge(object):
    """
    Instance of an edge between two node ports in the graph.

    :param source_port: The source port for the edge.
    :type source_port: azureml.pipeline.core.graph.OutputPort
    :param dest_port: The destination port for the edge.
    :type dest_port: azureml.pipeline.core.graph.InputPort
    """

    def __init__(self, source_port, dest_port):
        """
        Initialize Edge.

        :param source_port: The source port for the edge.
        :type source_port: azureml.pipeline.core.graph.OutputPort
        :param dest_port: The destination port for the edge.
        :type dest_port: azureml.pipeline.core.graph.InputPort
        """
        self._source_port = source_port
        self._dest_port = dest_port

    @property
    def source_port(self):
        """
        Source port of the Edge.

        :return: The source port.
        :rtype: azureml.pipeline.core.graph.OutputPort
        """
        return self._source_port

    @property
    def dest_port(self):
        """
        Destination port of the Edge.

        :return: The destination port.
        :rtype: azureml.pipeline.core.graph.InputPort
        """
        return self._dest_port


class _IntermediateEdgeBuilder(object):
    """
    An intermediate edge builder builds an edge when the edge's source is not an OutputPort.

    An intermediate edge builder is used when constructing a graph.
    """

    def __init__(self, source, dest_port):
        """
        Initialize _IntermediateEdgeBuilder.

        :param source: data reference object
        :type source: azureml.core.data.DataReference
        :param dest_port: destination port
        :type dest_port: azureml.pipeline.core.graph.InputPort
        """
        self._source = source
        self._dest_port = dest_port


class _PipelineIOEdgeBuilder(_IntermediateEdgeBuilder):
    """Instance of an edge builder between an InputPort and a DataPath."""

    def __init__(self, source, dest_port):
        """
        Initialize _PipelineIOEdgeBuilder.

        :param source: datapath source
        :type source: azureml.core.data.DataPath
        :param dest_port: destination port
        :type dest_port: azureml.pipeline.core.graph.InputPort
        """
        super(self.__class__, self).__init__(source, dest_port)

    @property
    def source(self):
        """
        Source of the Edge.

        :return: source
        :rtype: azureml.core.data.DataPath
        """
        return self._source

    @property
    def dest_port(self):
        """
        Destination port of the Edge.

        :return: dest_port
        :rtype: azureml.pipeline.core.graph.InputPort
        """
        return self._dest_port

    def create_edge(self, resolved_node):
        """
        Create the Edge.

        :param resolved_node: resolved node
        :type resolved_node: azureml.pipeline.core.graph.Node
        """
        resolved_port = resolved_node.get_output(DataSource.DATASOURCE_PORT_NAME)
        if not isinstance(resolved_port, OutputPort):
            raise ValueError('resolved port is of type:', type(resolved_port))
        self.dest_port.disconnect()  # disconnect incomplete edge
        self.dest_port.connect(resolved_port)  # connect to resolved OutputPort


class _DataReferenceEdgeBuilder(_IntermediateEdgeBuilder):
    """Instance of an edge builder between an InputPort and a DataReference or PortDataReference."""

    def __init__(self, source, dest_port):
        """
        Initialize _DataReferenceEdgeBuilder.

        :param source: data reference source
        :type source: azureml.core.data.DataReference
        :param dest_port: destination port
        :type dest_port: azureml.pipeline.core.graph.InputPort
        """
        super(self.__class__, self).__init__(source, dest_port)

    @property
    def source(self):
        """
        Source of the Edge.

        :return: source
        :rtype: azureml.core.data.DataReference
        """
        return self._source

    @property
    def dest_port(self):
        """
        Destination port of the Edge.

        :return: dest_port
        :rtype: azureml.pipeline.core.graph.InputPort
        """
        return self._dest_port

    def create_edge(self, resolved_node):
        """
        Create the Edge.

        :param resolved_node: resolved node
        :type resolved_node: azureml.pipeline.core.graph.Node
        """
        resolved_port = resolved_node.get_output(DataSource.DATASOURCE_PORT_NAME)
        if not isinstance(resolved_port, OutputPort):
            raise ValueError('resolved port is of type:', type(resolved_port))
        self.dest_port.disconnect()  # disconnect incomplete edge
        self.dest_port.connect(resolved_port)  # connect to resolved OutputPort


class _DatasetEdgeBuilder(_IntermediateEdgeBuilder):
    """Instance of an edge builder between an InputPort and a PipelineDataset."""

    def __init__(self, source, dest_port):
        """
        Initialize a _DatasetEdgeBuilder.

        :param source: The data source.
        :type source: PipelineDataset
        :param dest_port: The destination port.
        :type dest_port: azureml.pipeline.core.graph.InputPort
        """
        super(self.__class__, self).__init__(source, dest_port)

    @property
    def source(self):
        """
        Source of the Edge.

        :return: The source
        :rtype: PipelineDataset
        """
        return self._source

    @property
    def dest_port(self):
        """
        Destination port of the Edge.

        :return: The destination port.
        :rtype: azureml.pipeline.core.graph.InputPort
        """
        return self._dest_port

    def create_edge(self, resolved_node):
        """
        Create the Edge.

        :param resolved_node: resolved node
        :type resolved_node: azureml.pipeline.core.graph.Node
        """
        resolved_port = resolved_node.get_output(DataSource.DATASOURCE_PORT_NAME)
        if not isinstance(resolved_port, OutputPort):
            raise ValueError('resolved port is of type:', type(resolved_port))
        self.dest_port.disconnect()  # disconnect incomplete edge
        self.dest_port.connect(resolved_port)  # connect to resolved OutputPort


class _PipelineDataEdgeBuilder(_IntermediateEdgeBuilder):
    """Instance of an edge builder between an InputPort and a PipelineData or OutputPortBinding."""

    def __init__(self, source, dest_port):
        """
        Initialize _PipelineDataEdgeBuilder.

        :param source: pipeline data
        :type source: azureml.pipeline.core.builder.PipelineData or azureml.pipeline.core.graph.OutputPortBinding
        :param dest_port: destination port
        :type dest_port: azureml.pipeline.core.graph.InputPort
        """
        super(self.__class__, self).__init__(source, dest_port)

    @property
    def source(self):
        """
        Source of the Edge.

        :return: The edge source.
        :rtype: azureml.pipeline.core.builder.PipelineData
        """
        return self._source

    @property
    def dest_port(self):
        """
        Destination port of the Edge.

        :return: dest_port
        :rtype: azureml.pipeline.core.graph.InputPort
        """
        return self._dest_port

    def create_edge(self, resolved_node):
        """
        Create the Edge.

        :param resolved_node: resolved node
        :type resolved_node: azureml.pipeline.core.graph.Node
        """
        resolved_port = resolved_node.get_output(self.source._output_name)
        if not isinstance(resolved_port, OutputPort):
            raise ValueError('resolved port is of type:', type(resolved_port))
        self.dest_port.disconnect()  # disconnect incomplete edge
        self.dest_port.connect(resolved_port)  # connect to resolved OutputPort


class InputPortBinding(object):
    """
    Defines a binding from a source to an input of a step.

    An InputPortBinding can be used as an input to a step. The source can be a
    :class:`azureml.pipeline.core.PipelineData`, :class:`azureml.pipeline.core.PortDataReference`,
    :class:`azureml.data.data_reference.DataReference`, :class:`azureml.pipeline.core.PipelineDataset`,
    or :class:`azureml.pipeline.core.OutputPortBinding`.

    InputPortBinding is useful to specify the name of the step input, if it should be different than the name
    of the bind object (i.e. to avoid duplicate input/output names or because the step script needs an input to have
    a certain name). It can also be used to specify the bind_mode for :class:`azureml.pipeline.steps.PythonScriptStep`
    inputs.

    .. remarks::

        InputPortBinding is used to specify data dependencies in a Pipeline, it represents an input which a step
        requires for execution. InputPortBindings have a source, called bind_object, which specifies how the input
        data is produced.

        :class:`azureml.pipeline.core.PipelineData` and :class:`azureml.pipeline.core.OutputPortBinding` can be used
        as the bind_object for an InputPortBinding to specify that the input to the step will be produced by
        another step in the Pipeline.

        An example to build a Pipeline using InputPortBinding and PipelineData is as follows:

        .. code-block:: python

            from azureml.pipeline.core import PipelineData, InputPortBinding, Pipeline
            from azureml.pipeline.steps import PythonScriptStep

            step_1_output = PipelineData("output", datastore=datastore, output_mode="mount")

            step_1 = PythonScriptStep(
                name='prepare data',
                script_name="prepare_data.py",
                compute_target=compute,
                arguments=["--output", step_1_output],
                outputs=[step_1_output]
            )

            step_2_input = InputPortBinding("input", bind_object=step_1_output)

            step_2 = PythonScriptStep(
                name='train',
                script_name="train.py",
                compute_target=compute,
                arguments=["--input", step_2_input],
                inputs=[step_2_input]
            )

            pipeline = Pipeline(workspace=workspace, steps=[step_1, step_2])

        In this example the "train" step requires the output of the "prepare data" step as an input.

        :class:`azureml.pipeline.core.PortDataReference`, :class:`azureml.data.data_reference.DataReference`, or
        :class:`azureml.pipeline.core.PipelineDataset` can be used as the bind_object for an InputPortBinding to
        specify that the input to the step already exists at a specified location.

        An example to build a Pipeline using InputPortBinding and DataReference is as follows:

        .. code-block:: python

            from azureml.data.data_reference import DataReference
            from azureml.pipeline.core import InputPortBinding, Pipeline
            from azureml.pipeline.steps import PythonScriptStep

            data_reference = DataReference(datastore=datastore, path_on_datastore='sample_data.txt', mode="mount")
            step_1_input = InputPortBinding("input", bind_object=data_reference)

            step_1 = PythonScriptStep(
                name='train',
                script_name="train.py",
                compute_target=compute,
                arguments=["--input", step_1_input],
                inputs=[step_1_input]
            )

            pipeline = Pipeline(workspace=workspace, steps=[step_1])

        In this example the "train" step requires the "sample_data.txt" file specified by the
        DataReference as an input.


    :param name: Name of the input port to bind.
    :type name: str
    :param bind_object: The object to bind to the input port.
    :type bind_object: azureml.pipeline.core.PortDataReference,
                       azureml.data.data_reference.DataReference,
                       azureml.pipeline.core.PipelineData,
                       azureml.pipeline.core.OutputPortBinding,
                       azureml.pipeline.core.PipelineDataset
    :param bind_mode: Specifies whether the consuming step will use "download" or "mount" method to access the data.
    :type bind_mode: str
    :param path_on_compute: For "download" mode, the local path the step will read the data from.
    :type path_on_compute: str
    :param overwrite: For "download" mode, indicate whether to overwrite existing data.
    :type overwrite: bool
    :param is_resource: Indicate whether input is a resource. Resources are downloaded to the script folder and
        provide a way to change the behavior of script at run-time.
    :type is_resource: bool
    """

    def __init__(self, name, bind_object=None, bind_mode="mount", path_on_compute=None, overwrite=None,
                 is_resource=False):
        """
        Initialize InputPortBinding.

        :param name: Name of the input port to bind.
        :type name: str
        :param bind_object: The object to bind to the input port.
        :type bind_object: azureml.pipeline.core.PortDataReference
                           azureml.data.data_reference.DataReference
                           azureml.pipeline.core.PipelineData
                           azureml.pipeline.core.OutputPortBinding
                           azureml.pipeline.core.PipelineDataset
        :param bind_mode: Specifies whether the consuming step will use "download" or "mount"
            method to access the data.
        :type bind_mode: str
        :param path_on_compute: For "download" mode, the local path the step will read the data from.
        :type path_on_compute: str
        :param overwrite: For "download" mode, indicate whether to overwrite existing data.
        :type overwrite: bool
        :param is_resource: Indicate whether input is a resource. Resources are downloaded to the script folder and
            provide a way to change the behavior of script at run-time.
        :type is_resource: bool
        """
        if bind_object is None:
            raise ValueError("bind_object is required")
        # TODO: rationalize these!
        if bind_mode is not "mount" and bind_mode is not "download":
            raise ValueError("invalid bind_mode " + bind_mode)
        self._name = name
        self._bind_mode = bind_mode
        self._bind_object = bind_object
        self._path_on_compute = path_on_compute
        self._overwrite = overwrite
        self._data_type = self.get_bind_object_data_type()
        self._data_reference_name = self.get_bind_object_name()
        self._is_resource = is_resource

    @property
    def name(self):
        """
        Name of the Input port binding.

        :return: The name.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        Set the name of the Input port binding.

        :param value: The new name of the InputPortBinding.
        :type value: str
        """
        self._name = value

    @property
    def bind_mode(self):
        """
        Get the mode ("download" or "mount") the consuming step will use to access the data.

        :return: The bind mode ("download" or "mount").
        :rtype: str
        """
        return self._bind_mode

    @property
    def bind_object(self):
        """
        Get the object the InputPort will be bound to.

        :return: The bind object.
        :rtype: azureml.pipeline.core.PortDataReference,
                azureml.data.data_reference.DataReference,
                azureml.pipeline.core.PipelineData,
                azureml.pipeline.core.OutputPortBinding
                azureml.pipeline.core.PipelineDataset
        """
        return self._bind_object

    @property
    def path_on_compute(self):
        """
        Get the local path the step will read the data from.

        :return: The path on compute.
        :rtype: str
        """
        return self._path_on_compute

    @property
    def data_reference_name(self):
        """
        Get the name of the data reference associated with the InputPortBinding.

        :return: The data reference name.
        :rtype: str
        """
        return self._data_reference_name

    @property
    def overwrite(self):
        """
        For "download" mode, indicate whether to overwrite existing data.

        :return: The overwrite property.
        :rtype: bool
        """
        return self._overwrite

    @property
    def data_type(self):
        """
        Get the type of the input data.

        :return: The data type property.
        :rtype: str
        """
        return self._data_type

    @property
    def is_resource(self):
        """
        Get whether input is a resource.

        :return: Is input a resource.
        :rtype: bool
        """
        return self._is_resource

    def get_bind_object_name(self):
        """
        Get the name of the bind object.

        :return: The bind object name.
        :rtype: str
        """
        from azureml.pipeline.core.builder import PipelineData
        if isinstance(self.bind_object, PipelineData) or isinstance(self.bind_object, OutputPortBinding) \
                or isinstance(self.bind_object, _PipelineIO):
            return self.bind_object.name
        elif isinstance(self.bind_object, PortDataReference) or isinstance(self.bind_object, DataReference):
            return self.bind_object.data_reference_name
        elif isinstance(self.bind_object, PipelineDataset):
            return self.bind_object.name
        else:
            return None

    def get_bind_object_data_type(self):
        """
        Get the data type of the bind object.

        :return: The data type name.
        :rtype: str
        """
        from azureml.pipeline.core.builder import PipelineData
        if isinstance(self.bind_object, PipelineData) or isinstance(self.bind_object, OutputPortBinding):
            return self.bind_object.data_type
        elif isinstance(self.bind_object, PipelineDataset):
            return self.bind_object._data_type_short_name
        else:
            return None

    def as_resource(self):
        """
        Get a duplicate input port binding which can be used as a resource.

        :return: InputPortBinding with is_resource property set a True.
        :rtype: :class:`azureml.pipeline.core.InputPortBinding`
        """
        binding = self._clone()
        binding._is_resource = True
        return binding

    def _clone(self):
        return InputPortBinding(name=self.name, bind_object=self.bind_object, bind_mode=self.bind_mode,
                                path_on_compute=self.path_on_compute, overwrite=self.overwrite,
                                is_resource=self.is_resource)

    def __str__(self):
        """
        __str__ override.

        :return: str representation of the InputPortBinding.
        :rtype: str
        """
        return "$AZUREML_DATAREFERENCE_{0}".format(self.name)

    def __repr__(self):
        """
        Return __str__.

        :return: str representation of the InputPortBinding.
        :rtype: str
        """
        return self.__str__()


class OutputPortBinding(object):
    """
    OutputPortBinding specifies a named output of a step.

    OutputPortBinding can be used to specify the type of data which will be produced by a step and how the data will
    be produced. It can be used with :class:`azureml.pipeline.core.InputPortBinding` to specify that the step output
    is a required input of another step.

    .. remarks::

        OutputPortBinding can be used in a similar way as :class:`azureml.pipeline.core.PipelineData` when
        building a Pipeline to specify step inputs and outputs. The difference is OutputPortBinding needs to be
        used with :class:`azureml.pipeline.core.InputPortBinding` in order to be consumed as an input to another step.

        An example to construct a Pipeline with OutputPortBinding is as follows:

        .. code-block:: python

            from azureml.pipeline.core import OutputPortBinding, InputPortBinding, Pipeline
            from azureml.pipeline.steps import PythonScriptStep

            step_1_output = OutputPortBinding("output", datastore=datastore)

            step_1 = PythonScriptStep(
                name='process data',
                script_name="process_data.py",
                compute_target=compute,
                arguments=["--output", step_1_output],
                outputs=[step_1_output]
            )

            step_2_input = InputPortBinding("input", bind_object=step_1_output)

            step_2 = PythonScriptStep(
                name='train',
                script_name="train.py",
                compute_target=compute,
                arguments=["--input", step_2_input],
                inputs=[step_2_input]
            )

            pipeline = Pipeline(workspace=workspace, steps=[step_1, step_2])

        This will create a Pipeline with two steps. The process step will be executed first, then after it has
        completed, the train step will be executed. The orchestrator will provide the output produced by the process
        step, as described by the OutputPortBinding object, to the train step.


    :param name: Name of the OutputPortBinding object. Can only contain letters, digits, and underscores.
    :type name: str
    :param datastore: Datastore the PipelineData will reside on.
    :type datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
    :param output_name: Name of the output, if None name is used.
    :type output_name: str
    :param bind_mode: Specifies whether the producing step will use "upload" or "mount" method to access the data.
    :type bind_mode: str
    :param path_on_compute: For "upload" mode, the path the module writes the output to.
    :type path_on_compute: str
    :param is_directory: Whether the output is a directory or single file.
    :type is_directory: bool
    :param overwrite: For "upload" mode, whether to overwrite existing data.
    :type overwrite: bool
    :param data_type: Optional. Data type can be used to specify the expected type of the output and to detail how
                      consuming steps should use the data. Can be any user-defined string.
    :type data_type: str
    :param pipeline_output_name: If provided this output will be available by using
        PipelineRun.get_pipeline_output(). Pipeline output names must be unique in the pipeline.
    :type pipeline_output_name: str
    :param training_output: Defines output for training result. This is needed only for specific trainings which
                            result in different kinds of outputs such as Metrics and Model.
                            For example, :class:`azureml.train.automl.AutoMLStep` results in metrics and model.
                            You can also define specific training iteration or metric used to get best model.
    :type training_output: azureml.pipeline.core.TrainingOutput, optional
    """

    def __init__(self, name, datastore=None, output_name=None, bind_mode="mount", path_on_compute=None,
                 is_directory=None, overwrite=None, data_type=None, pipeline_output_name=None,
                 training_output=None):
        """
        Initialize OutputPortBinding.

        :param name: Name of the OutputPortBinding object. Can only contain letters, digits, and underscores.
        :type name: str
        :param datastore: Datastore the PipelineData will reside on.
        :type datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param output_name: Name of the output, if None name is used.
                            Can only contain letters, digits, and underscores.
        :type output_name: str
        :param bind_mode: Specifies whether the producing step will use "upload" or "mount" method to access the data.
        :type bind_mode: str
        :param path_on_compute: For "upload" mode, the path the module writes the output to.
        :type path_on_compute: str
        :param is_directory: if output is a directory
        :type is_directory: bool
        :param overwrite: For "upload" mode, whether to overwrite existing data.
        :type overwrite: bool
        :param data_type: Optional. Data type can be used to specify the expected type of the output and to detail how
                          consuming steps should use the data. Can be any user-defined string.
        :type data_type: str
        :param pipeline_output_name: If provided this output will be available by using
            PipelineRun.get_pipeline_output(). Pipeline output names must be unique in the pipeline.
        :type pipeline_output_name: str
        :param training_output: Defines output for training result. This is needed only for specific trainings which
                                result in different kinds of outputs such as Metrics and Model.
                                For example, :class:`azureml.train.automl.AutoMLStep` results in metrics and model.
                                You can also define specific training iteration or metric used to get best model.
        :type training_output: azureml.pipeline.core.TrainingOutput, optional
        """
        if bind_mode is not "mount" and bind_mode is not "upload":
            raise ValueError("Invalid bind_mode " + bind_mode)

        import re
        invalid_name_exp = re.compile('\\W')

        self._name = name
        if invalid_name_exp.search(self._name):
            raise ValueError("OutputPortBinding name: [{name}] is not a valid, as it may contain only letters, "
                             "digits, and underscores.".format(name=self._name))

        if output_name is None:
            output_name = name
        self._output_name = output_name
        if invalid_name_exp.search(self._output_name):
            raise ValueError("OutputPortBinding output_name: [{name}] is not a valid, as it may contain only letters, "
                             "digits, and underscores.".format(name=self._output_name))

        self._datastore = datastore
        self._bind_mode = bind_mode
        self._path_on_compute = path_on_compute
        self._is_directory = is_directory
        self._overwrite = overwrite
        self._producer = None
        self._data_type = data_type
        self._pipeline_output_name = pipeline_output_name
        self._training_output = training_output

    @property
    def name(self):
        """
        Name of the OutputPortBinding object.

        :return: The name.
        :rtype: str
        """
        return self._name

    @property
    def bind_mode(self):
        """
        Get the mode ("upload" or "mount") the producing step will use to create the data.

        :return: The bind mode.
        :rtype: str
        """
        return self._bind_mode

    @property
    def datastore(self):
        """
        Datastore the PipelineData will reside on.

        :return: The Datastore object.
        :rtype: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        """
        return self._datastore

    @datastore.setter
    def datastore(self, value):
        """
        Set the Datastore the PipelineData will reside on.

        :param value: The Datastore object.
        :type value: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        """
        self._datastore = value

    @property
    def _datastore_name(self):
        """
        Name of the Datastore the PipelineData will reside on.

        :return: The Datastore name.
        :rtype: str
        """
        if self._datastore is not None:
            return self._datastore.name
        else:
            return None

    @property
    def path_on_compute(self):
        """
        For "upload" mode, the path the module writes the output to.

        :return: path_on_compute
        :rtype: str
        """
        return self._path_on_compute

    @property
    def is_directory(self):
        """
        Whether the output is a directory.

        :return: is_directory
        :rtype: bool
        """
        return self._is_directory

    @property
    def overwrite(self):
        """
        For "upload" mode, indicate whether to overwrite existing data.

        :return: _overwrite
        :rtype: bool
        """
        return self._overwrite

    @property
    def data_type(self):
        """
        Get the type of data which will be produced.

        :return: The data type name.
        :rtype: str
        """
        return self._data_type

    @property
    def pipeline_output_name(self):
        """
        Get the name of the pipeline output corresponding to this OutputPortBinding.

        :return: The pipeline output name.
        :rtype: str
        """
        return self._pipeline_output_name

    @property
    def training_output(self):
        """
        Get training output.

        :return: Training output
        :rtype: azureml.pipeline.core.TrainingOutput
        """
        return self._training_output

    def _set_producer(self, step):
        self._producer = step

    def __str__(self):
        """
        __str__ override.

        :return: str representation of the OutputPortBinding.
        :rtype: str
        """
        return "$AZUREML_DATAREFERENCE_{0}".format(self.name)

    def __repr__(self):
        """
        Return __str__.

        :return: str representation of the OutputPortBinding.
        :rtype: str
        """
        return self.__str__()


class _NodeColors(object):
    """When checking for cycles in the graph, keep track of which nodes have been visited."""

    # Initial state (not visited yet)
    WHITE = 0

    # Currently being visited as part of a depth-first search
    GRAY = 1

    # Final state (completed visit of node)
    BLACK = 2


class Graph(object):
    """
    A class to define a pipeline run graph.

    :param name: Name of the graph.
    :type name: str
    :param context: The current graph context.
    :type context: _GraphContext
    """

    def __init__(self, name, context):
        """
        Initialize Graph.

        :param name: Name of the graph.
        :type name: str
        :param context: The current graph context.
        :type context: _GraphContext
        """
        self._context = context
        self._graph_provider = self._context.workflow_provider.graph_provider

        self._name = name
        self._nodes = {}
        self._node_names = {}
        self._module_nodes = {}
        self._datasource_nodes = {}
        self._datapath_parameters = {}
        self._finalized = False
        self._params = {}
        self._pipeline_outputs = {}

    def __str__(self):
        """
        __str__ override.

        :return: str representation of the Graph.
        :rtype: str
        """
        return "Graph(name:{})".format(self._name)

    def sequence(self, nodes):
        """
        Configure a list of nodes to run in a sequence following the first node in the list.

        :param nodes: The list of nodes.
        :type nodes: :class:`list`
        """
        if nodes is None or len(nodes) < 2:
            return

        node = nodes[0]
        for follower in nodes[1:]:
            follower.run_after(node)
            node = follower

    def add_module_node(self, name, input_bindings, output_bindings=None, param_bindings=None, module=None,
                        module_builder=None, module_wiring=None):
        """
        Add a module node to the graph.

        :param name: Name of the node
        :type name: str
        :param input_bindings: List of input port bindings
        :type input_bindings: :class:`list`
        :param output_bindings: List of output port bindings
        :type output_bindings: :class:`list`
        :param param_bindings: Dictionary of name-value pairs for parameter assignments
        :type param_bindings: dict
        :param module: Module for this node
        :type module: azureml.pipeline.core.graph.Module
        :param module_builder: _ModuleBuilder for this node
        :type module_builder: _ModuleBuilder
        :param module_wiring: mapping between the node's inputs/outputs and the module inputs/outputs. Holds
                              two keys,inputs and outputs, each mapped to a dict whose keys are the module's
                              inputs/outputs names, and the values are the node's ports
        :type module_wiring: {}

        :return: node
        :rtype: azureml.pipeline.core.graph.Node
        """
        if output_bindings is None:
            output_bindings = []
        if param_bindings is None:
            param_bindings = {}

        if module is None and module_builder is None:
            raise ValueError("Either module or module_builder is required")

        node_id = self._generate_node_id()
        node = ModuleNode(graph=self, name=name, node_id=node_id, module=module, module_builder=module_builder,
                          module_wiring=module_wiring)

        binding_to_module_output = {}
        binding_to_module_input = {}
        if node._module_wiring is not None:
            for out_target in node._module_wiring["outputs"].keys():
                out_port_bind = node._module_wiring["outputs"][out_target]
                binding_to_module_output[out_port_bind.name] = node._outputs[out_target]

            for inp_target in node._module_wiring["inputs"].keys():
                inp_port_bind = node._module_wiring["inputs"][inp_target]
                binding_to_module_input[inp_port_bind.name] = node._inputs[inp_target]

        # set param value overrides
        for parameter_name in param_bindings:
            param = param_bindings[parameter_name]
            # ignore dataset pipeline parameters as it is handled differently in aeva
            if isinstance(param, PipelineParameter) and (isinstance(param.default_value, PipelineDataset) or
                                                         PipelineDataset.is_dataset(param.default_value)):
                continue
            node.get_param(parameter_name).set_value(param_bindings[parameter_name])

        # wire up input bindings
        for input_binding in input_bindings:
            input_port = node.get_input(input_binding.name) \
                if node._module_wiring is None \
                else binding_to_module_input[input_binding.name]
            input_port.data_reference_name = input_binding.data_reference_name
            input_port.bind_mode = input_binding.bind_mode
            input_port.path_on_compute = input_binding.path_on_compute
            input_port.overwrite = input_binding.overwrite
            # create edge between input and bind object
            input_port.connect(input_binding.bind_object)

        # wire up output bindings
        for output_binding in output_bindings:
            output_port = \
                node.get_output(output_binding._output_name) \
                if node._module_wiring is None \
                else binding_to_module_output[output_binding._output_name]
            output_port.datastore_name = output_binding._datastore_name
            output_port.bind_mode = output_binding.bind_mode
            output_port.path_on_compute = output_binding.path_on_compute
            output_port.overwrite = output_binding.overwrite
            # add to graph's pipeline output dict
            if output_binding.pipeline_output_name is not None:
                if output_binding.pipeline_output_name in self._pipeline_outputs.keys():
                    raise ValueError("Duplicate pipeline output with name {0}"
                                     .format(output_binding.pipeline_output_name))
                output_port.pipeline_output_name = output_binding.pipeline_output_name
                self._pipeline_outputs[output_binding.pipeline_output_name] = output_port

        self._add_node_to_dicts(node)
        return node

    def _add_datapath_parameter(self, datapath_param):
        self._datapath_parameters[datapath_param.name] = datapath_param
        self._add_pipeline_params([datapath_param])

    def _add_pipeline_params(self, pipeline_params):
        for pipeline_param in pipeline_params:
            if pipeline_param.name not in self._params:
                self._params[pipeline_param.name] = self._transform_params_default_value(pipeline_param)
            else:
                if self._params[pipeline_param.name].default_value != pipeline_param.default_value:
                    # example scenario - different nodes use same pipeline param name but different default values
                    raise Exception('Graph already has pipeline parameter with same name {0} but different '
                                    'default values {1}, {2}'.format(pipeline_param.name,
                                                                     self._params[pipeline_param.name].default_value,
                                                                     pipeline_param.default_value))

    def _transform_params_default_value(self, pipeline_param):
        if PipelineDataset.is_dataset(pipeline_param.default_value):
            name = PipelineDataset.default_name(pipeline_param.default_value)
            pipeline_param.default_value = PipelineDataset(pipeline_param.default_value, name=name,
                                                           parameter_name=pipeline_param.name)
        if isinstance(pipeline_param.default_value, PipelineDataset):
            if not pipeline_param.default_value.parameter_name:
                pipeline_param.default_value._parameter_name = pipeline_param.name
        return pipeline_param

    def _add_node_to_dicts(self, node):
        node_id = node.node_id
        self._nodes[node_id] = node
        if node._module is not None or node._module_builder is not None:
            self._module_nodes[node_id] = node
        elif node._datasource is not None or node._datasource_builder is not None:
            self._datasource_nodes[node_id] = node
        else:
            raise ValueError("Unknown node type")

        if node.name not in self._node_names:
            self._node_names[node.name] = []
        self._node_names[node.name].append(node)

    @property
    def node_name_dict(self):
        """
        Get a dictionary containing all nodes indexed by name.

        :return: Dictionary of {node name, :class:`azureml.pipeline.core.graph.Node`}
        :rtype: dict
        """
        return self._node_names

    def add_datasource_node(self, name, datasource=None, datasource_builder=None, datapath_param_name=None):
        """
        Add a datasource node to the graph.

        :param name: Name of the node.
        :type name: str
        :param datasource: Datasource for this node.
        :type datasource: azureml.pipeline.core.graph.DataSource
        :param datasource_builder: _DatasourceBuilder for this node.
        :type datasource_builder: _DatasourceBuilder
        :param datapath_param_name: Datapath parameter name.
        :type datapath_param_name: str

        :return: node
        :rtype: azureml.pipeline.core.graph.Node
        """
        if datasource is None and datasource_builder is None:
            raise ValueError("Either datasource or datasource_builder is required")

        node_id = self._generate_node_id()
        node = DataSourceNode(graph=self, name=name, node_id=node_id, datasource=datasource,
                              datasource_builder=datasource_builder, datapath_param_name=datapath_param_name)

        self._add_node_to_dicts(node)

        return node

    def get_node(self, node_id):
        """
        Get a node by id.

        :param node_id: The node id.
        :type node_id: str

        :return: the node
        :rtype: azureml.pipeline.core.graph.Node
        """
        return self._nodes[node_id]

    @property
    def params(self):
        """
        Get a dictionary containing all graph parameters. Values are literal types or data reference as JSON string.

        :return: Dictionary of {param name, param value}
        :rtype: dict
        """
        return self._params

    @property
    def node_dict(self):
        """
        Get a dictionary containing all nodes.

        :return: Dictionary of {node Id, :class:`azureml.pipeline.core.graph.Node`}
        :rtype: dict
        """
        return self._nodes

    @property
    def nodes(self):
        """
        Get a list containing all nodes.

        :return: List of :class:`azureml.pipeline.core.graph.Node`
        :rtype: :class:`list`
        """
        return self._nodes.values()

    @property
    def module_nodes(self):
        """
        Get a list containing all module nodes.

        :return: List of :class:`azureml.pipeline.core.graph.Node`
        :rtype: :class:`list`
        """
        return self._module_nodes.values()

    @property
    def datasource_nodes(self):
        """
        Get a list containing all datasource nodes.

        :return: List of :class:`azureml.pipeline.core.graph.Node`
        :rtype: :class:`list`
        """
        return self._datasource_nodes.values()

    def delete_node(self, node_id):
        """
        Delete a node from the graph.

        :param node_id: node id
        :type node_id: str
        """
        raise NotImplementedError

    def connect(self, source_port, dest_port):
        """
        Connect two ports and creates an Edge.

        :param source_port: Output port from the node that is the source of the connection
        :type source_port: azureml.pipeline.core.graph.OutputPort
        :param dest_port: Input port from the node that is the destination of the connection
        :type dest_port: azureml.pipeline.core.graph.InputPort

        :return: edge
        :rtype: azureml.pipeline.core.graph.Edge
        """
        raise NotImplementedError

    @property
    def edges(self):
        """
        Get an iterator of edges.

        :return: a list of :class:`azureml.pipeline.core.graph.Edge`
        :rtype: :class:`list`
        """
        edges = []
        for node in self.module_nodes:
            for input in node.inputs:
                if input.incoming_edge is not None:
                    edges.append(input.incoming_edge)

        return edges

    def finalize(self, dry_run=None, regenerate_outputs=False):
        """
        Finalize resources for nodes in the graph.

        :param dry_run: set to True to report nodes that require new resources
        :type dry_run: bool
        :param regenerate_outputs: set to True to force a new run (disallows module/datasource reuse)
        :type regenerate_outputs: bool

        :return: Dictionary of {node_id, (resource_id, is_new_resource)}
        :rtype: dict
        """
        if dry_run is None:
            dry_run = False

        datatype_provider = self._context.workflow_provider.datatype_provider
        datatype_provider.ensure_default_datatypes()

        result = {}
        module_provider = self._context.workflow_provider.module_provider
        for node in self.module_nodes:
            if node._module is not None:
                finalized_mv = node._module.module_version.\
                    module(self._context.workflow_provider).resolve(node._module._default_version)
                node._module.module_version = finalized_mv
                node._module.id = finalized_mv.module_version_id
                result[node.node_id] = (node._module.id, False)
            else:
                module_builder = node._module_builder

                # Check if this module already exists
                fingerprint = module_builder.get_fingerprint()
                module_id = None
                module = None
                if not regenerate_outputs:
                    module = module_provider.find_module_by_fingerprint(fingerprint)

                if module is None:
                    new_module = True
                else:
                    new_module = False
                    module_id = module.id

                if dry_run:
                    if new_module:
                        print("Step %s is ready to be created [%s]"
                              % (node.name, node.node_id))
                    result[node.node_id] = (module_id, new_module)
                    continue

                if new_module:
                    module_id = module_builder.build()
                    print("Created step %s [%s][%s], (This step will run and generate new outputs)"
                          % (node.name, node.node_id, module_id, ))
                else:
                    if module.module_def.allow_reuse:
                        print("Created step %s [%s][%s], (This step is eligible to reuse a previous run's output)"
                              % (node.name, node.node_id, module_id,))
                    else:
                        print("Created step %s [%s][%s], (This step will run and generate new outputs)"
                              % (node.name, node.node_id, module_id,))

                if module is None:
                    module = module_provider.download(module_id)

                # update node
                node._module = module
                result[node.node_id] = (module_id, new_module)

        datasource_provider = self._context.workflow_provider.datasource_provider
        for node in self.datasource_nodes:
            if node._datasource is None:
                datasource_builder = node._datasource_builder

                # Check if this datasource already exists
                fingerprint = datasource_builder.get_fingerprint()
                datasource_id = None
                datasource = None
                if not regenerate_outputs:
                    datasource = datasource_provider.find_datasource_by_fingerprint(fingerprint)

                if datasource is None:
                    new_datasource = True
                else:
                    new_datasource = False
                    datasource_id = datasource.id

                if dry_run:
                    if new_datasource:
                        print("Data reference %s is ready to be created [%s], "
                              "(Consumers of this data will generate new runs.)" % (node.name, node.node_id))
                    result[node.node_id] = (datasource_id, new_datasource)
                    continue

                if new_datasource:
                    datasource_id = datasource_builder.build()
                    print("Created data reference %s for StepId [%s][%s], "
                          "(Consumers of this data will generate new runs.)"
                          % (node.name, node.node_id, datasource_id))
                else:
                    print("Using data reference %s for StepId [%s][%s], "
                          "(Consumers of this data are eligible to reuse prior runs.)"
                          % (node.name, node.node_id, datasource.id))

                if datasource is None:
                    datasource = datasource_provider.download(datasource_id)

                # update node
                node._datasource = datasource
                result[node.node_id] = (datasource_id, new_datasource)

        if not dry_run:
            self._finalized = True

        return result

    def _validate_pipeline_params(self, pipeline_params):
        if pipeline_params is not None:
            for param_name, value in pipeline_params.items():
                if param_name not in self._params:
                    raise Exception("Pipeline parameter with name {0} does not exist".format(param_name))

    def submit(self, pipeline_parameters=None, continue_on_step_failure=False, regenerate_outputs=False,
               parent_run_id=None):
        """
        Submit the graph to run in the cloud.

        :param pipeline_parameters: Parameters to pipeline execution
        :type pipeline_parameters: dict
        :param continue_on_step_failure: Flag to let the experiment continue executing if one step fails
        :type continue_on_step_failure: bool
        :param regenerate_outputs: set to True to force a new run (disallows module/datasource reuse)
        :type regenerate_outputs: bool
        :param parent_run_id: The parent pipeline run id,
         optional
        :type parent_run_id: str

        :return: a PipelineRun
        :rtype: azureml.pipeline.core.PipelineRun
        """
        self._validate_and_finalize(pipeline_parameters=pipeline_parameters, regenerate_outputs=regenerate_outputs)

        pipeline_run_id = self._graph_provider.submit(self, pipeline_parameters=pipeline_parameters,
                                                      continue_on_step_failure=continue_on_step_failure,
                                                      experiment_name=self._context._experiment_name,
                                                      parent_run_id=parent_run_id)
        pipeline_run = PipelineRun(experiment=self._context._experiment, run_id=pipeline_run_id,
                                   _service_endpoint=self._context.workflow_provider._service_caller._service_endpoint)

        return pipeline_run

    def _save(self, name=None, description=None, version=None, regenerate_outputs=False,
              continue_on_step_failure=None):
        """
        Save the graph as a published pipeline in the cloud.

        :param name: Name of the published pipeline.
        :type name: str
        :param description: Description of the published pipeline.
        :type description: str
        :param version: Version of the published pipeline.
        :type version: str
        :param regenerate_outputs: set to True to force a new run (disallows module/datasource reuse)
        :type regenerate_outputs: bool
        :param continue_on_step_failure: Whether to continue execution of other steps if a step fails, optional.
        :type continue_on_step_failure: bool

        :return: Created published pipeline.
        :rtype: azureml.pipeline.core.PublishedPipeline
        """
        self._validate_and_finalize(pipeline_parameters=None, regenerate_outputs=regenerate_outputs)

        return self._context.workflow_provider.published_pipeline_provider.create_from_graph(
            name=name, description=description, version=version, graph=self,
            continue_run_on_step_failure=continue_on_step_failure)

    def _validate_and_finalize(self, pipeline_parameters, regenerate_outputs):
        """
        Prepare the graph for submission.  Validate the parameters and finalize the constructed graph.

        :param pipeline_parameters: Parameters to pipeline execution
        :type pipeline_parameters: dict
        :param regenerate_outputs: set to True to force a new run (disallows module/datasource reuse)
        :type regenerate_outputs: bool
        """
        self._validate_pipeline_params(pipeline_parameters)

        if not self._finalized:
            self.finalize(dry_run=False, regenerate_outputs=regenerate_outputs)

    def _generate_node_id(self):
        """
        Generate an 8-character node Id.

        :return: node_id
        :rtype: str
        """
        guid = str(uuid.uuid4())
        while guid[0:8] in self._nodes:
            guid = str(uuid.uuid4())

        return guid[0:8]

    def validate(self):
        """
        Validate graph. Returns a list of errors.

        :return: List errors.
        :rtype: :class:`list`
        """
        errors = []
        try:
            for node_id in self._nodes:
                node = self._nodes[node_id]
                if node is None:
                    errors.append("[%s] MissingNode" % node_id)
                    continue

                if not isinstance(node, Node):
                    errors.append("[%s] UnexpectedType (%s) " % (node_id, type(node)))
                    continue

                for param_name in node._params:
                    param = node.get_param(param_name)
                    if param.param_def is None:
                        errors.append("[%s][%s] MissingParamDef" % (node_id, param_name))

                for output_name in node._outputs:
                    output = node.get_output(output_name)
                    if output._output_port_def is None:
                        errors.append("[%s][%s] MissingOutputDef" % (node_id, output_name))

            for edge in self.edges:
                valid_source = False
                source = "Missing"
                if edge.source_port is not None:
                    source = "UnexpectedType (%s)" % type(edge.source_port)
                    if isinstance(edge.source_port, OutputPort):
                        source = "MissingNode"
                        if edge.source_port.node is not None:
                            source = "Node UnexpectedType (%s)" % type(edge.source_port.node)
                            if isinstance(edge.source_port.node, Node):
                                source = "UnknownNode (%s)" % edge.source_port.node.node_id
                                if edge.source_port.node.node_id in self._nodes:
                                    source = "Missing PortDef (%s)" % edge.source_port.node.node_id
                                    if edge.source_port._output_port_def is not None:
                                        source = "%s (%s)" % (edge.source_port.name, edge.source_port.node.node_id)
                                        valid_source = True

                valid_dest = False
                dest = "Missing"
                if edge.dest_port is not None:
                    dest = "UnexpectedType (%s)" % type(edge.dest_port)
                    if isinstance(edge.dest_port, InputPort):
                        dest = "MissingNode"
                        if edge.dest_port.node is not None:
                            dest = "Node UnexpectedType (%s)" % type(edge.dest_port.node)
                            if isinstance(edge.dest_port.node, Node):
                                source = "UnknownNode (%s)" % edge.dest_port.node.node_id
                                if edge.dest_port.node.node_id in self._nodes:
                                    source = "Missing PortDef (%s)" % edge.dest_port.node.node_id
                                    if edge.dest_port._input_port_def is not None:
                                        dest = "%s (%s)" % (edge.dest_port.name, edge.dest_port.node.node_id)
                                        valid_dest = True

                if not valid_source or not valid_dest:
                    errors.append("Edge src[%s] dst[%s]" % (source, dest))

            cycle_result = self._validate_cycles()
            if cycle_result is not None:
                errors.append(cycle_result)
        except Exception as e:
            import traceback
            errors.append("Exception" + str(e))
            errors.append(traceback.format_exc())

        if len(errors) == 0:
            self.finalize(dry_run=True)

        return errors

    def _validate_cycles(self):
        """
        Check for cycles in the graph.  Returns an error message if there is a cycle.

        :return: Error message if a cycle was found, otherwise None
        :rtype: str
        """
        node_colors = {}
        for node_id in self.node_dict:
            node_colors[node_id] = _NodeColors.WHITE
        for node_id in self.node_dict:
            if node_colors[node_id] == _NodeColors.WHITE:
                result = self._validate_cycles_from_node(self.get_node(node_id), node_colors)
                if result is not None:
                    return result
        return None

    def _validate_cycles_from_node(self, node, node_colors):
        """
        Do a depth-first search starting from the given node to check for cycles.

        :param node: Starting node to search from
        :type node: Node
        :param node_colors: Node status per node ID (white - not visited yet, gray - in progress, black - completed)
        :type node_colors: dict
        :return: Error message if a cycle was found, otherwise None
        :rtype: str
        """
        node_colors[node.node_id] = _NodeColors.GRAY
        for input in node.inputs:
            neighbor = input.incoming_edge.source_port.node
            if node_colors[neighbor.node_id] == _NodeColors.GRAY:
                return "Cycle detected including node %s(%s)" % (node.name, node.node_id)
            if node_colors[neighbor.node_id] == _NodeColors.WHITE:
                result = self._validate_cycles_from_node(neighbor, node_colors)
                if result is not None:
                    return result
        node_colors[node.node_id] = _NodeColors.BLACK
        return None


class _PipelineIO(object):
    def __init__(self, datapath=None, datapath_param=None, datapath_compute_binding=None, name=None):
        self._datapath = datapath
        self._datapath_param = datapath_param
        self._datapath_compute_binding = datapath_compute_binding

        if not name:
            if self._datapath:
                self._name = self._datapath._name
            else:
                self._name = self._datapath_param.default_value._name
        else:
            self._name = name

        # used in the case of output in the pipeline
        self._producer = None

    def _set_producer(self, step):
        self._producer = step

    def __str__(self):
        """
        __str__ override.

        :return: str representation of the _PipelineIO
        :rtype: str
        """
        return "$AZUREML_DATAREFERENCE_{0}".format(self.name)

    def __repr__(self):
        """
        Return __str__.

        :return: str representation of the _PipelineIO
        :rtype: str
        """
        return self.__str__()

    @property
    def name(self):
        return self._name

    @property
    def datapath(self):
        if self._datapath:
            return self._datapath
        else:
            return self._datapath_param

    @property
    def datapath_param_name(self):
        if not self._datapath_param:
            return None
        else:
            return self._datapath_param.name

    @staticmethod
    def _validate(pipeline_io_tuple):
        if not len(pipeline_io_tuple) == 2:
            raise ValueError('Length of the tuple must be 2')

        if not isinstance(pipeline_io_tuple[0], DataPath) and not isinstance(pipeline_io_tuple[0], PipelineParameter):
            raise ValueError('First item in the tuple should be a DataPath or PipelineParameter')

        if not isinstance(pipeline_io_tuple[1], DataPathComputeBinding):
            raise ValueError('Second item in the tuple should be DataPathComputeBinding')

        if isinstance(pipeline_io_tuple[0], PipelineParameter):
            if not isinstance(pipeline_io_tuple[0].default_value, DataPath):
                raise ValueError('Default value for the PipelineParameter should be DataPath')

    @staticmethod
    def create(pipeline_io_tuple):
        _PipelineIO._validate(pipeline_io_tuple)

        if isinstance(pipeline_io_tuple[0], PipelineParameter):
            return _PipelineIO(datapath_param=pipeline_io_tuple[0],
                               datapath_compute_binding=pipeline_io_tuple[1])
        else:
            return _PipelineIO(datapath=pipeline_io_tuple[0], datapath_compute_binding=pipeline_io_tuple[1])

    def as_pipeline_parameter(self):
        if self._datapath_param:
            return self._datapath_param
        else:
            return None

    def as_input_port_binding(self):
        return InputPortBinding(name=self.name,
                                bind_object=self,
                                bind_mode=self._datapath_compute_binding._mode,
                                path_on_compute=self._datapath_compute_binding._path_on_compute,
                                overwrite=self._datapath_compute_binding._overwrite)

    def as_input(self):
        return self._create_data_reference()

    def as_output(self):
        return self._create_pipeline_data()

    def _create_data_reference(self):
        dpath = self._datapath

        if self._datapath_param:
            dpath = self._datapath_param.default_value

        return dpath.create_data_reference(data_reference_name=self.name,
                                           datapath_compute_binding=self._datapath_compute_binding)

    def _create_pipeline_data(self):
        from azureml.pipeline.core.builder import PipelineData
        return PipelineData(name=self._datapath._name,
                            datastore=self._datapath._datastore,
                            output_mode=self._datapath_compute_binding._mode,
                            output_path_on_compute=self._datapath_compute_binding._path_on_compute,
                            output_overwrite=self._datapath_compute_binding._overwrite)


class PipelineDataset(object):
    """
    Models data associated with an input of a StepRun that comes from a :class:`azureml.core.Dataset`.

    By default, the name of the dataset, the definition version, and the snapshot name (if snapshot is used)
    will be used as the name for the input. You can override the name with this class.

    .. remarks::

        Use PipelineDataset when constructing a :class:`azureml.pipeline.core.Pipeline` to specify that
        the input of a step is a Dataset.

        An example to use a PipelineDataset as a step input is as follows:

        .. code-block:: python

            from azureml.core import Dataset
            from azureml.pipeline.core import Pipeline
            from azureml.pipeline.steps import PythonScriptStep

            dataset = Dataset.get(ws, "<dataset_name>")

            step = PythonScriptStep(
                name='train step',
                script_name="train.py",
                compute_target=compute,
                arguments=["--input", dataset],
                inputs=[dataset]
            )

            pipeline = Pipeline(workspace=ws, steps=[step_1])

    :param dataset: The dataset that will be used as the input to the step.
    :type dataset: azureml.core.Dataset or azureml.data.dataset_definition.DatasetDefinition
    :param name: The name of the input in the pipeline.
    :type name: str
    :param bind_mode: How the dataset should be made available, either mount or download.
    :type bind_mode: str
    :param path_on_compute: The path on the compute where the data will be made available.
    :type path_on_compute: str
    :param overwrite: Whether to overwrite existing data or not.
    :type overwrite: bool
    :param parameter_name: The parameter name of the dataset. This is used for published pipeline.
    :type parameter_name: str
    """

    def __init__(self, dataset=None, name=None, bind_mode="mount", path_on_compute=None, overwrite=False,
                 parameter_name=None):
        """
        Initialize a PipelineDataset.

        :param dataset: The dataset that will be used as the input to the step.
        :type dataset: azureml.core.Dataset or azureml.data.dataset_definition.DatasetDefinition
        :param name: The name of the input in the pipeline.
        :type name: str
        :param bind_mode: How the dataset should be made available, either mount or download.
        :type bind_mode: str
        :param path_on_compute: The path on the compute where the data will be made available.
        :type path_on_compute: str
        :param overwrite: Whether to overwrite existing data or not.
        :type overwrite: bool
        """
        self._dataset = dataset
        self._name = name
        self._bind_mode = bind_mode
        self._path_on_compute = path_on_compute
        self._overwrite = overwrite
        self._parameter_name = parameter_name

        if self._dataset and not self._name:
            self._name = PipelineDataset.default_name(self._dataset)

    @property
    def dataset(self):
        """
        Get the dataset this input is binded to.

        :return: The dataset.
        :rtype: azureml.core.Dataset or azureml.data.dataset_definition.DatasetDefinition
        """
        return self._dataset

    @property
    def dataset_id(self):
        """
        Get the dataset ID.

        :return: The dataset ID.
        :rtype: str
        """
        if isinstance(self._dataset, Dataset):
            return self._dataset.id
        if isinstance(self._dataset, DatasetDefinition):
            return self._dataset._dataset_id
        raise ValueError('Expecting a Dataset or DatasetDefinition, but got {} instead'.format(type(self._dataset)))

    @property
    def dataset_version(self):
        """
        Get the dataset definition's version.

        :return: The dataset version.
        :rtype: str
        """
        if isinstance(self._dataset, Dataset):
            return self._dataset.definition_version
        if isinstance(self._dataset, DatasetDefinition):
            return self._dataset._version_id
        raise ValueError('Expecting a Dataset or DatasetDefinition, but got {} instead'.format(type(self._dataset)))

    @property
    def name(self):
        """
        Get the name of the input.

        :return: The name.
        :rtype: str
        """
        return self._name

    @property
    def workspace(self):
        """
        Get the workspace the dataset belongs to.

        :return: The workspace.
        :rtype: azureml.core.Workspace
        """
        if isinstance(self._dataset, Dataset):
            return self._dataset.workspace
        if isinstance(self._dataset, DatasetDefinition):
            return self._dataset._workspace
        raise ValueError('Expecting a Dataset or DatasetDefinition, but got {} instead'.format(type(self._dataset)))

    @property
    def bind_mode(self):
        """
        Get how the dataset should be made available.

        :return: The bind mode.
        :rtype: str
        """
        return self._bind_mode

    @property
    def path_on_compute(self):
        """
        Get the path where the data will be made available on the compute.

        :return: The path on compute.
        :rtype: str
        """
        return self._path_on_compute

    @property
    def overwrite(self):
        """
        Get value indicating whether to overwrite existing data.

        :return: Overwrite or not.
        :rtype: bool
        """
        return self._overwrite

    @property
    def parameter_name(self):
        """
        Get the pipeline parameter name of this pipeline dataset.

        :return: The parameter name.
        :rtype: str
        """
        return self._parameter_name

    @property
    def _hashable_content(self):
        return [self.name or PipelineDataset.default_name(self.dataset), self.bind_mode,
                self.path_on_compute, str(self.overwrite)]

    @property
    def _data_type_short_name(self):
        from azureml.core import Datastore

        dataset = self.dataset
        if isinstance(dataset, Dataset):
            dataset = dataset.definition
        datapath = dataset._get_datapath()
        ds_name = datapath.datastore_name
        datastore = Datastore(self.workspace, ds_name)
        # TODO: This is a temporary workaround and should be moved to the aether service
        return {
            'AzureBlob': 'AzureBlobReference',
            'AzureFile': 'AzureFilesReference',
            'AzureDataLake': 'AzureDataLakeReference',
            'AzureSqlDatabase': 'AzureSqlDatabaseReference',
            'AzurePostgreSql': 'AzurePostgresDatabaseReference',
            'AzureDataLakeGen2': 'AzureDataLakeGen2Reference'
        }[datastore.datastore_type]

    @staticmethod
    def default_name(dataset):
        """
        Get the default port name of a dataset/dataset definition.

        :param dataset: The dataset to calculate the name from.
        :type dataset: object
        :return: The name.
        :rtype: str
        """
        def sanitize(value):
            return re.sub(r'[^a-zA-Z0-9_]', '_', value)

        name = None
        if isinstance(dataset, Dataset):
            name = "{}_{}".format(dataset.name, dataset.definition_version)
        elif isinstance(dataset, DatasetDefinition):
            name = "{}_{}".format(dataset._dataset_id, dataset._version_id)
        else:
            raise ValueError("Invalid input type. Type of input: {}".format(type(dataset)))
        return sanitize(name)

    @staticmethod
    def is_dataset(dset):
        """
        Determine whether the input is a dataset or a dataset definition.

        :param dset: The input.
        :type dset: object
        :return: Whether input is a dataset or a dataset definition.
        :rtype: bool
        """
        return isinstance(dset, Dataset) or isinstance(dset, DatasetDefinition)

    @staticmethod
    def validate_dataset(dset):
        """
        Validate the state of the dataset.

        It will log a warning if the dataset is deprecated and throws an error if the datasaet is archived.

        :param dset: The dataset to be verified.
        :type dset: azureml.core.Dataset or azureml.data.dataset_definition.DatasetDefinition
        """
        if isinstance(dset, PipelineDataset):
            dset = dset.dataset
        if isinstance(dset, Dataset):
            if dset.state == "deprecated":
                module_logger.warning("Warning: dataset '{}' is deprecated.".format(dset.name))
            if dset.state == "Archived":
                message = "Error: dataset '{}' is archived and cannot be used.".format(dset.name)
                module_logger.error(message)
                raise ValueError(message)
        if isinstance(dset, DatasetDefinition):
            if dset._state == "Deprecated":
                message = "Warning: this definition is deprecated."
                dataset_and_version = ""
                if dset._deprecated_by_dataset_id:
                    dataset_and_version += "Dataset ID: {} ".format(dset._deprecated_by_dataset_id)
                if dset._deprecated_by_definition_version:
                    dataset_and_version += "Definition version: {}".format(dset._deprecated_by_definition_version)
                if dataset_and_version:
                    message += " Please use {} instead.".format(dataset_and_version.strip(" "))
                module_logger.warning(message)
            if dset._state == "Archived":
                message = "Error: definition version '{}' is archived and cannot be used".format(dset._version_id)
                module_logger.error(message)
                raise ValueError(message)

    def __str__(self):
        """
        Get the string representation of the PipelineDataset.

        This will actually be the environment variable name once this PipelineDataset is made available on the
        remote compute.

        :return: The string representation.
        :rtype: str
        """
        if not self.name:
            raise ValueError("PipelineDataset does not have a name.")
        return "$AZUREML_DATAREFERENCE_{0}".format(self.name)


class PortDataReference(object):
    """
    Models data associated with an output of a completed StepRun.

    A PortDataReference object can be used to download the output data which was produced by a
    :class:`azureml.pipeline.core.StepRun`. It can also be used as an step input in a future Pipeline.

    .. remarks::

        A PortDataReference points to data which was produced by a completed :class:`azureml.pipeline.core.StepRun`.

        Get a PortDataReference from a :class:`azureml.pipeline.core.PipelineRun` and download the output data
        as follows:

        .. code-block:: python

            from azureml.pipeline.core import PipelineRun, StepRun, PortDataReference

            pipeline_run = PipelineRun(experiment, "<pipeline_run_id>")
            step_run = pipeline_run.find_step_run("<node_name>")[0]
            port_data_reference = step_run.get_output_data("<output_name>")
            port_data_reference.download(local_path="path")

        A PortDataReference can be used as an input to a step in a :class:`azureml.pipeline.core.Pipeline`,
        similar to using a :class:`azureml.data.data_reference.DataReference`.

        An example to using a PortDataReference as a step input is as follows:

        .. code-block:: python

            from azureml.pipeline.core import PortDataReference, Pipeline, PipelineRun
            from azureml.pipeline.steps import PythonScriptStep

            pipeline_run = PipelineRun(experiment, "<pipeline_run_id>")
            step_run = pipeline_run.find_step_run("<node_name>")[0]
            port_data_reference = step_run.get_output_data("<output_name>")

            step_1 = PythonScriptStep(
                name='train',
                script_name="train.py",
                compute_target=compute,
                arguments=["--input", port_data_reference],
                inputs=[port_data_reference]
            )

            pipeline = Pipeline(workspace=workspace, steps=[step_1])

        In this example, the newly constructed Pipeline will use the output which was created by the completed
        PipelineRun as an input to the train step.


    :param context: The graph context object.
    :type context: _GraphContext
    :param pipeline_run_id: The id of the pipeline run which produced the output.
    :type pipeline_run_id: str
    :param data_reference: The data reference object.
    :type data_reference: azureml.data.data_reference.DataReference
    :param step_run: The StepRun object which produced the data.
    :type step_run: azureml.pipeline.run.StepRun
    """

    # TODO - should data_ref be replaced with datapath?
    def __init__(self, context, pipeline_run_id, data_reference, step_run=None):
        """
        Initialize PortDataReference.

        :param context: The graph context object.
        :type context: _GraphContext
        :param pipeline_run_id: The id of the pipeline run which produced the output.
        :type pipeline_run_id: str
        :param data_reference: The data reference object.
        :type data_reference: azureml.data.data_reference.DataReference
        :param step_run: The StepRun object which produced the data.
        :type step_run: azureml.pipeline.run.StepRun
        """
        self.data_reference_name = data_reference.data_reference_name
        self._path_on_datastore = data_reference.path_on_datastore
        self.pipeline_run_id = pipeline_run_id
        self._data_reference = data_reference
        self._context = context
        self._experiment = context._experiment
        self._step_run = step_run

    @property
    def datastore(self):
        """
        Get the Datastore associated with the PortDataReference.

        :return: The datastore object.
        :rtype: azureml.core.Datastore
        """
        return self._data_reference.datastore

    @property
    def datastore_name(self):
        """
        Get the name of the Datastore associated with the PortDataReference.

        :return: The datastore name.
        :rtype: str
        """
        return self.datastore.name

    @property
    def path_on_datastore(self):
        """
        Get the path on datastore for the PortDataReference.

        :return: The path on datastore.
        :rtype: str
        """
        return self._path_on_datastore

    def download(self, local_path, overwrite=None, show_progress=None):
        """
        Download the data represented by the PortDataReference.

        :param local_path: Local path to download to.
        :type local_path: str
        :param overwrite: If true, overwrite existing file, defaults to False.
        :type overwrite: bool, optional
        :param show_progress: Show the progress of download in the console, defaults to True.
        :type show_progress: bool, optional

        :return: The number of files successfully downloaded.
        :rtype: int
        """
        return self._context.workflow_provider.port_data_reference_provider.download(
            datastore_name=self.datastore_name,
            path_on_datastore=self._path_on_datastore,
            local_path=local_path,
            overwrite=overwrite,
            show_progress=show_progress)

    def as_download(self, input_name=None, path_on_compute=None, overwrite=None):
        """
        Consume the PortDataReference as a step input through the "download" mode.

        :param input_name: Specify a name for this input.
        :type input_name: str
        :param path_on_compute: The path on the compute to download the data to.
        :type path_on_compute: str
        :param overwrite: Use to indicate whether to overwrite existing data.
        :type overwrite: bool

        :return: The InputPortBinding with this PortDataReference as the source.
        :rtype: azureml.pipeline.core.graph.InputPortBinding
        """
        return self.create_input_binding(input_name=input_name, mode="download", path_on_compute=path_on_compute,
                                         overwrite=overwrite)

    def as_mount(self, input_name=None):
        """
        Consume the PortDataReference as a step input through the "mount" mode.

        :param input_name: Use to specify a name for this input.
        :type input_name: str

        :return: The InputPortBinding with this PortDataReference as the source.
        :rtype: azureml.pipeline.core.graph.InputPortBinding
        """
        return self.create_input_binding(input_name=input_name, mode="mount")

    def as_input(self, input_name):
        """
        Create an InputPortBinding and specify an input name (but use default mode).

        :param input_name: Use to specify a name for this input.
        :type input_name: str

        :return: The InputPortBinding with this PortDataReference as the source.
        :rtype: azureml.pipeline.core.graph.InputPortBinding
        """
        return self.create_input_binding(input_name=input_name)

    def create_input_binding(self, input_name=None, mode=None, path_on_compute=None, overwrite=None):
        """
        Create input binding with this PortDataReference as the source.

        :param input_name: The name of the input.
        :type input_name: str
        :param mode: The mode to access the PortDataReference ("mount" or "download").
        :type mode: str
        :param path_on_compute: For "download" mode, the path on the compute the data will reside.
        :type path_on_compute: str
        :param overwrite: For "download" mode, whether to overwrite existing data.
        :type overwrite: bool

        :return: The InputPortBinding with this PortDataReference as the source.
        :rtype: azureml.pipeline.core.graph.InputPortBinding
        """
        if input_name is None:
            input_name = self.data_reference_name

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

    def __str__(self):
        """
        __str__ override.

        :return: str representation of the PortDataReference
        :rtype: str
        """
        result = "$AZUREML_DATAREFERENCE_{0}".format(self.data_reference_name)
        return result

    def __repr__(self):
        """
        Return __str__.

        :return: str representation of the PortDataReference
        :rtype: str
        """
        return self.__str__()

    def _repr_html_(self):
        info = self._get_base_info_dict()
        return to_html(info)

    def _get_base_info_dict(self):
        pipeline_run = PipelineRun(self._experiment, self.pipeline_run_id)

        info = OrderedDict([
            ('Name', self.data_reference_name),
            ('Datastore', self.datastore_name),
            ('Path on Datastore', self._path_on_datastore),
            ('Produced By PipelineRun', make_link(pipeline_run.get_portal_url(), self.pipeline_run_id))
        ])

        if self._step_run is not None:
            info.update([('Produced By StepRun', make_link(self._step_run.get_portal_url(), self._step_run.id))])

        return info


def _submit_published_pipeline(published_pipeline, workspace, experiment_name, **kwargs):
    """
    Submit a published pipeline.

    :param published_pipeline: published pipeline to submit
    :type published_pipeline: PublishedPipeline
    :param workspace: workspace
    :type workspace: Workspace
    :param experiment_name: experiment name
    :type experiment_name: str
    :param kwargs: kwargs
    :type kwargs: dict

    :return: PipelineRun object
    :rtype: PipelineRun
    """
    pipeline_parameters = None
    parent_run_id = None
    continue_on_step_failure = None
    for key, value in kwargs.items():
        if key == 'pipeline_parameters':
            pipeline_parameters = value
        elif key == 'parent_run_id':
            parent_run_id = value
        elif key == 'continue_on_step_failure':
            continue_on_step_failure = value

    return published_pipeline.submit(workspace=workspace, experiment_name=experiment_name,
                                     pipeline_parameters=pipeline_parameters, parent_run_id=parent_run_id,
                                     continue_on_step_failure=continue_on_step_failure)


class PublishedPipeline(HasPipelinePortal):
    """
    A PublishedPipeline enables a Pipeline to be submitted without the Python code which constructed it.

    In addition, a PublishedPipeline can be used to resubmit a Pipeline with different
    :class:`azureml.pipeline.core.PipelineParameter` values and inputs.

    .. remarks::

        A PublishedPipeline can be created from either a :class:`azureml.pipeline.core.Pipeline`
        or a :class:`azureml.pipeline.core.PipelineRun`.

        An example to publish from a Pipeline is as follows:

        .. code-block:: python

            from azureml.pipeline.core import Pipeline

            pipeline = Pipeline(workspace=ws, steps=steps)
            published_pipeline = pipeline.publish(name="My_New_Pipeline",
                                                  description="My New Pipeline Description",
                                                  version="1.0",
                                                  continue_on_step_failure=True)

        To publish from a PipelineRun use:

        .. code-block:: python

            from azureml.pipeline.core import PipelineRun

            pipeline_run = PipelineRun(experiment=Experiment(ws, "Pipeline_experiment"), run_id="run_id")
            published_pipeline = pipeline_run.publish_pipeline(name="My_New_Pipeline",
                                                               description="My New Pipeline Description",
                                                               version="1.0",
                                                               continue_on_step_failure=True)

        Note: the continue_on_step_failure parameter specifies whether the execution of steps in the Pipeline will
        continue if one step fails. The default value is False, meaning when one step fails, the Pipeline execution
        will stop, canceling any running steps.

        Submit a PublishedPipeline using :func:`azureml.core.Experiment.submit`. When submit is called,
        a :class:`azureml.pipeline.core.PipelineRun` is created which in turn creates
        :class:`azureml.pipeline.core.StepRun` objects for each step in the workflow.

        An example to submit a PublishedPipeline is as follows:

        .. code-block:: python

            from azureml.pipeline.core import PublishedPipeline

            published_pipeline = PublishedPipeline.get(workspace=ws, id="published_pipeline_id")
            pipeline_run = experiment.submit(published_pipeline)

        There are a number of optional settings that can be specified when submitting a PublishedPipeline.
        These include:

        *  continue_on_step_failure: Whether to continue execution of other steps in the PipelineRun
                                     if a step fails, optional. If provided, will override the setting on the
                                     Pipeline.
        *  pipeline_parameters: Parameters to pipeline execution, dictionary of {name: value}.
                                See :class:`azureml.pipeline.core.PipelineParameter` for more details.
        *  parent_run_id: You can supply the run id to set the parent run of this pipeline run.

        An example to submit a PublishedPipeline using these settings is as follows:

        .. code-block:: python

            from azureml.pipeline.core import PublishedPipeline

            published_pipeline = PublishedPipeline.get(workspace=ws, id="published_pipeline_id")
            pipeline_run = experiment.submit(published_pipeline,
                                             continue_on_step_failure=True,
                                             pipeline_parameters={"param1": "value1"},
                                             parent_run_id="<run_id>")

    :param name: The name of the published pipeline.
    :type name: str
    :param graph_id: The id of the graph for this published pipeline
    :type graph_id: str
    :param description: The description of the published pipeline.
    :type description: str
    :param version: The published pipeline version.
    :type version: str
    :param published_pipeline_id: The id of the published pipeline.
    :type published_pipeline_id: str
    :param status: Status of the published pipeline ('Active' or 'Disabled')
    :type status: str
    :param total_run_steps: Number of steps in this pipeline
    :type total_run_steps: int
    :param workspace: The Workspace of the published pipeline.
    :type workspace: azureml.core.Workspace
    :param continue_on_step_failure: Whether to continue execution of other steps in the PipelineRun
                                     if a step fails, default is false.
    :type continue_on_step_failure: bool
    :param _pipeline_provider: The published pipeline provider.
    :type _pipeline_provider: _PublishedPipelineProvider
    """

    @experiment_method(submit_function=_submit_published_pipeline)
    def __init__(self, name, graph_id, description, version, published_pipeline_id, status, endpoint,
                 total_run_steps, workspace, continue_on_step_failure=None, _pipeline_provider=None):
        """
        Initialize Published Pipeline.

        :param name: The name of the published pipeline.
        :type name: str
        :param graph_id: The id of the graph for this published pipeline
        :type graph_id: str
        :param description: The description of the published pipeline.
        :type description: str
        :param version: The published pipeline version.
        :type version: str
        :param published_pipeline_id: The id of the published pipeline.
        :type published_pipeline_id: str
        :param status: Status of the published pipeline ('Active' or 'Disabled')
        :type status: str
        :param endpoint REST endpoint URL to submit pipeline runs for this pipeline
        :type endpoint: str
        :param total_run_steps: Number of steps in this pipeline
        :type total_run_steps: int
        :param workspace: The Workspace of the published pipeline.
        :type workspace: azureml.core.Workspace
        :param continue_on_step_failure: Whether to continue execution of other steps in the PipelineRun
                                         if a step fails, default is false.
        :type continue_on_step_failure: bool
        :param _pipeline_provider: The published pipeline provider.
        :type _pipeline_provider: _PublishedPipelineProvider
        """
        self._name = name
        self._description = description
        self._version = version
        self._graph_id = graph_id
        self._published_pipeline_id = published_pipeline_id
        self._status = status
        self._endpoint = endpoint
        self._total_run_steps = total_run_steps
        self._pipeline_provider = _pipeline_provider
        self._continue_on_step_failure = continue_on_step_failure
        self.workspace = workspace

        super(self.__class__, self).__init__(pipeline=self)

    @property
    def name(self):
        """
        Name of the published pipeline.

        :return: The published pipeline name.
        :rtype: str
        """
        return self._name

    @property
    def description(self):
        """
        Get the description of the published pipeline.

        :return: The description string.
        :rtype: str
        """
        return self._description

    @property
    def id(self):
        """
        Get the Published pipeline id.

        :return: The id of the published pipeline.
        :rtype: str
        """
        return self._published_pipeline_id

    @property
    def graph_id(self):
        """
        Get the id of the graph for this published pipeline.

        :return: The id of the graph.
        :rtype: str
        """
        return self._graph_id

    @property
    def version(self):
        """
        Version of the published pipeline.

        :return: The version.
        :rtype: str
        """
        return self._version

    @property
    def status(self):
        """
        Status of the published pipeline.

        :return: The status.
        :rtype: str
        """
        return self._status

    @property
    def endpoint(self):
        """
        Get REST endpoint url for running a published pipeline.

        :return: REST endpoint for running the published pipeline
        :rtype: str
        """
        return self._endpoint

    @property
    def total_run_steps(self):
        """
        Get the number of steps in this pipeline.

        :return: Number of steps
        :rtype: int
        """
        return self._total_run_steps

    @property
    def continue_on_step_failure(self):
        """
        Get the value of the continue_on_step_failure setting.

        :return: The value of the continue_on_step_failure setting
        :rtype: bool
        """
        return self._continue_on_step_failure

    def submit(self, workspace, experiment_name, pipeline_parameters=None, _workflow_provider=None,
               _service_endpoint=None, parent_run_id=None, continue_on_step_failure=None):
        """
        Submit the published pipeline. This is equivalent to using :func:`azureml.core.Experiment.submit`.

        Returns the submitted :class:`azureml.pipeline.core.PipelineRun`. Use this object to monitor and
        view details of the run.

        :param workspace: The workspace to submit the published pipeline on.
        :type workspace: azureml.core.Workspace
        :param experiment_name: The name of the experiment to submit to.
        :type experiment_name: str
        :param pipeline_parameters: Dictionary of parameters to assign new values {param name, param value}.
                                    See :class:`azureml.pipeline.core.PipelineParameter` for more details.
        :type pipeline_parameters: dict
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str
        :param parent_run_id: The parent pipeline run id,
         optional
        :type parent_run_id: str
        :param continue_on_step_failure: Whether to continue execution of other steps in the PipelineRun
                                         if a step fails, optional. If provided, will override the setting on the
                                         Pipeline.
        :type continue_on_step_failure: bool

        :return: The submitted pipeline run.
        :rtype: azureml.pipeline.core.PipelineRun
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        context = _GraphContext(experiment_name, workspace,
                                workflow_provider=_workflow_provider,
                                service_endpoint=_service_endpoint)

        pipeline_run_id = context.workflow_provider.published_pipeline_provider.submit(
            published_pipeline_id=self._published_pipeline_id, experiment_name=experiment_name,
            parameter_assignment=pipeline_parameters, parent_run_id=parent_run_id,
            continue_run_on_step_failure=continue_on_step_failure)

        pipeline_run = PipelineRun(experiment=context._experiment, run_id=pipeline_run_id,
                                   _service_endpoint=context.workflow_provider._service_caller._service_endpoint)
        return pipeline_run

    @staticmethod
    def get(workspace, id, _workflow_provider=None, _service_endpoint=None):
        """
        Get the published pipeline.

        :param workspace: The workspace the published pipeline was created on.
        :type workspace: azureml.core.Workspace
        :param id: Id of the published pipeline.
        :type id: str
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str

        :return: PublishedPipeline object
        :rtype: azureml.pipeline.core.graph.PublishedPipeline
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider,
                                      service_endpoint=_service_endpoint)
        return graph_context.workflow_provider.published_pipeline_provider.get_published_pipeline(
            published_pipeline_id=id)

    @staticmethod
    def get_all(workspace, active_only=True, _service_endpoint=None):
        """
        Get all published pipelines in the current workspace.

        NOTE: This method is being deprecated in favor of PublishedPipeline.list()

        :param workspace: The workspace the published pipeline was created on.
        :type workspace: azureml.core.Workspace
        :param active_only: If true, only return published pipelines which are currently active.
        :type active_only: Bool
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str

        :return: a list of :class:`azureml.pipeline.core.graph.PublishedPipeline`
        :rtype: :class:`list`
        """
        logging.warning("PublishedPipeline.get_all(workspace) is being deprecated. "
                        "Use PublishedPipeline.list(workspace) instead.")
        return PublishedPipeline.list(workspace=workspace, active_only=active_only,
                                      _service_endpoint=_service_endpoint)

    @staticmethod
    def list(workspace, active_only=True, _service_endpoint=None):
        """
        Get all published pipelines in the current workspace.

        :param workspace: The workspace the published pipeline was created on.
        :type workspace: azureml.core.Workspace
        :param active_only: If true, only return published pipelines which are currently active.
        :type active_only: Bool
        :param _service_endpoint: The service endpoint.
        :type _service_endpoint: str

        :return: a list of :class:`azureml.pipeline.core.graph.PublishedPipeline`
        :rtype: :class:`list`
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      service_endpoint=_service_endpoint)
        return graph_context.workflow_provider.published_pipeline_provider.get_all(active_only=active_only)

    def enable(self):
        """Set the published pipeline to be 'Active' and available to run."""
        self._set_status('Active')

    def disable(self):
        """Set the published pipeline to be 'Disabled' and unavailable to run."""
        self._set_status('Disabled')

    def _set_status(self, new_status):
        """Set the published pipeline status."""
        self._pipeline_provider.set_status(self.id, new_status)
        self._status = new_status

    def _repr_html_(self):
        info = self._get_base_info_dict(show_link=True)
        return to_html(info)

    def _get_base_info_dict(self, show_link):
        id = self.id
        endpoint = self.endpoint
        if show_link:
            id = make_link(self.get_portal_url(), self.id)
            endpoint = make_link(self.endpoint, 'REST Endpoint')
        return OrderedDict([
            ('Name', self.name),
            ('Id', id),
            ('Status', self.status),
            ('Endpoint', endpoint)
        ])

    def __str__(self):
        """Return the string representation of the PublishedPipeline."""
        info = self._get_base_info_dict(show_link=False)
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "Pipeline({0})".format(formatted_info)

    def __repr__(self):
        """Return the representation of the PublishedPipeline."""
        return self.__str__()

    def _to_dict_cli(self, verbose=True):
        """
        Serialize this pipeline information into a dictionary for CLI output.

        :param verbose: Whether to include all properties.
        :type verbose: Bool
        :return: A dictionary of {str, str} name/value pairs
        :rtype: dict
        """
        result_dict = self._get_base_info_dict(show_link=False)
        if verbose:
            result_dict["Description"] = self.description
            result_dict["Version"] = self.version
            result_dict["TotalRunSteps"] = self.total_run_steps

        return result_dict

    def _sanitize_name(self):
        """
        Sanitize the pipeline name so it can be used as an experiment name (replaces special characters with '_').

        :return: Sanitized name
        :rtype: str
        """
        import re
        return re.sub('[^0-9a-zA-Z_\-]+', '_', self.name)


class DataType(object):
    """
    Datatype for a piece of data (input or output).

    :param workspace: Workspace object this DataType belongs to.
    :type workspace: azureml.core.Workspace
    :param id: ID of the datatype
    :type id: str
    :param name: Name of the datatype
    :type name: str
    :param description: Description of the datatype
    :type description: str
    :param is_directory: True if the datatype represents a directory, False if it represents a single file
    :type is_directory: bool
    :param parent_datatype_ids: List of parent datatypes that this datatype is derived from
    :type parent_datatype_ids: :class:`list`
    """

    def __init__(self, workspace, id, name, description, is_directory, parent_datatype_ids):
        """
        Initialize DataType.

        :param workspace: Workspace object this DataType belongs to.
        :type workspace: azureml.core.Workspace
        :param id: ID of the datatype
        :type id: str
        :param name: Name of the datatype
        :type name: str
        :param description: Description of the datatype
        :type description: str
        :param is_directory: True if the datatype represents a directory, False if it represents a single file
        :type is_directory: bool
        :param parent_datatype_ids: List of parent datatypes that this datatype is derived from
        :type parent_datatype_ids: :class:`list`
        """
        self._id = id
        self._name = name
        self._description = description
        self._is_directory = is_directory
        self._parent_datatype_ids = parent_datatype_ids
        self._workspace = workspace

    @property
    def id(self):
        """
        Get the ID for this data.

        :return: The ID.
        :rtype: str
        """
        return self._id

    @property
    def name(self):
        """
        Name of the datatype.

        :return: The name.
        :rtype: str
        """
        return self._name

    @property
    def description(self):
        """
        Get the description of the datatype.

        :return: The description string.
        :rtype: str
        """
        return self._description

    @property
    def is_directory(self):
        """
        Return True if the datatype represents a directory, False if it represents a single file.

        :return: The is directory property.
        :rtype: bool
        """
        return self._is_directory

    @property
    def parent_datatype_ids(self):
        """
        List of parent datatypes that this datatype is derived from.

        :return: The list of datatype ids.
        :rtype: :class:`list`
        """
        return self._parent_datatype_ids

    def update(self, new_description=None, new_parent_datatypes=None):
        """
        Update this DataType's description or parent DataTypes.

        :param new_description: The new description of the DataType
        :type new_description: str
        :param new_parent_datatypes: List of new parent DataTypes. The new list will be added to the existing list of
                                     parent DataTypes for this DataType.
        :type new_parent_datatypes: :class:`list`
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        data_type_provider = \
            _GraphContext("placeholder", workspace=self._workspace).workflow_provider.datatype_provider

        data_type = data_type_provider.update_datatype(id=self.name, new_description=new_description,
                                                       new_parent_datatype_ids=new_parent_datatypes)

        self._parent_datatype_ids = data_type.parent_datatype_ids
        self._description = data_type.description

    @staticmethod
    def create_data_type(workspace, name, description, is_directory, parent_datatypes=None):
        """
        Create a new DataType.

        :param workspace: Workspace object this DataType belongs to.
        :type workspace: azureml.core.Workspace
        :param name: Name of the DataType
        :type name: str
        :param description: Description of the DataType
        :type description: str
        :param is_directory: True if the DataType represents a directory, False if it represents a single file
        :type is_directory: bool
        :param parent_datatypes: List of parent DataType names that this DataType is derived from
        :type parent_datatypes: :class:`list`

        :return: The created DataType.
        :rtype: azureml.pipeline.core.graph.DataType
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        data_type_provider = _GraphContext("placeholder", workspace=workspace).workflow_provider.datatype_provider

        data_type = data_type_provider.create_datatype(id=name, name=name, description=description,
                                                       is_directory=is_directory,
                                                       parent_datatype_ids=parent_datatypes)

        return data_type

    @staticmethod
    def list_data_types(workspace):
        """
        List the existing DataTypes on the given workspace.

        :param workspace: The workspace object.
        :type workspace: azureml.core.Workspace

        :return: The list of DataTypes.
        :rtype: :class:`list`
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        data_type_provider = _GraphContext("placeholder", workspace=workspace).workflow_provider.datatype_provider

        return data_type_provider.get_all_datatypes()


class StoredProcedureParameter(object):
    """Represents a SQL stored procedure parameter for use with SQL database references."""

    def __init__(self, name, value, type=None):
        """
        Initialize StoredProcedureParameter.

        :param name: the name of the stored procedure parameter.
        :type name: str
        :param value: the value of the stored procedure parameter.
        :type value: str
        :param type: the type of the stored procedure parameter value,
        defaults to azureml.pipeline.core.graph.StoredProcedureParameterType.String
        :type type: azureml.pipeline.core.graph.StoredProcedureParameterType
        """
        self.name = name
        self.value = value
        self.type = type or StoredProcedureParameterType.String


class StoredProcedureParameterType(Enum):
    """Represents type of SQL stored procedure parameter for use with SQL database references."""

    String = "String"
    Int = "Int"
    Decimal = "Decimal"
    Guid = "Guid"
    Boolean = "Boolean"
    Date = "Date"

    @staticmethod
    def from_str(code):
        """
        Create StoredProcedureParameterType from string representation.

        :param code: string to convert to StoredProcedureParameterType
        :param code: str
        :return: StoredProcedureParameterType enum
        :rtype: StoredProcedureParameterType
        """
        if code == '0':
            return StoredProcedureParameterType.String
        elif code == '1':
            return StoredProcedureParameterType.Int
        elif code == '2':
            return StoredProcedureParameterType.Decimal
        elif code == '3':
            return StoredProcedureParameterType.Guid
        elif code == '4':
            return StoredProcedureParameterType.Boolean
        elif code == '5':
            return StoredProcedureParameterType.Date
        else:
            raise ValueError("Not a supported value")
