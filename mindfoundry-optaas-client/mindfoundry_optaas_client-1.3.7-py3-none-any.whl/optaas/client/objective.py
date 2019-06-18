from typing import Any, Dict

from mindfoundry.optaas.client.goal import Goal


class Objective:
    """An objective for optimizing as part of a multi-objective Task.

    When evaluating a :class:`.Configuration` and producing a :class:`Result`, you can include a score for each Objective.

    Args:
        id (str): A unique id for the objective.
        goal (Goal, optional, default Goal.max): Whether OPTaaS should aim for the lowest (min) or highest (max) score.
        min_known_score (float, optional): Minimum known score value for this objective.
        max_known_score (float, optional): Maximum known score value for this objective.
    """

    def __init__(self, id: str,  # pylint: disable=redefined-builtin
                 goal: Goal = None, min_known_score: float = None, max_known_score: float = None) -> None:
        self._id = id
        self._goal = goal
        self._min_known_score = min_known_score
        self._max_known_score = max_known_score

    def to_json(self) -> Dict[str, Any]:
        json: Dict[str, Any] = {"id": self._id}
        if self._goal:
            json["goal"] = self._goal.name
        if self._min_known_score is not None:
            json["minKnownScore"] = self._min_known_score
        if self._max_known_score is not None:
            json["maxKnownScore"] = self._max_known_score
        return json
