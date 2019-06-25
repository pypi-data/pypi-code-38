# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Pandas data load limit since the parquet can be too large."""

from .._utils.time_utils import day_range, month_range
from azure.storage.blob import BlockBlobService


class PandasDataLoadLimitNone:
    """PandasDataLoadLimitNone controls how many parquets will be loaded (no limit)."""

    def __init__(self):
        """Initialize _match_paths."""
        self._match_paths = None

    def _contains_match_paths(self, path):
        if self._match_paths is None:
            return True

        for match_path in self._match_paths:
            if path.find(match_path) >= 0:
                return True
        return False

    def get_target_blob_paths(
            self,
            blob_service: BlockBlobService,
            blob_container_name: str,
            blob_relative_path: str):
        """
        Get target blob paths based on its own filters.

        :param blob_service: block blob service.
        :type blob_service: BlockBlobService
        :param blob_container_name: blob container name
        :type blob_container_name: str
        :param blob_relative_path: blob relative path
        :type blob_relative_path: str

        :return: a list of target blob paths within filter range.
        :rtype: list
        """
        print('Looking for parquet files...')
        blobs = blob_service.list_blobs(blob_container_name, blob_relative_path)
        target_paths = []
        for blob in blobs:
            if blob.name.endswith('.parquet') and self._contains_match_paths(blob.name) is True:
                target_paths.append(blob.name)
        return target_paths


class PandasDataLoadLimitToDay(PandasDataLoadLimitNone):
    """PandasDataLoadLimitToDay controls how many parquets of days will be loaded."""

    def __init__(
            self,
            start_date,
            end_date,
            path_pattern='/year=%d/month=%d/day=%d/'):
        """Initialize pandas data load limit to the last day.

        :param start_date: start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: end date you'd like to query inclusively.
        :type end_date: datetime
        :param path_pattern: blob path pattern.
        :type path_pattern: str
        """
        self.start_date = start_date
        self.end_date = end_date
        self.path_pattern = path_pattern
        super(PandasDataLoadLimitToDay, self).__init__()

    def get_target_blob_paths(
            self,
            blob_service: BlockBlobService,
            blob_container_name: str,
            blob_relative_path: str):
        """
        Get target blob paths based on its own filters.

        :param blob_service: block blob service.
        :type blob_service: BlockBlobService
        :param blob_container_name: blob container name
        :type blob_container_name: str
        :param blob_relative_path: blob relative path
        :type blob_relative_path: str

        :return: a list of target blob paths within filter range.
        :rtype: list
        """
        self._match_paths = []
        for current_day in day_range(self.start_date, self.end_date):
            self._match_paths.append(self.path_pattern % (
                current_day.year, current_day.month, current_day.day))

        if len(self._match_paths) > 1:
            print('Due to size, we only allow getting 1-day data into pandas dataframe!')
            print('We are taking the latest day: %s' % (self._match_paths[-1]))
            self._match_paths = self._match_paths[-1:]

        print('Target paths: %s' % (self._match_paths))
        return super(PandasDataLoadLimitToDay, self).get_target_blob_paths(
            blob_service=blob_service,
            blob_container_name=blob_container_name,
            blob_relative_path=blob_relative_path)


class PandasDataLoadLimitToMonth(PandasDataLoadLimitNone):
    """PandasDataLoadLimitToMonth controls how many parquets of months will be loaded."""

    def __init__(
            self,
            start_date,
            end_date,
            path_pattern='/year=%d/month=%d/'):
        """Initialize pandas data load limit to the last month.

        :param start_date: start date you'd like to query inclusively.
        :type start_date: datetime
        :param end_date: end date you'd like to query inclusively.
        :type end_date: datetime
        :param path_pattern: blob path pattern.
        :type path_pattern: str
        """
        self.start_date = start_date
        self.end_date = end_date
        self.path_pattern = path_pattern
        super(PandasDataLoadLimitToMonth, self).__init__()

    def get_target_blob_paths(
            self,
            blob_service: BlockBlobService,
            blob_container_name: str,
            blob_relative_path: str):
        """
        Get target blob paths based on its own filters.

        :param blob_service: block blob service.
        :type blob_service: BlockBlobService
        :param blob_container_name: blob container name
        :type blob_container_name: str
        :param blob_relative_path: blob relative path
        :type blob_relative_path: str

        :return: a list of target blob paths within filter range.
        :rtype: list
        """
        self._match_paths = []
        for current_month in month_range(self.start_date, self.end_date):
            self._match_paths.append(self.path_pattern % (current_month.year, current_month.month))

        if len(self._match_paths) > 1:
            print('Due to size, we only allow getting 1-month data into pandas dataframe!')
            print('We are taking the latest month: %s' % (self._match_paths[-1]))
            self._match_paths = self._match_paths[-1:]

        print('Target paths: %s' % (self._match_paths))
        return super(PandasDataLoadLimitToMonth, self).get_target_blob_paths(
            blob_service=blob_service,
            blob_container_name=blob_container_name,
            blob_relative_path=blob_relative_path)
