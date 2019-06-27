# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.widgets._telemetry_logger import _TelemetryLogger
from azureml.widgets._transformer import _DataTransformer
from collections import namedtuple

_logger = _TelemetryLogger.get_telemetry_logger(__name__)


class _AutoMLDataTransformer(_DataTransformer):
    """Transform run and metric data for AutoML runs."""

    def _get_additional_properties(self, run):
        property_bag = run._run_dto['properties']
        top_level_properties = run._run_dto
        goal = property_bag['goal'] if 'goal' in property_bag else None
        run_properties = property_bag['run_properties'] if 'run_properties' in property_bag else None

        if 'run_preprocessor' in property_bag and 'run_algorithm' in property_bag:
            if property_bag['run_preprocessor']:
                run_name = "{0}, {1}".format(property_bag['run_preprocessor'], property_bag['run_algorithm'])
            else:
                run_name = property_bag['run_algorithm']
        else:
            run_name = top_level_properties['status']
        return {
            'iteration': property_bag['iteration'],
            'goal': goal,
            'run_name': run_name,
            'run_properties': run_properties
        }

    def _get_objective(self, metric_name, pmc_name, pmc_goal):
        """
        If 'import azureml.train.automl' succeeds, call _get_objective_impl
        Else call _DataTransformer's _get_objective
        """
        try:
            # TODO: Remove dependency on azureml.train.automl as part 272181
            # Task 272181: Clean up server repo with new package structure
            import azureml.train.automl  # noqa: F401
            return self._get_objective_impl(metric_name, pmc_name, pmc_goal)
        except ImportError as e:
            message = 'ImportError: %s. metric_name:%s, pmc_name:%s, \
                       pmc_goal:%s' % (e, metric_name, pmc_name, pmc_goal)
            _logger.error(message)
            return super(_AutoMLDataTransformer, self).\
                _get_objective(metric_name, pmc_name, pmc_goal)

    def _get_objective_impl(self, metric_name, pmc_name, pmc_goal):
        """
        Gets the objective name and method for the given metric name. Steps:
        1.Find the objective for the given metric by looking up MetricObjective
        2.If current metric is pmc or
          If objective doesn't match Minimize or Maximize,
           then use pmc_goal as the objective

        :param metric_name: The given metric name
        :param pmc_name: The primary metric name
        :param pmc_goal: The primary metric objective
        :return: The objective name & method applicable for the given metric
        """
        # try:
        # TODO: Remove dependency on azureml.train.automl as part 272181
        # Task 272181: Clean up server repo with new package structure
        import azureml.train.automl  # noqa: F401
        from automl.client.core.common import constants
        ObjectiveInfo = namedtuple('ObjectiveInfo', 'name method')

        objective = \
            (constants.MetricObjective.Regression.get(metric_name) or
                constants.MetricObjective.Classification.get(metric_name))

        if((metric_name == pmc_name) or
            ((objective != constants.OptimizerObjectives.MINIMIZE) and
                (objective != constants.OptimizerObjectives.MAXIMIZE))):
            objective = pmc_goal

        method = (min, max)[objective ==
                            constants.OptimizerObjectives.MAXIMIZE]
        return ObjectiveInfo(name=method.__name__, method=method)
