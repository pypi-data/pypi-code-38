from sklearn.ensemble import AdaBoostClassifier as BaseAdaBoostClassifier, AdaBoostRegressor as BaseAdaBoostRegressor

from mindfoundry.optaas.client.parameter import Distribution
from mindfoundry.optaas.client.sklearn_pipelines.mixin import OptimizableBaseEstimator
from mindfoundry.optaas.client.sklearn_pipelines.parameter_maker import SklearnParameterMaker
from mindfoundry.optaas.client.sklearn_pipelines.utils import ParametersAndConstraints


class _OptimizableAdaBoost(OptimizableBaseEstimator):
    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Generates :class:`Parameters <.Parameter>` and :class:`Constraints <.Constraint>` to optimize an AdaBoost estimator."""

        return [
            sk.IntParameter('n_estimators', minimum=10, maximum=500),
            sk.FloatParameter('learning_rate', minimum=0.01, maximum=2.5, distribution=Distribution.LOGUNIFORM),
        ], []


class AdaBoostClassifier(BaseAdaBoostClassifier, _OptimizableAdaBoost):
    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Generates :class:`Parameters <.Parameter>` and :class:`Constraints <.Constraint>` to optimize an :class:`.AdaBoostClassifier`."""

        parameters, constraints = super().make_parameters_and_constraints(sk, **kwargs)
        parameters.append(sk.CategoricalParameter('algorithm', values=['SAMME', 'SAMME.R']))
        return parameters, constraints


class AdaBoostRegressor(BaseAdaBoostRegressor, _OptimizableAdaBoost):
    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Generates :class:`Parameters <.Parameter>` and :class:`Constraints <.Constraint>` to optimize an :class:`.AdaBoostRegressor`."""

        parameters, constraints = super().make_parameters_and_constraints(sk, **kwargs)
        parameters.append(sk.CategoricalParameter('loss', values=['linear', 'square', 'exponential']))
        return parameters, constraints
