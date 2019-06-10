# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module.py, module for managing modules and module versions."""
from __future__ import print_function
from azureml._html.utilities import to_html
from azureml.pipeline.core.graph import InputPortDef, OutputPortDef, ModuleDef
from collections import OrderedDict
from ._module_builder import _ModuleBuilder


class Module(object):
    """
    Module class.

    Module represents a computation unit, defines script which will run on compute target and describes its interface.
    Module interface describes inputs, outputs, parameter definitions. It doesn't bind them to specific values or data.
    Module has snapshot associated with it, captures script, binaries and files necessary to execute on compute target.

    .. remarks::

        A Module acts as a container of its versions. A example of a Module lifecycle is the following:

        .. code-block:: python

            from azureml.pipeline.core.graph import InputPortDef, OutputPortDef

            producer = Module.create(ws, "ProducerModule", "Producer")
            consumer = Module.create(ws, "ConsumerModule", "Consumer")
            datastore = ws.get_default_datastore()

            out1 = OutputPortDef(name="out1", default_datastore_name=datastore.name, default_datastore_mode="mount",
                                 is_directory=False)
            out2 = OutputPortDef(name="out2", default_datastore_name=datastore.name, default_datastore_mode="mount",
                                 is_directory=False)
            out3 = OutputPortDef(name="out3", default_datastore_name=datastore.name, default_datastore_mode="mount",
                                 is_directory=False)
            producer.publish("p_v1", "aml-compute", input_bindings=[],
                             output_bindings=[out1, out2, out3], version="1")
            in1 = InputPortDef(name="in1", default_datastore_mode="mount", data_types=["AnyFile", "AnyDirectory"])
            in2 = InputPortDef(name="in2", default_datastore_mode="mount", data_types=["AnyFile", "AnyDirectory"])
            in3 = InputPortDef(name="in3", default_datastore_mode="mount", data_types=["AnyFile", "AnyDirectory"])

            consumer.publish("c_v2", "aml-compute", input_bindings=[in1, in2, in3], output_bindings=[], version="2")

        In this case, two modules were created, each published a version. The producer module has a version that have
        3 outputs and the consumer module has a version that have3 inputs.

        These modules can be used when defining a a pipeline, in different steps, by using A StepModule for each of
        the module.

        .. code-block:: python

            from azureml.pipeline.core import Pipeline, PipelineData
            from azureml.pipeline.steps import ModuleStep

            wire1 = PipelineData("wire1", datastore=self.datastore)
            wire2 = PipelineData("wire2", datastore=self.datastore)
            wire3 = PipelineData("wire3", datastore=self.datastore)

            producer_step = ModuleStep(module=producer, outputs_map={"out1": wire1, "out2": wire2, "out3": wire3})
            consumer_step = ModuleStep(module=consumer, inputs_map={"in1": wire1, "in2": wire2, "in3": wire3})

            pipeline = Pipeline(workspace=ws, steps=[producer_step, consumer_step])

        This will create a Pipeline with two steps. The producer step will be executed first, then after it has
        completed, the consumer step will be executed. The orchestrator will provide the output produced by the
        producer module to the consumer module.

        The resolution which version of the module to use happens upon submission, and follows the following process:
        - Remove all disabled versions.
        - If a specific version was stated, use that, else
        - If a default version was defined to the Module, use that, else
        - If all versions follow semantic versioning without letters, take the highest value, else
        - Take the version of the Module that was updated last

        Note that since a node's inputs and outputs mapping to a module's input and output is defined upon Pipeline
        creation, if the resolved version upon submission has different interface from the one that is resolved
        upon pipeline creation, the pipeline submission would fail.

        The underlying module can be updated with new versions while keeping the default version the same.
        Modules are uniquely named within a workspace.

    :param workspace: Workspace object this Module will belong to.
    :type workspace: azureml.core.Workspace
    :param module_id: The Id of the Module.
    :type module_id: str
    :param name: The name of the Module.
    :type name: str
    :param description: Description of the Module.
    :type description: str
    :param status: The new status of the Module: 'Active', 'Deprecated' or 'Disabled'.
    :type status: str
    :param default_version: The default version of the Module.
    :type default_version: str
    :param module_version_list: The list of :class:`azureml.pipeline.core.ModuleVersionDescriptor`
    :type module_version_list: :class:`list`
    :param _module_provider: The Module provider.
    :type _module_provider: _AzureMLModuleProvider object
    :param _module_version_provider: The ModuleVersion provider.
    :type _module_version_provider: _AevaMlModuleVersionProvider object
    """

    def __init__(self, workspace, module_id, name, description, status, default_version, module_version_list,
                 _module_provider=None, _module_version_provider=None):
        """
        Initialize Module.

        :param workspace: Workspace object this Mdule will belong to.
        :type workspace: azureml.core.Workspace
        :param module_id: The Id of the Module.
        :type module_id: str
        :param name: The name of the Module.
        :type name: str
        :param description: Description of the Module.
        :type description: str
        :param status: The new status of the Module: 'Active' or 'Disabled'.
        :type status: str
        :param default_version: The default version of the Module.
        :type default_version: str
        :param module_version_list: The list of :class:`azureml.pipeline.core.ModuleVersionDescriptor`
        :type module_version_list: :class:`list`
        :param _module_provider: The Module provider.
        :type _module_provider: _AevaMlModuleProvider object
        :param _module_version_provider: The ModuleVersion provider.
        :type _module_version_provider: _AevaMlModuleVersionProvider object
        """
        self._workspace = workspace
        self._id = module_id
        self._name = name
        self._description = description
        self._status = status
        self._default_version = default_version
        self._module_version_list = module_version_list
        self._workspace = workspace
        self._module_provider = _module_provider
        self._module_version_provider = _module_version_provider

    @staticmethod
    def create(workspace, name, description, _workflow_provider=None):
        """
        Create the Module.

        :param workspace: The workspace the Module was created on.
        :type workspace: azureml.core.Workspace
        :param name: Name of the Module.
        :type name: str
        :param description: Description of the Module.
        :type description: str
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object

        :return: Module object
        :rtype: azureml.pipeline.core.Module
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider)
        azure_ml_module_provider = graph_context.workflow_provider.azure_ml_module_provider
        result = azure_ml_module_provider.create_module(name, description)
        return result

    @staticmethod
    def get(workspace, module_id=None, name=None, _workflow_provider=None):
        """
        Get the Module by name or by id, throws exception if either is not provided.

        :param workspace: The workspace the Module was created on.
        :type workspace: azureml.core.Workspace
        :param module_id: Id of the Module.
        :type module_id: str
        :param name: Name of the Module.
        :type name: str
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object

        :return: Module object
        :rtype: azureml.pipeline.core.Module
        """
        from azureml.pipeline.core._graph_context import _GraphContext
        graph_context = _GraphContext('placeholder', workspace,
                                      workflow_provider=_workflow_provider)
        azure_ml_module_provider = graph_context.workflow_provider.azure_ml_module_provider
        result = azure_ml_module_provider.get_module(module_id, name)
        return result

    @staticmethod
    def module_def_builder(name, description, execution_type, input_bindings, output_bindings, param_defs=None,
                           create_sequencing_ports=True, allow_reuse=True, version=None):
        """
        Create the module definition object that describes the step.

        :param name: The name the module.
        :type name: str
        :param description: The description of the module.
        :type description: str
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
        :param allow_reuse: If true the module will be available to be reused.
        :type allow_reuse: bool
        :param version: The version of the module.
        :type version: str

        :return: The module def object.
        :rtype: azureml.pipeline.core.graph.ModuleDef
        """
        all_datatypes = ["AnyFile", "AnyDirectory"]
        input_port_defs = []
        for input_binding in input_bindings:
            if isinstance(input_binding, InputPortDef):
                input_port_defs.append(input_binding)
            else:
                data_types = all_datatypes
                if input_binding.data_type is not None:
                    data_types = [input_binding.data_type]
                input_port_defs.append(InputPortDef(name=input_binding.name,
                                                    data_types=data_types,
                                                    default_datastore_mode=input_binding.bind_mode,
                                                    default_path_on_compute=input_binding.path_on_compute,
                                                    default_overwrite=input_binding.overwrite,
                                                    default_data_reference_name=input_binding.data_reference_name,
                                                    is_resource=input_binding.is_resource))

        output_port_defs = []
        for output_binding in output_bindings:
            if isinstance(output_binding, OutputPortDef):
                output_port_defs.append(output_binding)
            else:
                output_port_defs.append(OutputPortDef(name=output_binding._output_name,
                                                      default_datastore_name=output_binding._datastore_name,
                                                      default_datastore_mode=output_binding.bind_mode,
                                                      default_path_on_compute=output_binding.path_on_compute,
                                                      default_overwrite=output_binding.overwrite,
                                                      data_type=output_binding.data_type,
                                                      is_directory=output_binding.is_directory))

        module_def = ModuleDef(
            name=name,
            description=description,
            input_port_defs=input_port_defs,
            output_port_defs=output_port_defs,
            param_defs=param_defs,
            module_execution_type=execution_type,
            create_sequencing_ports=create_sequencing_ports,
            allow_reuse=allow_reuse,
            version=version)
        return module_def

    @staticmethod
    def get_versions(workspace, name, _workflow_provider=None):
        """
        Get all the versions of the module.

        :param workspace: The workspace the Module was created on.
        :type workspace: azureml.core.Workspace
        :param name: Name of the Module.
        :type name: str
        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object

        :return: The list of :class:`azureml.pipeline.core.ModuleVersionDescriptor`
        :rtype: :class:`list`
        """
        module = Module.get(workspace, name=name,
                            _workflow_provider=_workflow_provider)
        return module.module_version_list()

    @property
    def id(self):
        """
        Id of the Module.

        :return: The id.
        :rtype: str
        """
        return self._id

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
    def status(self):
        """
        Get the status of the Module.

        :return: The status.
        :rtype: str
        """
        return self._status

    @property
    def default_version(self):
        """
        Get the default version of the Module.

        :return: The default version string.
        :rtype: str
        """
        return self._default_version

    def module_version_list(self):
        """
        Get the module version list.

        :return: The list of :class:`azureml.pipeline.core.ModuleVersionDescriptor`
        :rtype: :class:`list`
        """
        return self._module_version_list

    def publish(self, description, execution_type, input_bindings, output_bindings,
                param_defs=None,
                create_sequencing_ports=True, version=None, is_default=False, content_path=None, hash_paths=None):
        """
        Create a ModuleVersion and add it to the mdodule.

        Create a ModuleVersion for the current Module.

        :param description: The description of the module.
        :type description: str
        :param execution_type: The execution type of the module.
        :type execution_type: str
        :param input_bindings: The Module input bindings.
        :type input_bindings: :class:`list`
        :param output_bindings: The Module output bindings.
        :type output_bindings: :class:`list`
        :param param_defs: The Module param definitions.
        :type param_defs: :class:`list`
        :param create_sequencing_ports: If true sequencing ports will be created for the module.
        :type create_sequencing_ports: bool
        :param version: The version of the module.
        :type version: str
        :param is_default: whether the published version is to be the default one
        :type is_default: bool
        :param content_path: directory
        :type content_path: str
        :param hash_paths: hash_paths
        :type hash_paths: :class:`list`

        :rtype: azureml.pipeline.core.ModuleVersion
        """
        if version is not None:
            found_version = next((item for item in self._module_version_list if item.version == version), None)
            if found_version is not None:
                raise Exception("provided version value already exist")
        mod_def = self.module_def_builder(self._name, description, execution_type, input_bindings, output_bindings,
                                          param_defs, create_sequencing_ports, True, version)

        module_version = self._module_version_provider.create_module_version(self._workspace,
                                                                             self._id, version,
                                                                             mod_def, content_path,
                                                                             _ModuleBuilder.calculate_hash(mod_def,
                                                                                                           hash_paths))
        module_version_descriptor = ModuleVersionDescriptor(module_version.version, module_version.module_version_id)
        self._module_version_list.append(module_version_descriptor)
        self._module_provider.update_module(module_version.module_id, versions=self._module_version_list)
        if is_default:
            self.set_default_version(module_version_descriptor.version)
        return module_version

    def resolve(self, version=None):
        """
        Resolve and return the right ModuleVersion.

        :return: The module version to use
        :rtype: azureml.pipeline.core.ModuleVersion
        """
        if version is not None:
            mvd = next((v for v in self._module_version_list if v.version == version), None)
            if mvd is not None:
                return self._get_module_version(mvd.module_version_id)
        mv = self.get_default()
        if mv is not None:
            return mv

        def find_highest_version(versions_list):
            if len(versions_list) == 1:
                return versions_list[0]["k"]
            else:
                # version list sorted desc by the first segment of the version
                versions_list.sort(key=lambda x: int(x["v"].split(".", 1)[0]), reverse=True)
                # filter only the largest ones
                tops = filter(lambda x: x["v"].split(".", 1)[0] == versions_list[0]["v"].split(".", 1)[0],
                              versions_list)
                # remove the first segment from the versions
                nexts = map(lambda y:
                            {"k": y["k"], "v": y["v"].split(".", 1)[1]} if len(y["v"].split(".", 1)) > 1 else None,
                            tops)
                # remove the empty cells
                next_version_list = list(filter(lambda k: k is not None, nexts))
                if len(next_version_list) == 0:
                    return versions_list[0]["k"]
                return find_highest_version(next_version_list)

        all_mvs = map(lambda v: self._get_module_version(v.module_version_id), self._module_version_list)
        non_disabled_versions = list(filter(lambda v: v.status != 'Disabled', all_mvs))
        if all(a.version is not None and a.version.replace(".", "1").isdigit() for a in non_disabled_versions):
            ver = find_highest_version(list(map(lambda x: {"k": x.version, "v": x.version},
                                                non_disabled_versions)))
            return self.resolve(ver)
        else:
            date_and_mv = list(map(lambda x: {"dt": x._entity.data.last_modified_date, "mv": x},
                                   non_disabled_versions))
            return max(date_and_mv, key=lambda k: k["dt"])["mv"]

    def enable(self):
        """Set the Module to be 'Active'."""
        self._set_status('Active')

    def disable(self):
        """Set the Module to be 'Disabled'."""
        self._set_status('Disabled')

    def deprecate(self):
        """Set the Module to be 'Deprecated'."""
        self._set_status('Deprecated')

    def _set_status(self, new_status):
        """Set the Module status."""
        self._module_provider.update_module(self._id, status=new_status)
        self._status = new_status

    def get_default_version(self):
        """
        Get the default version of Module.

        :return: default_version
        :rtype: str
        """
        return self._default_version

    def set_default_version(self, version_id):
        """
        Get the default module verion string.

        :return: The default version
        :rtype: str
        """
        if version_id is None:
            raise Exception("No version was provided to be set as default")

        found_module_version = next(
            (item for item in self._module_version_list if item.version == version_id),
            None)
        if found_module_version is None:
            raise Exception("provided version is not par of the module")
        self._module_provider.update_module(self._id, default_version=found_module_version.version)
        self._default_version = found_module_version.version

    def get_default(self):
        """
        Get the default module version object.

        :return: default_version
        :rtype: :class:`azureml.pipeline.core.ModuleVersion`
        """
        version_descriptor = next((mv for mv in self._module_version_list if mv.version == self.default_version),
                                  None)
        if version_descriptor is None:
            return None
        return self._get_module_version(version_descriptor.module_version_id)

    def set_name(self, name):
        """
        Set name of Module.

        :param name: Name to set.
        :type name: str
        """
        if name is None:
            raise Exception("No name was provided")
        self._module_provider.update_module(self._id, name=name)

    def set_description(self, description):
        """
        Set description of Module.

        :param description: Description to set.
        :type description: str
        """
        if description is None:
            raise Exception("No description was provided")
        self._module_provider.update_module(self._id, description=description)

    def _get_module_version(self, version_id):
        return self._module_version_provider.get_module_version(self._workspace,
                                                                module_version_id=version_id)

    def _repr_html_(self):
        info = self._get_base_info_dict()
        return to_html(info)

    def _get_base_info_dict(self):
        info = OrderedDict([
            ('Name', self.name),
            ('Id', self.id),
            ('Description', self.description),
            ('Versions', self._get_list_info_dict(self._module_version_list))
        ])
        return info

    def _get_list_info_dict(self, versions):
        list_info = [self._get_module_version_info_dict(version_item) for version_item in versions]
        return list_info

    @staticmethod
    def _get_module_version_info_dict(module_version):
        info = OrderedDict([
            ('Version', module_version.version),
            ('Module_version_id', module_version.module_id)
        ])
        return info

    def __str__(self):
        """Return the string representation of the Module."""
        info = OrderedDict([
            ('Name', self.name),
            ('Id', self.id),
            ('Description', self.description),
            ('Versions', [(module_version.version, module_version.module_id)
                          for module_version in self._module_version_list])
        ])
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "Module({0})".format(formatted_info)

    def __repr__(self):
        """Return the representation of the Module."""
        return self.__str__()


class ModuleVersion(object):
    """
    ModuleVersion class.

    ModuleVersion represents the actual computation unit.
    It is contained within a Module.
    """

    def __init__(self, workspace, module_entity, module_version_provider, version):
        """
        Initialize ModuleVersionDescriptor.

        :param workspace: Workspace object this Mdule will belong to.
        :type workspace: azureml.core.Workspace
        :param module_entity: The ModuleEntity object.
        :type module_entity: models.AzureMLModuleVersion
        :param module_version_provider: The version provider.
        :type module_version_provider: _AevaMlModuleVersionProvider
        :param version: The version number.
        :type version: str
        """
        self._workspace = workspace
        self._entity = module_entity
        self._version_provider = module_version_provider
        self._version = version

    @property
    def status(self):
        """
        Status of the Module Version.

        :return: The status.
        :rtype: str
        """
        return self._entity.data.entity_status

    @property
    def module_id(self):
        """
        Id of the containing Module.

        :return: The id.
        :rtype: str
        """
        return self._entity.module_id

    @property
    def description(self):
        """
        Get the description of the ModuleVersion.

        :return: The description.
        :rtype: str
        """
        return self._entity.data.description

    @property
    def module_version_id(self):
        """
        Id of the Module Version.

        :return: The id.
        :rtype: str
        """
        return self._entity.data.id

    @property
    def version(self):
        """
        Id of the containing Module.

        :return: The id.
        :rtype: str
        """
        return self._version

    @property
    def interface(self):
        """
        Get the interface of the module.

        :return: The structuredInterface.
        :rtype: model.structuredInterface
        """
        return self._entity.data.structured_interface

    def module(self, _workflow_provider=None):
        """
        Containing Module element.

        :param _workflow_provider: The workflow provider.
        :type _workflow_provider: _AevaWorkflowProvider object
        :return: Module object
        :rtype: azureml.pipeline.core.Module
        """
        return Module.get(self._workspace, _workflow_provider=_workflow_provider, module_id=self._entity.module_id)

    def _repr_html_(self):
        info = self._get_base_info_dict()
        return to_html(info)

    def _get_base_info_dict(self):
        info = OrderedDict([
            ('status', self._entity.data.entity_status),
            ('version', self._version),
            ('module_id', self._entity.module_id),
            ('module_version_id', self._entity.data.id)
        ])
        return info

    def set_description(self, description):
        """
        Set description of Module.

        :param description: Description to set.
        :type description: str
        """
        if description is None:
            raise Exception("No description was provided")
        self._version_provider.update_module_version(self._entity.data.id,
                                                     version=self.version,
                                                     description=description)

    def enable(self):
        """Set the ModuleVersion to be 'Active'."""
        self._set_status('Active')

    def disable(self):
        """Set the ModuleVersion to be 'Disabled'."""
        self._set_status('Disabled')

    def deprecate(self):
        """Set the ModuleVersion to be 'Deprecated'."""
        self._set_status('Deprecated')

    def _set_status(self, new_status):
        """Set the Module status."""
        self._version_provider.update_module_version(self._entity.data.id, version=self.version,
                                                     status=new_status)
        self._entity.data.entity_status = new_status

    def __str__(self):
        """Return the string representation of the ModuleVersion."""
        info = self._get_base_info_dict()
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "ModuleVersion({0})".format(formatted_info)

    def __repr__(self):
        """Return the representation of the ModuleVersion."""
        return self.__str__()


class ModuleVersionDescriptor(object):
    """A ModuleVersionDescriptor defines the version and id of a ModuleVersion."""

    def __init__(self, version, module_version_id):
        """
        Initialize ModuleVersionDescriptor.

        :param version: The version of the ModuleVersion.
        :type version: str
        :param module_version_id: The published ModuleVersion id.
        :type module_version_id: str
        """
        self._version = version
        self._module_version_id = module_version_id

    @property
    def version(self):
        """
        Version of the Module Version.

        :return: The version of ModuleVersion.
        :rtype: str
        """
        return self._version

    @property
    def module_version_id(self):
        """
        Id of the Module Version.

        :return: The id of Module.
        :rtype: str
        """
        return self._module_version_id

    def _repr_html_(self):
        info = self._get_base_info_dict()
        return to_html(info)

    def _get_base_info_dict(self):
        info = OrderedDict([
            ('Version', self.version),
            ('ModuleVersionId', self.module_version_id)
        ])
        return info

    def __str__(self):
        """Return the string representation of the ModuleVersionDescriptor."""
        info = self._get_base_info_dict()
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "ModuleVersionDescriptor({0})".format(formatted_info)

    def __repr__(self):
        """Return the representation of the ModuleVersionDescriptor."""
        return self.__str__()
