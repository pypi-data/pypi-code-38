import copy
from typing import List, Dict, Callable, Union, TYPE_CHECKING

from sklearn import clone
from sklearn.pipeline import Pipeline

from mindfoundry.optaas.client.configuration import Configuration
from mindfoundry.optaas.client.result import StoredResult, ScoringFunctionOutput, ScoreValueOrDict
from mindfoundry.optaas.client.session import OPTaaSResponse
from mindfoundry.optaas.client.sklearn_pipelines.mixin import EstimatorChoice, OptimizablePipeline
from mindfoundry.optaas.client.sklearn_pipelines.utils import EstimatorTuple, Estimator
from mindfoundry.optaas.client.task import Task
from mindfoundry.optaas.client.utils import move_dict_value_up_one_level, get_first_key

if TYPE_CHECKING:  # pragma: no cover
    from pandas import DataFrame  # pylint: disable=unused-import


class SklearnTask(Task):
    """A Task that can convert a :class:`.Configuration` into a sklearn :class:`.Pipeline`"""

    def __init__(self, task: Task, estimators: List[EstimatorTuple]) -> None:
        self._estimators = estimators
        super().__init__(task.json, task._session)  # pylint: disable=protected-access

    def run(self, scoring_function: Callable[[Pipeline], ScoringFunctionOutput], max_iterations: int,
            score_threshold: ScoreValueOrDict = None) -> Union[StoredResult, List[StoredResult]]:
        """Run this task, using the provided scoring function to calculate the score for each configuration.

        Args:
            scoring_function (Callable[[Pipeline], ScoringFunctionOutput]):
                Function that takes a sklearn Pipeline as input and returns a score or a tuple of (score, variance).
            max_iterations (int):
                Max number of iterations to run, i.e. number of results to record before stopping.
            score_threshold (float, optional):
                Stop running the task when the score is equal to or better than this value.

        Returns:
            The best recorded :class:`.Result` with the :class:`.Pipeline` that was used to achieve it.
            For multi-objective tasks, the set of Pareto front Results will be returned instead.

        Raises:
            :class:`.OPTaaSError` if the server is unavailable.
        """

        def calculate_score(**configuration_values):
            pipeline = self._make_pipeline(configuration_values['pipeline'])
            return scoring_function(pipeline)

        return super().run(scoring_function=calculate_score, max_iterations=max_iterations,
                           score_threshold=score_threshold)

    def _print_configuration(self, configuration: Configuration) -> None:
        print(f'Pipeline: {self.make_pipeline(configuration)}')

    def _make_stored_results(self, response: OPTaaSResponse) -> List[StoredResult]:
        results = super()._make_stored_results(response)
        for result in results:
            if isinstance(result.configuration, Configuration):
                result.pipeline = self.make_pipeline(result.configuration)
        return results

    def make_pipeline(self, configuration: Configuration) -> Pipeline:
        """Creates a sklearn :class:`.Pipeline` and sets its parameters based on the provided :class:`.Configuration`"""
        return self._make_pipeline(configuration.values['pipeline'])

    def _make_pipeline(self, pipeline_values: Dict) -> Pipeline:
        configuration_values = copy.deepcopy(pipeline_values)
        pipeline_parameters = self.parameters[0]['items']
        return self._make_pipeline_from_values(configuration_values, pipeline_parameters, self._estimators)

    def _make_pipeline_from_values(self, values: Dict, parameters: List[Dict], estimators: List[EstimatorTuple]):
        new_estimators = []

        for name, estimator in estimators:
            if name in values:
                estimator_parameter = next(p for p in parameters if p['name'] == name)
                new_estimator = self._make_estimator(name, estimator, values, estimator_parameter)
                new_estimators.append((name, new_estimator))

        return Pipeline(new_estimators)

    def _make_estimator(self, name: str, estimator: Estimator, values: Dict, estimator_parameter: Dict):
        if isinstance(estimator, OptimizablePipeline):
            return self._make_pipeline_from_values(values[name], estimator_parameter['items'], estimator.estimators)

        if isinstance(estimator, EstimatorChoice):
            choice = get_first_key(values[name])
            choice_index = int(choice)
            move_dict_value_up_one_level(values, name)
            estimator = estimator.estimators[choice_index]
            estimator_parameter = estimator_parameter['choices'][choice_index]
            return self._make_estimator(name, estimator, values, estimator_parameter)

        _flatten_values(values[name], estimator_parameter)
        cloned_estimator = clone(estimator)
        cloned_estimator.set_params(**values[name])
        return cloned_estimator


def _flatten_values(values: Dict, parameter_group: Dict) -> None:
    for parameter in parameter_group['items']:
        name = parameter['name']
        if name in values:
            if parameter['type'] == 'choice':
                move_dict_value_up_one_level(values, name)
            elif parameter['type'] == 'group':
                value: Dict = values.get(name)  # type: ignore
                group_values = list(value.values())
                if len(group_values) == 1 and isinstance(group_values[0], Dict):
                    values[name] = group_values[0]
                else:
                    values[name] = group_values
        else:
            values[name] = None
