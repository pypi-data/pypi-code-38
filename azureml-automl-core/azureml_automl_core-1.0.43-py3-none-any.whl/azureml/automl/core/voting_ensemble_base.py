# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base module for ensembling previous AutoML iterations."""
from typing import Any, Dict, Union
from abc import ABC

import numpy as np

from automl.client.core.common import constants
from automl.client.core.common import model_wrappers
from automl.client.core.common.exceptions import ConfigException
from . import ensemble_base
from .automl_base_settings import AutoMLBaseSettings


class VotingEnsembleBase(ensemble_base.EnsembleBase, ABC):
    """
    Class for ensembling previous AutoML iterations.

    The ensemble pipeline is initialized from a collection of already fitted pipelines.
    """

    def __init__(self, automl_settings: Union[str, Dict[str, Any], AutoMLBaseSettings]) -> None:
        """Create an Ensemble pipeline out of a collection of already fitted pipelines.

        :param automl_settings: settings for the AutoML experiments.
        """
        super(VotingEnsembleBase, self).__init__(automl_settings)

    def _create_ensembles(self, logger, fitted_pipelines, selector):
        trained_labels = None
        if selector.training_type == constants.TrainingType.MeanCrossValidation:
            use_cross_validation = True
            ensemble_estimator_tuples = self._create_fully_fitted_ensemble_estimator_tuples(logger,
                                                                                            fitted_pipelines,
                                                                                            selector.unique_ensemble)
            trained_labels = selector.dataset.get_meta('class_labels')
        else:
            use_cross_validation = False
            ensemble_estimator_tuples = [(
                str(fitted_pipelines[i][self.PIPELINES_TUPLES_ITERATION_INDEX]),
                fitted_pipelines[i][self.PIPELINES_TUPLES_PIPELINE_INDEX]) for i in selector.unique_ensemble]
            _, y_train, _ = selector.dataset.get_train_set()
            trained_labels = np.unique(y_train)

        # ensemble_estimator_tuples represents a list of tuples (iteration_index, fitted_pipeline)
        final_ensemble = self._get_voting_ensemble(trained_labels,
                                                   ensemble_estimator_tuples,
                                                   selector.unique_weights)

        cross_folded_ensembles = None
        if use_cross_validation:
            # for computing all the scores of the Ensemble we'll need the ensembles of cross-validated models.
            cross_folded_ensembles = []
            for fold_index, cv_split_tuple in enumerate(selector.dataset.get_CV_splits()):
                partial_fitted_estimators = [(
                    str(fitted_pipelines[i][self.PIPELINES_TUPLES_ITERATION_INDEX]),
                    fitted_pipelines[i][self.PIPELINES_TUPLES_PIPELINE_INDEX][fold_index])
                    for i in selector.unique_ensemble]

                _, y_train, _, _, _, _ = cv_split_tuple
                cv_train_labels = np.unique(y_train)
                cross_folded_ensemble = self._get_voting_ensemble(cv_train_labels,
                                                                  partial_fitted_estimators,
                                                                  selector.unique_weights)
                cross_folded_ensembles.append(cross_folded_ensemble)
        return final_ensemble, cross_folded_ensembles

    def _get_voting_ensemble(self, trained_labels, ensemble_estimator_tuples, unique_weights):
        if self._automl_settings.task_type == constants.Tasks.CLASSIFICATION:
            estimator = model_wrappers.PreFittedSoftVotingClassifier(estimators=ensemble_estimator_tuples,
                                                                     weights=unique_weights,
                                                                     classification_labels=trained_labels)
        elif self._automl_settings.task_type == constants.Tasks.REGRESSION:
            estimator = model_wrappers.PreFittedSoftVotingRegressor(estimators=ensemble_estimator_tuples,
                                                                    weights=unique_weights)
        else:
            raise ConfigException("Invalid task_type ({0})".format(self._automl_settings.task_type))
        return estimator
