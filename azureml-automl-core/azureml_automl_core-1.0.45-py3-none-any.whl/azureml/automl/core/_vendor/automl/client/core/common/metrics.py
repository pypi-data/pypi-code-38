# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Computation of available metrics."""
from typing import Any, cast, Dict, List, Optional, Union
from collections import OrderedDict
import logging
import sys

import numpy as np
from sklearn.base import TransformerMixin
import scipy.stats as st
import sklearn.metrics
import sklearn.preprocessing
import sklearn.utils

from automl.client.core.common import constants
from automl.client.core.common import logging_utilities as log_utils
from automl.client.core.common import metrics_utilities as metrics_utils
from automl.client.core.common.exceptions import ClientException, DataException


def minimize_or_maximize(metric, task=None):
    """Select the objective given a metric.

    Some metrics should be minimized and some should be maximized
    :param metric: the name of the metric to look up
    :param task: one of constants.Tasks.
    :return: returns one of constants.OptimizerObjectives.
    """
    if task is None:
        reg_metrics = get_default_metric_with_objective(
            constants.Tasks.REGRESSION)
        class_metrics = get_default_metric_with_objective(
            constants.Tasks.CLASSIFICATION)
        if metric in reg_metrics:
            task = constants.Tasks.REGRESSION
        elif metric in class_metrics:
            task = constants.Tasks.CLASSIFICATION
        else:
            msg = 'Could not find objective for metric "{0}"'.format(metric)
            raise ValueError(msg)
    return get_default_metric_with_objective(task)[metric]


def is_better(val1, val2, metric=None, task=None, objective=None):
    """Select the best of two values given metric or objectives.

    :param val1: scalar value
    :param val2: scalar value
    :param metric: the name of the metric to look up
    :param task: one of constants.Tasks.
    :param objective: one of constants.OptimizerObjectives.
    return: returns a boolean of if val1 is better than val2 in the situation
    """
    if objective is None:
        if metric is None:
            raise ValueError("Must specific either Metric or Objective")
        else:
            objective = minimize_or_maximize(metric, task)
    if objective == constants.OptimizerObjectives.MAXIMIZE:
        return val1 > val2
    elif objective == constants.OptimizerObjectives.MINIMIZE:
        return val1 < val2


def get_all_nan(task):
    """Create a dictionary of metrics to values for the given task.

    All metric values are set to nan initially
    :param task: one of constants.Tasks.
    :return: returns a dictionary of nans for each metric for the task.
    """
    metrics = get_default_metric_with_objective(task)
    return {m: np.nan for m in metrics}


def get_metric_ranges(task, for_assert_sane=False):
    """Get the metric range for the task.

    :param task: string "classification" or "regression"
    :param for_assert_sane: boolean indicates that this is being used
        by assert_metrics_sane and it is unsafe to apply clips.
    :return: returns tuple with min values dict and max value dict.
    """
    minimums = get_min_values(task)
    maximums = get_max_values(task, for_assert_sane=for_assert_sane)
    return minimums, maximums


def get_worst_values(task, for_assert_sane=False):
    """Get the worst values for metrics of the task.

    :param task: string "classification" or "regression"
    :param for_assert_sane: boolean indicates that this is being used
        by assert_metrics_sane and it is unsafe to apply clips.
    :return: returns a dictionary of metrics with the worst values.
    """
    minimums, maximums = get_metric_ranges(
        task, for_assert_sane=for_assert_sane)
    metrics = get_default_metric_with_objective(task)
    _MAX = constants.OptimizerObjectives.MAXIMIZE
    bad = {m: minimums[m] if obj == _MAX else maximums[m]
           for m, obj in metrics.items()}
    return bad


def get_min_values(task):
    """Get the minimum values for metrics for the task.

    :param task: string "classification" or "regression"
    :return: returns a dictionary of metrics with the min values.
    """
    metrics = get_default_metric_with_objective(task)
    # 0 is the minimum for metrics that are minimized and maximized
    bad = {m: 0.0 for m, obj in metrics.items()}
    bad[constants.Metric.R2Score] = -10.0  # R2 is different, clipped to -10.0
    bad[constants.Metric.Spearman] = -1.0
    return bad


def get_max_values(task, for_assert_sane=False):
    """Get the maximum values for metrics of the task.

    :param task: string "classification" or "regression"
    :param for_assert_sane: boolean indicates that this is being used
        by assert_metrics_sane and it is unsafe to apply clips.
    :return: returns a dictionary of metrics with the max values.
    """
    metrics = get_default_metric_with_objective(task)
    _MAX = constants.OptimizerObjectives.MAXIMIZE
    bad = {m: 1.0 if obj == _MAX else sys.float_info.max
           for m, obj in metrics.items()}
    # so the assertions don't fail, could also clip metrics instead
    if not for_assert_sane:
        bad[constants.Metric.LogLoss] = 10.0
        bad[constants.Metric.NormRMSE] = 10.0
        bad[constants.Metric.NormRMSLE] = 10.0
        bad[constants.Metric.NormMeanAbsError] = 10.0
        bad[constants.Metric.NormMedianAbsError] = 10.0
    return bad


def assert_metrics_sane(metrics, task):
    """Assert that the given metric values are sane.

    The metric values should not be worse than the worst possible values
    for those metrics given the objectives for those metrics
    :param task: string "classification" or "regression"
    """
    worst = get_worst_values(task, for_assert_sane=True)
    obj = get_default_metric_with_objective(task)
    for k, v in metrics.items():
        if not np.isscalar(v) or np.isnan(v):
            continue
        # This seems to vary a lot.
        if k == constants.Metric.ExplainedVariance:
            continue
        if obj[k] == constants.OptimizerObjectives.MAXIMIZE:
            assert v >= worst[k], (
                '{0} is not worse than {1} for metric {2}'.format(
                    worst[k], v, k))
        else:
            assert v <= worst[k], (
                '{0} is not worse than {1} for metric {2}'.format(
                    worst[k], v, k))


def get_default_metric_with_objective(task):
    """Get the dictionary of metric -> objective for the given task.

    :param task: string "classification" or "regression"
    :return: dictionary of metric -> objective
    """
    if task == constants.Tasks.CLASSIFICATION:
        return constants.MetricObjective.Classification
    elif task == constants.Tasks.REGRESSION:
        return constants.MetricObjective.Regression
    elif task == constants.Subtasks.FORECASTING:
        return constants.MetricObjective.Forecast
    else:
        raise NotImplementedError


def get_scalar_metrics(task):
    """Get the scalar metrics supported for a given task.

    :param task: string "classification" or "regression"
    :return: a list of the default metrics supported for the task
    """
    if task == constants.Tasks.CLASSIFICATION:
        return list(constants.Metric.SCALAR_CLASSIFICATION_SET)
    elif task == constants.Tasks.REGRESSION:
        return list(constants.Metric.SCALAR_REGRESSION_SET)
    else:
        raise NotImplementedError


def get_default_metrics(task):
    """Get the metrics supported for a given task as a set.

    :param task: string "classification" or "regression"
    :return: a list of the default metrics supported for the task
    """
    if task == constants.Tasks.CLASSIFICATION:
        return constants.Metric.CLASSIFICATION_SET
    elif task == constants.Tasks.REGRESSION:
        return constants.Metric.REGRESSION_SET
    elif task == constants.Subtasks.FORECASTING:
        return (constants.Metric.REGRESSION_SET | constants.Metric.FORECAST_SET)
    else:
        raise NotImplementedError


def _class_averaged_score(score_func,
                          y_true,
                          y_score,
                          average,
                          logger,
                          test_class_labels=None,
                          class_labels=None,
                          metric_name=None,
                          **kwargs):
    """Calculate class-averaged metrics like AUC_weighted only on classes present in test set.

    For the case when a model was trained on more classes than what the validation (or 'test') dataset contains
    we'll only average over those classes present in the validation dataset.

    Note that this implementation assumes that the y_score and y_true matrices have padding so that
    there is a column for all classes present in the entire dataset.  Thus, each column should map to
    the class_labels array.

    Example:

    Dataset classes: 0, 1, 2, 3, 4
    Training classes: 0, 1, 2, 3, 4
    Validation classes: 0, 1, 2, 4

    Initial predicted probabilities: (columns ordered by ascending labels)
    [[.25,  .2,  .3,   0, .25],
     [  0, .25,   0, .25,  .5],
     [.33, .33, .34,   0,  .0],
     [  0,  .7,   0,  .3,   0],
     [.25,  .3,   0,  .2, .25]]

    In this example the model was trained on all classes from the dataset, but class 3 was left
    out of the validation set. There is no meaningful interpretation for the score of class 3,
    so the column for label 3 of the predicted probabilities is dropped from the calculation (see below).

    Resulting predicted probabilities:
    [[.25,  .2,  .3, .25],
     [  0, .25,   0,  .5],
     [.33, .33, .34,  .0],
     [  0,  .7,   0,   0],
     [.25,  .3,   0, .25]]

    From this new matrix of predicted probabilities the class-averaged metrics are calculated normally by sklearn.

    :param score_func: sklearn score function that has an api like sklearn.metrics.roc_auc_score
    :param y_true: the test class label indicator matrix of shape (n_test_examples, len(class_labels))
    :param y_score: the predict_proba matrix from X_test, shape (n_test_examples, len(class_labels))
    :param average: the averaging strategy (e.g. "micro", "macro", etc.)
    :param test_class_labels: the class labels present in the validation set
    :param class_labels: the class labels present the entire dataset
    :kwargs keyword arguments to be passed into score_func
    :return: the output of score_func
    """
    if class_labels is not None:
        num_classes = len(class_labels)
    else:
        num_classes = 0

    # Micro averaging does not perform class level averaging, so handling imbalanced classes is not needed
    is_class_averaging = average != "micro"
    if is_class_averaging and \
            test_class_labels is not None \
            and class_labels is not None \
            and num_classes > 2:

        # Assert that padding logic is true
        if y_true.ndim == 2:
            padding_condition_y_true = np.shape(y_true)[1] == num_classes
        else:
            padding_condition_y_true = False

        if y_score.ndim == 2:
            padding_condition_y_score = np.shape(y_score)[1] == num_classes
        else:
            padding_condition_y_score = False

        msg = "len(class_labels) = {} should correpond to {}'s shape of = {}"
        assert padding_condition_y_true, msg.format(len(class_labels), "y_true", np.shape(y_true))
        assert padding_condition_y_score, msg.format(len(class_labels), "y_score", np.shape(y_score))

        # Intersection logic for only scoring on classes present in test set
        intersection_labels = np.intersect1d(test_class_labels, class_labels)
        intersection_indices = np.array(
            [i for i, val in enumerate(class_labels) if val in intersection_labels])
        dropped_classes = [_class for _class in class_labels if _class not in intersection_labels]
        if len(dropped_classes) > 0:
            dropped_msg_fmt = "For {}, the following classes were ignored since they are not in the test set: {}"
            dropped_msg = dropped_msg_fmt.format(metric_name, dropped_classes)
            logger.info(dropped_msg)
        y_true = y_true[:, intersection_indices]
        y_score = y_score[:, intersection_indices]

    if metric_name == constants.Metric.NormMacroRecall:
        num_classes = max(y_true.shape[1], 2)
        return score_func(y_true, y_score, logger=logger, num_classes=num_classes, **kwargs)
    else:
        # Else no intersection is performed we proceed with normal metric computation
        return score_func(y_true, y_score, average=average, **kwargs)


def _roc_auc_score_wrapper(y_true, y_score, test_class_labels, class_labels,
                           logger, metric_name, average='macro', **kwargs):
    return _class_averaged_score(sklearn.metrics.roc_auc_score,
                                 y_true=y_true,
                                 y_score=y_score,
                                 test_class_labels=test_class_labels,
                                 class_labels=class_labels,
                                 average=average,
                                 logger=logger,
                                 metric_name=metric_name,
                                 **kwargs)


def _average_precision_score_wrapper(y_true,
                                     y_score, test_class_labels, class_labels, logger,
                                     metric_name, average='macro', **kwargs):
    return _class_averaged_score(sklearn.metrics.average_precision_score,
                                 y_true=y_true,
                                 y_score=y_score,
                                 test_class_labels=test_class_labels,
                                 class_labels=class_labels,
                                 average=average,
                                 logger=logger,
                                 metric_name=metric_name,
                                 **kwargs)


def _norm_macro_recall_wrapper(y_true,
                               y_score, test_class_labels, class_labels, logger,
                               metric_name, average=None, **kwargs):
    return _class_averaged_score(_norm_macro_recall,
                                 y_true=y_true,
                                 y_score=y_score,
                                 test_class_labels=test_class_labels,
                                 class_labels=class_labels,
                                 average=average,
                                 logger=logger,
                                 metric_name=metric_name,
                                 **kwargs)


def _norm_macro_recall(y_true, y_pred, num_classes, logger=None, **kwargs):
    # need to use the actual prediction not the matrix here but need the matrix passed to _class_averaged_score
    # if we start doing calibration we need to change this
    BINARY_CUTOFF = .5
    R = 1 / num_classes
    if y_true.shape[1] > 1:
        y_true = np.argmax(y_true, 1)
    if y_pred.ndim == 1:
        y_pred = np.array(y_pred > BINARY_CUTOFF, dtype=int)
    else:
        y_pred = np.argmax(y_pred, 1)
    cmat = try_calculate_metric(
        sklearn.metrics.confusion_matrix,
        y_true=y_true, y_pred=y_pred,
        sample_weight=kwargs.get('sample_weight'),
        logger=logger)
    if isinstance(cmat, float):
        return constants.Defaults.DEFAULT_PIPELINE_SCORE
    else:
        cms = cmat.sum(axis=1)
        if cms.sum() == 0:
            return constants.Defaults.DEFAULT_PIPELINE_SCORE
        else:
            return max(
                0.0,
                (np.mean(cmat.diagonal() / cmat.sum(axis=1)) - R) /
                (1 - R))


def _mape(y_true: np.ndarray, y_pred: np.ndarray, logger: Optional[logging.Logger] = None) -> np.float64:
    """
    Calcualte the mean absolute precentage error.

    We remove NA and values where actual is close to zero to keep score from approaching inf.
    """
    not_na = ~(np.isnan(y_true))
    not_zero = ~np.isclose(y_true, 0.0)
    safe = not_na & not_zero

    y_true_safe = y_true[safe]
    y_pred_safe = y_pred[safe]

    if len(y_true_safe) < 1:
        raise ValueError("Not enough values to calculate MAPE. Ensure y_true has non-nan, non-zero values.")
    ape = 100 * np.abs((y_true_safe - y_pred_safe) / y_true_safe)

    return np.mean(ape)


def compute_metrics(y_pred: np.ndarray,
                    y_test: np.ndarray,
                    metrics: Optional[List[str]] = None,
                    task: str = constants.Tasks.CLASSIFICATION,
                    sample_weight: Optional[np.ndarray] = None,
                    num_classes: Optional[int] = None,
                    class_labels: Optional[np.ndarray] = None,
                    trained_class_labels: Optional[np.ndarray] = None,
                    y_transformer: Optional[TransformerMixin] = None,
                    y_max: Optional[float] = None,
                    y_min: Optional[float] = None,
                    y_std: Optional[float] = None,
                    bin_info: Optional[Dict[str, float]] = None) -> Dict[str, Union[float, Dict[str, Any]]]:
    """Compute the metrics given the test data results.

    :param y_pred: predicted value (in probability in case of classification)
    :param y_test: target value
    :param metrics: metric/metrics to compute
    :param num_classes: num of classes for classification task
    :param class_labels: labels for classification task
    :param trained_class_labels: labels for classification task as identified by the trained model
    :param task: ml task
    :param y_transformer: transformer used to transform labels
    :param y_max: max target value for regression task
    :param y_min: min target value for regression task
    :param y_std: standard deviation of regression targets
    :param sample_weight: weights for samples in dataset
    :param bin_info: information on how to bin regression data
    :return: returns a dictionary with metrics computed
    """
    if metrics is None:
        metrics = get_default_metrics(task)

    if task == constants.Tasks.CLASSIFICATION:
        return compute_metrics_classification(y_pred, y_test, metrics,
                                              num_classes=num_classes,
                                              sample_weight=sample_weight,
                                              class_labels=class_labels,
                                              trained_class_labels=trained_class_labels,
                                              y_transformer=y_transformer)
    elif task == constants.Tasks.REGRESSION:
        return compute_metrics_regression(y_pred, y_test, metrics,
                                          y_max, y_min, y_std,
                                          sample_weight=sample_weight,
                                          bin_info=bin_info)
    else:
        raise NotImplementedError


def compute_metrics_classification(y_pred_probs: np.ndarray,
                                   y_test: np.ndarray,
                                   metrics: List[str],
                                   num_classes: Optional[int] = None,
                                   sample_weight: Optional[np.ndarray] = None,
                                   class_labels: Optional[np.ndarray] = None,
                                   trained_class_labels: Optional[np.ndarray] = None,
                                   y_transformer: Optional[TransformerMixin] = None,
                                   logger: Optional[logging.Logger] = None) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute the metrics for a classification task.

    All class labels for y should come
    as seen by the fitted model (i.e. if the fitted model uses a y transformer the labels
    should also come transformed).

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if metrics
    calculation failed.

    :param y_pred_probs: The probability predictions.
    :param y_test: The target value. Transformed if using a y transformer.
    :param metrics: metric/metrics to compute
    :type metrics: list
    :param class_labels:
        Labels for classification task. This should be the entire y label set. These should
         be transformed if using a y transformer. Required for all non-scalars to be calculated.
    :param trained_class_labels:
        Labels for classification task as seen (trained on) by the
        trained model. Required when training set did not see all classes from full set.
    :param num_classes: Number of classes in the entire y set. Required for all metrics.
    :param sample_weight:
        The sample weight to be used on metrics calculation. This does not need
        to match sample weights on the fitted model.
    :param y_transformer: Used to inverse transform labels from `y_test`. Required for non-scalar metrics.
    :param logger: A logger to log errors and warnings
    :return: A dictionary with metrics computed.
    """
    if logger is None:
        logger = log_utils.NULL_LOGGER

    logger.info("Computing classification metrics")

    if y_pred_probs is None:
        raise ClientException("y_pred_probs must not be None")
    if y_test is None:
        raise ClientException("y_test must not be None")

    # num_classes should equal len(class_labels) if both provided
    if num_classes is not None and class_labels is not None and num_classes != len(class_labels):
        raise ClientException("num_classes ({}) does not equal class_labels length ({})."
                              .format(num_classes, len(class_labels)))

    # check trained_class_labels matches y_pred_probs
    if trained_class_labels is not None and len(trained_class_labels) != y_pred_probs.shape[1]:
        raise ClientException("trained_class_labels length ({}) does not match y_pred_probs.shape[1] ({})."
                              .format(len(trained_class_labels), y_pred_probs.shape[1]))

    # if trained_class_labels is not passed in we rely on class_labels or num_classes (or both), so check to make sure
    # they match y_pred_probs
    if trained_class_labels is None:
        if class_labels is not None and len(class_labels) != y_pred_probs.shape[1]:
            raise ClientException("class_labels length ({}) does not match y_pred_probs.shape[1] ({}) and you did not"
                                  " pass trained_class_labels.".format(len(class_labels), y_pred_probs.shape[1]))

        if num_classes is not None and num_classes != y_pred_probs.shape[1]:
            raise ClientException("num_classes ({}) does not match y_pred_probs.shape[1] ({}) and you did not pass"
                                  " trained_class_labels.".format(num_classes, y_pred_probs.shape[1]))

    if y_test.dtype == np.float32 or y_test.dtype == np.float64:
        # Assume that the task is set appropriately and that the data
        # just had a float label arbitrarily.
        y_test = y_test.astype(np.int64)

    # Some metrics use an eps of 1e-15 by default, which results in nans
    # for float32.
    if y_pred_probs.dtype == np.float32:
        y_pred_probs = y_pred_probs.astype(np.float64)

    if num_classes is None:
        num_classes = max(len(np.unique(y_test)), y_pred_probs.shape[1])

    if metrics is None:
        metrics = get_default_metrics(constants.Tasks.CLASSIFICATION)

    y_test = np.ravel(y_test)

    results = {}

    binarizer = sklearn.preprocessing.LabelBinarizer()

    if class_labels is not None:
        binarizer.fit(class_labels)
    else:
        binarizer.fit(y_test)

    y_test_bin = binarizer.transform(y_test)

    # Test class labels are needed to avoid imbalanced class problems for metrics
    # like AUC_macro.
    test_class_labels = np.unique(y_test)

    # we need to make sure that we have probabilities from all classes in the dataset
    # in case the trained model wasn't fitted on the entire set of class labels
    y_pred_probs = metrics_utils.pad_predictions(y_pred_probs, trained_class_labels, class_labels)

    y_pred_probs_full = y_pred_probs
    y_pred_bin = np.argmax(y_pred_probs_full, axis=1)

    if class_labels is not None:
        y_pred_bin = class_labels[y_pred_bin]

    if num_classes is None:
        num_classes = max(len(np.unique(y_test)), len(np.unique(y_pred_bin)))

    if num_classes == 2:
        # if both classes probs are passed, pick the positive class probs as
        # binarizer only outputs single column
        y_pred_probs = y_pred_probs[:, 1]

    # For accuracy table and confusion matrix,
    # the y_test_original is used to keep label consistency.
    # For other metrics, the y_test is passed.
    y_test_original = y_test
    if class_labels is not None:
        class_labels_original = class_labels
    if y_transformer is not None:
        y_test_original = y_transformer.inverse_transform(y_test_original)
        if class_labels is not None:
            class_labels_original = y_transformer.inverse_transform(class_labels_original)

    if constants.Metric.Accuracy in metrics:
        results[constants.Metric.Accuracy] = try_calculate_metric(
            score=sklearn.metrics.accuracy_score,
            y_true=y_test, y_pred=y_pred_bin,
            sample_weight=sample_weight,
            logger=logger)

    if constants.Metric.WeightedAccuracy in metrics:
        # accuracy weighted by number of elements for each class
        w = np.ones(y_test.shape[0])
        for idx, i in enumerate(np.bincount(y_test.ravel())):
            w[y_test.ravel() == idx] *= (i / float(y_test.ravel().shape[0]))
        results[constants.Metric.WeightedAccuracy] = try_calculate_metric(
            score=sklearn.metrics.accuracy_score,
            y_true=y_test, y_pred=y_pred_bin,
            sample_weight=w,
            logger=logger)

    if constants.Metric.NormMacroRecall in metrics:
        # this is what is used here
        # https://github.com/ch-imad/AutoMl_Challenge/blob/2353ec0
        # /Starting_kit/scoring_program/libscores.py#L187
        # for the AutoML challenge
        # https://competitions.codalab.org/competitions/2321
        # #learn_the_details-evaluation
        # This is a normalized macro averaged recall, rather than accuracy
        # https://github.com/scikit-learn/scikit-learn/issues/6747
        # #issuecomment-217587210
        # Random performance is 0.0 perfect performance is 1.0
        results[constants.Metric.NormMacroRecall] = try_calculate_metric(
            _norm_macro_recall_wrapper,
            y_true=y_test_bin, y_score=y_pred_probs,
            sample_weight=sample_weight,
            test_class_labels=test_class_labels,
            class_labels=class_labels,
            metric_name=constants.Metric.NormMacroRecall,
            logger=logger,
            is_pass_logger=True)

    if constants.Metric.LogLoss in metrics:
        results[constants.Metric.LogLoss] = try_calculate_metric(
            sklearn.metrics.log_loss,
            y_true=y_test, y_pred=y_pred_probs,
            labels=np.arange(0, num_classes),
            sample_weight=sample_weight,
            logger=logger)

    for name in metrics:
        # TODO: Remove this conditional once all metrics implement
        # the Metric interface for compute and aggregate
        if name in [constants.Metric.AccuracyTable,
                    constants.Metric.ConfusionMatrix]:
            try:
                metric_class = Metric.get_metric_class(name)
                metric = metric_class(y_test_original, y_pred_probs_full, logger=logger)
                score = metric.compute(sample_weights=sample_weight,
                                       class_labels=class_labels_original)
                results[name] = score
            except Exception as e:
                log_utils.log_traceback(e, logger, is_critical=False)
                if Metric.is_scalar(name):
                    results[name] = np.nan
                else:
                    results[name] = Metric.get_error_metric()

    for m in metrics:
        if 'AUC' in m:
            results[m] = try_calculate_metric(
                _roc_auc_score_wrapper,
                y_true=y_test_bin, y_score=y_pred_probs,
                average=m.replace('AUC_', ''),
                sample_weight=sample_weight,
                test_class_labels=test_class_labels,
                class_labels=class_labels,
                metric_name=m,
                logger=logger,
                is_pass_logger=True)

        if 'f1_score' in m:
            results[m] = try_calculate_metric(
                sklearn.metrics.f1_score,
                y_true=y_test, y_pred=y_pred_bin,
                average=m.replace('f1_score_', ''),
                sample_weight=sample_weight,
                logger=logger)

        if 'precision_score' in m and 'average' not in m:
            results[m] = try_calculate_metric(
                sklearn.metrics.precision_score,
                y_true=y_test, y_pred=y_pred_bin,
                average=m.replace('precision_score_', ''),
                sample_weight=sample_weight,
                logger=logger)

        if 'recall_score' in m or m == constants.Metric.BalancedAccuracy:
            if 'recall_score' in m:
                average_modifier = m.replace('recall_score_', '')
            elif m == constants.Metric.BalancedAccuracy:
                average_modifier = 'macro'
            results[m] = try_calculate_metric(
                sklearn.metrics.recall_score,
                y_true=y_test, y_pred=y_pred_bin,
                average=average_modifier,
                sample_weight=sample_weight,
                logger=logger)

        if 'average_precision_score' in m:
            results[m] = try_calculate_metric(
                _average_precision_score_wrapper,
                y_true=y_test_bin, y_score=y_pred_probs,
                average=m.replace('average_precision_score_', ''),
                sample_weight=sample_weight,
                test_class_labels=test_class_labels,
                class_labels=class_labels,
                metric_name=m,
                logger=logger,
                is_pass_logger=True)

    assert_metrics_sane(results, constants.Tasks.CLASSIFICATION)
    return results


def compute_mean_cv_scores(
        scores: List[Dict[Any, Any]],
        metrics: List[str],
        logger: Optional[logging.Logger] = None) -> Dict[str, Union[float, Dict[str, Any]]]:
    """Compute mean scores across validation folds.

    :param scores: list of metrics
    :param metrics: list of metrics to compute means for.
    :return: mean score for each of the metrics.
    """
    means = {}      # type: Dict[str, Union[float, Dict[str, Any]]]
    for name in metrics:
        if name in scores[0]:
            split_results = [score[name] for score in scores if name in score]
            if name in constants.Metric.SCALAR_FULL_SET:
                means[name] = float(np.mean(split_results))
            elif name in constants.Metric.NONSCALAR_FULL_SET:
                metric_class = Metric.get_metric_class(name)
                try:
                    means[name] = metric_class.aggregate(split_results)
                except Exception as e:
                    log_utils.log_traceback(e, logger, is_critical=False)
                    means[name] = Metric.get_error_metric()
    for train_type in constants.TrainingResultsType.ALL_TIME:
        train_times = [res[train_type] for res in scores if train_type in res]
        if train_times:
            means[train_type] = float(np.mean(train_times))

    return means


def try_calculate_metric(score, logger=None, is_pass_logger=False, **kwargs):
    """Calculate the metric given a metric calculation function.

    :param score: an sklearn metric calculation function to score
    :param logger: a logger (or SafeLogger) for logging errors
    :param is_pass_logger: flag for whether the logger should be passed into score
    :return: the calculated score (or nan if there was an exception)
    """
    try:
        if is_pass_logger:
            return score(logger=logger, **kwargs)
        else:
            return score(**kwargs)
    except Exception as e:
        log_utils.log_traceback(e, logger, is_critical=False)
        return constants.Defaults.DEFAULT_PIPELINE_SCORE


def compute_metrics_regression(y_pred: np.ndarray,
                               y_test: np.ndarray,
                               metrics: List[str],
                               y_max: Optional[float] = None,
                               y_min: Optional[float] = None,
                               y_std: Optional[float] = None,
                               sample_weight: Optional[np.ndarray] = None,
                               bin_info: Optional[Dict[str, float]] = None,
                               logger: Optional[logging.Logger] = None) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute the metrics for a regression task.

    `y_max`, `y_min`, and `y_std` should be based on `y_test` information unless
    you would like to compute multiple metrics for comparison (ex. cross validation),
    in which case, you should use a common range and standard deviation. You may
    also pass in `y_max`, `y_min`, and `y_std` if you do not want it to be calculated.

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if metric calculation failed.

    :param y_pred: The predict values.
    :param y_test: The target values.
    :param metrics: List of metric names for metrics to calculate.
    :type metrics: list
    :param y_max: The max target value.
    :param y_min: The min target value.
    :param y_std: The standard deviation of targets value.
    :param sample_weight:
        The sample weight to be used on metrics calculation. This does not need
        to match sample weights on the fitted model.
    :param bin_info:
        The binning information for true values. This should be calculated from
        :class:`ClientDatasets` :func:`make_bin_info`. Required for calculating
        non-scalar metrics.
    :param logger: A logger to log errors and warnings
    :return: A dictionary with metrics computed.
    """
    if logger is None:
        logger = log_utils.NULL_LOGGER

    logger.info("Computing regression metrics")

    if y_pred is None:
        raise DataException("y_pred must not be None")
    if y_test is None:
        raise DataException("y_test must not be None")

    y_test = np.ravel(y_test)
    y_pred = np.ravel(y_pred)

    if y_min is None:
        y_min = np.min(y_test)
    if y_max is None:
        y_max = np.max(y_test)
        assert y_max > y_min
    if y_std is None:
        y_std = np.std(y_test)

    if metrics is None:
        metrics = get_default_metrics(constants.Tasks.REGRESSION)

    try:
        sklearn.utils.check_array(y_test, ensure_2d=False)
    except ValueError as e:
        raise DataException.from_exception(e, 'y_test failed sklearn.utils.check_array() validation check.')

    try:
        sklearn.utils.check_array(y_pred, ensure_2d=False)
    except ValueError as e:
        raise DataException.from_exception(e, 'y_pred failed sklearn.utils.check_array() validation check.')

    has_negative_values = False
    if (y_test < 0).any() or (y_pred < 0).any():
        has_negative_values = True

    results = {}

    # Regression metrics The scale of some of the metrics below depends on the
    # scale of the data. For this reason, we rescale it by the distance between
    # y_max and y_min. Since this can produce negative values we take the abs
    # of the distance https://en.wikipedia.org/wiki/Root-mean-square_deviation

    if constants.Metric.ExplainedVariance in metrics:
        try:
            bac = sklearn.metrics.explained_variance_score(
                y_test, y_pred, sample_weight=sample_weight,
                multioutput='uniform_average')
        except ValueError as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            bac = np.nan
        results[constants.Metric.ExplainedVariance] = bac

    if constants.Metric.R2Score in metrics:
        try:
            bac = sklearn.metrics.r2_score(
                y_test, y_pred,
                sample_weight=sample_weight, multioutput='uniform_average')
        except ValueError as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            bac = np.nan
        results[constants.Metric.R2Score] = np.clip(
            bac, constants.Metric.CLIPS_NEG[constants.Metric.R2Score], 1.0)

    if constants.Metric.Spearman in metrics:
        try:
            bac = st.spearmanr(y_test, y_pred)[0]
        except ValueError as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            bac = np.nan
        results[constants.Metric.Spearman] = bac

    if constants.Metric.MAPE in metrics:
        try:
            bac = try_calculate_metric(_mape, y_true=y_test, y_pred=y_pred, logger=logger)
        except ValueError as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            bac = np.nan
        results[constants.Metric.MAPE] = bac

    # mean AE
    if constants.Metric.MeanAbsError in metrics:
        try:
            bac = sklearn.metrics.mean_absolute_error(
                y_test, y_pred,
                sample_weight=sample_weight, multioutput='uniform_average')
        except ValueError as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            bac = np.nan
        results[constants.Metric.MeanAbsError] = bac

    if constants.Metric.NormMeanAbsError in metrics:
        try:
            bac = sklearn.metrics.mean_absolute_error(
                y_test, y_pred,
                sample_weight=sample_weight, multioutput='uniform_average')
            bac = bac / np.abs(y_max - y_min)
        except ValueError as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            bac = np.nan
        results[constants.Metric.NormMeanAbsError] = bac

    # median AE
    if constants.Metric.MedianAbsError in metrics:
        try:
            bac = sklearn.metrics.median_absolute_error(y_test, y_pred)
        except ValueError as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            bac = np.nan
        results[constants.Metric.MedianAbsError] = bac

    if constants.Metric.NormMedianAbsError in metrics:
        try:
            bac = sklearn.metrics.median_absolute_error(y_test, y_pred)
            bac = bac / np.abs(y_max - y_min)
        except ValueError as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            bac = np.nan
        results[constants.Metric.NormMedianAbsError] = bac

    # RMSE
    if constants.Metric.RMSE in metrics:
        try:
            bac = np.sqrt(
                sklearn.metrics.mean_squared_error(
                    y_test, y_pred, sample_weight=sample_weight,
                    multioutput='uniform_average'))
        except ValueError as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            bac = np.nan
        results[constants.Metric.RMSE] = bac

    if constants.Metric.NormRMSE in metrics:
        try:
            bac = np.sqrt(
                sklearn.metrics.mean_squared_error(
                    y_test, y_pred, sample_weight=sample_weight,
                    multioutput='uniform_average'))
            bac = bac / np.abs(y_max - y_min)
        except ValueError as e:
            log_utils.log_traceback(e, logger, is_critical=False)
            bac = np.nan
        results[constants.Metric.NormRMSE] = np.clip(
            bac, 0,
            constants.Metric.CLIPS_POS.get(constants.Metric.NormRMSE, 100))

    # RMSLE
    if constants.Metric.RMSLE in metrics:
        if has_negative_values:
            logger.warning('Skipping RMSLE calculation since y_test/y_pred contains negative values.')
            bac = np.nan
        else:
            try:
                bac = np.sqrt(
                    sklearn.metrics.mean_squared_log_error(
                        y_test, y_pred, sample_weight=sample_weight,
                        multioutput='uniform_average')
                )
                bac = np.clip(
                    bac, 0,
                    constants.Metric.CLIPS_POS.get(constants.Metric.RMSLE, 100))
            except ValueError as e:
                log_utils.log_traceback(e, logger, is_critical=False)
                bac = np.nan
        results[constants.Metric.RMSLE] = bac

    if constants.Metric.NormRMSLE in metrics:
        if has_negative_values:
            logger.warning('Skipping NormRMSLE calculation since y_test/y_pred contains negative values.')
            bac = np.nan
        else:
            try:
                bac = np.sqrt(
                    sklearn.metrics.mean_squared_log_error(
                        y_test, y_pred, sample_weight=sample_weight,
                        multioutput='uniform_average'))
                bac = bac / np.abs(np.log1p(y_max) - np.log1p(y_min))
                bac = np.clip(
                    bac, 0,
                    constants.Metric.CLIPS_POS.get(
                        constants.Metric.NormRMSLE, 100))
            except ValueError as e:
                log_utils.log_traceback(e, logger, is_critical=False)
                bac = np.nan
        results[constants.Metric.NormRMSLE] = bac

    for name in metrics:
        # TODO: Remove this conditional once all metrics implement
        # the Metric interface for compute and aggregate
        if name in [constants.Metric.Residuals,
                    constants.Metric.PredictedTrue]:
            try:
                metric_class = Metric.get_metric_class(name)
                metric = metric_class(y_test, y_pred)
                results[name] = metric.compute(bin_info=bin_info,
                                               y_std=y_std)
            except Exception as e:
                log_utils.log_traceback(e, logger, is_critical=False)
                if Metric.is_scalar(name):
                    results[name] = np.nan
                else:
                    results[name] = Metric.get_error_metric()

    assert_metrics_sane(results, constants.Tasks.REGRESSION)
    return results


def compute_metrics_forecasting(y_pred: np.ndarray,
                                y_test: np.ndarray,
                                horizons: np.ndarray,
                                metrics: List[str],
                                y_max: Optional[float] = None,
                                y_min: Optional[float] = None,
                                y_std: Optional[float] = None,
                                sample_weight: Optional[np.ndarray] = None,
                                bin_info: Optional[Dict[str, float]] = None,
                                logger: Optional[logging.Logger] = None) -> Dict[str, Union[float, Dict[str, Any]]]:
    """
    Compute the metrics for a forecast task.

    `y_max`, `y_min`, and `y_std` should be based on `y_test` information unless
    you would like to compute multiple metrics for comparison (ex. cross validation),
    in which case, you should use a common range and standard deviation. You may
    also pass in `y_max`, `y_min`, and `y_std` if you do not want it to be calculated.

    All metrics present in `metrics` will be present in the output dictionary with either
    the value(s) calculated or `nan` if metric calculation failed.

    :param y_pred: The predict values.
    :param y_test: The target values.
    :param horizons: The horizon of each prediction. If missing or not relevant, pass None.
    :param metrics: List of metric names for metrics to calculate.
    :type metrics: list
    :param y_max: The max target value.
    :param y_min: The min target value.
    :param y_std: The standard deviation of targets value.
    :param sample_weight:
        The sample weight to be used on metrics calculation. This does not need
        to match sample weights on the fitted model.
    :param bin_info:
        The binning information for true values. This should be calculated from
        :class:`ClientDatasets` :func:`make_bin_info`. Required for calculating
        non-scalar metrics.
    :param logger: A logger to log errors and warnings
    :return: A dictionary with metrics computed.
    """
    if len(horizons) != len(y_pred) or len(y_pred) != len(y_test):
        raise ValueError("Data to calculate metrics doesn't align.")

    y_test = np.ravel(y_test)
    y_pred = np.ravel(y_pred)

    if logger is None:
        logger = log_utils.NULL_LOGGER

    results = {}
    for name in metrics:
        if name in constants.Metric.NONSCALAR_FORECAST_SET:
            try:
                metric_class = Metric.get_metric_class(name)
                metric = metric_class(y_pred, y_test, horizons, logger=logger)
                results[name] = metric.compute(bin_info=bin_info,
                                               y_std=y_std)
            except Exception as e:
                log_utils.log_traceback(e, logger, is_critical=False)
                if Metric.is_scalar(name):
                    results[name] = np.nan
                else:
                    results[name] = Metric.get_error_metric()
    return results


class Metric:
    """Abstract class for all metrics."""

    SCHEMA_TYPE = 'schema_type'
    SCHEMA_VERSION = 'schema_version'
    DATA = 'data'

    ERRORS = 'errors'

    def __init__(self, y_test, y_pred, logger=None):
        """Initialize the metric class.

        :param y_test: The true labels for computing the metric.
        :param y_pred: The predicted labels for computing the metric.
        """
        if y_test.shape[0] != y_pred.shape[0]:
            raise ValueError("Mismatched input shapes: y_test={}, y_pred={}"
                             .format(y_test.shape, y_pred.shape))
        self._y_test = y_test
        self._y_pred = y_pred
        self._logger = logger if logger is not None else log_utils.NULL_LOGGER
        self._data = {}     # type: Dict[Union[str, int], Any]

    @staticmethod
    def aggregate(scores):
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        raise NotImplementedError

    @staticmethod
    def check_aggregate_scores(scores):
        """
        Check that the scores to be aggregated are reasonable.

        :param scores: scores computed by a metric
        :return: an aggregated score of the same shape as each of the inputs
        """
        if len(scores) == 0:
            raise ValueError("Scores must not be empty to aggregate")
        if np.nan in scores:
            return False
        for score in scores:
            if Metric.is_error_metric(score):
                return False
        return True

    @staticmethod
    def is_error_metric(score):
        """
        Get whether the given score is an error metric.

        :param score: the score to test
        :return: True if the metric errored on computation, otherwise False
        """
        return Metric.ERRORS in score

    @staticmethod
    def get_error_metric(message: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get a dictionary representation of a failed nonscalar metric.

        :param message: the error message that was thrown
        :return: dictionary with the error message
        """
        if message is None:
            message = "Unexpected error occurred while calculating metric"
        return {
            Metric.ERRORS: [str(message)]
        }

    @staticmethod
    def is_scalar(metric_name):
        """
        Check whether a given metric is scalar or nonscalar.

        :param metric_name: the name of the metric found in constants.py
        :return: boolean for if the metric is scalar
        """
        if metric_name in constants.Metric.SCALAR_FULL_SET:
            return True
        elif metric_name in constants.Metric.NONSCALAR_FULL_SET:
            return False
        raise ValueError("{} metric is not supported".format(metric_name))

    @staticmethod
    def _data_to_dict(schema_type, schema_version, data):
        return {
            Metric.SCHEMA_TYPE: schema_type,
            Metric.SCHEMA_VERSION: schema_version,
            Metric.DATA: data
        }

    @staticmethod
    def get_metric_class(metric_name):
        """Return the metric class based on the constant name of the metric.

        :param metric: the constant name of the metric
        :return: the class of the metric
        """
        class_map = {
            constants.Metric.AccuracyTable: AccuracyTableMetric,
            constants.Metric.ConfusionMatrix: ConfusionMatrixMetric,
            constants.Metric.Residuals: ResidualsMetric,
            constants.Metric.PredictedTrue: PredictedTrueMetric,
            constants.Metric.ForecastResiduals: ForecastResidualsMetric,
            constants.Metric.ForecastMAPE: ForecastMapeMetric
        }
        if metric_name not in class_map:
            raise ValueError("Metric class {} was not found in \
                              Metric.get_metric_class".format(metric_name))
        return class_map[metric_name]

    @staticmethod
    def _make_json_safe(o):
        make_safe = Metric._make_json_safe
        scalar_types = [int, float, str, type(None)]
        if type(o) in scalar_types:
            return o
        elif isinstance(o, dict):
            return {k: make_safe(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [make_safe(v) for v in o]
        elif isinstance(o, tuple):
            return tuple(make_safe(v) for v in o)
        elif isinstance(o, np.ndarray):
            return make_safe(o.tolist())
        else:
            # if item is a numpy scalar type try to convert it to python builtin
            try:
                return o.item()
            except Exception as e:
                raise ValueError("Cannot encode type {}".format(type(o))) from e


class ClassificationMetric(Metric):
    """Abstract class for classification metrics."""

    def compute(self, sample_weights=None, class_labels=None):
        """Compute the metric.

        :param sample_weights: the weighting of each sample in the calculation
        :param class_labels: the labels for the classes in the dataset
        :return: the computed metric
        """
        raise NotImplementedError


class RegressionMetric(Metric):
    """Abstract class for regression metrics."""

    def compute(self, sample_weights=None, bin_info=None,
                y_min=None, y_max=None, y_std=None):
        """Compute the metric.

        :param sample_weights: the weighting of each sample in the calculation
        :param bin_info: metadata about the dataset needed to compute bins
            for some metrics
        :param y_min: the minimum target value
        :param y_max: the maximum target value
        :param y_std: the standard deviation of targets
        :return: the computed metric
        """
        raise NotImplementedError


class ForecastMetric(RegressionMetric):
    """Abstract class for forecast metrics."""

    y_pred_str = 'y_pred'
    y_test_str = 'y_test'

    def __init__(
            self,
            y_pred: np.ndarray,
            y_test: np.ndarray,
            horizons: np.ndarray,
            logger: Optional[logging.Logger] = None) -> None:
        """Initialize the forecast metric class.

        :param y_pred: The predicted labels for computing the metric.
        :param y_test: The true labels for computing the metric.
        :param horizons: The integer horizon alligned to each y_test. These values should be computed
            by the timeseries transformer. If the timeseries transformer does not compute a horizon,
            ensure all values are the same (ie. every y_test should be horizon 1.)
        """
        self.horizons = horizons
        super(ForecastMetric, self).__init__(y_test, y_pred, logger=logger)

    def compute(
            self,
            sample_weights: Optional[np.ndarray] = None,
            bin_info: Optional[Dict[str, float]] = None,
            y_min: Optional[float] = None,
            y_max: Optional[float] = None,
            y_std: Optional[float] = None) -> Dict[str, Any]:
        """Compute the metric.

        :param sample_weights: the weighting of each sample in the calculation
        :param bin_info: metadata about the dataset needed to compute bins
            for some metrics
        :param y_min: the minimum target value
        :param y_max: the maximum target value
        :param y_std: the standard deviation of targets
        :return: the computed metric
        """
        raise NotImplementedError

    def _group_raw_by_horizon(self) -> Dict[int, Dict[str, List[float]]]:
        """
        Group y_true and y_pred by horizon.

        :return: A dictionary of horizon to y_true, y_pred.
        """
        grouped_values = {}         # type: Dict[int, Dict[str, List[float]]]
        for idx, h in enumerate(self.horizons):
            if h in grouped_values:
                grouped_values[h][ForecastMetric.y_pred_str].append(self._y_pred[idx])
                grouped_values[h][ForecastMetric.y_test_str].append(self._y_test[idx])
            else:
                grouped_values[h] = {
                    ForecastMetric.y_pred_str: [self._y_pred[idx]],
                    ForecastMetric.y_test_str: [self._y_test[idx]]
                }

        return grouped_values

    @staticmethod
    def _group_scores_by_horizon(score_data: List[Dict[int, Dict[str, Any]]]) -> Dict[int, List[Any]]:
        """
        Group computed scores by horizon.

        :param score_data: The dictionary of data from a cross-validated model.
        :return: The data grouped by horizon in sorted order.
        """
        grouped_data = {}       # type: Dict[int, List[Any]]
        for cv_fold in score_data:
            for horizon in cv_fold.keys():
                if horizon in grouped_data.keys():
                    grouped_data[horizon].append(cv_fold[horizon])
                else:
                    grouped_data[horizon] = [cv_fold[horizon]]

        # sort data by horizon
        grouped_data_sorted = OrderedDict(sorted(grouped_data.items()))
        return grouped_data_sorted


class AccuracyTableMetric(ClassificationMetric):
    """
    Accuracy Table Metric.

    The accuracy table metric is a multi-use non-scalar metric
    that can be used to produce multiple types of line charts
    that vary continuously over the space of predicted probabilities.
    Examples of these charts are receiver operating characteristic,
    precision-recall, and lift curves.

    The calculation of the accuracy table is similar to the calculation
    of a receiver operating characteristic curve. A receiver operating
    characteristic curve stores true positive rates and
    false positive rates at many different probability thresholds.
    The accuracy table stores the raw number of
    true positives, false positives, true negatives, and false negatives
    at many probability thresholds.

    Probability thresholds are evenly spaced thresholds between 0 and 1.
    If NUM_POINTS were 5 the probability thresholds would be
    [0.0, 0.25, 0.5, 0.75, 1.0].
    These thresholds are useful for computing charts where you want to
    sample evenly over the space of predicted probabilities.

    Percentile thresholds are spaced according to the distribution of
    predicted probabilities. Each threshold corresponds to the percentile
    of the data at a probability threshold.
    For example, if NUM_POINTS were 5, then the first threshold would be at
    the 0th percentile, the second at the 25th percentile, the
    third at the 50th, and so on.

    The probability tables and percentile tables are both 3D lists where
    the first dimension represents the class label*, the second dimension
    represents the sample at one threshold (scales with NUM_POINTS),
    and the third dimension always has 4 values: TP, FP, TN, FN, and
    always in that order.

    * The confusion values (TP, FP, TN, FN) are computed with the
    one vs. rest strategy. See the following link for more details:
    `https://en.wikipedia.org/wiki/Multiclass_classification`
    """

    SCHEMA_TYPE = constants.Metric.SCHEMA_TYPE_ACCURACY_TABLE
    SCHEMA_VERSION = '1.0.1'

    NUM_POINTS = 100

    PROB_TABLES = 'probability_tables'
    PERC_TABLES = 'percentile_tables'
    PROB_THOLDS = 'probability_thresholds'
    PERC_THOLDS = 'percentile_thresholds'
    CLASS_LABELS = 'class_labels'

    @staticmethod
    def _data_to_dict(data):
        schema_type = AccuracyTableMetric.SCHEMA_TYPE
        schema_version = AccuracyTableMetric.SCHEMA_VERSION
        return Metric._data_to_dict(schema_type, schema_version, data)

    def _make_thresholds(self):
        probability_thresholds = np.linspace(0, 1, AccuracyTableMetric.NUM_POINTS)
        all_predictions = self._y_pred.ravel()
        percentile_thresholds = np.percentile(all_predictions, probability_thresholds * 100)
        return probability_thresholds, percentile_thresholds

    def _build_tables(self, class_labels, thresholds):
        """
        Create the accuracy table per class.

        Sweeps the thresholds to find accuracy data over the space of
        predicted probabilities.
        """
        y_test_bin = self._binarize_y_test(class_labels)
        data = zip(y_test_bin.T, self._y_pred.T)
        tables = [self._build_table(tbin, pred, thresholds) for tbin, pred in data]
        full_tables = self._pad_tables(class_labels, tables)
        return full_tables

    def _binarize_y_test(self, class_labels):
        """
        One-hot encode the test targets.

        If there are only two classes in the test data
        another column is appended to the array to complete the encoding.
        """
        binarizer = sklearn.preprocessing.LabelBinarizer()
        binarizer.fit(class_labels)
        y_test_bin = binarizer.transform(self._y_test)
        if y_test_bin.shape[1] == 1:
            y_test_bin = np.concatenate((1 - y_test_bin, y_test_bin), axis=1)
        return y_test_bin

    def _pad_tables(self, class_labels, tables):
        """Add padding tables for missing validation classes."""
        y_labels = np.unique(self._y_test)
        full_tables = []
        table_index = 0
        for class_label in class_labels:
            if class_label in y_labels:
                full_tables.append(tables[table_index])
                table_index += 1
            else:
                full_tables.append(np.zeros((AccuracyTableMetric.NUM_POINTS, 4), dtype=int))
        return full_tables

    def _build_table(self, class_y_test_bin, class_y_pred, thresholds):
        """Calculate the confusion values at all thresholds for one class."""
        table = []
        n_positive = np.sum(class_y_test_bin)
        n_samples = class_y_test_bin.shape[0]
        for threshold in thresholds:
            under_threshold = class_y_test_bin[class_y_pred < threshold]
            fn = np.sum(under_threshold)
            tn = under_threshold.shape[0] - fn
            tp, fp = n_positive - fn, n_samples - n_positive - tn
            conf_values = np.array([tp, fp, tn, fn], dtype=int)
            table.append(conf_values)
        return table

    def compute(self, sample_weights=None, class_labels=None):
        """Compute the score for the metric."""
        if class_labels is None:
            raise ValueError("Class labels required to compute AccuracyTable")

        probability_thresholds, percentile_thresholds = self._make_thresholds()
        probability_tables = self._build_tables(class_labels, probability_thresholds)
        percentile_tables = self._build_tables(class_labels, percentile_thresholds)

        string_labels = [str(label) for label in class_labels]
        self._data[AccuracyTableMetric.CLASS_LABELS] = string_labels
        self._data[AccuracyTableMetric.PROB_TABLES] = probability_tables
        self._data[AccuracyTableMetric.PERC_TABLES] = percentile_tables
        self._data[AccuracyTableMetric.PROB_THOLDS] = probability_thresholds
        self._data[AccuracyTableMetric.PERC_THOLDS] = percentile_thresholds
        ret = AccuracyTableMetric._data_to_dict(self._data)
        return Metric._make_json_safe(ret)

    @staticmethod
    def aggregate(scores):
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return Metric.get_error_metric()

        score_data = [score[Metric.DATA] for score in scores]
        prob_tables = [d[AccuracyTableMetric.PROB_TABLES] for d in score_data]
        perc_tables = [d[AccuracyTableMetric.PERC_TABLES] for d in score_data]
        data_agg = {
            AccuracyTableMetric.PROB_TABLES: (
                np.sum(prob_tables, axis=0)),
            AccuracyTableMetric.PERC_TABLES: (
                np.sum(perc_tables, axis=0)),
            AccuracyTableMetric.PROB_THOLDS: (
                score_data[0][AccuracyTableMetric.PROB_THOLDS]),
            AccuracyTableMetric.PERC_THOLDS: (
                score_data[0][AccuracyTableMetric.PERC_THOLDS]),
            AccuracyTableMetric.CLASS_LABELS: (
                score_data[0][AccuracyTableMetric.CLASS_LABELS])
        }
        ret = AccuracyTableMetric._data_to_dict(data_agg)
        return Metric._make_json_safe(ret)


class ConfusionMatrixMetric(ClassificationMetric):
    """
    Confusion Matrix Metric.

    This metric is a wrapper around the sklearn confusion matrix.
    The metric data contains the class labels and a 2D list
    for the matrix itself.
    See the following link for more details on how the metric is computed:
    `https://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html`
    """

    SCHEMA_TYPE = constants.Metric.SCHEMA_TYPE_CONFUSION_MATRIX
    SCHEMA_VERSION = '1.0.0'

    MATRIX = 'matrix'
    CLASS_LABELS = 'class_labels'

    @staticmethod
    def _data_to_dict(data):
        schema_type = ConfusionMatrixMetric.SCHEMA_TYPE
        schema_version = ConfusionMatrixMetric.SCHEMA_VERSION
        return Metric._data_to_dict(schema_type, schema_version, data)

    def _compute_matrix(self, class_labels, sample_weights=None):
        """Compute the matrix from prediction data."""
        y_pred_indexes = np.argmax(self._y_pred, axis=1)
        y_pred_labels = class_labels[y_pred_indexes]
        y_true = self._y_test

        if y_pred_labels.dtype.kind == 'f':
            class_labels = class_labels.astype(str)
            y_true = y_true.astype(str)
            y_pred_labels = y_pred_labels.astype(str)

        return sklearn.metrics.confusion_matrix(y_true=y_true,
                                                y_pred=y_pred_labels,
                                                sample_weight=sample_weights,
                                                labels=class_labels)

    def compute(self, sample_weights=None, class_labels=None):
        """Compute the score for the metric."""
        if class_labels is None:
            raise ValueError("Class labels required to compute \
                             ConfusionMatrixMetric")
        string_labels = [str(label) for label in class_labels]
        self._data[ConfusionMatrixMetric.CLASS_LABELS] = string_labels
        matrix = self._compute_matrix(class_labels,
                                      sample_weights=sample_weights)
        self._data[ConfusionMatrixMetric.MATRIX] = matrix
        ret = ConfusionMatrixMetric._data_to_dict(self._data)
        return Metric._make_json_safe(ret)

    @staticmethod
    def aggregate(scores):
        """Folds several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return Metric.get_error_metric()

        score_data = [score[Metric.DATA] for score in scores]
        matrices = [d[ConfusionMatrixMetric.MATRIX] for d in score_data]
        matrix_sum = np.sum(matrices, axis=0)
        agg_class_labels = score_data[0][ConfusionMatrixMetric.CLASS_LABELS]
        data_agg = {
            ConfusionMatrixMetric.CLASS_LABELS: agg_class_labels,
            ConfusionMatrixMetric.MATRIX: matrix_sum
        }
        ret = ConfusionMatrixMetric._data_to_dict(data_agg)
        return Metric._make_json_safe(ret)


class HasVariance(object):
    """A mixin to compute variance."""

    @staticmethod
    def _total_variance(counts, means, variances):
        """
        Compute total population variance.

        Computes the variance of a population given the counts, means, and
        variances of several sub-populations.
        This uses the law of total variance:
        `https://en.wikipedia.org/wiki/Law_of_total_variance`
        var(y) = E[var(y|x)] + var(E[y|x])
            y: predicted value
            x: cross-validation index

        var(y|x) = variances
        E[y|x] = means
        E[var(y|x)] = np.sum(counts * variances) / total_count
        var(E[y|x]) = np.sum(counts * (means - total_mean) ** 2) / total_count
        """
        total_count = np.sum(counts)
        total_mean = np.sum(counts * means) / total_count
        unweighted_vars = variances + (means - total_mean) ** 2
        total_var = np.sum(counts * unweighted_vars) / total_count
        return total_var


class ResidualsMetric(RegressionMetric, HasVariance):
    """
    Residuals Metric.

    This metric contains the data needed to display a histogram of
    residuals for a regression task.
    The residuals are predicted - actual.

    The bounds of this histogram are determined by the standard
    deviation of the targets for the full dataset. This value is
    passed to the metrics module as y_std. This is why y_std is
    required to compute this metric.
    The first and last bins are not necessarily the same width as
    the other bins. The first bin is [y_min, -2 * y_std].
    The last bin is [2 * y_std, y_max].
    If the regressor performs fairly well most of the residuals will
    be around zero and less than the standard deviation of the original
    data.

    The internal edges are evenly spaced.
    """

    SCHEMA_TYPE = constants.Metric.SCHEMA_TYPE_RESIDUALS
    SCHEMA_VERSION = '1.0.0'

    EDGES = 'bin_edges'
    COUNTS = 'bin_counts'
    MEAN = 'mean'
    STDDEV = 'stddev'
    RES_COUNT = 'res_count'

    @staticmethod
    def _data_to_dict(data):
        schema_type = ResidualsMetric.SCHEMA_TYPE
        schema_version = ResidualsMetric.SCHEMA_VERSION
        return Metric._data_to_dict(schema_type, schema_version, data)

    def compute(self, sample_weights=None, bin_info=None,
                y_min=None, y_max=None, y_std=None):
        """Compute metric.

        :param sample_weights: a list of sample weights for the data
        :param bin_info: metadata about the dataset needed to compute bins
            for some metrics
        :param y_min: minimum target value for the full dataset
        :param y_max: maximum target value for the full dataset
        :param y_std: standard deviation of target values
        :return: the metric
        """
        if y_std is None:
            raise ValueError("y_std required to compute ResidualsMetric")

        num_bins = 10
        # If full dataset targets are all zero we still need a bin
        y_std = y_std if y_std != 0 else 1
        residuals = self._y_pred - self._y_test

        mean = np.mean(residuals)
        stddev = np.std(residuals)
        res_count = len(residuals)

        counts, edges = ResidualsMetric._hist_by_bound(residuals, 2 * y_std, num_bins)
        ResidualsMetric._simplify_edges(residuals, edges)

        self._data[ResidualsMetric.EDGES] = edges
        self._data[ResidualsMetric.COUNTS] = counts
        self._data[ResidualsMetric.MEAN] = mean
        self._data[ResidualsMetric.STDDEV] = stddev
        self._data[ResidualsMetric.RES_COUNT] = res_count
        ret = ResidualsMetric._data_to_dict(self._data)
        return Metric._make_json_safe(ret)

    @staticmethod
    def _hist_by_bound(values, bound, num_bins):
        # Need to subtract one because num_bins needs (num_bins + 1) edges, but we also have inf/-inf.
        num_edges = num_bins - 1
        min_decimal_places = 2

        bound = abs(bound)
        num_bound_decimal_places = int(max(min_decimal_places, -1 * np.log10(bound) + (min_decimal_places + 1)))
        bound = np.ceil(bound * (10 ** num_bound_decimal_places)) / (10 ** num_bound_decimal_places)

        bin_size = bound / num_edges
        bin_edges = np.linspace(-bound, bound, num_edges)
        num_decimal_places = int(max(min_decimal_places, -1 * np.log10(bin_size) + (min_decimal_places + 1)))
        for i, edge in enumerate(bin_edges):
            bin_edges[i] = np.around(edge, decimals=num_decimal_places)
        bins = np.r_[-np.inf, bin_edges, np.inf]
        return np.histogram(values, bins=bins)

    @staticmethod
    def _simplify_edges(residuals, edges):
        """Set the first and last edges of the histogram to be real numbers.

        If the minimum residual is in the outlier bin then the left
        edge is set to that residual value. Otherwise, the left edge
        is set to be evenly spaced with the rest of the bins
        This is repeated on the right side of the histogram.
        """
        assert(len(edges) >= 4)
        min_residual = np.min(residuals)

        # Keep left edge greater than negative infinity
        if min_residual < edges[1]:
            edges[0] = min_residual
        else:
            edges[0] = edges[1] - np.abs(edges[2] - edges[1])

        # Keep right edge less than infinity
        max_residual = np.max(residuals)
        if max_residual >= edges[-2]:
            edges[-1] = max_residual
        else:
            edges[-1] = edges[-2] + np.abs(edges[-2] - edges[-3])

    @staticmethod
    def aggregate(scores):
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return Metric.get_error_metric()

        score_data = [score[Metric.DATA] for score in scores]
        edges = [d[ResidualsMetric.EDGES] for d in score_data]
        counts = [d[ResidualsMetric.COUNTS] for d in score_data]
        agg_edges = ResidualsMetric._aggregate_edges(edges)
        agg_counts = np.sum(counts, axis=0)

        means = np.array([d[ResidualsMetric.MEAN] for d in score_data])
        res_counts = np.array([d[ResidualsMetric.RES_COUNT] for d in score_data])
        stddevs = np.array([d[ResidualsMetric.STDDEV] for d in score_data])
        variances = stddevs ** 2

        agg_res_count = np.sum(res_counts)
        agg_mean = np.sum(means * res_counts) / agg_res_count
        agg_stddev = np.sqrt(ResidualsMetric._total_variance(res_counts, means, variances))
        data_agg = {
            ResidualsMetric.EDGES: agg_edges,
            ResidualsMetric.COUNTS: agg_counts,
            ResidualsMetric.MEAN: agg_mean,
            ResidualsMetric.STDDEV: agg_stddev,
            ResidualsMetric.RES_COUNT: agg_res_count,
        }
        ret = ResidualsMetric._data_to_dict(data_agg)
        return Metric._make_json_safe(ret)

    @staticmethod
    def _aggregate_edges(all_edges):
        all_edges_arr = np.array(all_edges)
        ret = np.copy(all_edges_arr[0])
        ret[0] = np.min(all_edges_arr[:, 0])
        ret[-1] = np.max(all_edges_arr[:, -1])
        return ret.tolist()


class ForecastMapeMetric(ForecastMetric):
    """Mape Metric based on horizons."""

    SCHEMA_TYPE = constants.Metric.SCHEMA_TYPE_MAPE
    SCHEMA_VERSION = '1.0.0'

    MAPE = 'mape'
    COUNT = 'count'

    def compute(
            self,
            sample_weights: Optional[np.ndarray] = None,
            bin_info: Optional[Dict[str, float]] = None,
            y_min: Optional[float] = None,
            y_max: Optional[float] = None,
            y_std: Optional[float] = None) -> Dict[str, Any]:
        """Compute mape by horizon."""
        grouped_values = self._group_raw_by_horizon()
        for h in grouped_values:
            partial_pred = np.array(grouped_values[h][ForecastMetric.y_pred_str])
            partial_test = np.array(grouped_values[h][ForecastMetric.y_test_str])

            self._data[h] = {
                ForecastMapeMetric.MAPE: _mape(partial_test, partial_pred),
                ForecastMapeMetric.COUNT: len(partial_pred)
            }

        ret = Metric._data_to_dict(
            ForecastMapeMetric.SCHEMA_TYPE,
            ForecastMapeMetric.SCHEMA_VERSION,
            self._data)
        return cast(Dict[str, Any], Metric._make_json_safe(ret))

    @staticmethod
    def aggregate(scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return Metric.get_error_metric()

        score_data = [score[Metric.DATA] for score in scores]
        grouped_data = ForecastMetric._group_scores_by_horizon(score_data)

        data = {}
        for horizon in grouped_data:
            agg_count = 0
            agg_mape = 0.0
            folds = grouped_data[horizon]
            for fold in folds:
                fold_count = fold[ForecastMapeMetric.COUNT]
                agg_count += fold_count
                agg_mape += fold[ForecastMapeMetric.MAPE] * fold_count
            agg_mape = agg_mape / agg_count
            data[horizon] = {
                ForecastMapeMetric.MAPE: agg_mape,
                ForecastMapeMetric.COUNT: agg_count
            }

        ret = Metric._data_to_dict(
            ForecastMapeMetric.SCHEMA_TYPE,
            ForecastMapeMetric.SCHEMA_VERSION,
            data)
        return cast(Dict[str, Any], Metric._make_json_safe(ret))


class ForecastResidualsMetric(ForecastMetric, HasVariance):
    """Residuals Metric."""

    SCHEMA_TYPE = constants.Metric.SCHEMA_TYPE_RESIDUALS
    SCHEMA_VERSION = '1.0.0'

    EDGES = 'bin_edges'
    COUNTS = 'bin_counts'
    MEAN = 'mean'
    STDDEV = 'stddev'
    RES_COUNT = 'res_count'

    def compute(self, sample_weights=None, bin_info=None,
                y_min=None, y_max=None, y_std=None):
        """
        Compute metric.

        :param sample_weights: a list of sample weights for the data
        :param bin_info: metadata about the dataset needed to compute bins
            for some metrics
        :param y_min: minimum target value for the full dataset
        :param y_max: maximum target value for the full dataset
        :param y_std: standard deviation of target values
        :return: the metric
        """
        if y_std is None:
            raise ValueError("y_std required to compute ResidualsMetric")

        num_bins = 10
        # If full dataset targets are all zero we still need a bin
        y_std = y_std if y_std != 0 else 1

        self._data = {}
        grouped_values = self._group_raw_by_horizon()
        for h in grouped_values:
            self._data[h] = {}
            partial_residuals = np.array(grouped_values[h][ForecastMetric.y_pred_str]) \
                - np.array(grouped_values[h][ForecastMetric.y_test_str])
            mean = np.mean(partial_residuals)
            stddev = np.std(partial_residuals)
            res_count = len(partial_residuals)

            counts, edges = ResidualsMetric._hist_by_bound(partial_residuals, 2 * y_std, num_bins)
            ResidualsMetric._simplify_edges(partial_residuals, edges)
            self._data[h][ForecastResidualsMetric.EDGES] = edges
            self._data[h][ForecastResidualsMetric.COUNTS] = counts
            self._data[h][ForecastResidualsMetric.MEAN] = mean
            self._data[h][ForecastResidualsMetric.STDDEV] = stddev
            self._data[h][ForecastResidualsMetric.RES_COUNT] = res_count

        ret = Metric._data_to_dict(
            ForecastResidualsMetric.SCHEMA_TYPE,
            ForecastResidualsMetric.SCHEMA_VERSION,
            self._data)
        return Metric._make_json_safe(ret)

    @staticmethod
    def aggregate(scores):
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return Metric.get_error_metric()

        score_data = [score[Metric.DATA] for score in scores]
        grouped_data = ForecastMetric._group_scores_by_horizon(score_data)

        data = {}
        for horizon in grouped_data:
            # convert data to how residuals expects
            partial_scores = [{Metric.DATA: fold_data} for fold_data in grouped_data[horizon]]
            # use aggregate from residuals
            data[horizon] = ResidualsMetric.aggregate(partial_scores)[Metric.DATA]

        ret = Metric._data_to_dict(
            ForecastResidualsMetric.SCHEMA_TYPE,
            ForecastResidualsMetric.SCHEMA_VERSION,
            data)
        return Metric._make_json_safe(ret)


class PredictedTrueMetric(RegressionMetric, HasVariance):
    """
    Predicted vs True Metric.

    This metric can be used to compare the distributions of true
    target values to the distribution of predicted values.

    The predictions are binned and standard deviations are calculated
    for error bars on a line chart.
    """

    SCHEMA_TYPE = constants.Metric.SCHEMA_TYPE_PREDICTIONS
    SCHEMA_VERSION = '1.0.0'

    EDGES = 'bin_edges'
    COUNTS = 'bin_counts'
    MEANS = 'bin_averages'
    STDEVS = 'bin_errors'

    @staticmethod
    def _data_to_dict(data):
        schema_type = PredictedTrueMetric.SCHEMA_TYPE
        schema_version = PredictedTrueMetric.SCHEMA_VERSION
        return Metric._data_to_dict(schema_type, schema_version, data)

    def compute(self, sample_weights=None, bin_info=None,
                y_min=None, y_max=None, y_std=None):
        """Compute metric.

        :param sample_weights: a list of sample weights for the data
        :param bin_info: metadata about the dataset needed to compute bins
            for some metrics
        :param y_min: minimum target value for the full dataset
        :param y_max: maximum target value for the full dataset
        :param y_std: standard deviation of target values
        :return: the metric
        """
        if bin_info is None:
            raise ValueError("bin_info is required to \
                             compute PredictedTrueMetric")

        n_bins = bin_info['number_of_bins']
        bin_starts = bin_info['bin_starts']
        bin_ends = bin_info['bin_ends']
        bin_edges = np.r_[bin_starts, bin_ends[-1]]
        # As long as we guarantee all points fit in the edges of bin_info
        # we can use np.digitize only on the ends.
        bin_indices = np.digitize(self._y_test, bin_ends, right=True)

        bin_counts = []
        bin_means = []
        bin_stdevs = []
        for bin_index in range(n_bins):
            y_pred_in_bin = self._y_pred[np.where(bin_indices == bin_index)]
            bin_count = y_pred_in_bin.shape[0]
            bin_counts.append(bin_count)
            if bin_count == 0:
                bin_means.append(0)
                bin_stdevs.append(0)
            else:
                bin_means.append(y_pred_in_bin.mean())
                bin_stdevs.append(y_pred_in_bin.std())

        self._data[PredictedTrueMetric.EDGES] = bin_edges
        self._data[PredictedTrueMetric.COUNTS] = np.array(bin_counts, dtype=int)
        self._data[PredictedTrueMetric.MEANS] = np.array(bin_means)
        self._data[PredictedTrueMetric.STDEVS] = np.array(bin_stdevs)

        ret = PredictedTrueMetric._data_to_dict(self._data)
        return Metric._make_json_safe(ret)

    @staticmethod
    def aggregate(scores):
        """Fold several scores from a computed metric together.

        :param scores: a list of computed scores
        :return: the aggregated scores
        """
        if not Metric.check_aggregate_scores(scores):
            return Metric.get_error_metric()

        EDGES = PredictedTrueMetric.EDGES
        COUNTS = PredictedTrueMetric.COUNTS
        MEANS = PredictedTrueMetric.MEANS
        STDEVS = PredictedTrueMetric.STDEVS

        score_data = [score[Metric.DATA] for score in scores]

        n_bins = len(score_data[0][COUNTS])

        bin_counts = []
        bin_means = []
        bin_stdevs = []
        for bin_index in range(n_bins):
            split_counts = np.array([d[COUNTS][bin_index] for d in score_data])
            split_means = np.array([d[MEANS][bin_index] for d in score_data])
            split_stdevs = np.array([d[STDEVS][bin_index] for d in score_data])

            bin_count = np.sum(split_counts)
            bin_counts.append(bin_count)
            if bin_count == 0:
                bin_means.append(0)
                bin_stdevs.append(0)
            else:
                bin_mean = np.sum(split_counts * split_means) / bin_count
                bin_means.append(bin_mean)
                split_vars = split_stdevs ** 2
                bin_var = PredictedTrueMetric._total_variance(
                    split_counts, split_means, split_vars)
                bin_stdevs.append(bin_var ** 0.5)

        data_agg = {
            EDGES: score_data[0][EDGES],
            COUNTS: np.array(bin_counts, dtype=int),
            MEANS: np.array(bin_means),
            STDEVS: np.array(bin_stdevs)
        }

        ret = PredictedTrueMetric._data_to_dict(data_agg)
        return Metric._make_json_safe(ret)
