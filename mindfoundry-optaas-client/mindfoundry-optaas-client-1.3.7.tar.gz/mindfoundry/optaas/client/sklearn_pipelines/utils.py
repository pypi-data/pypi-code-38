import warnings
from abc import ABC, abstractmethod
from typing import List, Union, Tuple

from numpy import nextafter
from sklearn.base import BaseEstimator

from mindfoundry.optaas.client.constraint import Constraint
from mindfoundry.optaas.client.parameter import GroupParameter, Parameter

SMALLEST_NUMBER_ABOVE_ZERO = nextafter(0.0, 1)
LARGEST_NUMBER_BELOW_ONE = nextafter(1.0, 0)

ParametersAndConstraints = Tuple[List[Parameter], List[Constraint]]


class Optimizable(ABC):
    """Superclass for all optimizable steps."""

    @abstractmethod
    def make_all_parameters_and_constraints(self, estimator_name: str, id_prefix: str,
                                            **kwargs) -> ParametersAndConstraints:
        """Returns all parameters and constraints for multiple estimators in a group or choice."""
        pass


Estimator = Union[BaseEstimator, Optimizable]
EstimatorTuple = Tuple[str, Estimator]


def _get_all_parameters_and_constraints(estimators: List[EstimatorTuple], id_prefix: str,
                                        **kwargs) -> ParametersAndConstraints:
    all_parameters = []
    all_constraints = []

    for estimator_name, estimator in estimators:
        if isinstance(estimator, Optimizable):
            parameters, constraints = estimator.make_all_parameters_and_constraints(estimator_name, id_prefix, **kwargs)
        else:
            warnings.warn(f"{type(estimator).__name__} is not an Optimizable estimator.")
            parameters = [GroupParameter(estimator_name, id=_make_id(id_prefix + estimator_name), items=[])]
            constraints = []

        all_parameters.extend(parameters)
        all_constraints.extend(constraints)

    return all_parameters, all_constraints


def _make_id(estimator_name: str) -> str:
    return estimator_name.replace(' ', '-')


class MissingArgumentError(ValueError):
    """Raised when a required argument is missing from kwargs in :meth:`.OPTaaSClient.create_sklearn_task`"""

    def __init__(self, required_arg: str, estimator) -> None:
        super().__init__(f"{required_arg} is required in kwargs in order to optimize {type(estimator).__name__}")
