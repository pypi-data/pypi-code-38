# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Sweeper that sweeps and returns whether or not to include the featurizer(s) provide any lift."""
from typing import Any, Union, List
import copy

from sklearn.pipeline import make_union
import numpy as np
import scipy

from automl.client.core.common import logging_utilities
from .abstract_sweeper import AbstractSweeper


class BinarySweeper(AbstractSweeper):
    """Sweeper that sweeps and returns whether or not to include the featurizer(s) provide any lift."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Create a Binary sweeper."""
        super(BinarySweeper, self).__init__(*args, **kwargs)

    def sweep(self, column: Union[str, List[str]], featurize_separately: bool = False, *args: Any, **kwargs: Any) \
            -> bool:
        """Sweeper method."""
        # Sample
        if self._use_cross_validation:
            raise NotImplementedError()

        class_name = type(self).__name__
        self._logger.info("{} {}: Begin sweeping".format(class_name, self))

        is_experiment_better = False
        try:
            X_train, X_valid, y_train_sample, y_valid_sample = self._data_provider.get_train_validation_sets()
            if isinstance(column, list):
                X_train_sample = X_train.iloc[:, column]
                X_valid_sample = X_valid.iloc[:, column]
            else:
                X_train_sample = X_train[column]
                X_valid_sample = X_valid[column]

            # Featurizer
            baseline_featurizer = self._baseline
            experiment_featurizer = self._experiment
            if self._include_baseline_features_in_experiment:
                experiment_featurizer = make_union(self._baseline, self._experiment)

            baseline_features, experiment_features, baseline_valid_features, experiment_valid_features \
                = self._featurize(X_train_sample, y_train_sample, X_valid_sample, y_valid_sample,
                                  baseline_featurizer, experiment_featurizer, featurize_separately)

            # Train
            baseline_estimator = copy.deepcopy(self._estimator)
            experiment_estimator = self._estimator

            baseline_estimator.fit(baseline_features, y_train_sample)
            experiment_estimator.fit(experiment_features, y_train_sample)

            # Validate
            baseline_score = self._scorer.score(
                estimator=baseline_estimator,
                valid_features=baseline_valid_features,
                y_actual=y_valid_sample
            )

            experiment_score = self._scorer.score(
                estimator=experiment_estimator,
                valid_features=experiment_valid_features,
                y_actual=y_valid_sample
            )

            is_experiment_better = self._scorer.is_experiment_better_than_baseline(
                baseline_score=baseline_score,
                experiment_score=experiment_score,
                epsilon=self._epsilon)

            self._logger.info(
                "{name} {sweeper}: Baseline score={bscore}, "
                "Experiment score={escore}, "
                "IsExperimentBetter="
                "{is_experiment_better}".format(
                    name=class_name,
                    sweeper=self,
                    bscore=baseline_score,
                    escore=experiment_score,
                    is_experiment_better=is_experiment_better))

        except Exception as ex:
            self._logger.warning("{} {}: Failed due to exception {ex}".format(class_name,
                                                                              sweeper=self,
                                                                              ex=ex))
            logging_utilities.log_traceback(ex, self._logger, is_critical=False)
        finally:
            self._logger.info("{} {}: Finished sweeping.".format(class_name, self))
            return is_experiment_better

    def _featurize(self, X, y, X_valid, y_valid, baseline_featurizer,
                   experiment_featurizer, featurize_seperately):
        if featurize_seperately:
            baseline_features_list = []
            experiment_features_list = []
            baseline_features_valid_list = []
            experiment_features_valid_list = []
            for col in X:
                baseline_features_list.append(baseline_featurizer.fit_transform(X[col], y))
                experiment_features_list.append(experiment_featurizer.fit_transform(X[col], y))
                baseline_features_valid_list.append(baseline_featurizer.transform(X_valid[col]))
                experiment_features_valid_list.append(experiment_featurizer.transform(X_valid[col]))
            if scipy.sparse.issparse(baseline_features_list[0]):
                baseline_features = scipy.sparse.hstack(baseline_features_list)
                baseline_features_valid = scipy.sparse.hstack(baseline_features_valid_list)
            else:
                baseline_features = np.hstack(baseline_features_list)
                baseline_features_valid = np.hstack(baseline_features_valid_list)

            if scipy.sparse.issparse(experiment_features_list[0]):
                experiment_features = scipy.sparse.hstack(experiment_features_list)
                experiment_features_valid = scipy.sparse.hstack(experiment_features_valid_list)
            else:
                experiment_features = np.hstack(experiment_features_list)
                experiment_features_valid = np.hstack(experiment_features_valid_list)
        else:
            baseline_features = baseline_featurizer.fit_transform(X, y)
            experiment_features = experiment_featurizer.fit_transform(X, y)
            baseline_features_valid = baseline_featurizer.transform(X_valid)
            experiment_features_valid = experiment_featurizer.transform(X_valid)
        return baseline_features, experiment_features, baseline_features_valid, experiment_features_valid
