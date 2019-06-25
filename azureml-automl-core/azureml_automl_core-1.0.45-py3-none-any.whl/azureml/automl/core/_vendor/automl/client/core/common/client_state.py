# Copyright (c) 2017 Microsoft Corporation.  All rights reserved.
"""Client State Module."""
from typing import Any, List, Set
import copy

import numpy as np
import scipy.stats as st

from automl.client.core.common import constants
from automl.client.core.common import metrics


class IterationConfig:
    """
    Configuration for an iteration.

    Includes a pipeline hash and a training percent.
    """

    def __init__(self, pipeline_id, training_percent):
        """Create an iteration configuration."""
        self.pipeline_id = pipeline_id
        self.training_percent = training_percent

    @staticmethod
    def from_dict(d):
        """
        Create an iteration configuration from a dictionary.

        :param d: Dictionary to use.
        :return: The initialized iteration configuration
        """
        d_copy = copy.deepcopy(d)
        ret = IterationConfig(None, None)
        ret.__dict__ = d_copy
        return ret

    def to_dict(self):
        """Create a dictionary from an IterationConfig."""
        d = copy.deepcopy(self.__dict__)
        return d


class IterationInfo:
    """Iteration information object."""

    def __init__(self, pipeline_id, training_percent, score,
                 predicted_time, predicted_metrics, actual_time):
        """Create an iteration information object."""
        self.config = IterationConfig(pipeline_id, training_percent)
        self.score = score
        self.predicted_time = predicted_time
        self.predicted_metrics = predicted_metrics
        self.actual_time = actual_time

    @staticmethod
    def from_dict(d):
        """
        Create an iteration info object from a dictionary.

        :param d: The dictionary to use.
        :return: An iteration info object.
        """
        d_copy = copy.deepcopy(d)
        d_copy['config'] = IterationConfig.from_dict(d_copy['config'])
        ret = IterationInfo(None, None, None, None, None, None)
        ret.__dict__ = d_copy
        return ret

    def to_dict(self):
        """Create a dictionary from an IterationInfo."""
        d = copy.deepcopy(self.__dict__)
        d['config'] = d['config'].to_dict()
        return d


class ClientState:
    """Tracks the history of a client's optimization loop."""

    def __init__(self, metric, task):
        """Create a client state object."""
        self._iteration_infos = []  # type: List[IterationInfo]
        self._has_predicted_times = False
        self._metric = metric
        self._task = task
        self._to_be_evaluated = set()  # type: Set[Any]

    @staticmethod
    def from_dict(d):
        """
        Create a client state object from a dictionary.

        :param d: The dictionary to use.
        :return: A client state object.
        """
        d_copy = copy.deepcopy(d)
        d_copy['_iteration_infos'] = [IterationInfo.from_dict(ii) for ii
                                      in d_copy['_iteration_infos']]

        ret = ClientState(None, None)
        ret.__dict__ = d_copy
        return ret

    def to_dict(self):
        """Create a dictionary from a ClientState."""
        d = copy.deepcopy(self.__dict__)
        d['_iteration_infos'] = [ii.to_dict() for ii in d['_iteration_infos']]
        return d

    def pipeline_hashes(self):
        """Return a list of pipeline hashes."""
        return [i.config.pipeline_id for i in self._iteration_infos]

    def pipeline_training_percents(self):
        """Return a list of pipeline training percents."""
        return [i.config.training_percent for i in self._iteration_infos]

    def iteration_configs(self):
        """Return a list of iteration configurations."""
        return [i.config for i in self._iteration_infos]

    def iteration_infos(self):
        """Return a list of iteration information objects."""
        return self._iteration_infos

    def _clip(self, score):
        if (self._metric in constants.Metric.CLIPS_POS or
                self._metric in constants.Metric.CLIPS_NEG):
            score = np.clip(
                score,
                constants.Metric.CLIPS_NEG.get(self._metric, None),
                constants.Metric.CLIPS_POS.get(self._metric, None))
        return score

    def optimization_scores(self, clip=True, filter_training_percent=None):
        """Return a list of scores for the metric being optimized."""
        if filter_training_percent:
            vals = [float(ii.score[self._metric]) for ii in
                    self._iteration_infos if ii.config.training_percent ==
                    filter_training_percent]
        else:
            vals = [float(ii.score[self._metric]) for ii in
                    self._iteration_infos]
        if clip:
            vals = [self._clip(x) for x in vals]
        return vals

    def _reduce_space(self, scores):
        return {key: val for key, val in scores.items() if key in [
            self._metric, constants.TrainingResultsType.TRAIN_TIME]}

    def all_scores(self, reduced=False):
        """Return a list of all scores."""
        to_return = [ii.score if not reduced else self._reduce_space(
            ii.score) for ii in self._iteration_infos]
        return to_return

    def all_predicted_metrics(self):
        """Return a list of all predicted metircs."""
        return [ii.predicted_metrics for ii in self._iteration_infos]

    def training_times(self):
        """Return a tuple of (predicted times, actual times)."""
        return (self.predicted_times(), self.actual_times())

    def predicted_times(self):
        """Return a list of predicted times."""
        return [ii.predicted_time for ii in self._iteration_infos
                ] if self._has_predicted_times else []

    def actual_times(self):
        """Return a list of actual times."""
        return [ii.actual_time for ii in self._iteration_infos]

    def update(self, pid, score, predicted_time, actual_time,
               predicted_metrics=None, training_percent=100):
        """Add a new pipeline result.

        :param pid: Pipeline id (hash).
        :param score: A dict of results from validation set.
        :param predicted_time: The pipeline training time predicted
            by the server.
        :param actual_time: The actual pipeline training time.
        :param predicted_metrics: A dict of string to flow representing
            the predicted metrics for the pipeline
        :param training_percent: The training percent that was used.
        """
        if predicted_time:
            self._has_predicted_times = True

        self._iteration_infos.append(
            IterationInfo(pid, training_percent, score,
                          predicted_time, predicted_metrics, actual_time))

    def get_best_pipeline_index(self):
        """Return the best pipeline index."""
        if np.isnan(self.optimization_scores()).all():
            return None
        objective = metrics.minimize_or_maximize(self._metric, self._task)
        if objective == 'maximize':
            return np.nanargmax(self.optimization_scores())
        else:
            return np.nanargmin(self.optimization_scores())

    def get_cost_stats(self):
        """Return the cost statistics used to evaluate performance of the cost model."""
        ret = {}
        actual_times = self.actual_times()
        predicted_times = self.predicted_times()

        if actual_times:
            ret['avg_pipeline_time'] = np.mean(actual_times)

        if predicted_times and actual_times:
            errors = (np.array(predicted_times) -
                      np.array(actual_times))
            ret['RMSE'] = np.sqrt(np.mean(np.square(errors)))
            ret['errors'] = errors.tolist()
            ret['spearman'] = st.spearmanr(
                np.array(predicted_times), np.array(actual_times))[0]

        return ret

    def _blob_time_accumulation(self):
        """Return the amount of time that using the blob has saved/ cost us so far.

        For use with cached runner.
        """
        actual_times = self.actual_times()
        blob_times = np.array([score.get(
            constants.TrainingResultsType.BLOB_TIME, 0) for score in self.all_scores()])
        differences = blob_times - actual_times
        # if everything were cached and blob time were zero this would be the time saved
        extra_time = np.sum(actual_times)
        # if the blob time is greater than the time reported in actual times, then the blob cost us time
        # subtract the difference to get the true time it should have taken
        extra_time -= np.sum(differences[blob_times >= actual_times])
        # elif if the blob time is less than the reported time in actual times, then the blob saved us time
        # but we still need to subtract the time the blob took.
        extra_time -= np.sum(blob_times[blob_times < actual_times])
        return extra_time

    def _add_to_be_evaluated(self, recommendations):
        """Keep track of pipelines recommended but not evaluated."""
        if isinstance(recommendations, list):
            self._to_be_evaluated.update([
                recommendation.pipeline_id.id() if (hasattr(
                    recommendation, 'pipeline_id') and recommendation.pipeline_id)
                else recommendation.p_spec.pipeline_id
                for recommendation in recommendations])
        else:
            self._to_be_evaluated.add(recommendations.pipeline_id.id() if (hasattr(
                recommendations, 'pipeline_id') and recommendations.pipeline_id)
                else recommendations.p_spec.pipeline_id)

    def _remove_to_be_evaluated(self, pipeline_id):
        """Remove a pipeline from queue when it has been evaluated."""
        self._to_be_evaluated.difference_update(pipeline_id)
