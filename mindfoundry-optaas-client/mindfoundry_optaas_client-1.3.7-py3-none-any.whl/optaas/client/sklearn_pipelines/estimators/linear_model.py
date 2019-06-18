from sklearn.linear_model import Lasso as BaseLasso, Ridge as BaseRidge

from mindfoundry.optaas.client.sklearn_pipelines.mixin import OptimizableBaseEstimator
from mindfoundry.optaas.client.sklearn_pipelines.parameter_maker import SklearnParameterMaker
from mindfoundry.optaas.client.sklearn_pipelines.utils import ParametersAndConstraints, SMALLEST_NUMBER_ABOVE_ZERO


class _OptimizableLinearModel(OptimizableBaseEstimator):
    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Generates :class:`Parameters <.Parameter>` and :class:`Constraints <.Constraint>` to optimize a linear model."""

        return [sk.FloatParameter('alpha', minimum=SMALLEST_NUMBER_ABOVE_ZERO, maximum=1)], []


class Lasso(BaseLasso, _OptimizableLinearModel):
    """Allows us to optimize a :class:`.Lasso` estimator."""
    pass


class Ridge(BaseRidge, _OptimizableLinearModel):
    """Allows us to optimize a :class:`.Ridge` estimator."""
    pass
