# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Runs all enabled features sweepers."""
from typing import Any, cast, Dict, List, Optional, Tuple
from functools import reduce
import logging

import numpy as np
import os
import pickle
import tempfile
from sklearn.base import BaseEstimator
from sklearn.pipeline import make_pipeline, Pipeline

from automl.client.core.common import activity_logger, logging_utilities, resource_limits
from automl.client.core.common.exceptions import ConfigException
from automl.client.core.common.limit_function_call_for_win import enforce_time_limit
from automl.client.core.common.types import DataInputType, DataSingleColumnInputType
from ..configuration import FeatureConfig, SweeperConfig, ConfigKeys
from ..configuration.sampler_config import SamplerConfig
from ..estimation import Estimators
from ..featurization import Featurizers
from ..sampling import Samplers, AbstractSampler, \
    DataProvider, DiskBasedDataProvider, InMemoryDataProvider
from ..scoring import Scorers, AbstractScorer
from ..sweeping.abstract_sweeper import AbstractSweeper
from ..sweeping.sweepers import Sweepers
from ..stats_computation import RawFeatureStats


class MetaSweeper:
    """Runs all enabled features sweepers."""

    DEFAULT_SWEEPER_TIMEOUT_SEC = 3600  # 1 hour

    def __init__(self, task: str, timeout_sec: int = DEFAULT_SWEEPER_TIMEOUT_SEC,
                 logger: Optional[logging.Logger] = None) -> None:
        """Load configuration and create sweeper configurations."""
        self._logger = logger or logging.getLogger(MetaSweeper.__class__.__name__)
        self._task = task
        global_config = self._get_config()
        self._cfg = global_config.get(task, {})

        self._enabled = self._cfg.get(ConfigKeys.SWEEPING_ENABLED, False)
        self._sweepers = []  # type: List[AbstractSweeper]
        self._enabled_sweeper_configs = []  # type: List[SweeperConfig]

        if self._enabled:
            sweeper_configs = [{}] if self._cfg is None \
                else self._cfg.get(ConfigKeys.ENABLED_SWEEPERS, [])  # type: List[Dict[str, Any]]
            for sweeper_config in sweeper_configs:
                self._enabled_sweeper_configs.append(SweeperConfig.from_dict(sweeper_config))

        self._timeout_sec = timeout_sec
        self._temp_files_to_cleanup = []  # type: List[str]
        self._page_sampled_data_to_disk = self._cfg.get(ConfigKeys.PAGE_SAMPLED_DATA_TO_DISK, True)
        self._run_sweeping_in_isolation = self._cfg.get(ConfigKeys.RUN_SWEEPING_IN_ISOLATION, True)

    def sweep(self, X: DataInputType, y: DataSingleColumnInputType,
              stats_and_column_purposes: List[Tuple[RawFeatureStats, str, str]]) -> List[Tuple[str, Pipeline]]:
        """Sweep through all the sweepers in the configurations."""
        if self._enabled is False:
            self._logger.debug("Feature sweeping disabled.")
            return []

        sweepers = self._build_sweepers(X, y, sweeper_configs=self._enabled_sweeper_configs)
        column_groups = {}  # type: Dict[str, List[str]]
        is_valid, msg = self._validate(X, y)
        if not is_valid:
            self._logger.info(msg)
            return []

        for _, column_purpose, column in stats_and_column_purposes:
            column_groups.setdefault(column_purpose.lower(), []).append(column)

        file_handle, checkpoint_file = tempfile.mkstemp(suffix=".ck", prefix="feature_sweep_", dir=os.getcwd())
        self._temp_files_to_cleanup.append(checkpoint_file)
        # after creating the file, mkstemp holds a lock on it, preventing us from removing it after we're done
        # so we'll close that handle right after creation
        os.close(file_handle)
        logger = self._logger if isinstance(self._logger, activity_logger.TelemetryActivityLogger) else None
        kwargs = {"sweepers": sweepers,
                  "enabled_sweeper_configs": self._enabled_sweeper_configs,
                  "checkpoint_file": checkpoint_file,
                  "X": X,
                  "y": y,
                  "column_groups": column_groups,
                  "logger": logger}  # type: Dict[str, Any]

        exit_status = None
        result = None  # type: Optional[List[Tuple[Any, Pipeline]]]
        try:
            if self._run_sweeping_in_isolation is False:
                return MetaSweeper._sweep_internal(**kwargs)

            # TODO: encapsulate this forking logic to SafeEnforceLimits (including JobObject support for Win)
            if os.name == "nt":
                result = enforce_time_limit(self._timeout_sec, MetaSweeper._sweep_internal, kwargs)
                if isinstance(result, tuple) and len(result) == 2:
                    # in case of errors enforce_time_limit returns a tuple, otherwise a single value
                    # TODO: unify it and hide all this complexity
                    result, exit_status = result
            else:
                constraints = resource_limits.DEFAULT_RESOURCE_LIMITS
                constraints[resource_limits.TIME_CONSTRAINT] = self._timeout_sec
                limiter = resource_limits.SafeEnforceLimits(enable_limiting=True, run_as_spawn=True, **constraints)
                args = (sweepers, self._enabled_sweeper_configs, checkpoint_file, X, y, column_groups, logger)
                kwargs = {}
                result, exit_status, _ = limiter.execute(MetaSweeper._sweep_internal, *args, **kwargs)

            # the subprocess can silently fail, in which case fallback to recovering from checkpoint file
            if result is None:
                self._logger.warning("Feature sweeping silently failed. ExitStatus: {}".format(exit_status))
                result = self._recover_sweeping_from_checkpointfile(checkpoint_file)
        except Exception as ex:
            self._logger.warning("Feature sweeping sub-process failed due to {ex}".format(ex=ex))
            logging_utilities.log_traceback(ex, self._logger, is_critical=False)
            result = self._recover_sweeping_from_checkpointfile(checkpoint_file)
        finally:
            self._remove_temporary_files()

        return cast(List[Tuple[str, Any]], result)

    def _recover_sweeping_from_checkpointfile(self, checkpoint_file: str) -> List[Tuple[Any, Pipeline]]:
        # let's try to open the checkpoint file and recover as much as possible from there.
        result = []
        self._logger.info("Recovering sweeping metadata from checkpoint file")
        try:
            with open(checkpoint_file, 'rb') as ck_file:
                for row in ck_file:
                    sweeper_idx, columns = pickle.loads(row)
                    sweeper_config = self._enabled_sweeper_configs[int(sweeper_idx)]

                    result.append((columns,  # Handle group of columns case.
                                   self._build_featurizers(sweeper_config._experiment, logger=self._logger)))
            recovered_sweeps_count = len(result)
            if recovered_sweeps_count > 0:
                self._logger.debug(
                    "Recovered {} sweeping metadata items from checkpoint file.".format(recovered_sweeps_count))
        except Exception as ex:
            logging_utilities.log_traceback(
                ex,
                self._logger,
                override_error_msg="Failed to recover feature sweeping state from checkpoint file due to {}".
                format(ex),
                is_critical=False
            )
        return result

    @staticmethod
    def _sweep_internal(sweepers: List[AbstractSweeper], enabled_sweeper_configs: List[SweeperConfig],
                        checkpoint_file: str, X: DataInputType, y: DataSingleColumnInputType,
                        column_groups: Dict[str, List[str]],
                        logger: Optional[logging.Logger] = None) -> List[Tuple[str, Pipeline]]:
        return_transforms = []  # type: List[Tuple[Any, Any]]
        logger = logger or logging.getLogger(MetaSweeper.__class__.__name__)

        logger.info("Begin Feature Sweeping...")

        with open(checkpoint_file, mode='wb', buffering=1) as ck_file:
            for sweeper_idx, sweeper in enumerate(sweepers):
                sweeper_config = enabled_sweeper_configs[sweeper_idx]
                cols = []  # type: List[str]
                for purpose in sweeper_config._column_purposes:
                    group = purpose.get("group", False)
                    for t in purpose.get("types", []):
                        cols.extend(column_groups.get(t.lower(), []))

                if len(cols) == 0:
                    logger.info("No columns eligible for sweeping, continuing with next sweeper.")
                    continue

                if not group:
                    for col_id, column in enumerate(cols):
                        if sweeper.sweep(column):
                            logger.debug("Sweep returned true for: {sweeper} on column index: {col}".format(
                                sweeper=sweeper, col=col_id))

                            # persist our progress so far in case this child process dies out of a sudden
                            ck_file.write(pickle.dumps((sweeper_idx, column)))
                            return_transforms.append((column, sweeper._experiment))
                        else:
                            logger.debug(
                                "Sweep returned false for: {sweeper} "
                                "on col id: {col}".format(sweeper=sweeper, col=col_id))
                else:
                    featurize_separately = False
                    if group == 'score':
                        featurize_separately = True
                    col_string = reduce(lambda a, b: str(a) + "," + str(b), cols)
                    if sweeper.sweep(cols, featurize_separately=featurize_separately):
                        logger.debug("Sweep returned true for: {sweeper} on column index: {col}".format(
                            sweeper=sweeper, col=col_string))
                        ck_file.write(pickle.dumps((sweeper_idx, col_string)))
                        if featurize_separately:
                            return_transforms.extend((col, sweeper._experiment) for col in cols)
                        else:
                            return_transforms.append((cols, sweeper._experiment))
                    else:
                        logger.debug(
                            "Sweep returned false for: {sweeper} "
                            "for col ids: {col}".format(sweeper=sweeper, col=col_string))

        logger.info("Finished sweeping with all feature sweepers.")
        return return_transforms

    def _build_sweepers(self, X: DataInputType, y: DataSingleColumnInputType,
                        sweeper_configs: Optional[List[SweeperConfig]] = None) -> List[AbstractSweeper]:
        """Sweep over all enabled sweepers."""
        if not sweeper_configs:
            return []

        self._logger.debug("Sweeper configuration: {c}".format(c=sweeper_configs))
        logger_kwargs = {'logger': self._logger}
        sweepers = []
        enabled_sweeper_configs = [cfg for cfg in sweeper_configs if cfg._enabled]
        for enabled_sweeper_config in enabled_sweeper_configs:
            sampler = self._build_sampler(
                SamplerConfig.from_dict(enabled_sweeper_config._sampler), task=self._task, logger=self._logger)
            estimator = Estimators.get(enabled_sweeper_config._estimator)  # type: Optional[BaseEstimator]
            scorer = Scorers.get(
                enabled_sweeper_config._scorer,
                task=self._task, logger=self._logger)  # type: Optional[AbstractScorer]
            baseline_featurizer = self._build_featurizers(enabled_sweeper_config._baseline,
                                                          logger=self._logger)  # type: FeatureConfig
            experiment_featurizer = self._build_featurizers(enabled_sweeper_config._experiment,
                                                            logger=self._logger)  # type: FeatureConfig

            include_baseline_features = True
            if enabled_sweeper_config._experiment:
                include_baseline_features = enabled_sweeper_config._experiment. \
                    get(ConfigKeys.INCLUDE_BASELINE_FEATURES, True)

            data_provider = self._build_data_provider(X, y, sampler)

            kwargs = {"data_provider": data_provider, "estimator": estimator, "scorer": scorer,
                      "baseline": baseline_featurizer, "experiment": experiment_featurizer,
                      "epsilon": enabled_sweeper_config._epsilon, "task": self._task,
                      "include_baseline_features_in_experiment": include_baseline_features,
                      **logger_kwargs}  # type: Dict[str, Any]

            sweeper = Sweepers.get(enabled_sweeper_config._type, **kwargs)  # type: Optional[AbstractSweeper]
            if sweeper:
                sweepers.append(sweeper)

        return sweepers

    def _remove_temporary_files(self) -> None:
        for file_name in self._temp_files_to_cleanup:
            try:
                os.remove(file_name)
            except IOError as ex:
                self._logger.warning("Failed to remove {} due to {}".format(file_name, ex))

    @classmethod
    def _validate(cls, X: DataInputType, y: DataSingleColumnInputType) -> Tuple[bool, str]:
        if X is None or y is None:
            return False, "X or y cannot be None"

        if len(X) != len(y):
            return False, "Number of rows in X must be equal to the number of rows in y."

        if len(np.unique(y)) == 1:
            return False, "Number of classes in y must be more than 1."

        return True, ''

    @classmethod
    def _build_sampler(cls, sampler_config: SamplerConfig, task: str, logger: logging.Logger) -> AbstractSampler:
        """
        Build sampler from the given sampler configuration.

        :param sampler_config: Sampler configuration.
        :param task: Task type.
        :return: Created sampler.
        """
        sampler_id = sampler_config.id
        sampler_args = sampler_config.sampler_args
        sampler_kwargs = sampler_config.sampler_kwargs
        sampler_kwargs["task"] = task
        sampler_kwargs["logger"] = logger

        sampler = Samplers.get(sampler_id, *sampler_args, **sampler_kwargs)
        return cast(AbstractSampler, sampler)

    @classmethod
    def _build_featurizers(cls, feature_config: Dict[str, Any], logger: logging.Logger) -> Pipeline:
        feature_steps = feature_config.get(ConfigKeys.FEATURIZERS)
        if not isinstance(feature_steps, list):
            raise ConfigException("Incorrect configuration. {Key} missing in featurization.".format(
                Key=ConfigKeys.FEATURIZERS))
        steps = []

        for c in feature_steps:
            f_config = FeatureConfig.from_dict(c)
            if isinstance(logger, activity_logger.TelemetryActivityLogger):
                # we'll only pass down the logger if we know it's pickleable
                f_config.featurizer_kwargs['logger'] = logger
            steps.append(Featurizers.get(f_config))

        return make_pipeline(*steps)

    def _build_data_provider(self, X: DataInputType, y: DataSingleColumnInputType,
                             sampler: AbstractSampler) -> DataProvider:
        # sample the data before creating the sweeper
        X_sampled, y_sampled, splitting_config = sampler.sample(X, y)
        data_provider = None  # type: Optional[DataProvider]
        if self._page_sampled_data_to_disk:
            file_handle, dataset_file = tempfile.mkstemp(suffix=".ds", prefix="sampled_dataset_", dir=os.getcwd())
            self._temp_files_to_cleanup.append(dataset_file)

            with os.fdopen(file_handle, "wb") as f:
                pickle.dump((X_sampled, y_sampled), f)

            data_provider = DiskBasedDataProvider(dataset_file, splitting_config)
        else:
            data_provider = InMemoryDataProvider(X_sampled, y_sampled, splitting_config)

        return data_provider

    def _get_config(self) -> Dict[str, Any]:
        """Read config and setup the list of enabled sweepers."""
        try:
            return SweeperConfig(logger=self._logger).get_config()
        except (IOError, FileNotFoundError) as e:
            self._logger.info("Error trying to read configuration file: {e}".format(e=e))
            return {}
