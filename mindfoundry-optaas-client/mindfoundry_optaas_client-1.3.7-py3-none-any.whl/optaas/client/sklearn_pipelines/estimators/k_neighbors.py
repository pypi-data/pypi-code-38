from sklearn.neighbors import KNeighborsClassifier as BaseKNeighborsClassifier, \
    KNeighborsRegressor as BaseKNeighborsRegressor

from mindfoundry.optaas.client.parameter import Distribution
from mindfoundry.optaas.client.sklearn_pipelines.mixin import OptimizableBaseEstimator
from mindfoundry.optaas.client.sklearn_pipelines.parameter_maker import SklearnParameterMaker
from mindfoundry.optaas.client.sklearn_pipelines.utils import ParametersAndConstraints


class _OptimizableKNeighbors(OptimizableBaseEstimator):
    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Generates :class:`Parameters <.Parameter>` and :class:`Constraints <.Constraint>` to optimize a KNeighbors estimator."""

        parameters = [
            sk.IntParameter('n_neighbors', minimum=1, maximum=20, distribution=Distribution.LOGUNIFORM),
            sk.CategoricalParameter('weights', values=["uniform", "distance"]),
            sk.CategoricalParameter('p', values=[1, 2]),
        ]

        return parameters, []


class KNeighborsClassifier(BaseKNeighborsClassifier, _OptimizableKNeighbors):
    """Allows us to optimize :class:`.KNeighborsClassifier` estimators."""
    pass


class KNeighborsRegressor(BaseKNeighborsRegressor, _OptimizableKNeighbors):
    """Allows us to optimize :class:`.KNeighborsRegressor` estimators."""
    pass
