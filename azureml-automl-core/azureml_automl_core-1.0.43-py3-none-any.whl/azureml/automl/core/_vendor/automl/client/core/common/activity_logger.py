# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Activity-based loggers."""
from typing import Any, Dict, Iterator, Optional, Tuple
from abc import ABC, abstractmethod
from datetime import datetime
import copy
import contextlib
import logging
import platform
import uuid

from automl.client.core.common import constants as constants
from automl.client.core.common import logging_utilities as logging_util


class Activities:
    """Constants for activity logging."""

    Preprocess = 'preprocess'
    FitIteration = 'fit_iteration'
    Fit = 'fit'


class ActivityLogger(logging.Logger, ABC):
    """Abstract base class for activity loggers."""

    def __init__(self, name: str = "ActivityLogger", *args: Any, **kwargs: Any):
        """Init a ActivityLogger class with default name.

        Keyword Arguments:
            :param name: logger instant name
            :type name: str
        """
        self.custom_dimensions = {'app_name': constants.DEFAULT_LOGGING_APP_NAME}
        super().__init__(name, *args, **kwargs)

    def _merge_kwarg_extra(self,
                           properties: Dict[str, Any],
                           **kwargs: Any) -> Tuple[Dict[str, Any], Any]:
        """Update and return the kwargs['extra'] as extra and the kwargs that pops extra key."""
        if "extra" in kwargs:
            properties = copy.deepcopy(self.custom_dimensions)
            extra = kwargs.pop("extra")
            if "properties" in extra:
                properties.update(extra['properties'])
            extra['properties'] = properties
        else:
            properties = self.custom_dimensions  # no need to update properties if no extra
            extra = {'properties': properties}
        return extra, kwargs

    def update_default_property(self,
                                key: str,
                                value: Any) -> None:
        """Update default property in the class.

        Arguments:
            :param key: The custom dimension key needs to be changed.
            :type key: str
            :param value: The value of the corresponding key.
            :type value: Any
        """
        self.custom_dimensions[key] = value

    def update_default_properties(self,
                                  properties_dict: Dict[str, Any]) -> None:
        """Update default properties in the class.

        Arguments:
            :param properties_dict: The dict contains all the properties that need to be updated.
            :type properties_dict: dict
        """
        self.custom_dimensions.update(properties_dict)

    def set_custom_dimensions_on_log_config(self, log_config: logging_util.LogConfig) -> None:
        """
        Log activity with duration and status.

        :param log_config: LogConfig class.
        """
        log_config.set_custom_dimensions(self.custom_dimensions)

    @abstractmethod
    def _log_activity(self,
                      logger: logging.Logger,
                      activity_name: str,
                      activity_type: Optional[str] = None,
                      custom_dimensions: Optional[Dict[str, Any]] = None) -> Iterator[Optional[Any]]:
        """
        Log activity - should be overridden by subclasses with a proper implementation.

        :param logger:
        :param activity_name:
        :param activity_type:
        :param custom_dimensions:
        :return:
        """
        raise NotImplementedError

    @contextlib.contextmanager
    def log_activity(self,
                     logger: logging.Logger,
                     activity_name: str,
                     activity_type: Optional[str] = None,
                     custom_dimensions: Optional[Dict[str, Any]] = None) -> Iterator[Optional[Any]]:
        """
        Log an activity using the given logger.

        :param logger:
        :param activity_name:
        :param activity_type:
        :param custom_dimensions:
        :return:
        """
        return self._log_activity(logger, activity_name, activity_type, custom_dimensions)


class DummyActivityLogger(ActivityLogger):
    """Dummy activity logger."""

    def _log_activity(self,
                      logger: logging.Logger,
                      activity_name: str,
                      activity_type: Optional[str] = None,
                      custom_dimensions: Optional[Dict[str, Any]] = None) -> Iterator[None]:
        """
        Do nothing.

        :param logger:
        :param activity_name:
        :param activity_type:
        :param custom_dimensions:
        """
        yield


class TelemetryActivityLogger(ActivityLogger):
    """Telemetry activity logger."""

    def __init__(self, namespace=None,
                 filename=None,
                 verbosity=None,
                 custom_dimensions=None,
                 extra_handlers=None,
                 component_name=None):
        """
        Construct activity logger object.

        :param namespace: namespace
        :param filename: log file name
        :param verbosity: logger verbosity
        :param custom_dimensions: custom dimensions
        :param component_name: component name for telemetry state.
        """
        super().__init__("TelemetryActivityLogger")
        self.namespace = namespace
        self.filename = filename
        self.verbosity = verbosity
        self.component_name = component_name
        self.custom_dimensions = {
            'app_name': constants.DEFAULT_LOGGING_APP_NAME,
            'automl_client': None,
            'automl_sdk_version': None,
            'child_run_id': None,
            'common_core_version': None,
            'compute_target': None,
            'experiment_id': None,
            'os_info': platform.platform(),
            'parent_run_id': None,
            'region': None,
            'service_url': None,
            'subscription_id': None,
            'task_type': None
        }
        if custom_dimensions is not None:
            self.custom_dimensions.update(custom_dimensions)
        self._logger = self._get_logger(extra_handlers)

    def log(self,
            level: int,
            msg: str,
            *args: Any,
            **kwargs: Any) -> None:
        """Log message with custom dimensions.

        Arguments:
            :param level: Log level.
            :type level: int
            :param msg: logging message.
            :type msg: str
        """
        extra, kwargs = self._merge_kwarg_extra(self.custom_dimensions, **kwargs)
        self._logger.log(level, msg, extra=extra, *args, **kwargs)

    def debug(self,
              msg: str,
              *args: Any,
              **kwargs: Any) -> None:
        """Override logger debug.

        Arguments:
            :param msg: logging message.
            :type msg: str
        """
        self.log(logging.DEBUG, msg, *args, **kwargs)

    def info(self,
             msg: str,
             *args: Any,
             **kwargs: Any) -> None:
        """Override logger info.

        Arguments:
            :param msg: logging message.
            :type msg: str
        """
        self.log(logging.INFO, msg, *args, **kwargs)

    def warning(self,
                msg: str,
                *args: Any,
                **kwargs: Any) -> None:
        """Override logger warning.

        Arguments:
            :param msg: logging message.
            :type msg: str
        """
        self.log(logging.WARNING, msg, *args, **kwargs)

    def error(self,
              msg: str,
              *args: Any,
              **kwargs: Any) -> None:
        """Override logger error.

        Arguments:
            :param msg: logging message.
            :type msg: str
        """
        self.log(logging.ERROR, msg, *args, **kwargs)

    def critical(self,
                 msg: str,
                 *args: Any,
                 **kwargs: Any) -> None:
        """Override logger error.

        Arguments:
            :param msg: logging message.
            :type msg: str
        """
        self.log(logging.CRITICAL, msg, *args, **kwargs)

    def __getstate__(self):
        """
        Get state picklable objects.

        :return: state
        """
        return {
            'namespace': self.namespace,
            'filename': self.filename,
            'verbosity': self.verbosity,
            'component_name': self.component_name,
            'custom_dimensions': self.custom_dimensions,
            '_logger': None,
        }

    def __setstate__(self, state):
        """
        Set state for object reconstruction.

        :param state: pickle state
        """
        self.namespace = state['namespace']
        self.filename = state['filename']
        self.verbosity = state['verbosity']
        self.component_name = state['component_name']
        self.custom_dimensions = state['custom_dimensions']
        self._logger = self._get_logger()

    def _get_logger(self, extra_handlers=None):
        return logging_util.get_logger(
            namespace=self.namespace,
            filename=self.filename,
            verbosity=self.verbosity,
            extra_handlers=extra_handlers,
            component_name=self.component_name)

    def _log_activity(self,
                      logger: logging.Logger,
                      activity_name: str,
                      activity_type: Optional[str] = None,
                      custom_dimensions: Optional[Dict[str, Any]] = None) -> Iterator[None]:
        """
        Log activity with duration and status.

        :param logger: logger
        :param activity_name: activity name
        :param activity_type: activity type
        :param custom_dimensions: custom dimensions
        """
        activity_info = {'activity_id': str(uuid.uuid4()),
                         'activity_name': activity_name,
                         'activity_type': activity_type}    # type: Dict[str, Any]

        activity_info.update(self.custom_dimensions)

        completion_status = constants.TelemetryConstants.SUCCESS

        start_time = datetime.utcnow()
        self._logger.info("ActivityStarted: {}".format(activity_name), extra={"properties": activity_info})

        try:
            yield
        except Exception:
            completion_status = constants.TelemetryConstants.FAILURE
            raise
        finally:
            end_time = datetime.utcnow()
            duration_ms = round((end_time - start_time).total_seconds() * 1000, 2)
            activity_info["durationMs"] = duration_ms
            activity_info["completionStatus"] = completion_status

            self._logger.info("ActivityCompleted: Activity={}, HowEnded={}, Duration={}[ms]".
                              format(activity_name, completion_status, duration_ms),
                              extra={"properties": activity_info})
