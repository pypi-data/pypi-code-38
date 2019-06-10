# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Dataset module manages the interactions with Azure Machine Learning Datasets.

This module provides methods for creating, managing data and performing actions on data.
"""

from azureml.data.dataset_type_definitions import (
    HistogramCompareMethod,
    PromoteHeadersBehavior,
    SkipLinesBehavior,
    FileEncoding)
from collections import OrderedDict


class Dataset(object):
    """The Dataset class is a resource for exploring, transforming and managing data in Azure Machine Learning.

    You can explore your data with summary statistics and transform it using intelligent transforms.
    When you are ready to use the data for training, you can save the Dataset to your AzureML workspace to get
    versioning and reproducibility capabilities.

    To learn more about Azure ML Datasets, go to: https://aka.ms/azureml/concepts/datasets.
    """

    def __init__(self, definition, workspace=None, name=None, id=None):
        """Initialize the Dataset object.

        To obtain a Dataset that has already been registered with the workspace, use the get method.

        :param definition: The Dataset definition.
        :type definition: azureml.data.DatasetDefinition
        :param workspace: The workspace in which the Dataset exists
        :type workspace: azureml.core.Workspace, optional
        :param name: The name of the Dataset.
        :type name: str, optional
        :param id: The unique identifier of the Dataset.
        :type id: str, optional
        :return: The corresponding Dataset for the definition.
        :rtype: azureml.core.dataset.Dataset
        """
        self._definition = definition
        self._workspace = workspace
        self._name = name
        self._id = id
        self._is_visible = True
        self._tags = {}
        self._description = None
        self._state = None
        self._deprecated_by_dataset_id = None
        self._deprecated_by_definition = None

    @property
    def name(self):
        """Return the Dataset name.

        :return: Dataset name.
        :rtype: str
        """
        return self._name

    @property
    def workspace(self):
        """If the Dataset was registered in an AzureML workspace, return that. Otherwise, returns None.

        :return: The workspace.
        :rtype: azureml.core.Workspace
        """
        return self._workspace

    @property
    def id(self):
        """If the Dataset was registered in an AzureML workspace, return the ID of the Dataset. Otherwise, return None.

        :return: Dataset id.
        :rtype: str
        """
        return self._id

    @property
    def definition_version(self):
        """Return the version of the current definition of the Dataset.

        .. remarks::

            A Dataset definition is a series of steps that specify how to read and transform data.

            A Dataset registered in an AzureML workspace can have multiple definitions, each created by calling
            :func: ~azureml.core.dataset.Dataset.update_definition. Each definition has an unique identifier. The
            current definition is the latest one created, whose id is returned by this.

            For unregistered Datasets, only one definition exists.

        :return: Dataset definition version.
        :rtype: str
        """
        if self.definition is None:
            return None
        return self.definition._version_id

    @property
    def definition(self):
        """Return the current Dataset definition.

        .. remarks::

            A Dataset definition is a series of steps that specify how to read and transform data.

            A Dataset registered in an AzureML workspace can have multiple definitions, each created by calling
            :func: ~azureml.core.dataset.Dataset.update_definition. Each definition has an unique identifier. Having
            multiple definitions allows you to make changes to existing Datasets without breaking models and
            pipelines that depend on the older definition.

            For unregistered Datasets, only one definition exists.

        :return: Dataset definition.
        :rtype: azureml.data.dataset_definition.DatasetDefinition
        """
        if self._definition is None and self.id is not None:
            self._definition = self.get_definition()
        return self._definition

    @property
    def is_visible(self):
        """Control the visibility of a registered Dataset in the Azure ML workspace UI.

        .. remarks::

            +----------+---------------------------------------+
            |  Value   |              Behavior                 |
            +----------+---------------------------------------+
            |   true   |  Default. Dataset is visible in       |
            |          |  Workspace UI.                        |
            +----------+---------------------------------------+
            |  false   |  Dataset is hidden in Workspace UI.   |
            +----------+---------------------------------------+

            Has no effect on unregistered Datasets.

        :return: Dataset visibility.
        :rtype: bool
        """
        return self._is_visible

    @property
    def tags(self):
        """Return the tags associated with the Dataset.

        :return: Dataset tags.
        :rtype: dict[str, str]
        """
        return self._tags

    @property
    def description(self):
        """Return the description of the Dataset.

        .. remarks::

            Description of the data in the Dataset. Filling it in allows users of the workspace to
            understand what the data represents, and how they can use it.

        :return: Dataset description.
        :rtype: str
        """
        return self._description

    @property
    def state(self):
        """Return the state of the Dataset.

            +------------+------------------------------------------------------------------------------+
            |    State   |                      Meaning and effect                                      |
            +------------+------------------------------------------------------------------------------+
            | Active     | Active definitions are exactly what they sound like, all actions can be      |
            |            | performed on active definitions.                                             |
            +------------+------------------------------------------------------------------------------+
            | Deprecated | A deprecated definition can be used, but will result in a warning being      |
            |            | logged in the logs everytime the underlying data is accessed.                |
            +------------+------------------------------------------------------------------------------+
            | Archived   | An archived definition cannot be used to perform any action. To perform      |
            |            | actions on an archived definition, it must be reactivated.                   |
            +------------+------------------------------------------------------------------------------+

        :return: Dataset state.
        :rtype: str
        """
        return self._state

    @staticmethod
    def get(workspace, name=None, id=None):
        """Get a Dataset that already exists in the workspace by specifying either its name or id.

        .. remarks::

            You can provide either name or id.
            If both are given, will throw an exception if name and id are not matching.
            Will throw an exception if the Dataset with the specified name or id cannot
            be found in the workspace.

        :param workspace: The existing AzureML workspace in which the Dataset was created.
        :type workspace: azureml.core.Workspace
        :param name: The name of the Dataset to be retrieved.
        :type name: str, optional
        :param id: Unique Identifier of the Dataset in the workspace.
        :type id: str, optional
        :return: Dataset with the specified name or id.
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset._client().get(workspace, name, id)

    @staticmethod
    def list(workspace):
        """List all of the Datasets in the workspace, including ones with is_visible=False.

        :param workspace: The :class: azureml.core.Workspace for which you want to retrieve the list of Datasets
        :type workspace: azureml.core.Workspace
        :return: List of Dataset objects
        :rtype: List[azureml.core.dataset.Dataset]
        """
        return Dataset._client().list(workspace)

    def get_definitions(self):
        """Get all the definitions of the Dataset.

        .. remarks::

            A Dataset registered in an AzureML workspace can have multiple definitions, each created by calling
            :func: ~azureml.core.dataset.Dataset.update_definition. Each definition has an unique identifier. The
            current definition is the latest one created.

            For unregistered Datasets, only one definition exists.

        :return: Dictionary of Dataset definitions
        :rtype: Dict[str, azureml.data.dataset_definition.DatasetDefinition]
        """
        if self.id is None:
            return [self.definition]
        return Dataset._client().get_dataset_definitions(self)

    def get_definition(self, version_id=None):
        """Get a specific definition of the Dataset.

        .. remarks::

            If version_id is provided, then try to get the definition corresponding to that version.
            If that version does not exist, will throw an exception.
            If version_id is omitted, then retrieves the latest version.

        :param version_id: The version_id of the Dataset definition
        :type version_id: str, optional
        :return: Dataset definition
        :rtype: azureml.data.dataset_definition.DatasetDefinition
        """
        if self.id is None:
            return self.definition

        return Dataset._client().get_dataset_definition(self, version_id)

    @staticmethod
    def from_pandas_dataframe(
            dataframe,
            path=None):
        """Create unregistered, in-memory Dataset from pandas dataframe.

        .. remarks::
            Use this method to convert pandas dataframe to Dataset.
            Dataset created by this method can not be registered as the data is from memory.

            Pandas frame is converted to csv file locally and, If path is DataRefernce,
            then pandas frame will be uploaded to data store, and create a Dataset based of the DataReference.
            If path is local folder, Dataset will be created off of local file. which cannot be deleted.

            Raises exception, if the current Datareference is not a folder path.

        :param dataframe: Pandas DataFrame
        :type dataframe: pandas.DataFrame
        :param path: Data path in registered datastore or local folder path.
        :type path: azureml.data.data_reference.DataReference or str
        :return: Dataset object.
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset._client().from_pandas_dataframe(dataframe, path)

    @staticmethod
    def from_delimited_files(
            path,
            separator=',',
            header=PromoteHeadersBehavior.ALL_FILES_HAVE_SAME_HEADERS,
            encoding=FileEncoding.UTF8,
            quoting=False,
            infer_column_types=True,
            skip_rows=0,
            skip_mode=SkipLinesBehavior.NO_ROWS,
            comment=None,
            include_path=False,
            archive_options=None):
        """Create unregistered, in-memory Dataset from delimited files.

        .. remarks::

            Use this method to read delimited text files when you want to control the options used.

            After creating a Dataset, you should use :func: ~azureml.core.dataset.Dataset.get_profile to list
            detected column types and summary statistics for each column.

            The returned Dataset is not registered with the workspace.

        :param path: Data path in registered datastore or local path.
        :type path: azureml.data.data_reference.DataReference or str
        :param separator: The separator used to split columns.
        :type separator: str
        :param header: Controls how column headers are promoted when reading from files.
        :type header: :class: azureml.contrib.dataset.PromoteHeadersBehavior, optional
        :param encoding: The encoding of the files being read.
        :type encoding: :class: azureml.dataprep.FileEncoding, optional
        :param quoting: Specify how to handle new line characters within quotes.
            The default (False) is to interpret new line characters as starting new rows, irrespective of whether
            the new line characters are within quotes or not.
            If set to True, new line characters inside quotes will not result in new rows, and file reading
            speed will slow down.
        :type quoting: bool, optional
        :param infer_column_types: If true, column data types will be inferred.
        :type infer_column_types: bool, optional
        :param skip_rows: How many rows to skip in the file(s) being read.
        :type skip_rows: int, optional
        :param skip_mode: Controls how rows are skipped when reading from files.
        :type skip_mode: :class: azureml.core.dataset.SkipLinesBehavior, optional
        :param comment: Character used to indicate comment lines in the files being read.
            Lines beginning with this string will be skipped
        :type comment: str, optional
        :param include_path: Whether to include a column containing the path of the file from which the data was read.
            This is useful when you are reading multiple files, and want to know which file a particular record
            originated from, or to keep useful information in file path.
        :type include_path: bool, optional
        :param archive_options: Options for archive file, including archive type and entry glob pattern.
            We only support ZIP as archive type at the moment. For example, specifying

            .. code-block:: python

                archive_options = ArchiveOptions(archive_type = ArchiveType.ZIP, entry_glob = '*10-20.csv')

            reads all files with name ending with "10-20.csv" in ZIP.
        :type archive_options: azureml.dataprep.api._archiveoption.ArchiveOptions
        :return: Dataset object.
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset._client().from_delimited_files(
            path=path,
            separator=separator,
            header=header,
            encoding=encoding,
            quoting=quoting,
            infer_column_types=infer_column_types,
            skip_rows=skip_rows,
            skip_mode=skip_mode,
            comment=comment,
            include_path=include_path,
            archive_options=archive_options)

    @staticmethod
    def auto_read_files(path, include_path=False):
        """Analyzes the file(s) at the specified path and returns a new Dataset.

        .. remarks::

            Use this method when you'd like to have file formats and delimiters detected automatically.

            After creating a Dataset, you should use :func: ~azureml.core.Dataset.get_profile to list
            detected column types and summary statistics for each column.

            The returned Dataset is not registered with the workspace.


        :param path: Data path in registered datastore or local path.
        :type path: azureml.data.data_reference.DataReference or str
        :param include_path: Whether to include a column containing the path of the file from which the data was read.
            Useful when reading multiple files, and want to know which file a particular record originated from.
            Also useful if there is information in file path or name that you want in a column.
        :type include_path: bool, optional
        :return: Dataset object.
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset._client().auto_read_files(path, include_path)

    @staticmethod
    def from_parquet_files(path, include_path=False):
        """Create unregistered, in-memory Dataset from parquet files.

        .. remarks::

            Use this method to read Parquet files.

            After creating a Dataset, you should use :func: ~azureml.core.dataset.Dataset.get_profile to list
            detected column types and summary statistics for each column.

            The returned Dataset is not registered with the workspace.

        :param path: Data path in registered datastore or local path.
        :type path: azureml.data.data_reference.DataReference or str
        :param include_path: Whether to include a column containing the path of the file from which the data was read.
            This is useful when you are reading multiple files, and want to know which file a particular record
            originated from, or to keep useful information in file path.
        :type include_path: bool, optional
        :return: Dataset object.
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset._client().from_parquet_files(path, include_path)

    @staticmethod
    def from_excel_files(
            path,
            sheet_name=None,
            use_column_headers=False,
            skip_rows=0,
            include_path=False,
            infer_column_types=True):
        """Create unregistered, in-memory Dataset from Excel files.

        .. remarks::

            Use this method to read Excel files in .xlsx format. Data can be read from one sheet in each Excel file.
            After creating a Dataset, you should use :func: ~azureml.core.dataset.Dataset.get_profile to list
            detected column types and summary statistics for each column. The returned Dataset is not registered
            with the workspace.

        :param path: Data path in registered datastore or local path.
        :type path: azureml.data.data_reference.DataReference or str
        :param sheet_name: The name of the Excel sheet to load.
            By default we read the first sheet from each Excel file.
        :type sheet_name: str, optional
        :param use_column_headers: Controls whether to use the first row as column headers.
        :type use_column_headers: bool, optional
        :param skip_rows: How many rows to skip in the file(s) being read.
        :type skip_rows: int, optional
        :param include_path: Whether to include a column containing the path of the file from which the data was read.
            This is useful when you are reading multiple files, and want to know which file a particular record
            originated from, or to keep useful information in file path.
        :type include_path: bool, optional
        :param infer_column_types: If true, column data types will be inferred.
        :type infer_column_types: bool, optional
        :return: Dataset object.
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset._client().from_excel_files(
            path,
            sheet_name,
            use_column_headers,
            skip_rows,
            include_path,
            infer_column_types)

    @staticmethod
    def from_binary_files(path):
        """Create unregistered, in-memory Dataset from binary files.

        .. remarks::

            Use this method to read files as streams of binary data. Returns one file stream object per
                file read. Use this method when you're reading images, videos, audio or other binary data.

            :func: ~azureml.core.dataset.Dataset.get_profile and :func: ~azureml.core.dataset.Dataset.create_snapshot
                will not work as expected for a Dataset created by this method.

            The returned Dataset is not registered with the workspace.

        :param path: Data path in registered datastore or local path.
        :type path: azureml.data.data_reference.DataReference or str
        :return: Dataset object.
        :rtype: azureml.core.dataset.Dataset

        """
        return Dataset._client().from_binary_files(path)

    @staticmethod
    def from_sql_query(data_source, query):
        """Create unregistered, in-memory Dataset from sql query.

        :param data_source: The details of the Azure SQL datastore.
        :type data_source: azureml.data.azure_sql_database_datastore.AzureSqlDatabaseDatastore
        :param query: The query to execute to read data.
        :type query: str
        :return: Local Dataset object.
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset._client().from_sql_query(data_source, query)

    @staticmethod
    def from_json_files(path, encoding=FileEncoding.UTF8, flatten_nested_arrays=False, include_path=False):
        """Create unregistered, in-memory Dataset from json files.

        :param path: The path to the file(s) or folder(s) that you want to load and parse. It can either be a
            local path or an Azure Blob url. Globbing is supported. For example, you can use path = "./data*" to
            read all files with name starting with "data".
        :type path: azureml.data.data_reference.DataReference or str
        :param encoding: The encoding of the files being read.
        :type encoding: azureml.dataprep.typedefinitions.FileEncoding
        :param flatten_nested_arrays: Property controlling program's handling of nested arrays.
            If you choose to flatten nested JSON arrays, it could result in a much larger number of rows.
        :type flatten_nested_arrays: bool, optional
        :param include_path: Whether to include a column containing the path from which the data was read.
            This is useful when you are reading multiple files, and might want to know which file a particular record
            originated from, or to keep useful information in file path.
        :type include_path: bool, optional
        :return: Local Dataset object.
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset._client().from_json_files(
            path=path,
            encoding=encoding,
            flatten_nested_arrays=flatten_nested_arrays,
            include_path=include_path)

    def register(self, workspace, name, description=None, tags=None,
                 visible=True, exist_ok=False, update_if_exist=False):
        """Register the Dataset in the workspace, making it available to other users of the workspace.

        :param workspace: The AzureML workspace in which the Dataset is to be registered
        :type workspace: azureml.core.Workspace
        :param name: The name of the Dataset in the workspace
        :type name: str
        :param description: Description of the Dataset.
        :type description: str, optional
        :param tags: Tags to associate with the Dataset.
        :type tags: dict[str,str], optional
        :param visible: Controls visibility of the Dataset to the user in the UI.
            false=hidden in UI, available via SDK.
        :type visible: bool, optional
        :param exist_ok: If True the method returns the Dataset if it already exists in the given workspace, else error
        :type exist_ok: bool, optional
        :param update_if_exist: If exist_ok is True and update_if_exist is True, this method will update
            the definition and return the updated Dataset.
        :type update_if_exist: bool, optional
        :return: Registered Dataset object in the workspace.
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset._client().register(
            workspace, name, self.definition, description, tags, visible, exist_ok, update_if_exist)

    def update(self, name=None, description=None, tags=None, visible=None):
        """Update the Dataset mutable attributes in the workspace and return the updated Dataset from the workspace.

        :param name: The name of the Dataset in the workspace.
        :type name: str, optional
        :param description: Description of the data.
        :type description: str, optional
        :param tags: Tags to associate the Dataset with.
        :type tags: dict[str,str], optional
        :param visible: Visibility of the Dataset to the user in the UI.
        :type visible: bool, optional
        :return: Updated Dataset object from the workspace.
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset._client().update(self.workspace, self.id, name, description, tags, visible)

    def update_definition(self, definition, definition_update_message):
        """Update the Dataset definition.

        .. remarks::

            To consume the updated Dataset, use the object returned by this method.

        :param definition: The new definition of this Dataset.
        :type definition: azureml.data.DatasetDefinition
        :param definition_update_message: Definition update message.
        :type definition_update_message: str
        :return: Updated Dataset object from the workspace.
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset._client().update_definition(self, definition, definition_update_message)

    def to_pandas_dataframe(self):
        """Create a Pandas dataframe by executing the transformation pipeline defined by this Dataset definition.

        .. remarks::

            Return a Pandas DataFrame fully materialized in memory.

        :return: A Pandas DataFrame.
        :rtype: pandas.core.frame.DataFrame
        """
        return Dataset._client().to_pandas_dataframe(self.definition)

    def to_spark_dataframe(self):
        """Create a Spark DataFrame that can execute the transformation pipeline defined by this Dataset definition.

        .. remarks::

            The Spark Dataframe returned is only an execution plan and does not actually contain any data,
            as Spark Dataframes are lazily evaluated.

        :return: A Spark DataFrame.
        :rtype: pyspark.sql.DataFrame
        """
        return Dataset._client().to_spark_dataframe(self.definition)

    def head(self, count):
        """Pull the specified number of records specified from this Dataset and returns them as a DataFrame.

        :param count: The number of records to pull.
        :type count: int
        :return: A Pandas DataFrame.
        :rtype: pandas.core.frame.DataFrame
        """
        return Dataset._client().head(self.definition, count)

    def create_snapshot(self, snapshot_name, compute_target=None, create_data_snapshot=False, target_datastore=None):
        """Create a snapshot of the registered Dataset.

        .. remarks::

            Snapshots capture point in time summary statistics of the underlying data
                and an optional copy of the data itself. To learn more about creating snapshots,
                go to https://aka.ms/azureml/howto/createsnapshots.


        :param snapshot_name: The snapshot name. Snapshot names should be unique within a Dataset.
        :type snapshot_name: str
        :param compute_target: compute target to perform the snapshot profile creation, optional.
            If omitted, the local compute is used.
        :type compute_target: azureml.core.compute.ComputeTarget or str, optional
        :param create_data_snapshot: If True, a materialized copy of the data will be created, optional.
        :type create_data_snapshot: bool, optional
        :param target_datastore: Target datastore to save snapshot.
            If omitted, the snapshot will be created in the default storage of the workspace.
        :type target_datastore: azureml.data.azure_storage_datastore.AbstractAzureStorageDatastore or str, optional
        :return: Dataset snapshot object.
        :rtype: azureml.data.dataset_snapshot.DatasetSnapshot
        """
        return Dataset._client().create_snapshot(self.definition, snapshot_name, compute_target,
                                                 create_data_snapshot, target_datastore)

    def get_snapshot(self, snapshot_name):
        """Get snapshot of the Dataset by name.

        :param snapshot_name: The snapshot name
        :type snapshot_name: str
        :return: Dataset snapshot object.
        :rtype: azureml.data.dataset_snapshot.DatasetSnapshot
        """
        return Dataset._client().get_snapshot(self.workspace, snapshot_name, self.id)

    def delete_snapshot(self, snapshot_name):
        """Delete snapshot of the Dataset by name.

        .. remarks::
            Use this to free up storage consumed by data saved in snapshots that you no longer need.

        :param snapshot_name: The snapshot name
        :type snapshot_name: str
        :return: None.
        :rtype: None
        """
        return Dataset._client().delete_snapshot(self.workspace, snapshot_name, self.id)

    def get_all_snapshots(self):
        """Get all snapshots of the Dataset.

        :return: List of Dataset snapshots.
        :rtype: List[azureml.data.dataset_snapshot.DatasetSnapshot]
        """
        return Dataset._client().get_all_snapshots(self.workspace, self.id)

    def generate_profile(self, compute_target=None, workspace=None, arguments=None):
        """Generate new profile for the Dataset.

        .. remarks::

             Synchronous call, will block till it completes. Call :func: get_result to get the result of
                the action.

        :param compute_target: compute target to perform the snapshot profile creation, optional.
            If omitted, the local compute is used.
        :type compute_target: azureml.core.compute.ComputeTarget or str, optional
        :param workspace: Workspace, required for transient(unregistered) Datasets.
        :type workspace: azureml.core.Workspace, optional
        :param arguments: Profile arguments. Valid arguments are

            +--------------------------+--------------------+--------------------------------------+
            |         Argument         |        Type        |              Description             |
            +--------------------------+--------------------+--------------------------------------+
            |   include_stype_counts   |        bool        | Check if values look like some       |
            |                          |                    | well known semantic types            |
            |                          |                    | - email address, IP Address (V4/V6), |
            |                          |                    | US phone number, US zipcode,         |
            |                          |                    | Latitude/Longitude                   |
            |                          |                    | Turning this on impacts performance. |
            +--------------------------+--------------------+--------------------------------------+
            | number_of_histogram_bins |        int         | Number of histogram bins to use for  |
            |                          |                    | numeric data, default value is 10    |
            +--------------------------+--------------------+--------------------------------------+

        :type arguments: Dict[str,object], optional
        :return: Dataset action run object.
        :rtype: azureml.data.dataset_action_run.DatasetActionRun
        """
        return Dataset._client().generate_profile(self, compute_target, workspace, arguments)

    def get_profile(self, arguments=None, generate_if_not_exist=True, workspace=None, compute_target=None):
        """Get summary statistics on the Dataset computed earlier.

        .. remarks::

            For a Dataset registered with an AML workspace, this method retrieves an existing profile that
                was created earlier by calling :func: get_profile if it is still valid. Profiles are invalidated
                when changed data is detected in the Dataset or the arguments to get_profile are different from
                the ones used when the profile was generated. If the profile is not present or invalidated,
                generate_if_not_exist will determine if a new profile is generated.

            For a Dataset that is not registered with an AML workspace, this method always runs generate_profile
                and returns the result.

        :param arguments: Profile arguments.
        :type arguments: Dict[str,object], optional
        :param generate_if_not_exist: generate profile if it does not exist.
        :type generate_if_not_exist: bool, optional
        :param workspace: Workspace, required for transient(unregistered) Datasets.
        :type workspace: azureml.core.Workspace, optional
        :param compute_target: compute target to execute the profile action, optional.
        :type compute_target: azureml.core.compute.ComputeTarget or str, optional
        :return: DataProfile of the Dataset.
        :rtype: azureml.dataprep.DataProfile
        """
        return Dataset._client().get_profile_with_state(
            self,
            arguments,
            generate_if_not_exist,
            workspace,
            compute_target)

    def deprecate(self, deprecate_by_dataset_id):
        """Deprecate the Dataset, with a pointer to the new Dataset.

        .. remarks::

            Deprecated Datasets will log warnings when they are consumed. Deprecating a dataset deprecates all
                its definitions.

            Deprecated Datasets can still be consumed. To completely block a Dataset from being consumed, archive it.

            If deprecated by accident, reactivate will activate it.

        :param deprecate_by_dataset_id: Dataset Id which is the intended replacement for this Dataset.
        :type deprecate_by_dataset_id: str
        :return: None.
        :rtype: None
        """
        return Dataset._client().deprecate(self.workspace, self.id, self._etag, deprecate_by_dataset_id)

    def archive(self):
        """Archive the Dataset.

        .. remarks::

            After archival, any attempt to consume the Dataset will result in an error.
            If archived by accident, reactivate will activate it.

        :return: None.
        :rtype: None
        """
        return Dataset._client().archive(self.workspace, self.id, self._etag)

    def reactivate(self):
        """Reactivate the Dataset. Works on Datasets that have been deprecated or archived.

        :return: None.
        :rtype: None
        """
        return Dataset._client().reactivate(self.workspace, self.id, self._etag)

    def compare_profiles(self,
                         rhs_dataset,
                         profile_arguments=dict(),
                         include_columns=None,
                         exclude_columns=None,
                         histogram_compare_method=HistogramCompareMethod.WASSERSTEIN):
        """
        Compare the current Dataset's profile with rhs_dataset profile.

        .. remarks::

            This is for registered Datasets only.
            Raises exception, if the current Dataset's profile does not exist.
            For unregistered Datasets use profile.compare method.


        :param rhs_dataset: Another Dataset also called right hand side Dataset for comparision.
        :type rhs_dataset: azureml.core.dataset.Dataset
        :param profile_arguments: Arguments to retrive specific profile.
        :type profile_arguments: Dict, optional
        :param include_columns: List of column names to be included in comparison.
        :type include_columns: List[str], optional
        :param exclude_columns: List of column names to be excluded in comparison.
        :type exclude_columns: List[str], optional
        :param histogram_compare_method: Enum describing the method, ex: Wasserstein or Energy
        :type histogram_compare_method: azureml.data.dataset_type_definitions.HistogramCompareMethod, optional
        :return: Difference of the profiles.
        :rtype: azureml.dataprep.api.typedefinitions.DataProfileDifference
        """
        return Dataset._client().compare_dataset_profiles(
            lhs_dataset=self,
            rhs_dataset=rhs_dataset,
            profile_arguments=profile_arguments,
            compute_target=None,
            include_columns=include_columns,
            exclude_columns=exclude_columns,
            histogram_compare_method=histogram_compare_method)

    def sample(self, sample_strategy, arguments):
        """Generate a new sample from the source Dataset, using the sampling strategy and parameters provided.

        .. remarks::

            Samples are generated by executing the transformation pipeline defined by this Dataset, and then
            applying the sampling strategy and parameters to the output data.

        :param sample_strategy: Sample strategy to use: top_n, simple_random or stratified.
        :type sample_strategy: str
        :param arguments: Sample arguments.
        :type arguments: Dict[str,object]

            +-----------------------+---------------------+--------------------+-------------------------------------+
            |    Sampling method    |      Argument       |        Type        |              Description            |
            +-----------------------+---------------------+--------------------+-------------------------------------+
            |         top_n         |         n           |     integer        | Select top N rows as your sample    |
            +-----------------------+---------------------+--------------------+-------------------------------------+
            |     simple_random     |     probability     |      float         |  Simple random sampling where each  |
            |                       |                     |                    |  row has equal probability of being |
            |                       |                     |                    |  selected. Probability should be a  |
            |                       |                     |                    |  number between 0 and 1.            |
            +-----------------------+---------------------+--------------------+-------------------------------------+
            |                       |        seed         |        float       |  Used by random number generator.   |
            |                       |                     |                    |  Use if you want repeatability.     |
            +-----------------------+---------------------+--------------------+-------------------------------------+
            |      stratified       |      columns        |       List[str]    |  List of strata columns in data     |
            +-----------------------+---------------------+--------------------+-------------------------------------+
            |                       |        seed         |        float       |  Used by random number generator.   |
            |                       |                     |                    |  Use if you want repeatability.     |
            +-----------------------+---------------------+--------------------+-------------------------------------+
            |                       |      fractions      | Dict[Tuple, float] |  Tuple - column values that define  |
            |                       |                     |                    |          a stratum, must be in same |
            |                       |                     |                    |          order as column names      |
            |                       |                     |                    |  float - weight attached to         |
            |                       |                     |                    |          a stratum during sampling  |
            +-----------------------+---------------------+--------------------+-------------------------------------+

        :return: Sample Dataset object.
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset._client().sample(self, sample_strategy, arguments, self._file_type)

    def _get_datapath(self):
        return self.definition._get_datapath()

    @staticmethod
    def _from_dataflow(
            dataflow):
        """Create unregistered, in-memory Dataset from dataflow.

        .. remarks::
            Use this method to convert dataflow to Dataset.

        :param dataflow: Dataflow object.
        :type dataflow: azureml.dataprep.Dataflow
        :return: Dataset object.
        :rtype: azureml.core.dataset.Dataset
        """
        return Dataset._client()._get_dataset_from_dataflow(
            dataflow=dataflow,
            file_data_path=Dataset._client()._get_source_path(dataflow),
            file_type=Dataset._client()._get_source_file_type(dataflow))

    @staticmethod
    def _get_definition_json(workspace, dataset_name, version=None):
        return Dataset._client()._get_definition_json(workspace, dataset_name, version)

    def __str__(self):
        """Format Dataset data into a string.

        :return:
        :rtype: str
        """
        info = self._get_base_info_dict()
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "Dataset({0})".format(formatted_info)

    def __repr__(self):
        """Representation of the object.

        :return: Return the string form of the Dataset object
        :rtype: str
        """
        return self.__str__()

    def __getitem__(self, key):
        """Keep the selected columns.

        Return a new dataflow always referencing the latest definition with an additional keep_columns
        transformation of the columns specific in the argument.

        :param key: The columns to keep.
        :type key: str or list
        :raises KeyError: if key is not of type str or list.
        :return: The new Dataset definition with the keep_columns transformation.
        :rtype: azureml.dataprep.Dataflow
        """
        if isinstance(key, str):
            return self.get_definition()[[key]]
        if isinstance(key, list):
            return self.get_definition()[key]
        raise KeyError('Only string or list of strings can be used to select columns')

    def _get_base_info_dict(self):
        """Return base info dictionary.

        :return:
        :rtype: OrderedDict
        """
        return OrderedDict([
            ('Name', self.name),
            ('Workspace', self.workspace.name if self.workspace is not None else None)
        ])

    def _file_type(self):
        """Get the file type from the definition associated with Dataset.

        This is for SDK internal Use Only.
        :return: The file type.
        :rtype: str
        """
        return self.definition._file_type if self.definition is not None else None

    @staticmethod
    def _client():
        """Get Dataset client.

        :return: Returns the client
        :rtype: DatasetClient
        """
        from azureml.data._dataset_client import _DatasetClient
        return _DatasetClient

    class Scenario(object):
        """Well known constants for supported Dataset Scenarios.

        This is used by Runs, Models, and Datadrift to identify what different Datasets were used for in different
        parts of the Azure ML process.
        """

        TRAINING = "training"
        VALIDATION = "validation"
        INFERENCING = "inferencing"
