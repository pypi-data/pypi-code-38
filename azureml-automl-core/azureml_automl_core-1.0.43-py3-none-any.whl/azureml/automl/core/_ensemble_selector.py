# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for selecting algorithms for AutoMLs ensembling feature."""
from typing import cast, List, Optional, Sized, Tuple
from collections import Counter
import logging

from sklearn.base import TransformerMixin
from sklearn.pipeline import Pipeline
import numpy as np
from automl.client.core.common import constants, datasets, metrics
from automl.client.core.common import metrics_utilities as metrics_utils


class EnsembleSelector:
    """Ensembling Selection Algorithm following Caruana's Ensemble Selection from Library of Models paper."""

    # during the greedy selection phase, we will choose only the models within X % of the best score
    SELECTION_GREEDY_SCORE_THRESHOLD = 0.05
    # maximum number of pipelines to start the ensemble with
    MAXIMUM_PIPELINES_IN_GREEDY_PHASE = 5

    def __init__(self,
                 logger: logging.Logger,
                 fitted_models: List[Tuple[int, Pipeline]],
                 dataset: datasets.ClientDatasets,
                 training_type: constants.TrainingType,
                 metric: str,
                 iterations: int = 10,
                 y_transformer: Optional[TransformerMixin] = None) -> None:
        """Create EnsembleSelector used for choosing the pipelines that should be part of an ensemble.

        Arguments:
            :param logger: Logger instance
            :type logger: logging.Logger
            :param fitted_models: A list containing the fitted pipelines associated to AutoML iterations
                The pipelines should be sorted based on their primary metric score.
            :type fitted_models: list of tuples (iteration, fitted_pipeline(s))
            :param dataset: The training dataset.
            :type dataset: datasets.ClientDatasets
            :param training_type: Type of training (eg: TrainAndValidate split, CrossValidation split, etc.)
            :type training_type: constants.TrainingType enumeration
            :param metric: The metric that we're optimizing for during the selection algorithm
            :type metric: str

        Keyword Arguments:
            :param iterations: Number of iterations for Selection algorithm (default: {10})
            :type iterations: int
        """
        # validate the task_type parameter to be within the supported range
        if dataset is None:
            raise ValueError("dataset is a required parameter for the EnsembleSelector.select() method")

        # validate the input metric to optimize on
        task_type = dataset.get_task()
        if task_type == constants.Tasks.CLASSIFICATION and metric in constants.Metric.CLASSIFICATION_SET:
            self.metric_objective = constants.MetricObjective.Classification[metric]
        elif task_type == constants.Tasks.REGRESSION and metric in constants.Metric.REGRESSION_SET:
            self.metric_objective = constants.MetricObjective.Regression[metric]
        else:
            raise ValueError("The metric ({0}) to optimize for, is not currently supported".format(metric))

        if iterations < 1:
            raise ValueError("iterations parameter needs to be >=1")
        if logger is None:
            raise ValueError("logger parameter can not be None")

        self.fitted_models = fitted_models
        self.dataset = dataset
        self.training_type = training_type
        self.metric = metric
        self.iterations = iterations
        self.task_type = task_type
        self.model_count = len(fitted_models)
        if self.task_type == constants.Tasks.CLASSIFICATION:
            self.class_labels = self.dataset._dataset['class_labels']
            self.num_classes = len(self.class_labels)
            self.y_min = None
            self.y_max = None
        else:
            self.num_classes = 1
            self.class_labels = None
            self.y_min, self.y_max = self.dataset.get_y_range()
        self.logger = logger
        self.y_transformer = y_transformer
        self.unique_ensemble = None
        self.unique_weights = None
        self.predictions = None  # type: np.ndarray
        self.y_valid = None  # type: np.ndarray
        self.sample_weight_valid = None
        self.cross_validate_indices = None

    def select(self):
        """Select fitted pipelines that should be part of the Ensemble."""
        if self.iterations == 1:
            # short circuiting for the case of 1 iteration
            # so that we don't do any extra compute in the selection phases
            initial_size = 1
        else:
            initial_size = min(EnsembleSelector.MAXIMUM_PIPELINES_IN_GREEDY_PHASE, self.iterations // 2)

        self.logger.debug("Initial size {0}".format(initial_size))
        self._compute_trained_class_labels()
        self._compute_models_predictions()

        # prime the ensemble list with the models having the best scores
        single_model_scores = np.zeros(self.model_count)
        for i in range(self.model_count):
            single_model_scores[i] = self._get_model_score(self.predictions[:, :, i])
        self.logger.info("Single models scores: {0}".format(single_model_scores))

        # the fitted pipelines are already sorted based on their scores from best to worst
        # then we need to choose the best initial ones to start the ensemble with
        if self.metric_objective == constants.OptimizerObjectives.MAXIMIZE:
            # compute the threshold score based on the best individual score
            if single_model_scores[0] > 0:
                threshold_score = (1 - EnsembleSelector.SELECTION_GREEDY_SCORE_THRESHOLD) * single_model_scores[0]
            else:
                threshold_score = (1 + EnsembleSelector.SELECTION_GREEDY_SCORE_THRESHOLD) * single_model_scores[0]
            count = np.sum(single_model_scores >= threshold_score)
            initial_size = min(count, initial_size)
        else:
            # compute the threshold score based on the best individual score
            if single_model_scores[0] > 0:
                threshold_score = (1 + EnsembleSelector.SELECTION_GREEDY_SCORE_THRESHOLD) * single_model_scores[0]
            else:
                threshold_score = (1 - EnsembleSelector.SELECTION_GREEDY_SCORE_THRESHOLD) * single_model_scores[0]
            count = np.sum(single_model_scores <= threshold_score)

            initial_size = min(count, initial_size)
        # we'll just take the first elements within that list for starting the ensemble.
        ensemble = list(range(0, initial_size))
        # after priming the ensemble, we'll need to keep on adding
        # models to it until we reach the desired count
        number_of_models_needed = self.iterations - len(ensemble)

        # as we try to create ensembles, we'll maintain the one that had the best score
        best_ensemble = list(ensemble)
        best_ensemble_score = self._get_ensemble_score(best_ensemble)

        self.logger.info("Starting ensemble hill climbing. Current ensemble: {0}, current score: {1}"
                         .format(best_ensemble, best_ensemble_score))

        # Currently we only support ensemble selection with replacement.
        # This means we allow a model to be added multiple times to the ensemble during the selection steps.
        # In the end we extract the unique models and assign them weights based on how many times
        # they got added during selection.
        for iteration in range(number_of_models_needed):
            scores = np.zeros([self.model_count])
            for j in range(len(self.fitted_models)):
                # we'll temporarily add this model to the ensemble and will simulate
                # the overall score of the resulting ensemble
                ensemble.append(j)

                # get the score of this simulated ensemble
                scores[j] = self._get_ensemble_score(ensemble)

                self.logger.debug("Iteration {0}. Simulating ensemble: {1} yielded score {2}"
                                  .format(iteration, ensemble, scores[j]))

                # remove this model from the ensemble and continue with another
                ensemble.pop()

            # after we've tried the end-score with each of the individual ensembles,
            # get the best one from this iteration
            best, current_ensemble_score = self._choose_best_model_for_ensemble(scores, single_model_scores)
            ensemble.append(best)
            self.logger.debug("Iteration {0}, current ensemble: {1}, current score :{2}"
                              .format(iteration, ensemble, current_ensemble_score))

            # if the current ensemble beat our best one, update our references
            if current_ensemble_score == self._get_better_score(best_ensemble_score, current_ensemble_score):
                best_ensemble = list(ensemble)
                best_ensemble_score = current_ensemble_score
                self.logger.info("Iteration {0}, new best ensemble: {1}, new best score :{2}"
                                 .format(iteration, ensemble, current_ensemble_score))

        weights = self._compute_weights(best_ensemble)
        self.logger.info("Final ensemble: {0}, score: {1}. Best individual model score: {2}"
                         .format(best_ensemble, best_ensemble_score, single_model_scores[ensemble[0]]))

        unique_ensemble = list(set(best_ensemble))

        unique_weights = [weights[i] for i in unique_ensemble if weights[i] > 0]

        self.logger.info("Unique models IDs in the ensemble: {0}. Weights: {1}"
                         .format(unique_ensemble, unique_weights))
        self.unique_ensemble = unique_ensemble
        self.unique_weights = unique_weights
        return self.unique_ensemble, self.unique_weights

    def _choose_best_model_for_ensemble(self, ensemble_scores, single_model_scores):
        best_score = None
        if self.metric_objective == constants.OptimizerObjectives.MAXIMIZE:
            # first we need to find what's the maximum score for the ensembles simulated
            best_score = np.nanmax(ensemble_scores)
            # then find the model indices that maximized the ensemble (there can be multiple)
            maximum_score_indices = np.where(ensemble_scores == best_score)[0]
            # if there are multiple single models, choose the best one (the one that has maximum individual score)
            best = maximum_score_indices[np.nanargmax(
                [single_model_scores[i] for i in maximum_score_indices])]
        else:
            # similarly if we need to minimize the score, do same thing but look for the minimum score
            best_score = np.nanmin(ensemble_scores)
            minimum_score_indices = np.where(ensemble_scores == best_score)[0]
            best = minimum_score_indices[np.nanargmin(
                [single_model_scores[i] for i in minimum_score_indices])]
        return best, best_score

    def _get_better_score(self, score1, score2):
        if self.metric_objective == constants.OptimizerObjectives.MAXIMIZE:
            return max(score1, score2)
        else:
            return min(score1, score2)

    def _compute_models_predictions(self):
        # 3 dimensional array [validationSetSize, numberOfClasses, numberOfModels]
        pipeline_tuple_index = 1
        X_valid = None
        y_valid = None
        cross_validate_indices = None     # type: Optional[List[Tuple[int, int]]]

        if self.training_type == constants.TrainingType.TrainAndValidation:
            X_valid, y_valid, sample_weight_valid = self.dataset.get_valid_set()
            validation_set_size = X_valid.shape[0]
            predictions = np.zeros((validation_set_size, self.num_classes, self.model_count))

            for index, model_tuple in enumerate(self.fitted_models):
                # the tuple is (iterationIndex, pipeline, algo_name)
                pipeline = model_tuple[pipeline_tuple_index]
                if pipeline is None:
                    continue
                predictions[:, :, index] = self._get_model_predictions(pipeline,
                                                                       X_valid,
                                                                       self.trained_class_labels[0])

        elif self.training_type == constants.TrainingType.MeanCrossValidation:
            # we'll first arrange the y_valid and the weights to follow the same order as CV folds
            # we don't care about the X_valid, because we anyhow generate the predictions at this time
            # so we'll use them for computing the scores throughout the selection process.
            sample_weight_valid = None
            for split_index, (_, _, _, _, y_valid_fold, sample_wt_valid_fold) in \
                    enumerate(self.dataset.get_CV_splits()):
                if split_index == 0:
                    cross_validate_indices = [(0, len(y_valid_fold))]
                    y_valid = y_valid_fold
                    sample_weight_valid = sample_wt_valid_fold
                else:
                    prev_length = len(cast(Sized, y_valid))
                    cast(List[Tuple[int, int]], cross_validate_indices)\
                        .append((prev_length, prev_length + len(y_valid_fold)))
                    y_valid = np.concatenate((y_valid, y_valid_fold))
                    if sample_wt_valid_fold is not None:
                        sample_weight_valid = np.concatenate((sample_weight_valid, sample_wt_valid_fold))

            predictions = np.zeros((cast(np.ndarray, y_valid).shape[0], self.num_classes, self.model_count))

            for index, model_tuple in enumerate(self.fitted_models):
                temp = None
                for split_index, (_, _, _, X_valid_fold, y_valid_fold,
                                  sample_wt_valid_fold) in enumerate(self.dataset.get_CV_splits()):
                    pipeline = model_tuple[pipeline_tuple_index][split_index]
                    model_predictions = self._get_model_predictions(pipeline,
                                                                    X_valid_fold,
                                                                    self.trained_class_labels[split_index])

                    if split_index == 0:
                        temp = model_predictions
                    else:
                        temp = np.concatenate((temp, model_predictions))
                predictions[:, :, index] = temp
        else:
            raise ValueError("Unsupported TrainingType")
        # store these as instance fields for later reuse inside this class' methods
        self.predictions = predictions
        self.y_valid = y_valid  # type: np.ndarray
        self.sample_weight_valid = sample_weight_valid
        self.cross_validate_indices = cross_validate_indices

    def _get_model_predictions(self, model, validation_set, trained_class_labels):
        if self.task_type == constants.Tasks.CLASSIFICATION:
            if hasattr(model, 'predict_proba'):
                result = model.predict_proba(validation_set)
                # let's make sure all the predictions have same number of columns
                result = metrics_utils.pad_predictions(result, trained_class_labels, self.class_labels)
            else:
                raise ValueError("model object {} doesn't expose predict_proba method".format(model))
        else:
            # for regression models, we'll use predict method
            result = model.predict(validation_set)[:, None]
        return result

    def _get_ensemble_predictions(self, ensemble_list: List[int]) -> np.ndarray:
        # slice the predictions array to only contain the predictions for the
        # members of the ensemble
        predictions_sliced = self.predictions[:, :, np.array(ensemble_list)]
        if self.cross_validate_indices is None:
            return self._get_ensemble_predictions_simple(predictions_sliced)
        else:
            # we'll do similar procedure as above, but for each fold separately
            ensemble_predictions = None
            for cv_indices in self.cross_validate_indices:
                temp = self._get_ensemble_predictions_simple(predictions_sliced[cv_indices[0]:cv_indices[1]])
                if ensemble_predictions is None:
                    ensemble_predictions = temp
                else:
                    ensemble_predictions = np.concatenate((ensemble_predictions, temp))
            return ensemble_predictions

    def _get_ensemble_predictions_simple(self, predictions: np.ndarray) -> np.ndarray:
        # predictions is 3 dimensional array [validationSetSize, numberOfClasses, numberOfModels]
        # we compute the average from the predictions of each model
        temp = predictions.mean(2)
        if self.task_type == constants.Tasks.CLASSIFICATION:
            # for classification we normalize the avg class probability.
            # this is to make sure they are summing up to 1 (or 100%)
            temp /= temp.sum(1)[:, None]
        else:
            temp = temp[:, None]
        return temp

    def _get_ensemble_score(self, ensemble_list):
        predictions = self._get_ensemble_predictions(ensemble_list)
        return self._get_model_score(predictions)

    def _get_model_score(self, model_predictions: np.ndarray) -> float:
        # compute scores on the predictions array slice corresponding to that model index
        if self.task_type == constants.Tasks.REGRESSION:
            y_pred = model_predictions[:, 0]
        else:
            y_pred = model_predictions

        # we shouldn't be passing the trained_class_labels to the metrics calculation,
        # because we've already padded the predictions inside this class.
        # otherwise, metrics calculation might be doing double padding.
        model_score = None
        if self.cross_validate_indices is None:
            # all the predictions are for a single model
            all_metrics = metrics.compute_metrics(y_pred=y_pred,
                                                  y_test=self.y_valid,
                                                  sample_weight=self.sample_weight_valid,
                                                  metrics=[self.metric],
                                                  num_classes=self.num_classes,
                                                  class_labels=self.class_labels,
                                                  task=self.task_type,
                                                  y_max=self.y_max,
                                                  y_min=self.y_min,
                                                  y_transformer=self.y_transformer)
            model_score = cast(float, all_metrics[self.metric])
        else:
            cv_scores = []
            # we'll need to slice our predictions based on the CV splits indices
            for cv_indices in self.cross_validate_indices:
                y_pred_slice = y_pred[cv_indices[0]:cv_indices[1]]
                y_valid_slice = self.y_valid[cv_indices[0]:cv_indices[1]]
                sample_weight_slice = None if self.sample_weight_valid is None \
                    else self.sample_weight_valid[cv_indices[0]:cv_indices[1]]
                all_metrics = metrics.compute_metrics(y_pred=y_pred_slice,
                                                      y_test=y_valid_slice,
                                                      sample_weight=sample_weight_slice,
                                                      metrics=[self.metric],
                                                      num_classes=self.num_classes,
                                                      class_labels=self.class_labels,
                                                      task=self.task_type,
                                                      y_max=self.y_max,
                                                      y_min=self.y_min,
                                                      y_transformer=self.y_transformer)
                cv_scores.append(all_metrics[self.metric])
            model_score = float(np.mean(cv_scores))
        return model_score

    def _compute_weights(self, ensemble):
        # create a list with the count of occurrences of each model inside the
        # ensemble : Tuple<modelIndex, count>
        occurrences = Counter(ensemble).most_common()
        weights = np.zeros(self.model_count, dtype=float)
        for occurrence_tuple in occurrences:
            weights[occurrence_tuple[0]] = float(occurrence_tuple[1]) / len(ensemble)

        return weights

    def _compute_trained_class_labels(self):
        # for classification tasks we need to maintain the class labels that were used during training
        # otherwise the metrics might not be accurate
        # for CV, we'll maintain a list of class labels corresponding to each fold
        # for anything other than Classification tasks, we'll store None so that we can simply pass the value
        # down to the metrics calculation function without any extra checks
        self.trained_class_labels = []  # type: List[Optional[np.ndarray]]

        if self.training_type == constants.TrainingType.TrainAndValidation:
            if self.task_type == constants.Tasks.CLASSIFICATION:
                _, y_train, _ = self.dataset.get_train_set()
                self.trained_class_labels.append(np.unique(y_train))
            else:
                self.trained_class_labels.append(None)
        elif self.training_type == constants.TrainingType.MeanCrossValidation:
            for _, y_train_fold, _, _, _, _ in self.dataset.get_CV_splits():
                if self.task_type == constants.Tasks.CLASSIFICATION:
                    self.trained_class_labels.append(np.unique(y_train_fold))
                else:
                    self.trained_class_labels.append(None)
