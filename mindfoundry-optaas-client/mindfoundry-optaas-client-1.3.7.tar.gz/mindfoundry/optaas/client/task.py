from typing import Any, List, Dict, Callable, Union, TYPE_CHECKING

from mindfoundry.optaas.client.configuration import Configuration
from mindfoundry.optaas.client.goal import Goal
from mindfoundry.optaas.client.prediction import Prediction
from mindfoundry.optaas.client.result import StoredResult, Result, ScoreValue, ScoreDict, ScoreValueOrDict, VarianceValueOrDict, \
    ScoringFunctionOutput
from mindfoundry.optaas.client.session import OPTaaSSession, OPTaaSResponse
from mindfoundry.optaas.client.utils import _pprint

if TYPE_CHECKING:  # pragma: no cover
    from pandas import DataFrame  # pylint: disable=unused-import

_MULTI_OBJECTIVE_UNSUPPORTED_ERROR = "best_first is not supported for multi-objective Tasks.\n" \
                                     "Did you mean get_pareto_set?"

_SINGLE_OBJECTIVE_UNSUPPORTED_ERROR = "get_pareto_set is not supported for single-objective Tasks.\n" \
                                      "Did you mean get_best_result_and_configuration?"


class Task:
    """Allows you to access Task attributes and perform all Task-related functions.

    Attributes:
        json (Dict): The full JSON representation of this Task in OPTaaS.
        id (str): Unique id for the Task.
        title (str): Name/description as provided when the Task was created.
        parameters (List[Dict]): JSON representation of the :class:`Parameters <.Parameter>` defined for this Task.
        constraints (List[str]): List of OPTaaS string representations of the :class:`Constraints <.Constraint>` defined for this Task.
        status (str): Current status of the Task, e.g. 'running' or 'done'
        number_of_iterations (int): Number of :class:`Results <.Result>` provided for this Task so far.
        user_defined_data (Any): Any other data as provided when the Task was created.
    """

    def __init__(self, json: dict, session: OPTaaSSession) -> None:
        self.json = json
        self.id = json['id']  # pylint: disable=invalid-name
        self.parameters = json['parameters']
        self.constraints = json['constraints']
        self._update_attributes(json)

        self._session = session
        self._task_url = json['_links']['self']['href']
        self._configurations_url = json['_links']['configurations']['href']
        self._results_url = json['_links']['results']['href']
        self._complete_url = json['_links']['complete']['href']
        self._resume_url = json['_links']['resume']['href']
        self._predictions_url = json['_links']['predictions']['href']
        self._pareto_url = json['_links']['pareto']['href']

    def _update_attributes(self, json: dict):
        self.title = json['title']
        self.status = json['status']
        self.number_of_iterations = json['numberOfIterations']
        self.user_defined_data = json.get('userDefined')

    def run(self, scoring_function: Callable[..., ScoringFunctionOutput], max_iterations: int,
            score_threshold: ScoreValueOrDict = None) -> Union[StoredResult, List[StoredResult]]:
        """Run this task, using the provided scoring function to calculate the score for each configuration.

        Args:
            scoring_function (Callable[..., ScoringFunctionOutput]):
                Function that takes configuration values as arguments, e.g. if you have parameters x and y, your
                function would be `def get_score(x, y)`.
                The function can return just a score, or a tuple of (score, variance).
                For multi-objective tasks the score and variance must be dictionaries, with Objective.id values as keys, e.g.
                `{"id1": 1.23, "id2": 4.56}`.
            max_iterations (int):
                Max number of iterations to run, i.e. number of results to record before stopping.
            score_threshold (ScoreValueOrDict, optional, defaults to min/max known score if defined):
                Stop running the task when the score is equal to or better than this value.
                For multi-objective tasks, use a dictionary with Objective.id values as keys, e.g.
                `{"id1": 1.23, "id2": 4.56}`.

        Returns:
            The best recorded :class:`.Result` with the :class:`.Configuration` that was used to achieve it.
            For multi-objective tasks, the set of Pareto front Results will be returned instead.

        Raises:
            :class:`.OPTaaSError` if the server is unavailable.
        """
        print(f'Running task "{self.title}" for {max_iterations} iterations')

        reached_threshold = self._reached_threshold_if_defined(score_threshold)

        print()
        configuration = self.generate_configurations(1)[0]

        for i in range(max_iterations):
            scoring_result = scoring_function(**configuration.values)

            if isinstance(scoring_result, tuple):
                score, variance = scoring_result
                print(f'Iteration: {i}    Score: {score}    Variance: {variance}')
            else:
                score = scoring_result
                variance = None  # type: ignore
                print(f'Iteration: {i}    Score: {score}')

            self._print_configuration(configuration)
            print()

            configuration = self.record_result(configuration=configuration, score=score, variance=variance)
            if reached_threshold(score):  # type: ignore
                break

        return_value = self.get_pareto_set() if self.json.get('objectives') else self.get_best_result_and_configuration()

        self.complete()
        self.refresh()
        print('Task Completed')
        print()

        return return_value  # type: ignore

    def _print_configuration(self, configuration: Configuration) -> None:  # pylint: disable=no-self-use
        print(f'Configuration: {configuration.values}')

    def _reached_threshold_if_defined(self, score_threshold: ScoreValueOrDict = None) -> Union[Callable[[ScoreValue], bool],
                                                                                               Callable[[ScoreDict], bool]]:
        objectives = self.json.get('objectives')
        if objectives:
            if score_threshold is None or isinstance(score_threshold, Dict):
                return self._reached_multi_objective_threshold_if_defined(objectives, score_threshold or {})
            raise ValueError("Score threshold must be a dictionary")

        goal = Goal[self.json['goal']]

        if score_threshold is None:
            score_threshold = self.json.get('minKnownScore' if goal == Goal.min else 'maxKnownScore')
            if score_threshold is None:
                print('(no score threshold set)')
                return lambda score: False

        print(f'(or until score is {score_threshold} or better)')
        if goal == Goal.min:
            return lambda score: score <= score_threshold
        return lambda score: score >= score_threshold

    @staticmethod
    def _reached_multi_objective_threshold_if_defined(objectives: List[Dict],
                                                      score_threshold: ScoreDict) -> Callable[[ScoreDict], bool]:
        goals = {objective['id']: Goal[objective['goal']] for objective in objectives}

        for objective in objectives:
            id_ = objective['id']
            if id_ not in score_threshold:
                best_known_score = objective.get('minKnownScore' if goals[id_] == Goal.min else 'maxKnownScore')
                if best_known_score is not None:
                    score_threshold[id_] = best_known_score

        if score_threshold == {}:
            return lambda scores: False

        print(f'(or until scores are {score_threshold} or better)')

        def reached_all_thresholds(scores: ScoreDict) -> bool:
            for id_, threshold in score_threshold.items():
                score = scores.get(id_)
                if score is None:
                    return False
                if goals[id_] == Goal.min:
                    if score > threshold:
                        return False
                elif score < threshold:
                    return False
            return True

        return reached_all_thresholds

    def refresh(self):
        """Make a GET request to OPTaaS to retrieve the latest Task data and update this object accordingly."""
        response = self._session.get(self._task_url)
        self._update_attributes(response.body)

    def delete(self):
        """Delete this Task (cannot be undone)."""
        self._session.delete(self._task_url)

    def generate_configurations(self, quantity: int = 1) -> List[Configuration]:
        """Make a POST request to OPTaaS to generate a set of new :class:`Configurations <.Configuration>` for this Task.

        Args:
            quantity (int, optional, default 1): The number of configurations to generate (minimum 1).

        Returns:
            A list of the newly created :class:`Configurations <.Configuration>`.

        Raises:
            :class:`.OPTaaSError` if the server is unavailable or the quantity is invalid.
        """
        response = self._session.post(self._configurations_url + f'?quantity={quantity}', {})
        return [Configuration(json) for json in response.body['configurations']]

    def add_user_defined_configuration(self, values: Dict, score: ScoreValueOrDict = None, variance: VarianceValueOrDict = None,
                                       user_defined_data: Any = None) -> Configuration:
        """Make a POST request to OPTaaS to store a new user-provided :class:`.Configuration` using the values provided.

        Also optionally store a :class:`.Result` for this Configuration using the provided `score`.

        This is useful for giving OPTaaS a "warm start" by providing some examples of good/bad Configurations.

        Args:
            values (Dict): Values assigned to each :class:`.Parameter`. See :attr:`.Configuration.values`.
            score (ScoreValueOrDict, optional): Score obtained when using this Configuration.
                For multi-objective tasks, a dictionary of scores for each objective, using Objective.id values as keys, e.g.
                `{"id1": 1.23, "id2": 4.56}`.
            variance (VarianceValueOrDict >=0, optional, defaults to 0): Variance associated with the score.
                For multi-objective tasks, a dictionary of variances for each objective, using Objective.id values as keys, e.g.
                `{"id1": 1.23, "id2": 4.56}`.
            user_defined_data (Any, optional, ignored if `score` is not provided): Any other data to store in the Result.

        Returns:
            The newly created :class:`.Configuration`

        Raises:
            :class:`.OPTaaSError` if the values are otherwise invalid or the server is unavailable.
        """
        body: Dict = {'values': values}
        if score is not None:
            result = Result(configuration=_MockConfiguration(), score=score, variance=variance,
                            user_defined_data=user_defined_data)
            body['results'] = [result.to_json_without_configuration()]

        response = self._session.post(self._configurations_url, body)
        return Configuration(response.body['configurations'][0])

    def record_result(self, configuration: Configuration, score: ScoreValueOrDict = None, error: str = None,
                      variance: VarianceValueOrDict = None, user_defined_data: Any = None) -> Configuration:
        """Make a POST request to OPTaaS to record a :class:`.Result` for the given :class:`.Configuration`.

        Must specify **either** `score` **or** `error`.

        After the Result is recorded, OPTaaS will automatically generate the next Configuration for you to try.

        Args:
            configuration (Configuration): The Configuration used to obtain this Result.
            score (ScoreValueOrDict): The score obtained.
                For multi-objective tasks, a dictionary of scores for each objective, using Objective.id values as keys, e.g.
                `{"id1": 1.23, "id2": 4.56}`.
            error (Any): Any data related to an error encountered while calculating the score.
            variance (VarianceValueOrDict >=0, optional, defaults to 0): Variance associated with the score.
                For multi-objective tasks, a dictionary of variances for each objective, using Objective.id values as keys, e.g.
                `{"id1": 1.23, "id2": 4.56}`.
            user_defined_data (Any, optional): Any other data you wish to store as part of this Result.

        Returns:
            The next :class:`.Configuration` generated by OPTaaS.

        Raises:
            :class:`.OPTaaSError` if the data provided is invalid or the server is unavailable.
            :class:`.ValueError` if both score and error are provided, or neither.
        """
        result = Result(configuration=configuration, score=score, error=error, variance=variance,
                        user_defined_data=user_defined_data)
        response = self._session.post(configuration.results_url, result.to_json_without_configuration())
        return Configuration(response.body['nextConfiguration'])

    def record_results(self, results: List[Result]) -> List[Configuration]:
        """Make a POST request to OPTaaS to store a batch of :class:`Results <.Result>` and get the next batch of :class:`Configurations <.Configuration>`.

        Args:
            results (List[Result]): List of Results to record. Must be non-empty.

        Returns:
            A list of the same length as `results`, containing the next :class:`Configurations <.Configuration>` for you to try.

        Raises:
            :class:`.OPTaaSError` if the data provided is invalid or the server is unavailable.
            :class:`.ValueError` if the result list is empty.
        """
        if not results:
            raise ValueError("Result list must be non-empty.")

        body = {'results': [result.to_json() for result in results]}
        response = self._session.post(self._results_url, body)
        return [Configuration(json) for json in response.body['nextConfigurations']]

    def get_configurations(self, limit: int = None) -> List[Configuration]:
        """Make a GET request to OPTaaS to retrieve a list of :class:`Configurations <.Configuration>` for this Task.

        Args:
            limit (int, optional, minimum 1): Upper bound on the number of Configurations that will be returned.

        Returns:
            The list of :class:`Configurations <.Configuration>`.

        Raises:
            :class:`.OPTaaSError` if the limit is invalid or the server is unavailable.
        """
        url = self._configurations_url
        if limit is not None:
            url += f'?limit={limit}'
        response = self._session.get(url)
        return [Configuration(json) for json in response.body['configurations']]

    def get_configuration(self, configuration_id: str) -> Configuration:
        """Make a GET request to OPTaaS to retrieve a specific :class:`.Configuration` by id.

        Args:
            configuration_id (str): Unique id for the Configuration.

        Returns:
            The retrieved :class:`.Configuration`.

        Raises:
            :class:`.OPTaaSError` if the configuration_id is invalid or the server is unavailable.
        """
        url = f'{self._configurations_url}/{configuration_id}'
        response = self._session.get(url)
        return Configuration(response.body)

    def get_results(self, limit: int = None, best_first: bool = False, as_dataframe: bool = False,
                    include_configurations=None) -> Union[List[StoredResult], 'DataFrame']:
        """Make a GET request to OPTaaS to retrieve a list of :class:`Results <.StoredResult>` for this Task.

        Args:
            limit (int, optional, minimum 1): Upper bound on the number of Results that will be returned.
            best_first (bool, optional, default False):
                If True, Results will appear in score order, with the best score first (not currently supported for multi-objective tasks).
                If False, Results will appear in the order they were created.
            as_dataframe (bool, optional, default False):
                Return the data as a Pandas DataFrame. It will include a column for each parameter, plus the
                score, variance and error from each Result.
            include_configurations: Deprecated.

        Returns:
            The list of :class:`Results <.StoredResult>` or a DataFrame.

        Raises:
            :class:`.OPTaaSError` if the limit is invalid or the server is unavailable.
        """
        if include_configurations is not None:
            raise ValueError("include_configurations has been deprecated. Results will now always include the Configuration.")

        if best_first and self.json.get('objectives'):
            raise ValueError(_MULTI_OBJECTIVE_UNSUPPORTED_ERROR)

        url = self._results_url
        query_params: Dict[str, Any] = {}
        if limit is not None:
            query_params['limit'] = limit
        if best_first:
            query_params['order'] = 'bestFirst'
        response = self._session.get(url, query_params=query_params)
        results = self._make_stored_results(response)
        if as_dataframe:
            from pandas.io.json import json_normalize
            return json_normalize([result.as_pandas_row() for result in results])
        return results

    def _make_stored_results(self, response: OPTaaSResponse) -> List[StoredResult]:  # pylint: disable=no-self-use
        return [StoredResult(json) for json in response.body['results']]

    def get_result(self, result_id: int) -> StoredResult:
        """Make a GET request to OPTaaS to retrieve a specific :class:`.StoredResult` by id.

        Args:
            result_id (str): Unique id for the Result.

        Returns:
            The retrieved :class:`.StoredResult`.

        Raises:
            :class:`.OPTaaSError` if the result_id is invalid or the server is unavailable.
        """
        url = f'{self._results_url}/{result_id}'
        response = self._session.get(url)
        return StoredResult(response.body)

    def get_best_result_and_configuration(self) -> StoredResult:
        """Make a GET request to OPTaaS to retrieve the Result with the best score, including the Configuration used to obtain it.

        Not currently supported for multi-objective Tasks.

        Returns:
            The best :class:`.StoredResult` with included :class:`.Configuration`.

        Raises:
            :class:`.OPTaaSError` if the server is unavailable.
            :class:`.ValueError` if no results have been posted for this task.
        """
        results = self.get_results(best_first=True, limit=1)
        if results:
            return results[0]
        raise ValueError('No results available for this task yet')

    def get_pareto_set(self) -> List[StoredResult]:
        """Make a GET request to OPTaaS to retrieve the set of Pareto front Results for a multi-objective Task.

        These are the Results where, for each objective, the score cannot be improved without reducing the score for another objective.

        Not supported for single-objective Tasks.

        Note: if a Result doesn't contain a score value for all Objectives, it will be excluded from the Pareto set.

        Returns:
            The list of Pareto front Results.

        Raises:
            :class:`.OPTaaSError` if the server is unavailable or the task is not multi-objective.
        """
        if not self.json.get('objectives'):
            raise ValueError(_SINGLE_OBJECTIVE_UNSUPPORTED_ERROR)
        response = self._session.get(self._pareto_url)
        return self._make_stored_results(response)

    def get_surrogate_predictions(self, configurations: List[Dict]) -> List[Prediction]:
        """Make a POST request to OPTaaS to retrieve the surrogate prediction for some configurations

        Args:
            configurations (List[Dict]): key value pairs corresponding to parameter names and their values.
            See :attr:`.Configuration.values`.

        Returns:
            :List[Prediction]: a list of objects, each containing the mean and variance of the surrogate at each
            corresponding configuration point.
            For multi-objective Tasks, the mean and variance are dictionaries containing mean (and
            variance respectively) for each objective.

        Raises:
            :class:`.OPTaaSError` if the configurations are invalid or the server is unavailable
        """
        body = {'configurations': [{'values': configuration} for configuration in configurations]}
        response = self._session.post(self._predictions_url, body)
        predictions = response.body['predictions']
        return [Prediction(json=prediction) for prediction in predictions]

    def complete(self):
        """Make a PUT request to OPTaaS to complete the task (no further configurations or results can be created)"""
        self._session.put(self._complete_url, {})

    def resume(self):
        """Make a PUT request to OPTaaS to resume a completed task"""
        self._session.put(self._resume_url, {})

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.__dict__ == other.__dict__

    def __repr__(self):
        return _pprint(self, 'id', 'title', 'user_defined_data', 'parameters', 'constraints')


class _MockConfiguration(Configuration):
    """Used only internally, to post a result for a user-defined configuration."""

    def __init__(self):  # pylint: disable=super-init-not-called
        pass
