# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Public data base class."""

from ..environ import RuntimeEnv
from typing import Any, List, Optional

from .._utils.telemetry_utils import get_opendatasets_logger
from azureml.telemetry.activity import ActivityType, log_activity


class PublicData:
    """Public data class contains common properties and methods for each open datasets."""

    _registry_id = ''

    @property
    def id(self) -> Any:
        """Get location id of the open data."""
        return self.__id

    @id.setter
    def id(self, value):
        """Set location id of the open data."""
        self.__id = value

    @property
    def cols(self) -> List[str]:
        """Get column name list which the user wants to retrieve."""
        return self.__cols

    @cols.setter
    def cols(self, value: List[str]):
        """Set column names user wants to retrieve."""
        self.__cols = value

    @property
    def env(self) -> RuntimeEnv:
        """Runtime environment."""
        return self.__env

    @env.setter
    def env(self, value: RuntimeEnv):
        self.__env = value

    @property
    def registry_id(self) -> str:
        """
        Get the registry id of this public dataset registered at the backend.

        We use this registry id to get latest metadata like storage location.
        Expect all public data sub classes to assign _registry_id.

        :return: registry id in string.
        :rtype: str
        """
        return self._registry_id

    def __init__(self, cols: Optional[List[str]], enable_telemetry: bool = True):
        """
        Initialize with columns.

        :param cols: column name list which the user wants to enrich
        :param enable_telemetry: whether to send telemetry
        """
        self.enable_telemetry = enable_telemetry
        self.cols = list(cols) if cols is not None else None
        if self.enable_telemetry:
            self.logger = get_opendatasets_logger(__name__)
            self.log_properties = self.get_common_log_properties()
            self.log_properties['cols'] = self.cols

        if self.cols is None:
            self.selected_columns = ['*']
        else:
            self.selected_columns = list(set(self.cols + self._get_mandatory_columns()))

    def _get_mandatory_columns(self):
        """
        Get mandatory columns to select.

        :return: a list of column names.
        :rtype: list
        """
        return []

    def get_common_log_properties(self):
        """Get common log properties."""
        return {'RegistryId': self.registry_id}

    def get_enricher(self):
        """Get enricher."""
        if self.enable_telemetry:
            with log_activity(
                    self.logger,
                    'get_enricher',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties) as activity_logger:
                return self._get_enricher(activity_logger)
        else:
            return self._get_enricher(None)

    def _get_enricher(self, activity_logger):
        """
        Get enricher, internal to override.

        :param activity_logger: activity logger, could be None.
        :return: enricher class object.
        """
        return None

    def to_spark_dataframe(self):
        """To spark dataframe."""
        if self.enable_telemetry:
            with log_activity(
                    self.logger,
                    'to_spark_dataframe',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties) as activity_logger:
                return self._to_spark_dataframe(activity_logger)
        else:
            return self._to_spark_dataframe(None)

    def _to_spark_dataframe(self, activity_logger):
        """
        To SPARK dataframe, internal to override.

        :param activity_logger: activity logger, could be None.
        :return: SPARK dataframe.
        """
        return None

    def to_pandas_dataframe(self):
        """To pandas dataframe."""
        if self.enable_telemetry:
            with log_activity(
                    self.logger,
                    'to_pandas_dataframe',
                    ActivityType.PUBLICAPI,
                    custom_dimensions=self.log_properties) as activity_logger:
                return self._to_pandas_dataframe(activity_logger)
        else:
            return self._to_pandas_dataframe(None)

    def _to_pandas_dataframe(self, activity_logger):
        """
        To pandas dataframe, internal to override.

        :param activity_logger: activity logger, could be None.
        :return: Pandas dataframe.
        """
        return None
