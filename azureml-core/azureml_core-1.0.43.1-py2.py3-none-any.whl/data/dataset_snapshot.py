# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""A module for managing DatasetSnapshot operations."""

from collections import OrderedDict
from azureml.data.dataset_type_definitions import HistogramCompareMethod


class DatasetSnapshot(object):
    """A class for managing DatasetSnapshot operations."""

    def __init__(self, workspace, snapshot_name, dataset_id, definition_version=None, time_stamp=None,
                 profile_action_id=None, datastore_name=None, relative_path=None, dataset_name=None):
        """Datasetsnapshot is a combination of Profile and an optional materialized copy of the data.

        To learn more about Dataset Snapshots, go to https://aka.ms/azureml/howto/createsnapshots

        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace.
        :param snapshot_name: The name of the Dataset snapshot.
        :type snapshot_name: str
        :param dataset_id: The identifier of the Dataset.
        :type dataset_id: str
        :param definition_version: Definition version of the Dataset.
        :type definition_version: str
        :param time_stamp: Snapshot creation time.
        :type time_stamp: datetime
        :param profile_action_id: Snapshot profile action id.
        :type profile_action_id: str
        :param datastore_name: Snapshot data store name.
        :type datastore_name: str
        :param relative_path: Snapshot data relative path
        :type relative_path: str
        :param dataset_name: The name of the Dataset.
        :type dataset_name: str
        """
        from azureml.core import Dataset

        self._workspace = workspace
        self._name = snapshot_name
        self._dataset_id = dataset_id
        self._definition_version = definition_version
        self._time_stamp = time_stamp
        self._profile_action_id = profile_action_id
        self._datastore_name = datastore_name
        self._relative_path = relative_path

        # This is a hack, we should either return the dataset name in the DTO or remove the _dataset_name field.
        dataset = Dataset.get(workspace, id=dataset_id)
        self._dataset_name = dataset_name or dataset.name

    @property
    def name(self):
        """Return the Dataset snapshot name.

        :return: Dataset snapshot name.
        :rtype: str
        """
        return self._name

    @property
    def workspace(self):
        """AML workspace where the Dataset is registered.

        :return: The workspace.
        :rtype: azureml.core.Workspace
        """
        return self._workspace

    @property
    def dataset_id(self):
        """Dataset identifier.

        :return: Dataset id.
        :rtype: str
        """
        return self._dataset_id

    def get_profile(self):
        """Get the profile of the Dataset snapshot.

        :return: DataProfile of the Dataset snapshot
        :rtype: azureml.dataprep.DataProfile
        """
        return DatasetSnapshot._client().get_profile(
            workspace=self._workspace,
            dataset_id=self._dataset_id,
            version_id=self._definition_version,
            snapshot_name=self._name,
            action_id=self._profile_action_id)

    def to_pandas_dataframe(self):
        """Create a Pandas dataframe by loading the data saved with the snapshot.

        .. remarks::

            The Pandas DataFrame is fully materialized in memory. If the snapshot was created
            with create_data_snapshot=False, will throw an exception. To check if the snapshot
            contains data, use :func: is_data_snapshot_available.

        :return: A Pandas DataFrame.
        :rtype: pandas.core.frame.DataFrame
        """
        return self._get_dataflow().to_pandas_dataframe()

    def to_spark_dataframe(self):
        """Create a Spark DataFrame by loading the data saved with the snapshot.

        .. remarks::

            The Spark Dataframe returned is only an execution plan and does not actually contain any data,
            as Spark Dataframes are lazily evaluated. If the snapshot was created with
            create_data_snapshot=False, will throw an exception when you try to access the data.To check if
            the snapshot contains data, use :func: is_data_snapshot_available.

        :return: A Spark DataFrame.
        :rtype: pyspark.sql.DataFrame
        """
        return self._get_dataflow().to_spark_dataframe()

    def get_status(self):
        """Get the Dataset snapshot creation status.

        :return: Status of Dataset snapshot
        :rtype: str
        """
        return DatasetSnapshot._client()._get_snapshot_status(
            workspace=self._workspace,
            dataset_id=self._dataset_id,
            profile_action_id=self._profile_action_id)

    @staticmethod
    def get(workspace, snapshot_name, dataset_name=None, dataset_id=None):
        """Get the snapshot of Dataset by snapshot name.

        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        :param snapshot_name: The name of the Dataset snapshot.
        :type snapshot_name: str
        :param dataset_name: The name of the Dataset.
        :type Dataset_name: str
        :param dataset_id: Identifier of the Dataset.
        :type dataset_id: uuid
        :return: Dataset snapshot
        :rtype: azureml.data.DatasetSnapshot
        """
        return DatasetSnapshot._client().get_snapshot(
            workspace=workspace,
            snapshot_name=snapshot_name,
            dataset_id=dataset_id,
            dataset_name=dataset_name)

    @staticmethod
    def get_all(workspace, dataset_name):
        """Get all the snapshots of the given Dataset.

        :param workspace: The workspace.
        :type workspace: azureml.core.Workspace
        :param dataset_name: The name of the Dataset.
        :type Dataset_name: str
        :return: List of Dataset snapshots
        :rtype: List[azureml.data.DatasetSnapshot]
        """
        return DatasetSnapshot._client().get_all_snapshots(workspace=workspace, dataset_name=dataset_name)

    def _get_dataflow(self):
        """Get the dataflow from Dataset snapshot.

        :return: Dataflow object
        :rtype: azureml.dataprep.Dataflow
        """
        if self._datastore_name is None or self._relative_path is None:
            raise Exception(
                """Data copy is not available.
                Create snapshot with flag 'create_data_snapshot=True' to save the copy of the data.""")

        return DatasetSnapshot._client()._get_dataflow(self._workspace, self._datastore_name, self._relative_path)

    def compare_profiles(
            self,
            rhs_dataset_snapshot,
            include_columns=None,
            exclude_columns=None,
            histogram_compare_method=HistogramCompareMethod.WASSERSTEIN):
        """
        Compare the current dataset profile with rhs_dataset profile.

        If profiles do not exists this method will raise an exception.

        :param rhs_dataset_snapshot: Dataset snapshot to compare with.
        :type rhs_dataset_snapshot: azureml.data.dataset_snapshot.DatasetSnapshot
        :param include_columns: List of column names to be included in comparison.
        :type include_columns: List[str]
        :param exclude_columns: List of column names to be excluded in comparison.
        :type exclude_columns: List[str]
        :param histogram_compare_method: Enum describing the method, ex: WASSERSTEIN or ENERGY
        :type histogram_compare_method: azureml.data.dataset_type_definitions.HistogramCompareMethod
        :return: Difference of the profiles.
        :rtype: azureml.dataprep.api.typedefinitions.DataProfileDifference
        """
        return DatasetSnapshot._client().compare_dataset_snapshot_profiles(
            lhs_dataset_snapshot=self,
            rhs_dataset_snapshot=rhs_dataset_snapshot,
            compute_target=None,
            include_columns=include_columns,
            exclude_columns=exclude_columns,
            dataset_snapshot_name=self._name,
            histogram_compare_method=histogram_compare_method)

    def wait_for_completion(self, show_output=True, status_update_frequency=10):
        """Wait for the completion of DatasetSnapshot generaton.

        :param show_output: If True the method will print the output, optional
        :type show_output: bool
        :param status_update_frequency: Action run status update frequency in seconds, optional
        :type status_update_frequency: int
        """
        DatasetSnapshot._client()._wait_for_completion(
            workspace=self._workspace,
            dataset_id=self._dataset_id,
            action_id=self._profile_action_id,
            show_output=show_output,
            status_update_frequency=status_update_frequency)

    def is_data_snapshot_available(self):
        """Check if the materialized copy of the snapshot is available.

        :return: True if data snapshot is available.
        :rtype: bool
        """
        return self._datastore_name is not None and self.get_status() == "Completed"

    def __str__(self):
        """Format DatasetSnapshot data into a string.

        :return:
        :rtype: str
        """
        info = self._get_base_info_dict()
        formatted_info = ',\n'.join(["{}: {}".format(k, v) for k, v in info.items()])
        return "DatasetSnapshot({0})".format(formatted_info)

    def __repr__(self):
        """Representation of the object.

        :return: Return the string form of the DatasetSnapshot object
        :rtype: str
        """
        return self.__str__()

    def _get_base_info_dict(self):
        """Return base info dictionary.

        :return:
        :rtype: OrderedDict
        """
        return OrderedDict([
            ('Name', self._name),
            ('Dataset Id', self._dataset_id),
            ('Workspace', self._workspace.name),
            ('Dataset definition version', self._definition_version),
            ('Snapshot created date', self._time_stamp)
        ])

    @staticmethod
    def _client():
        """Get a Dataset client.

        :return: Returns the client
        :rtype: DatasetClient
        """
        from ._dataset_client import _DatasetClient
        return _DatasetClient
