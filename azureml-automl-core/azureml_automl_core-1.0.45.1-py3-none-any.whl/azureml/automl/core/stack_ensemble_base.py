# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Base module for ensembling previous AutoML iterations."""
from typing import Any, Dict, Tuple, Type, Union
from abc import ABC
import json
import numpy as np
import typing

from sklearn import base
from sklearn import linear_model
from sklearn import model_selection

from automl.client.core.common import constants
from automl.client.core.common import metrics
from automl.client.core.common import model_wrappers
from automl.client.core.common import pipeline_spec as pipeline_spec_module
from automl.client.core.common import runner
from automl.client.core.common.types import DataInputType, DataSingleColumnInputType

from . import _ensemble_selector
from . import ensemble_base
from .automl_base_settings import AutoMLBaseSettings


class StackEnsembleBase(ensemble_base.EnsembleBase, ABC):
    """
    Class for creating a Stacked Ensemble based on previous AutoML iterations.

    The ensemble pipeline is initialized from a collection of already fitted pipelines.
    """

    def __init__(self, automl_settings: Union[str, Dict[str, Any], AutoMLBaseSettings],
                 settings_type: 'Type[ensemble_base.SettingsType]') -> None:
        """Create an Ensemble pipeline out of a collection of already fitted pipelines.

        :param automl_settings: settings for the AutoML experiments.
        :param settings_type: the type for the settings object.
        """
        super(StackEnsembleBase, self).__init__(automl_settings, settings_type)
        self._meta_learner_type = getattr(self._automl_settings, "stack_meta_learner_type", None)
        self._meta_learner_kwargs = getattr(self._automl_settings, "stack_meta_learner_kwargs", None)

    def _create_ensembles(self, logger, fitted_pipelines, selector):
        logger.info("Creating a Stack Ensemble out of iterations: {}".format(selector.unique_ensemble))

        if selector.training_type == constants.TrainingType.TrainAndValidation:
            return self._create_stack_ensembles_train_validation(logger,
                                                                 fitted_pipelines,
                                                                 selector)
        elif selector.training_type == constants.TrainingType.MeanCrossValidation:
            return self._create_stack_ensembles_cross_validation(logger,
                                                                 fitted_pipelines,
                                                                 selector)
        else:
            raise ValueError("Unsupported training type ({})".format(selector.training_type))

    def _create_stack_ensembles_train_validation(self,
                                                 logger,
                                                 fitted_pipelines,
                                                 selector):
        problem_info = selector.dataset.get_problem_info()
        X_base_train, X_meta_train, y_base_train, y_meta_train, sample_weight_base_train, sample_weight_meta_train = \
            self._split_train_set_for_scoring_train_valid(selector)

        _, y_valid, sample_weight_valid = selector.dataset.get_valid_set()
        self._meta_learner_type, self._meta_learner_kwargs = self._determine_meta_learner_type([y_valid, y_meta_train])

        # for this type of training, we need the meta_model to be trained on the predictions
        # over the validation set from all the base learners.
        # This will be the ensemble returned for predictions on new data.
        all_prediction_list = []
        base_learners_tuples = []
        pipeline_specs = []
        for model_index in selector.unique_ensemble:
            base_learners_tuples.append(
                (str(fitted_pipelines[model_index][self.PIPELINES_TUPLES_ITERATION_INDEX]),
                 fitted_pipelines[model_index][self.PIPELINES_TUPLES_PIPELINE_INDEX]))
            pipeline_specs.append(fitted_pipelines[model_index][self.PIPELINES_TUPLES_PIPELINE_SPEC_INDEX])
            model_predictions = selector.predictions[:, :, model_index]
            # for regression we need to slice the matrix because there's a single "class" in the second dimension
            if selector.task_type == constants.Tasks.REGRESSION:
                model_predictions = model_predictions[:, 0]
            all_prediction_list.append(model_predictions)

        meta_learner_training_set = model_wrappers.StackEnsembleBase._horizontal_concat(all_prediction_list)
        meta_learner, meta_learner_supports_sample_weights = self._create_meta_learner()

        self._fit_meta_learner(
            meta_learner, meta_learner_training_set, y_valid,
            sample_weight_valid, meta_learner_supports_sample_weights)

        fully_fitted_stack_ensemble = self._create_stack_ensemble(base_learners_tuples, meta_learner)

        scoring_meta_learner = self._train_meta_learner_for_scoring_ensemble_with_train_validate(
            X_base_train, X_meta_train, y_base_train, y_meta_train, sample_weight_base_train,
            sample_weight_meta_train, pipeline_specs, selector.task_type, problem_info)

        # after we've trained the meta learner, we can reuse the fully trained base learners (on 100% of train set)
        scoring_stack_ensemble = self._create_stack_ensemble(base_learners_tuples, scoring_meta_learner)
        return fully_fitted_stack_ensemble, scoring_stack_ensemble

    def _create_stack_ensembles_cross_validation(self,
                                                 logger,
                                                 fitted_pipelines,
                                                 selector):
        # we'll need to fetch the fully fitted models for the models that will be part of the base learners
        # so far the selection algo has been using the partially fitted ones for each AUTO ML iteration
        fully_fitted_learners_tuples = self._create_fully_fitted_ensemble_estimator_tuples(logger,
                                                                                           fitted_pipelines,
                                                                                           selector.unique_ensemble)
        # fully_fitted_learners_tuples represents a list of tuples (iteration, fitted_pipeline)
        y_valid_full = selector.y_valid
        sample_weights_valid_full = selector.sample_weight_valid

        all_out_of_fold_predictions = []
        for model_index in selector.unique_ensemble:
            # get the vertical concatenation of the out of fold predictions from the selector
            # as they were already computed during the selection phase
            model_predictions = selector.predictions[:, :, model_index]
            if selector.task_type == constants.Tasks.REGRESSION:
                model_predictions = model_predictions[:, 0]
            all_out_of_fold_predictions.append(model_predictions)
        meta_learner_training = model_wrappers.StackEnsembleBase._horizontal_concat(all_out_of_fold_predictions)

        y_valid_folds = []
        for _, _, _, _, y_valid_fold, _ in selector.dataset.get_CV_splits():
            y_valid_folds.append(y_valid_fold)
        self._meta_learner_type, self._meta_learner_kwargs = self._determine_meta_learner_type(y_valid_folds)

        meta_learner, meta_learner_supports_sample_weights = self._create_meta_learner()
        self._fit_meta_learner(
            meta_learner, meta_learner_training, y_valid_full,
            sample_weights_valid_full, meta_learner_supports_sample_weights)

        fully_fitted_stack_ensemble = self._create_stack_ensemble(fully_fitted_learners_tuples, meta_learner)

        # Now we need to construct some Stack Ensembles to be used for computing the metric scores
        # we'll need to keep one fold out (holdout) from the CV folds and concatenate vertically those predictions.
        # The vertical concatenation has already happened within the EnsembleSelector.
        # The concatenated predictions will be used for training the meta model in a CV fashion
        # then we'll create a StackedEnsemble where the base learners are the partially fitted models
        # from the selected AutoML iteration which haven't seen the holdout set.
        # Again, we'll reuse the selector.predictions matrix along with the row ranges corresponding to each fold,
        # excluding each time a different range
        cross_validated_stack_ensembles = []
        # get the CV indices from selector
        # this represents the range of indices within the predictions matrix which contains
        # the partial model's (corresponding to this training fold) predictions on y_valid.
        for fold_index, cv_indices in enumerate(selector.cross_validate_indices):
            base_learners_tuples = []
            stacker_training_set = []
            # Fetch each train/validation fold from the CV splits. this will be used for training of the stacker.
            # The ensemble selector keeps track of the ranges of row indices that correspond to each out of fold
            # predictions slice within the selector.predictions matrix.
            # Here, cv_indices is an interval represented through a tuple(row_index_start, row_index_end).
            slice_to_exclude_from_predictions = range(cv_indices[0], cv_indices[1])
            for counter, model_index in enumerate(selector.unique_ensemble):
                # get the partially fitted model that hasn't been trained on this holdout set
                # this will be used as base learner for this scoring StackEnsemble
                base_learners_tuples.append(
                    (str(fitted_pipelines[model_index][self.PIPELINES_TUPLES_ITERATION_INDEX]),
                     fitted_pipelines[model_index][self.PIPELINES_TUPLES_PIPELINE_INDEX][fold_index]))
                # we'll grab all the out of fold predictions for this model excluding the holdout set.
                # these predictions will be used as training data for the meta_learner
                stacker_training_set.append(
                    np.delete(all_out_of_fold_predictions[counter],
                              slice_to_exclude_from_predictions, axis=0))
            # create the meta learner model and then fit it
            scoring_meta_learner = base.clone(meta_learner)
            meta_learner_training_set = model_wrappers.StackEnsembleBase._horizontal_concat(stacker_training_set)
            y_train_fold = np.delete(selector.y_valid, slice_to_exclude_from_predictions)
            if selector.sample_weight_valid is not None:
                sample_weights_train_fold = np.delete(selector.sample_weight_valid, slice_to_exclude_from_predictions)
            else:
                sample_weights_train_fold = None

            self._fit_meta_learner(
                scoring_meta_learner,
                meta_learner_training_set, y_train_fold,
                sample_weights_train_fold, meta_learner_supports_sample_weights)

            scoring_stack_ensemble = self._create_stack_ensemble(base_learners_tuples, scoring_meta_learner)

            if selector.task_type == constants.Tasks.CLASSIFICATION:
                # For cases when the base learner predictions have been padded so that all CV models have the same
                # shape, we'll have to ensure the StackEnsemble is aware of all classes involved in the padding.
                # For that, we'll have to override the classes_ attribute so that when later predicting, it'll apply
                # the same padding logic as it was applied during training.
                scoring_stack_ensemble.classes_ = fully_fitted_stack_ensemble.classes_

            cross_validated_stack_ensembles.append(scoring_stack_ensemble)

        return fully_fitted_stack_ensemble, cross_validated_stack_ensembles

    def _split_train_set_for_scoring_train_valid(
        self, selector: _ensemble_selector.EnsembleSelector) -> Tuple[
            DataInputType, DataSingleColumnInputType, DataInputType, DataSingleColumnInputType,
            DataSingleColumnInputType, DataSingleColumnInputType]:
        # We'll need to retrain the base learners pipelines on 80% (the default) of the training set
        # and we'll use the remaining 20% to generate out of fold predictions which will
        # represent the input training set of the meta_learner.
        X, y, sample_weight = selector.dataset.get_train_set()

        meta_learner_train_percentage = getattr(
            self._automl_settings, "stack_meta_learner_train_percentage",
            constants.EnsembleConstants.DEFAULT_TRAIN_PERCENTAGE_FOR_STACK_META_LEARNER)

        stratify = y if selector.task_type == constants.Tasks.CLASSIFICATION else None

        sample_weight_base_train = None
        sample_weight_meta_train = None
        if sample_weight is not None:
            try:
                (X_base_train, X_meta_train, y_base_train, y_meta_train, sample_weight_base_train,
                    sample_weight_meta_train) = model_selection.train_test_split(
                        X, y, sample_weight, test_size=meta_learner_train_percentage, stratify=stratify)
            except ValueError:
                # in case stratification fails, fall back to non-stratify train/test split
                (X_base_train, X_meta_train, y_base_train, y_meta_train, sample_weight_base_train,
                    sample_weight_meta_train) = model_selection.train_test_split(
                        X, y, sample_weight, test_size=meta_learner_train_percentage, stratify=None)
        else:
            try:
                X_base_train, X_meta_train, y_base_train, y_meta_train =\
                    model_selection.train_test_split(X, y, test_size=meta_learner_train_percentage, stratify=stratify)
            except ValueError:
                # in case stratification fails, fall back to non-stratify train/test split
                X_base_train, X_meta_train, y_base_train, y_meta_train =\
                    model_selection.train_test_split(X, y, test_size=meta_learner_train_percentage, stratify=None)

        return (
            X_base_train, X_meta_train, y_base_train, y_meta_train,
            sample_weight_base_train, sample_weight_meta_train)

    def _train_meta_learner_for_scoring_ensemble_with_train_validate(
            self, X_base_train, X_meta_train, y_base_train, y_meta_train, sample_weight_base_train,
            sample_weight_meta_train, base_learners_pipeline_specs, task_type, problem_info):

        meta_learner, meta_learner_supports_sample_weights = self._create_meta_learner()
        scoring_base_learners = self._instantiate_pipelines_from_specs(base_learners_pipeline_specs, problem_info)

        for scoring_base_learner in scoring_base_learners:
            runner.ClientRunner.fit_pipeline(
                scoring_base_learner, X_base_train, y_base_train, sample_weight_base_train)
        if task_type == constants.Tasks.CLASSIFICATION:
            # use the predict probabilities to return the class because the meta_learner was trained on probabilities
            predictions = [estimator.predict_proba(X_meta_train) for estimator in scoring_base_learners]
            concat_predictions = model_wrappers.StackEnsembleBase._horizontal_concat(predictions)
        else:
            predictions = [estimator.predict(X_meta_train) for estimator in scoring_base_learners]
            concat_predictions = model_wrappers.StackEnsembleBase._horizontal_concat(predictions)

        self._fit_meta_learner(
            meta_learner, concat_predictions, y_meta_train,
            sample_weight_meta_train, meta_learner_supports_sample_weights)
        return meta_learner

    def _determine_meta_learner_type(self, y_meta_list: typing.List[np.ndarray]) -> Tuple[str, Dict[str, Any]]:
        meta_learner_type = self._meta_learner_type
        meta_learner_kwargs = self._meta_learner_kwargs
        # if the user hasn't explicitly specified the learner type for the Stacker, we need to figure out a default
        if meta_learner_type is None:
            # instantiate a KFold instance to figure out how many folds are used by CV learners.
            required_cv_count = model_selection.KFold().n_splits

            if self._automl_settings.task_type == constants.Tasks.REGRESSION:
                # we'll iterate through all the sets of target values used for the meta learner to figure out if
                # we could use Cross Validation while training the ElasticNet or not.
                validation_sizes = [len(y) for y in y_meta_list]
                if (min(validation_sizes) > required_cv_count):
                    meta_learner_type = constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.ElasticNetCV
                else:
                    meta_learner_type = constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.ElasticNet
            elif self._automl_settings.task_type == constants.Tasks.CLASSIFICATION:
                # we want to see whether the current data allows us to do LogisticRegressionCV,
                # otherwise we'll fallback to simple LogisticRegression.
                # both learners have a common set of parameters
                meta_learner_kwargs = {}
                # for metrics where we would recommend using class_weights, set the parameter to balanced
                if self._automl_settings.primary_metric in constants.Metric.CLASSIFICATION_BALANCED_SET:
                    meta_learner_kwargs['class_weight'] = 'balanced'
                else:
                    meta_learner_kwargs['class_weight'] = None

                # First, compute the unique classes and return the inverse function to compute each class in y from
                # the list of unique classes
                can_use_cv = True
                # we'll iterate through all the sets of target values used for the meta learner
                # For Train/Validation we check the initial validation set which is used for th final StackEnsemble,
                # and also the split we take for training the meta learner inside the scoring StackEnsemble.
                # For CrossValidation, we'll have to check all the validation sets.
                for y_meta_train in y_meta_list:
                    y_meta_train_unique, y_meta_train_counts = np.unique(y_meta_train, return_counts=True)

                    if y_meta_train_counts.min() < required_cv_count:
                        can_use_cv = False
                        break
                if can_use_cv:
                    meta_learner_type = \
                        constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LogisticRegressionCV
                    # let's also try to set some defaults, unless the user overrides them
                    meta_learner_kwargs['refit'] = True

                else:
                    meta_learner_type = \
                        constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LogisticRegression

                if self._meta_learner_kwargs is not None:
                    meta_learner_kwargs.update(self._meta_learner_kwargs)
            else:
                raise ValueError("Unsupported task_type=({})".format(self._automl_settings.task_type))
        return meta_learner_type, meta_learner_kwargs

    def _create_meta_learner(self) -> typing.Tuple[base.BaseEstimator, bool]:
        meta_learner_ctor = None  # type: typing.Union[typing.Any, typing.Callable[..., typing.Any]]
        meta_learner_kwargs = {}  # type: typing.Dict[str, typing.Any]
        meta_learner_supports_sample_weights = True

        if self._meta_learner_type == constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LightGBMClassifier \
                or self._meta_learner_type == \
                constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LightGBMRegressor:
            if self._automl_settings.task_type == constants.Tasks.CLASSIFICATION:
                meta_learner_ctor = model_wrappers.LightGBMClassifier
            else:
                meta_learner_ctor = model_wrappers.LightGBMRegressor
            meta_learner_kwargs = {"min_child_samples": 10}
        elif self._meta_learner_type == constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LogisticRegression:
            meta_learner_ctor = linear_model.LogisticRegression
        elif self._meta_learner_type == \
                constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LogisticRegressionCV:
            meta_learner_ctor = linear_model.LogisticRegressionCV
            meta_learner_kwargs = {'scoring': Scorer(self._automl_settings.primary_metric)}
        elif self._meta_learner_type == constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.LinearRegression:
            meta_learner_ctor = linear_model.LinearRegression
        elif self._meta_learner_type == constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.ElasticNet:
            meta_learner_ctor = linear_model.ElasticNet
            meta_learner_supports_sample_weights = False
        elif self._meta_learner_type == constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.ElasticNetCV:
            meta_learner_ctor = linear_model.ElasticNetCV
            meta_learner_supports_sample_weights = False
        else:
            err = "{} is not supported as a model type for the Stack Meta Learner. Currently supported list: {}"\
                .format(
                    getattr(self._automl_settings, 'stack_meta_learner_type', []),
                    constants.EnsembleConstants.StackMetaLearnerAlgorithmNames.ALL)
            raise ValueError(err)

        if self._meta_learner_kwargs is not None:
            meta_learner_kwargs.update(self._meta_learner_kwargs)

        return (meta_learner_ctor(**meta_learner_kwargs), meta_learner_supports_sample_weights)

    def _create_stack_ensemble(self, base_layer_tuples, meta_learner):
        result = None
        if self._automl_settings.task_type == constants.Tasks.CLASSIFICATION:
            result = model_wrappers.StackEnsembleClassifier(base_learners=base_layer_tuples, meta_learner=meta_learner)
        else:
            result = model_wrappers.StackEnsembleRegressor(base_learners=base_layer_tuples, meta_learner=meta_learner)
        return result

    @staticmethod
    def _fit_meta_learner(meta_learner, X, y, sample_weight, learner_supports_sample_weights):
        if learner_supports_sample_weights:
            meta_learner.fit(X, y, sample_weight=sample_weight)
        else:
            meta_learner.fit(X, y)
        return meta_learner

    @staticmethod
    def _instantiate_pipelines_from_specs(pipeline_specs, problem_info):
        pipelines = []
        for spec in pipeline_specs:
            pipeline_dict = json.loads(spec)
            spec_obj = pipeline_spec_module.PipelineSpec.from_dict(pipeline_dict)
            pipeline = spec_obj.instantiate_pipeline_spec(problem_info)
            pipelines.append(pipeline)
        return pipelines


class Scorer:
    """Scorer class that encapsulates our own metric computation."""

    def __init__(self, metric: str):
        """Create an AutoMLScorer for a particular metric.

        :param metric: The metric we need to calculate the score for.
        """
        self._metric = metric

    def __call__(self, estimator, X, y=None):
        """Return the score of the estimator.

        :param estimator: The estimator to score
        :param X: the input data to compute the score on
        :param y: the target values associate to the input
        """
        y_preds = estimator.predict_proba(X)
        return metrics.compute_metrics_classification(y_preds, y, metrics=[self._metric])[self._metric]
