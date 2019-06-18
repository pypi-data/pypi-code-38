from typing import Sequence

from sklearn.ensemble import \
    RandomForestClassifier as BaseRandomForestClassifier, \
    ExtraTreesClassifier as BaseExtraTreesClassifier, \
    RandomForestRegressor as BaseRandomForestRegressor, \
    ExtraTreesRegressor as BaseExtraTreesRegressor, \
    GradientBoostingClassifier as BaseGradientBoostingClassifier, \
    GradientBoostingRegressor as BaseGradientBoostingRegressor
from sklearn.tree import DecisionTreeClassifier as BaseDecisionTreeClassifier, \
    DecisionTreeRegressor as BaseDecisionTreeRegressor

from mindfoundry.optaas.client.parameter import Distribution
from mindfoundry.optaas.client.sklearn_pipelines.mixin import OptimizableBaseEstimator
from mindfoundry.optaas.client.sklearn_pipelines.parameter_maker import SklearnParameterMaker
from mindfoundry.optaas.client.sklearn_pipelines.utils import ParametersAndConstraints, SMALLEST_NUMBER_ABOVE_ZERO


class _OptimizableEnsemble(OptimizableBaseEstimator):
    """Superclass for optimizable ensemble estimators."""

    # Properties must be specified in subclasses
    criterion_values: Sequence[str] = None  # type: ignore
    min_samples_split_distribution: Distribution = None  # type: ignore
    max_depth_distribution: Distribution = None  # type: ignore
    min_impurity_decrease_maximum: float = None  # type: ignore

    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Generates :class:`Parameters <.Parameter>` and :class:`Constraints <.Constraint>` to optimize ensemble estimators."""

        parameters = [
            sk.CategoricalParameter('max_features', values=['auto', 'sqrt', 'log2']),
            sk.IntParameter('min_samples_split', minimum=2, maximum=20,
                            distribution=self.min_samples_split_distribution),
            sk.IntParameter('min_samples_leaf', minimum=1, maximum=20),
            sk.CategoricalParameter('criterion', values=self.criterion_values),
            sk.IntParameter('max_leaf_nodes', minimum=10, maximum=10000, optional=True,
                            distribution=Distribution.LOGUNIFORM),
            sk.IntParameter('max_depth', minimum=1, maximum=100, optional=True,
                            distribution=self.max_depth_distribution),  # type: ignore
            sk.FloatParameter('min_weight_fraction_leaf', minimum=0.0, maximum=0.5),
            sk.FloatParameter('min_impurity_decrease', minimum=0, maximum=self.min_impurity_decrease_maximum),  # type: ignore
        ]
        return parameters, []


class _OptimizableForestOrTree(_OptimizableEnsemble):
    """Superclass for optimizable forest/tree-based estimators."""

    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Generates :class:`Parameters <.Parameter>` and :class:`Constraints <.Constraint>` to optimize forest/tree-based estimators."""

        parameters, constraints = super().make_parameters_and_constraints(sk, **kwargs)

        # Fix hacky default set by sklearn in v0.20
        if sk.defaults.get("n_estimators") == "warn":
            sk.defaults["n_estimators"] = 100

        parameters.extend([
            sk.BoolParameter('bootstrap'),
            sk.IntParameter('n_estimators', minimum=10, maximum=500),
        ])

        return parameters, constraints


class _OptimizableEnsembleClassifier(_OptimizableEnsemble):
    """Superclass for optimizable ensemble classifiers."""

    criterion_values = ['gini', 'entropy']
    min_impurity_decrease_maximum = 1


class _OptimizableEnsembleRegressor(_OptimizableEnsemble):
    """Superclass for optimizable ensemble regressors."""

    criterion_values = ['mse', 'mae']
    min_impurity_decrease_maximum = 0.01


class _OptimizableRandomForest(_OptimizableForestOrTree):
    """Superclass for optimizable RandomForest estimators."""

    min_samples_split_distribution = Distribution.UNIFORM
    max_depth_distribution = Distribution.LOGUNIFORM


class _OptimizableExtraTrees(_OptimizableForestOrTree):
    """Superclass for optimizable ExtraTrees estimators."""

    min_samples_split_distribution = Distribution.LOGUNIFORM
    max_depth_distribution = Distribution.UNIFORM


class RandomForestClassifier(BaseRandomForestClassifier, _OptimizableEnsembleClassifier, _OptimizableRandomForest):
    """Allows us to optimize :class:`.RandomForestClassifier` estimators."""
    pass


class ExtraTreesClassifier(BaseExtraTreesClassifier, _OptimizableEnsembleClassifier, _OptimizableExtraTrees):
    """Allows us to optimize :class:`.ExtraTreesClassifier` estimators."""
    pass


class RandomForestRegressor(BaseRandomForestRegressor, _OptimizableEnsembleRegressor, _OptimizableRandomForest):
    """Allows us to optimize :class:`.RandomForestRegressor` estimators."""
    pass


class ExtraTreesRegressor(BaseExtraTreesRegressor, _OptimizableEnsembleRegressor, _OptimizableExtraTrees):
    """Allows us to optimize :class:`.ExtraTreesRegressor` estimators."""
    pass


class _OptimizableDecisionTree(_OptimizableEnsemble):
    """Superclass for optimizable DecisionTree estimators."""

    min_samples_split_distribution = Distribution.LOGUNIFORM
    max_depth_distribution = Distribution.UNIFORM

    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Generates :class:`Parameters <.Parameter>` and :class:`Constraints <.Constraint>` to optimize DecisionTree-based estimators."""

        parameters, constraints = super().make_parameters_and_constraints(sk, **kwargs)

        parameters.extend([
            sk.CategoricalParameter('splitter', values=["best", "random"]),
        ])

        return parameters, constraints


class DecisionTreeClassifier(BaseDecisionTreeClassifier, _OptimizableDecisionTree, _OptimizableEnsembleClassifier):
    """Allows us to optimize a :class:`.DecisionTreeClassifier`."""
    pass


class DecisionTreeRegressor(BaseDecisionTreeRegressor, _OptimizableDecisionTree):
    """Allows us to optimize a :class:`.DecisionTreeRegressor`."""

    criterion_values = ["mse", "friedman_mse", "mae"]
    min_impurity_decrease_maximum = 0.01


class _OptimizableGradientBoosting(_OptimizableEnsemble):
    """Superclass for optimizable GradientBoosting estimators."""

    criterion_values = ["mse", "friedman_mse", "mae"]
    min_impurity_decrease_maximum = 1
    min_samples_split_distribution = Distribution.UNIFORM
    max_depth_distribution = Distribution.UNIFORM

    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Generates :class:`Parameters <.Parameter>` and :class:`Constraints <.Constraint>` to optimize a GradientBoosting estimator."""

        parameters, constraints = super().make_parameters_and_constraints(sk, **kwargs)

        parameters.extend([
            sk.FloatParameter('learning_rate', minimum=SMALLEST_NUMBER_ABOVE_ZERO, maximum=1),
            sk.IntParameter('n_estimators', minimum=10, maximum=500),
            sk.FloatParameter('subsample', minimum=0, maximum=1),
        ])

        return parameters, constraints


class GradientBoostingClassifier(BaseGradientBoostingClassifier, _OptimizableGradientBoosting):
    """Allows us to optimize a :class:`.GradientBoostingClassifier`."""

    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Generates :class:`Parameters <.Parameter>` and :class:`Constraints <.Constraint>` to optimize a :class:`.GradientBoostingClassifier`.

        Args:
            class_count (int, optional): Number of classes in the classification dataset.
                If set to a number other than `2`, the `loss` parameter will not be optimized (because it can only be set to "deviance").
        """

        parameters, constraints = super().make_parameters_and_constraints(sk, **kwargs)

        if kwargs.get('class_count') == 2:
            parameters.append(sk.CategoricalParameter('loss', values=["deviance", "exponential"]))

        return parameters, constraints

    def _make_estimator(self, append=True):
        pass  # BaseGradientBoostingClassifier doesn't implement this either


class GradientBoostingRegressor(BaseGradientBoostingRegressor, _OptimizableGradientBoosting):
    """Allows us to optimize a :class:`.GradientBoostingRegressor`."""

    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Generates :class:`Parameters <.Parameter>` and :class:`Constraints <.Constraint>` to optimize a :class:`.GradientBoostingClassifier`."""

        parameters, constraints = super().make_parameters_and_constraints(sk, **kwargs)

        parameters.extend([
            sk.CategoricalParameter('loss', values=["ls", "lad", "huber", "quantile"]),
            sk.FloatParameter('alpha', minimum=SMALLEST_NUMBER_ABOVE_ZERO, maximum=1),
        ])

        return parameters, constraints

    def _make_estimator(self, append=True):
        pass  # BaseGradientBoostingClassifier doesn't implement this either
