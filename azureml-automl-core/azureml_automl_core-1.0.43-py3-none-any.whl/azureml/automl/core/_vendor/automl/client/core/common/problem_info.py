# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""A container for information about the problem being worked on.

This is used to pass information to the server to use to give
better pipelines to try next.
"""
import copy
import json

from automl.client.core.common import constants, resource_limits
from automl.client.core.common.constants import \
    TimeConstraintEnforcement as time_constraint


class ProblemInfo:
    """Container object for metadata about the problem being worked on.

    Provides more information that can be used to predict future pipelines
    This information is important for predicting the cost of a pipeline when
        the data is not directly available for inspection.
    """

    def __init__(
            self, dataset_samples=0, dataset_features=0, dataset_classes=0,
            dataset_num_categorical=0,
            dataset_categoricals=None,
            dataset_y_std=0,
            dataset_uid=None,
            runtime_constraints=None,
            num_threshold_buffers=3,
            num_recommendations=1,
            num_threads=1,
            is_sparse=False,
            pipeline_profile=constants.PipelineMaskProfiles.MASK_NONE,
            constraint_mode=time_constraint.TIME_CONSTRAINT_PER_ITERATION,
            cost_mode=constants.PipelineCost.COST_FILTER,
            task=constants.Tasks.CLASSIFICATION,
            training_percent=None,  # Default of None is 100%
            subsampling=False,
            metric="AUC_macro",
            model_names_whitelisted=None,
            model_names_blacklisted=None,
            kernel='linear',
            subsampling_treatment=constants.SubsamplingTreatment.LINEAR,
            subsampling_schedule=constants.SubsamplingSchedule.HYPERBAND_CLIP):
        """Construct ProblemInfo.

        :param dataset_samples: number of samples in the whole dataset
        :param dataset_features: number of features in the dataset
        :param dataset_classes: number of classes in the targets of the dataset
        :param dataset_num_categorical: number of categorical features in
            the dataset
        :param dataset_categoricals: Boolean array indicating the categorical features
        :param dataset_y_std: standard deviation of targets
        :param dataset_uid: string identifier for dataset.
        :param runtime_constraints:
        :param num_threshold_buffers:
        :param num_recommendations:
        :param num_threads:
        :param is_sparse:
        :param pipeline_profile:
        :param constraint_mode:
        :param cost_mode: behavior to follow when filtering on costly pipelines
        :param task: machine learning task being executed
            (classification or regression)
        :param training_percent:
        :param subsampling: use subsampling
        :param metric: metric to be optimized
        :param model_names_whitelisted: model names to be whitelisted,
                the model names are in constants.LegacyModelNames, this take
                priority over blacklist models
        :param model_names_blacklisted: model names to be blacklisted,
                the model names are in constants.LegacyModelNames
        :param kernel: kernel to use for subsampling model
        :param subsampling_treatment: how to use subsampling percentage
        :param subsampling_schedule: how to schedule training percentages
        """
        self.dataset_samples = dataset_samples
        self.dataset_features = dataset_features
        self.dataset_classes = dataset_classes
        self.dataset_num_categorical = dataset_num_categorical
        self.dataset_categoricals = dataset_categoricals
        self.dataset_y_std = dataset_y_std
        self.dataset_uid = dataset_uid
        self.subsampling = subsampling
        self.task = task
        self.metric = metric
        self.num_threads = num_threads
        self.pipeline_profile = pipeline_profile
        self.is_sparse = is_sparse
        self.runtime_constraints = (
            runtime_constraints or resource_limits.DEFAULT_RESOURCE_LIMITS)
        self.constraint_mode = constraint_mode
        self.cost_mode = cost_mode
        self.training_percent = training_percent
        self.num_recommendations = num_recommendations
        self._server_threshold_events = 0
        self._num_threshold_buffers = num_threshold_buffers
        self._start_time = None
        self._current_time = None
        self.model_names_whitelisted = model_names_whitelisted
        self.model_names_blacklisted = model_names_blacklisted
        # Used in total-cost mode.
        self._max_time = self.runtime_constraints[resource_limits.TOTAL_TIME_CONSTRAINT] \
            if self.constraint_mode in [time_constraint.TIME_CONSTRAINT_TOTAL_AND_ITERATION,
                                        time_constraint.TIME_CONSTRAINT_TOTAL] else None
        self.kernel = kernel
        self.subsampling_treatment = subsampling_treatment
        self.subsampling_schedule = subsampling_schedule

    @staticmethod
    def from_dict(d):
        """Create a ProblemInfo object.

        :param d: dictionary of dataset attributes
        :return: a ProblemInfo object
        """
        ret = ProblemInfo()
        ret.__dict__ = copy.deepcopy(d)
        return ret

    def to_dict(self):
        """Convert the current ProblemInfo object into a dictionary.

        :return: dictionary of dataset attributes
        """
        d = copy.deepcopy(self.__dict__)
        return d

    def __str__(self):
        """Get a string representation of the problem info."""
        return 'ProblemInfo(' + json.dumps(self.to_dict()) + ')'

    def get_time_constraint(self):
        """Get the time constraint placed on the experiment.

        :return: the time constraint
        """
        return self.runtime_constraints[resource_limits.TIME_CONSTRAINT]

    def set_time_constraint(self, new_constraint):
        """Set the time constraint placed on the experiment.

        :param new_constraint: int, time constraint in seconds
        """
        self.set_runtime_constraint({resource_limits.TIME_CONSTRAINT: new_constraint})

    def set_runtime_constraint(self, new_constraint):
        """
        Set the runtime constraint.

        :param new_constraint: a dict of constraints to be set.
            the keys for the constraints are in resource_limits.default_resource_limits
            if a constraint key does not exist in the dict it will be left unchanged.
        """
        if new_constraint:
            for c in resource_limits.DEFAULT_RESOURCE_LIMITS:
                if c in new_constraint:
                    self.runtime_constraints[c] = new_constraint[c]

    def handle_server_code(self, status_code):
        """Call on the client side to interpret server codes.

        :param status_code: A code sent from the server, e.g.
            to increase the time constraint.
        :param runner: The Runner object to also update if necessary.
        """
        if (self.constraint_mode ==
            time_constraint.TIME_CONSTRAINT_PER_ITERATION and
            status_code and status_code ==
                constants.ServerStatus.INCREASE_TIME_THRESHOLD):
            self._server_threshold_events += 1
            if self._server_threshold_events >= self._num_threshold_buffers:
                self._server_threshold_events = 0
                new_threshold = int(
                    self.runtime_constraints[
                        resource_limits.TIME_CONSTRAINT] * 1.5)
                print('Increasing time constraint to {0}'.format(
                    new_threshold))
                self.runtime_constraints[
                    resource_limits.TIME_CONSTRAINT] = new_threshold

    def done(self, final_fit_expected_time=None):
        """Return true if client should halt training."""
        return (
            self.constraint_mode in [
                time_constraint.TIME_CONSTRAINT_TOTAL,
                time_constraint.TIME_CONSTRAINT_TOTAL_AND_ITERATION] and
            self.runtime_constraints[resource_limits.TOTAL_TIME_CONSTRAINT] <= (
                0 if final_fit_expected_time else final_fit_expected_time
            ))

    def set_start_time(self, t):
        """Set the start time."""
        self._start_time = t

    def update_time(self, t, training_times=0, predict_times=0):
        """Update the current time.

        :param t: current time measured by time.time()
        :param training_times: Optional parameter used when using cached results
            to account for the time we are skipping
        :param predict_times: Optional parameter to ignore the time that it takes
            to predict pipelines
        """
        self._current_time = t + training_times - predict_times
        if (self.constraint_mode in [
                time_constraint.TIME_CONSTRAINT_TOTAL,
                time_constraint.TIME_CONSTRAINT_TOTAL_AND_ITERATION]):
            self.runtime_constraints[resource_limits.TOTAL_TIME_CONSTRAINT] = int(
                self._max_time - (self._current_time - self._start_time))

    def set_cost_mode(self):
        """Set the cost mode for the problem."""
        if (self.dataset_samples is None or self.dataset_samples <= 0 or
            self.dataset_classes is None or self.dataset_classes <= 0 or
            self.dataset_features is None or self.dataset_features <= 0 or
            self.get_time_constraint() is None or
                self.get_time_constraint() <= 0):
            self.cost_mode = constants.PipelineCost.COST_NONE

    def update_pipeline_profile(self, pipeline_profile):
        """
        Update the pipeline profile.

        Where the pipeline profile is the pipeline mask(s) to apply.
        """
        if isinstance(self.pipeline_profile, list):
            if (pipeline_profile not in
                    self.pipeline_profile):
                self.add_pipeline_profile(pipeline_profile)
        elif (self.pipeline_profile == constants.PipelineMaskProfiles.MASK_NONE or
                self.pipeline_profile is None):
            self.set_pipeline_profile(pipeline_profile)
        elif self.pipeline_profile != pipeline_profile:
            self.add_pipeline_profile(pipeline_profile)

    def add_pipeline_profile(self, pipeline_profile):
        """
        Add the pipeline profile.

        Where the pipeline profile is the pipeline mask(s) to apply.
        """
        if isinstance(self.pipeline_profile, list):
            self.pipeline_profile.append(pipeline_profile)
        else:
            self.pipeline_profile = [self.pipeline_profile, pipeline_profile]

    def set_pipeline_profile(self, pipeline_profile):
        """
        Set the pipeline profile.

        Where the pipeline profile is the pipeline mask(s) to apply.
        """
        self.pipeline_profile = pipeline_profile

    def clean_dataset_info(self):
        """Clean the ProblemInfo of all potentially sensitive user data."""
        self.dataset_categoricals = None
