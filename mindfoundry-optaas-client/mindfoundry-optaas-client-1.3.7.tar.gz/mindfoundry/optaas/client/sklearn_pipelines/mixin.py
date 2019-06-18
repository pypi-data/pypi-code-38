from abc import ABC, abstractmethod
from typing import Any, List

from sklearn.base import BaseEstimator

from mindfoundry.optaas.client.parameter import GroupParameter, ChoiceParameter
from mindfoundry.optaas.client.sklearn_pipelines.parameter_maker import SklearnParameterMaker
from mindfoundry.optaas.client.sklearn_pipelines.utils import _make_id, _get_all_parameters_and_constraints, \
    MissingArgumentError, Estimator, EstimatorTuple, ParametersAndConstraints, Optimizable


class OptimizablePipeline(Optimizable):
    """A pipeline-like object to which will be used to generate parameters and constraints for optimization.

    Args:
        estimators (List[EstimatorTuple]):
            List of (name, estimator) tuples as you would provide when creating a sklearn :class:`.Pipeline`.
            An estimator can be:
                * A subclass of :class:`.OptimizableBaseEstimator`
                * A subclass of :class:`.BaseEstimator` (in which case a warning will be displayed informing you that it won't be optimized)
                * An :meth:`~mindfoundry.optaas.client.sklearn_pipelines.mixin.optional_step`
                * A :meth:`~mindfoundry.optaas.client.sklearn_pipelines.mixin.choice` or :meth:`~mindfoundry.optaas.client.sklearn_pipelines.mixin.optional_choice`
                * Another :class:`.OptimizablePipeline`
        optional (bool): Whether this will be an optional step (defaults to False).
    """

    def __init__(self, estimators: List[EstimatorTuple], optional: bool = False) -> None:
        self.estimators = estimators
        self.optional = optional

    def make_all_parameters_and_constraints(self, estimator_name: str, id_prefix: str,
                                            **kwargs) -> ParametersAndConstraints:
        pipeline_name = estimator_name
        prefix = id_prefix + pipeline_name + '__'
        parameters, constraints = _get_all_parameters_and_constraints(self.estimators, prefix, **kwargs)
        grouped_parameter = GroupParameter(pipeline_name, id=_make_id(id_prefix + pipeline_name), items=parameters,
                                           optional=self.optional)
        return [grouped_parameter], constraints


class OptimizableBaseEstimator(BaseEstimator, Optimizable, ABC):
    """Mixin that allows an estimator to be optimized by OPTaaS. Subclasses must implement `make_parameters_and_constraints`."""

    @abstractmethod
    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Abstract method that should generate the :class:`Parameters <.Parameter>` and
        :class:`Constraints <.Constraint>` required to optimize a sklearn estimator.

        When implementing this method, make sure to use the :class:`SklearnParameterMaker` `sk` to create parameters
        e.g. call `sk.IntParameter(...)` instead of `IntParameter(...)`.

        If the parameter you want to optimize can take values of different types, use a :meth:`ChoiceParameter <.SklearnParameterMaker.ChoiceParameter>`.
        For an example, see `n_components` in :class:`.PCA`. If the parameter value needs to be a list or array, use a
        :meth:`GroupParameter <.SklearnParameterMaker.GroupParameter>`. For an example, see `weights` in :class:`.VotingClassifier`.

        Args:
            sk (SklearnParameterMaker): Allows you to create parameters with the correct names and defaults.
            kwargs: Additional arguments required to optimize certain estimators, e.g. `feature_count`
                (number of features in your data set, required to optimize :class:`.PCA`)

        Returns:
            A tuple of 2 lists (:class:`Parameters <.Parameter>`, :class:`Constraints <.Constraint>`)

        Raises:
            :class:`.MissingArgumentError` if a required argument is missing from `kwargs`.
        """
        pass

    def get_required_kwarg(self, kwargs, arg_name: str) -> Any:
        """Returns value of a kwarg required to optimize this estimator. Raises error if argument not set.

        Args:
            kwargs: Arguments taken from :meth:`.make_parameters_and_constraints`.
            arg_name (str): Name of the required argument.

        Returns:
            Value of argument.

        Raises:
            :class:`.MissingArgumentError` if the argument is not present.
        """
        if arg_name not in kwargs:
            raise MissingArgumentError(arg_name, self)
        return kwargs[arg_name]

    def make_all_parameters_and_constraints(self, estimator_name: str, id_prefix: str,
                                            **kwargs) -> ParametersAndConstraints:
        estimator_id = _make_id(id_prefix + estimator_name)
        parameter_maker = SklearnParameterMaker(estimator_id, self)
        parameters, constraints = self.make_parameters_and_constraints(parameter_maker, **kwargs)
        grouped_parameter = GroupParameter(estimator_name, id=estimator_id, items=parameters,
                                           optional=isinstance(self, OptionalStepMixin))
        return [grouped_parameter], constraints


class OptionalStepMixin(OptimizableBaseEstimator):
    """Mixin that allows an estimator to be optional, i.e. it may be omitted from a :class:`.Configuration` generated by OPTaaS.

    Example:
        `class MyEstimator(OptionalStepMixin):`

    Your estimator can define `make_parameters_and_constraints` if you wish to optimize its parameters, or you can
    leave it undefined and use the default provided below.
    """

    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """A default implementation for when you need an optional estimator without optimizing any of its parameters."""
        return [], []


class EstimatorChoice(Optimizable):
    """Allows OPTaaS to choose one of many estimators for a step in a pipeline.

    Args:
        *estimators (Estimator): Estimators from which to choose.
        optional (bool): Whether this will be an optional step (defaults to False).
    """

    def __init__(self, *estimators: Estimator, optional: bool = False) -> None:
        self.estimators = estimators
        self.optional = optional

    def make_all_parameters_and_constraints(self, estimator_name: str, id_prefix: str,
                                            **kwargs) -> ParametersAndConstraints:
        choices, constraints = _get_all_parameters_and_constraints([
            (str(i), estimator) for i, estimator in enumerate(self.estimators)
        ], id_prefix + estimator_name + '__', **kwargs)
        choice_parameter = ChoiceParameter(estimator_name, id=_make_id(estimator_name), choices=choices,
                                           optional=self.optional)
        return [choice_parameter], constraints


def optional_step(estimator: Estimator) -> OptionalStepMixin:
    """Wrapper method to easily make an estimator optional in an OPTaaS :class:`.SklearnTask`.

    The :class:`.OptionalStepMixin` class will be added to the estimator object's base classes (only this instance will
    be affected, not the entire class).

    Example:
        `create_sklearn_task(estimators=[ ('my_optional_step', optional_step(MyEstimator())) ])`
    """

    estimator_type = type(estimator)
    estimator.__class__ = type(estimator_type.__name__, (estimator_type, OptionalStepMixin), {})
    return estimator  # type: ignore


def choice(*estimators: Estimator) -> EstimatorChoice:
    """Convenience method for creating a choice of estimators in a pipeline."""
    return EstimatorChoice(*estimators)


def optional_choice(*estimators: Estimator) -> EstimatorChoice:
    """Convenience method for creating a choice of estimators as an optional step in a pipeline."""
    return EstimatorChoice(*estimators, optional=True)
