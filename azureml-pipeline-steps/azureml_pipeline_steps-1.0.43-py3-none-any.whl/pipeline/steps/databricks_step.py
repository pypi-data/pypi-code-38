# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""To add a step to run a Databricks notebook or a python script on DBFS."""
from azureml.pipeline.core import PipelineStep
from azureml.pipeline.core.graph import ParamDef
from azureml.pipeline.core._module_builder import _InterfaceModuleBuilder, _FolderModuleBuilder
from azureml.core.runconfig import RunConfiguration

import logging


class DatabricksStep(PipelineStep):
    """Adds a Databricks notebook or a python script on DBFS as a step in a Pipeline.

    See example of using this step in notebook https://aka.ms/pl-databricks

    :param name: Name of the step
    :type name: str
    :param inputs: List of input connections for data consumed by this step. Fetch this inside the notebook
                    using dbutils.widgets.get("input_name"). Can be DataReference or PipelineData. DataReference
                    represents an existing piece of data on a datastore. Essentially this is a path on a
                    datastore. DatabricksStep supports datastores that encapsulates Azure blob or ADLS v1.
                    PipelineData represents intermediate data produced by another step in a pipeline.
    :type inputs: list[azureml.pipeline.core.graph.InputPortBinding, azureml.data.data_reference.DataReference,
                       azureml.pipeline.core.PortDataReference, azureml.pipeline.core.builder.PipelineData,
                       azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                       azureml.pipeline.core.PipelineDataset]
    :param outputs: List of output port definitions for outputs produced by this step. Fetch this inside the
                    notebook using dbutils.widgets.get("output_name"). Should be PipelineData.
    :type outputs: list[azureml.pipeline.core.graph.OutputPortBinding, azureml.pipeline.core.builder.PipelineData]
    :param existing_cluster_id: Cluster ID of an existing interactive cluster on the Databricks workspace.
        If you are passing this parameter, you cannot pass any of the following parameters which are used to
        create a new cluster:
        -   spark_version
        -   node_type
        -   num_workers
        -   min_workers
        -   max_workers
        -   spark_env_variables
        -   spark_conf

        Note: For creating a new job cluster, you will need to pass the above parameters. You can pass
        these parameters directly or you can pass them as part of the RunConfiguration object using the
        runconfig parameter. However, you can’t pass the parameters via runconfig and directly at the same time
        as that will lead to ambiguity, and hence, DatabricksStep will report an error.
    :type existing_cluster_id: str
    :param spark_version: The version of spark for the Databricks run cluster. Example: "4.0.x-scala2.11"
    :type spark_version: str
    :param node_type: The Azure VM node types for the Databricks run cluster. Example: "Standard_D3_v2"
    :type node_type: str
    :param num_workers: Specifies a static number of workers for the Databricks run cluster.
                        Exactly one of num_workers or min_workers and max_workers is required
    :type num_workers: int
    :param min_workers: Specifies a min number of workers to use for auto-scaling the Databricks run cluster
    :type min_workers: int
    :param max_workers: Specifies a max number of workers to use for auto-scaling the Databricks run cluster
    :type max_workers: int
    :param spark_env_variables: The spark environment variables for the Databricks run cluster
    :type spark_env_variables: dict
    :param spark_conf: The spark configuration for the Databricks run cluster
    :type spark_conf: dict
    :param init_scripts: DBFS paths to init scripts for the new cluster
    :type init_scripts: [str]
    :param notebook_path: The path to the notebook in the Databricks instance. This class allows four ways of
                          specifying the code that you wish to execute on the Databricks cluster.
                          1.	If you want to execute a notebook that is present in the Databricks workspace:
                          notebook_path=notebook_path,
                          notebook_params={'myparam': 'testparam'},
                          2.	If you want to execute a Python script that is present in DBFS:
                          python_script_path=python_script_dbfs_path,
                          python_script_params={'arg1', 'arg2'},
                          3.	If you want to execute a JAR that is present in DBFS:
                          main_class_name=main_jar_class_name,
                          jar_params={'arg1', 'arg2'},
                          jar_libraries=[JarLibrary(jar_library_dbfs_path)],
                          4.	If you want to execute a Python script that is present on your local machine:
                          python_script_name=python_script_name,
                          source_directory=source_directory,
    :type notebook_path: str
    :param notebook_params: Parameters for the Databricks notebook (dictionary of {str:str}).
        Parameters passed to the notebook using the notebook_params parameter are available as widgets.
        You can fetch the values from these widgets inside your notebook using `dbutils.widgets.get("myparam")`.
    :type notebook_params: dict
    :param python_script_path: The path to the python script in the DBFS or S3.
    :type python_script_path: str
    :param python_script_params: Parameters for the python script (list of str).
    :type python_script_params: list
    :param main_class_name: The name of the entry point in a JAR module.
    :type main_class_name: str
    :param jar_params: Parameters for the JAR module (list of str).
    :type jar_params: list
    :param python_script_name: Name of a python script (relative to source_directory). If the script takes inputs
        and outputs, those will be passed to the script as parameters.

        If you specify a DataReference object as inout with `data_reference_name="input1` and a
        PipelineData object as output with `name=output1`, then the inputs and outputs will be passed to the script
        as parameters. This is how they will look like and you will need to parse the arguments
        in your script to access the paths of each input and output:
        `"—input1","wasbs://test@storagename.blob.core.windows.net/test","—output1",
        "wasbs://test@storagename.blob.core.windows.net/b3e26de1-87a4-494d-a20f-1988d22b81a2/output1"`

        In addition, the following parameters will be available within the script:
        -   AZUREML_RUN_TOKEN: The AML token for authenticating with Azure Machine Learning.
        -   AZUREML_RUN_ID: Azure Machine Learning Run ID for this run.
        -   AZUREML_ARM_SUBSCRIPTION: Azure subscription for your AML workspace.
        -   AZUREML_ARM_RESOURCEGROUP: Azure resource group for your Azure Machine Learning workspace.
        -   AZUREML_ARM_WORKSPACE_NAME: Name of your Azure Machine Learning workspace.
        -   AZUREML_ARM_PROJECT_NAME: Name of your Azure Machine Learning experiment.
        -   AZUREML_SCRIPT_DIRECTORY_NAME: Directory path structure in DBFS where source_directory has been copied.

        When you are executing a python script from your local machine on Databricks using
        AZUREML_SCRIPT_DIRECTORY_NAME_ARG_VARIABLE DatabricksStep your source_directory is copied over to DBFS
        and the directory structure path on DBFS is passed as a parameter to your script when it begins execution.
        This parameter is labelled as --AZUREML_SCRIPT_DIRECTORY_NAME. You need to prefix it with the
        string "dbfs:/" or "/dbfs/" to access the directory in DBFS.
    :type python_script_name: str
    :param source_directory: Folder that contains the script and other files
    :type source_directory: str
    :param hash_paths: List of paths to hash when checking for changes to the contents of source_directory.  If
        there are no changes detected, the pipeline will reuse the step contents from a previous run.  By default
        contents of the source_directory is hashed (except filed under .amlignore or .gitignore).
        Parameter `hash_paths` will be deprecated.
    :type hash_paths: [str]
    :param run_name: The name in Databricks for this run
    :type run_name: str
    :param timeout_seconds: Timeout for the Databricks run
    :type timeout_seconds: int
    :param runconfig: Runconfig to use
        Note: You can pass the following libraries (as many as you like) as dependencies to your job
        using the following parameters: maven_libraries, pypi_libraries, egg_libraries, jar_libraries,
        or rcran_libraries. You can pass these parameters directly or as part of the RunConfiguration
        object using the runconfig parameter, but you cannot do both at the same time.
    :type runconfig: azureml.core.runconfig.RunConfiguration
    :param maven_libraries: Maven libraries for the Databricks run
    :type maven_libraries: list[azureml.core.runconfig.MavenLibrary]
    :param pypi_libraries: PyPi libraries for the Databricks run
    :type pypi_libraries: list[azureml.core.runconfig.PyPiLibrary]
    :param egg_libraries: egg libraries for the Databricks run
    :type egg_libraries: list[azureml.core.runconfig.EggLibrary]
    :param jar_libraries: jar libraries for the Databricks run
    :type jar_libraries: list[azureml.core.runconfig.JarLibrary]
    :param rcran_libraries: rcran libraries for the Databricks run
    :type rcran_libraries: list[azureml.core.runconfig.RCranLibrary]
    :param compute_target: Azure Databricks compute. Before you can use DatabricksStep to execute your scripts
        or notebooks on an Azure Databricks workspace, you need to add the Azure Databricks workspace as a
        compute target to your Azure Machine Learning workspace.
    :type compute_target: str, azureml.core.compute.DatabricksCompute
    :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
        Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
        parameters remain unchanged, the output from the previous run of this step is reused. When reusing
        the step, instead of submitting the job to compute, the results from the previous run are immediately
        made available to any subsequent steps.
    :type allow_reuse: bool
    :param version: Optional version tag to denote a change in functionality for the step
    :type version: str
    """

    def __init__(self, name, inputs=None, outputs=None, existing_cluster_id=None, spark_version=None, node_type=None,
                 num_workers=None, min_workers=None, max_workers=None, spark_env_variables=None, spark_conf=None,
                 init_scripts=None, notebook_path=None, notebook_params=None, python_script_path=None,
                 python_script_params=None, main_class_name=None, jar_params=None, python_script_name=None,
                 source_directory=None, hash_paths=None, run_name=None, timeout_seconds=None, runconfig=None,
                 maven_libraries=None, pypi_libraries=None, egg_libraries=None, jar_libraries=None,
                 rcran_libraries=None, compute_target=None, allow_reuse=True, version=None):
        """
        Add a DataBricks notebook or a python script on DBFS as a node.

        :param name: Name of the step
        :type name: str
        :param inputs: List of input connections for data consumed by this step. Fetch this inside the notebook
                        using dbutils.widgets.get("input_name")
        :type inputs: [InputPortBinding, DataReference, PortDataReference, PipelineData,
                    azureml.core.Dataset, azureml.data.dataset_definition.DatasetDefinition,
                    azureml.pipeline.core.PipelineDataset]
        :param outputs: List of output port definitions for outputs produced by this step. Fetch this inside the
                        notebook using dbutils.widgets.get("output_name")
        :type outputs: [OutputPortBinding, PipelineData]
        :param existing_cluster_id: Cluster ID of an existing Interactive cluster on the Databricks workspace. If you
                                    are providing this, do not provide any of the parameters below that are used to
                                    create a new cluster such as spark_version, node_type, etc.
        :type existing_cluster_id: str
        :param spark_version: The version of spark for the Databricks run cluster. Example: "4.0.x-scala2.11"
        :type spark_version: str
        :param node_type: The Azure vm node types for the Databricks run cluster. Example: "Standard_D3_v2"
        :type node_type: str
        :param num_workers: Specifies a static number of workers for the Databricks run cluster.
                            Exactly one of num_workers or min_workers and max_workers is required
        :type num_workers: int
        :param min_workers: Specifies a min number of workers to use for auto-scaling the Databricks run cluster
        :type min_workers: int
        :param max_workers: Specifies a max number of workers to use for auto-scaling the Databricks run cluster
        :type max_workers: int
        :param spark_env_variables: The spark environment variables for the Databricks run cluster
        :type spark_env_variables: {str:str}
        :param spark_conf: The spark configuration for the Databricks run cluster
        :type spark_conf: {str:str}
        :param init_scripts: DBFS paths to init scripts for the new cluster
        :type init_scripts: [str]
        :param notebook_path: The path to the notebook in the Databricks instance. . This class allows four ways of
        specifying the code that you wish to execute on the Databricks cluster.
        1.	If you want to execute a notebook that is present in the Databricks workspace:
        notebook_path=notebook_path,
        notebook_params={'myparam': 'testparam'},
        2.	If you want to execute a Python script that is present in DBFS:
        python_script_path=python_script_dbfs_path,
        python_script_params={'arg1', 'arg2'},
        3.	If you want to execute a JAR that is present in DBFS:
        main_class_name=main_jar_class_name,
        jar_params={'arg1', 'arg2'},
        jar_libraries=[JarLibrary(jar_library_dbfs_path)],
        4.	If you want to execute a Python script that is present on your local machine:
        python_script_name=python_script_name,
        source_directory=source_directory,
        :type notebook_path: str
        :param notebook_params: Parameters  for the Databricks notebook (dictionary of {str:str}). Fetch this inside
                                the notebook using dbutils.widgets.get("myparam")
        :type notebook_params: {str:str}
        :param python_script_path: The path to the python script in the DBFS or S3. If you are providing this,
                            do not provide python_script_name which is used for uploading script from local machine.
        :type python_script_path: str
        :param python_script_params: Parameters for the python script (list of str).
        :type python_script_params: list(str)
        :param main_class_name: The name of the entry point in a JAR module. If you are providing this, do not
                                provide any python script or notebook related parameters.
        :type main_class_name: str
        :param jar_params: Parameters for the JAR module (list of str).
        :type jar_params: list(str)
        :param python_script_name: name of a python script on your local machine (relative to source_directory).
                                If you are providing this do not provide python_script_path which is used to execute
                                a remote python script; or any of the JAR or notebook related parameters.
        :type python_script_name: str
        :param source_directory: folder that contains the script and other files
        :type source_directory: str
        :param hash_paths: List of paths to hash when checking for changes to the step contents.  If
            there are no changes detected, the pipeline will reuse the step contents from a previous run.  By default
            contents of the source_directory is hashed (except files listed in .amlignore or .gitignore).
            Parameter `hash_paths` will be deprecated.
        :type hash_paths: [str]
        :param run_name: The name in Databricks for this run
        :type run_name: str
        :param timeout_seconds: Timeout for the Databricks run
        :type timeout_seconds: int
        :param runconfig: Runconfig to use. Either pass runconfig or each library type as a separate parameter but
                            do not mix the two.
        :type runconfig: azureml.core.runconfig.RunConfiguration
        :param maven_libraries: maven libraries for the Databricks run
        :type maven_libraries: [MavenLibrary]
        :param pypi_libraries: pypi libraries for the Databricks run
        :type pypi_libraries: [PyPiLibrary]
        :param egg_libraries: egg libraries for the Databricks run
        :type egg_libraries: [EggLibrary]
        :param jar_libraries: jar libraries for the Databricks run
        :type jar_libraries: [JarLibrary]
        :param rcran_libraries: rcran libraries for the Databricks run
        :type rcran_libraries: [RCranLibrary]
        :param compute_target: Azure Databricks compute. Before you can use DatabricksStep to execute your scripts
            or notebooks on an Azure Databricks workspace, you need to add the Azure Databricks workspace as a
            compute target to your Azure Machine Learning workspace. Then you can pass the compute target to the
            DatabricksStep using this parameter.
        :type compute_target: str, azureml.core.compute.DatabricksCompute
        :param allow_reuse: Whether the step should reuse previous results when re-run with the same settings.
            Reuse is enabled by default. If the step contents (scripts/dependencies) as well as inputs and
            parameters remain unchanged, the output from the previous run of this step is reused. When reusing
            the step, instead of submitting the job to compute, the results from the previous run are immediately
            made available to any subsequent steps.
        :type allow_reuse: bool
        :param version: Optional version tag to denote a change in functionality for the step
        :type version: str
        """
        if runconfig is not None and (maven_libraries is not None or
                                      pypi_libraries is not None or
                                      egg_libraries is not None or
                                      jar_libraries is not None or
                                      rcran_libraries is not None):
            raise ValueError("Either pass runconfig or each library type as a separate parameter")
        if (self._runconfig_cluster_present(runconfig) and (existing_cluster_id is not None or
                                                            spark_version is not None or
                                                            node_type is not None or
                                                            num_workers is not None or
                                                            min_workers is not None or
                                                            max_workers is not None or
                                                            spark_env_variables is not None or
                                                            spark_conf is not None or
                                                            init_scripts is not None)):
            raise ValueError("Either pass cluster in runconfig  or each cluster parameter separately")
        if runconfig is not None:
            if not isinstance(runconfig, RunConfiguration):
                raise ValueError("runconfig must be a RunConfiguration")
            libraries_dict = self._get_libraries_from_runconfig(runconfig)
            maven_libraries = libraries_dict['maven_libraries']
            pypi_libraries = libraries_dict['pypi_libraries']
            egg_libraries = libraries_dict['egg_libraries']
            jar_libraries = libraries_dict['jar_libraries']
            rcran_libraries = libraries_dict['rcran_libraries']
        if maven_libraries is None:
            maven_libraries = []
        if pypi_libraries is None:
            pypi_libraries = []
        if egg_libraries is None:
            egg_libraries = []
        if jar_libraries is None:
            jar_libraries = []
        if rcran_libraries is None:
            rcran_libraries = []
        if name is None:
            raise ValueError("name is required")
        if not isinstance(name, str):
            raise ValueError("name must be a string")

        if self._runconfig_cluster_present(runconfig):
            existing_cluster_id = runconfig.environment.databricks.cluster.existing_cluster_id
            spark_version = runconfig.environment.databricks.cluster.spark_version
            node_type = runconfig.environment.databricks.cluster.node_type
            num_workers = runconfig.environment.databricks.cluster.num_workers
            if runconfig.environment.databricks.cluster.min_workers is not None:
                min_workers = runconfig.environment.databricks.cluster.min_workers
            if runconfig.environment.databricks.cluster.max_workers is not None:
                max_workers = runconfig.environment.databricks.cluster.max_workers
            spark_env_variables = runconfig.environment.databricks.cluster.spark_env_variables
            spark_conf = runconfig.environment.databricks.cluster.spark_conf
            init_scripts = runconfig.environment.databricks.cluster.init_scripts

        if existing_cluster_id is None:
            if spark_version is None:
                spark_version = "4.0.x-scala2.11"
            if not isinstance(spark_version, str):
                raise ValueError("spark_version must be a string")
            if node_type is None:
                node_type = "Standard_D3_v2"
            if not isinstance(node_type, str):
                raise ValueError("node_type must be a string")
            if num_workers is None and (min_workers is None or max_workers is None):
                raise ValueError("one of num_workers or min_workers and max_workers is required")
            if num_workers is not None and (min_workers is not None or max_workers is not None):
                raise ValueError("exactly one of num_workers or min_workers and max_workers is required")
            if num_workers is not None and not isinstance(num_workers, int):
                raise ValueError("num_workers must be an int")
            if min_workers is not None and not isinstance(min_workers, int):
                raise ValueError("min_workers must be an int")
            if max_workers is not None and not isinstance(max_workers, int):
                raise ValueError("max_workers must be an int")
            if spark_env_variables is None:
                spark_env_variables = {'PYSPARK_PYTHON': '/databricks/python3/bin/python3'}
        else:
            if not isinstance(existing_cluster_id, str):
                raise ValueError("existing_cluster_id must be a string")

        if notebook_path is not None:
            if not isinstance(notebook_path, str):
                raise ValueError("notebook_path must be a string")
            if python_script_path is not None or main_class_name is not None or python_script_name is not None:
                raise ValueError("Exactly one of notebook_path, python_script_path, python_script_name or "
                                 "main_class_name is required")
        if python_script_path is not None:
            if not isinstance(python_script_path, str):
                raise ValueError("python_script_path must be a string")
            if notebook_path is not None or main_class_name is not None or python_script_name is not None:
                raise ValueError("Exactly one of notebook_path, python_script_path, python_script_name or "
                                 "main_class_name is required")
        if main_class_name is not None:
            if not isinstance(main_class_name, str):
                raise ValueError("main_class_name must be a string")
            if notebook_path is not None or python_script_path is not None or python_script_name is not None:
                raise ValueError("Exactly one of notebook_path, python_script_path, python_script_name or "
                                 "main_class_name is required")
        if python_script_name is not None:
            if not isinstance(python_script_name, str):
                raise ValueError("python_script_name must be a string")
            if notebook_path is not None or python_script_path is not None or main_class_name is not None:
                raise ValueError("Exactly one of notebook_path, python_script_path, python_script_name or "
                                 "main_class_name is required")
            if source_directory is None:
                raise ValueError("If python_script_name is specified then source_directory must be too")

        if notebook_path is None and python_script_path is None and main_class_name is None and \
                python_script_name is None:
            raise ValueError("Exactly one of notebook_path, python_script_path, python_script_name or "
                             "main_class_name is required")

        if notebook_path is not None and notebook_params is None:
            notebook_params = {}
        if python_script_path is not None and python_script_params is None:
            python_script_params = []
        if python_script_name is not None and python_script_params is None:
            python_script_params = []
        if main_class_name is not None and jar_params is None:
            jar_params = []
        if compute_target is None:
            raise ValueError('compute_target is required')

        if isinstance(compute_target, str):
            compute_name = compute_target
        else:
            compute_name = compute_target.name
        self._allow_reuse = allow_reuse
        self._version = version
        self._params = dict()

        # add params
        if timeout_seconds is not None:
            if not isinstance(timeout_seconds, int):
                raise ValueError("timeout_seconds must be an int")
            self._params["timeout_seconds"] = timeout_seconds
        if run_name is not None:
            if not isinstance(run_name, str):
                raise ValueError("run_name must be a string")
            self._params["run_name"] = run_name

        if existing_cluster_id is None:
            self._params["spark_version"] = spark_version
            self._params["node_type_id"] = node_type
            if num_workers is not None:
                self._params["num_workers"] = num_workers
            else:
                self._params["max_workers"] = max_workers
                self._params["min_workers"] = min_workers

            if spark_env_variables is not None:
                self._params["spark_env_vars"] = ";".join('{0}={1}'.format(key, value) for key, value in
                                                          spark_env_variables.items())
            if spark_conf is not None:
                self._params["spark_conf"] = ";".join('{0}={1}'.format(key, value) for key, value in
                                                      spark_conf.items())
            if init_scripts is not None:
                if not isinstance(init_scripts, list):
                    raise ValueError('init_scripts should be a list of strings')
                else:
                    self._params["init_scripts"] = ",".join(i for i in init_scripts)
        else:
            self._params["existing_cluster_id"] = existing_cluster_id

        if notebook_path is not None:
            self._params["notebook_path"] = notebook_path
            parameters = ";".join('{0}={1}'.format(key, value) for key, value in notebook_params.items())
            if parameters is not "":
                self._params["base_parameters"] = parameters

        if python_script_path is not None:
            self._params["python_script_path"] = python_script_path
            if python_script_params:
                self._params["python_script_params"] = self._encode_string_params(python_script_params)

        if main_class_name is not None:
            self._params["main_class_name"] = main_class_name
            if jar_params:
                self._params["jar_params"] = self._encode_string_params(jar_params)

        if python_script_name is not None:
            self._params["python_script_name"] = python_script_name
            if python_script_params:
                self._params["python_script_params"] = self._encode_string_params(python_script_params)
            self._source_directory = source_directory
            self._hash_paths = hash_paths or []

            if self._hash_paths:
                logging.warning("Parameter 'hash_paths' will be deprecated. All files under source_directory " +
                                "will be hashed except files listed in .amlignore or .gitignore.")

            self._create_folder_module = True
        else:
            self._create_folder_module = False

        j_libraries = ",".join(j.library for j in jar_libraries)
        if j_libraries is not "":
            self._params["jar_libraries"] = j_libraries
        e_libraries = ",".join(e.library for e in egg_libraries)
        if e_libraries is not "":
            self._params["egg_libraries"] = e_libraries
        p_libraries = self._serialize_pypi_libraries(pypi_libraries)
        if p_libraries is not "":
            self._params["pypi_libraries"] = p_libraries
        r_libraries = self._serialize_rcran_libraries(rcran_libraries)
        if r_libraries is not "":
            self._params["rcran_libraries"] = r_libraries
        m_libraries = self._serialize_maven_libraries(maven_libraries)
        if m_libraries is not "":
            self._params["maven_libraries"] = m_libraries

        self._params["compute_name"] = compute_name

        self._pipeline_params_in_step_params = PipelineStep._get_pipeline_parameters_step_params(self._params)
        PipelineStep._process_pipeline_io(None, inputs, outputs)
        super(self.__class__, self).__init__(name, inputs, outputs)

    def __str__(self):
        """
        __str__ override.

        :return: str representation of the Databricks step.
        :rtype: str
        """
        result = "DatabricksStep_{0}".format(self.name)
        return result

    def __repr__(self):
        """
        Return __str__.

        :return: str representation of the Databricks step.
        :rtype: str
        """
        return self.__str__()

    def create_node(self, graph, default_datastore, context):
        """
        Create a node from this Databricks step and add to the given graph.

        :param graph: The graph object to add the node to.
        :type graph: azureml.pipeline.core.graph.Graph
        :param default_datastore: default datastore
        :type default_datastore: azureml.core.AbstractAzureStorageDatastore, azureml.core.AzureDataLakeDatastore
        :param context: The graph context.
        :type context: _GraphContext

        :return: The created node.
        :rtype: azureml.pipeline.core.graph.Node
        """
        input_bindings, output_bindings = self.create_input_output_bindings(self._inputs, self._outputs,
                                                                            default_datastore)

        param_defs = []
        for param_name in self._params:
            is_metadata_param = param_name != "notebook_path" and \
                param_name != "base_parameters" and \
                param_name != "python_script_path" and \
                param_name != "python_script_params" and \
                param_name != "main_class_name" and \
                param_name != "jar_params" and \
                param_name != "python_script_name"

            param_defs.append(ParamDef(param_name, self._params[param_name],
                                       is_metadata_param=is_metadata_param))

        module_def = self.create_module_def(execution_type="databrickscloud", input_bindings=input_bindings,
                                            output_bindings=output_bindings, param_defs=param_defs,
                                            allow_reuse=self._allow_reuse, version=self._version)
        if self._create_folder_module:
            source_directory, hash_paths = self.get_source_directory_and_hash_paths(
                context, self._source_directory, self._params["python_script_name"], self._hash_paths)

            hash_paths.append(source_directory)

            module_builder = _FolderModuleBuilder(
                content_root=source_directory,
                hash_paths=hash_paths,

                context=context,
                module_def=module_def)
        else:
            module_builder = _InterfaceModuleBuilder(
                context=context,
                module_def=module_def)

        node = graph.add_module_node(name=self.name, input_bindings=input_bindings, output_bindings=output_bindings,
                                     param_bindings=self._params, module_builder=module_builder)
        PipelineStep. \
            _configure_pipeline_parameters(graph, node,
                                           pipeline_params_in_step_params=self._pipeline_params_in_step_params)
        return node

    @staticmethod
    def _runconfig_cluster_present(runconfig):
        if (runconfig is not None and runconfig.environment is not None and
                runconfig.environment.databricks is not None and runconfig.environment.databricks.cluster is not None):
            return True
        else:
            return False

    @staticmethod
    def _get_libraries_from_runconfig(runconfig):
        """Extract libraries from runconfig.

        :param runconfig: Runconfig to use
        :type runconfig: azureml.core.runconfig.RunConfiguration

        :return: libraries dictionary
        :rtype: dict[str, list]
        """
        if runconfig is not None and \
                runconfig.environment is not None and \
                runconfig.environment.databricks is not None:
            return {'maven_libraries': runconfig.environment.databricks.maven_libraries,
                    'pypi_libraries': runconfig.environment.databricks.pypi_libraries,
                    'rcran_libraries': runconfig.environment.databricks.rcran_libraries,
                    'jar_libraries': runconfig.environment.databricks.jar_libraries,
                    'egg_libraries': runconfig.environment.databricks.egg_libraries}
        else:
            return {'maven_libraries': [],
                    'pypi_libraries': [],
                    'rcran_libraries': [],
                    'jar_libraries': [],
                    'egg_libraries': []}

    @staticmethod
    def _serialize_maven_libraries(maven_libraries):
        maven_lib_serialized = []
        for m in maven_libraries:
            # coordinates is the only required field
            if not m.repo and not m.exclusions:
                maven_lib_serialized.append('coordinates={0}'.format(m.coordinates))
            elif m.repo and not m.exclusions:
                maven_lib_serialized.append('coordinates={0}|repo={1}'.format(m.coordinates, m.repo))
            elif not m.repo and m.exclusions:
                maven_lib_serialized.append('coordinates={0}|exclusions={1}'.format(m.coordinates,
                                                                                    ','.join(m.exclusions)))
            else:
                # All fields are present
                maven_lib_serialized.append('coordinates={0}|repo={1}|exclusions={2}'.format(m.coordinates, m.repo,
                                                                                             ','.join(m.exclusions)))
        return ";".join(maven_lib_serialized)

    @staticmethod
    def _serialize_pypi_libraries(pypi_libraries):
        pypi_lib_serialized = []
        for p in pypi_libraries:
            if p.repo:
                pypi_lib_serialized.append('package={0}|repo={1}'.format(p.package, p.repo))
            else:
                pypi_lib_serialized.append('package={0}'.format(p.package))
        return ";".join(pypi_lib_serialized)

    @staticmethod
    def _serialize_rcran_libraries(rcran_libraries):
        rcran_lib_serialized = []
        for r in rcran_libraries:
            if r.repo:
                rcran_lib_serialized.append('package={0}|repo={1}'.format(r.package, r.repo))
            else:
                rcran_lib_serialized.append('package={0}'.format(r.package))
        return ";".join(rcran_lib_serialized)

    @staticmethod
    def _encode_string_params(params_list):
        r"""
        Convert a list of strings to a string.

        Replace every instance of | with |- then join all strings using ||.
        Eg. ["arg1", "arg||2"] -> "arg1||arg|-|-2".

        :param params_list: List of parameters
        :type params_list: list(str)

        :return: Encoded string
        :rtype: str
        """
        params_list = [param.replace("|", "|-") for param in params_list]
        return "||".join(params_list)
