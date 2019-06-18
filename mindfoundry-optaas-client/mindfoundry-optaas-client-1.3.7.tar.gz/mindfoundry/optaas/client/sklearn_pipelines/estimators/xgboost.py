from xgboost.sklearn import XGBClassifier as BaseXGBClassifier

from mindfoundry.optaas.client.sklearn_pipelines.mixin import OptimizableBaseEstimator
from mindfoundry.optaas.client.sklearn_pipelines.parameter_maker import SklearnParameterMaker
from mindfoundry.optaas.client.sklearn_pipelines.utils import ParametersAndConstraints, SMALLEST_NUMBER_ABOVE_ZERO


class XGBClassifier(BaseXGBClassifier, OptimizableBaseEstimator):
    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Generates :class:`Parameters <.Parameter>` and :class:`Constraints <.Constraint>` to optimize a :class:`.XGBClassifier` estimator.

        Args:
            gpu_enabled (bool, optional, default=False):
                If True, the `objective` parameter will include gpu-specific values such as 'gpu:reg:linear'.
        """

        objective_values = [
            'reg:linear', 'reg:logistic', 'binary:logistic', 'binary:logitraw', 'count:poisson',
            'survival:cox', 'multi:softmax', 'multi:softprob', 'rank:pairwise', 'reg:gamma', 'reg:tweedie'
        ]

        if kwargs.get('gpu_enabled'):
            objective_values += ['gpu:reg:linear', 'gpu:reg:logistic', 'gpu:binary:logistic', 'gpu:binary:logitraw']

        parameters = [
            sk.CategoricalParameter('objective', values=objective_values),
            sk.CategoricalParameter('booster', values=["gbtree", "gblinear", "dart"]),
            sk.FloatParameter('learning_rate', minimum=0, maximum=1),
            sk.FloatParameter('gamma', minimum=0, maximum=20),
            sk.IntParameter('max_depth', minimum=0, maximum=20),
            sk.IntParameter('min_child_weight', minimum=0, maximum=10),
            sk.IntParameter('max_delta_step', minimum=0, maximum=10),
            sk.FloatParameter('subsample', minimum=SMALLEST_NUMBER_ABOVE_ZERO, maximum=1),
            sk.FloatParameter('colsample_bytree', minimum=SMALLEST_NUMBER_ABOVE_ZERO, maximum=1),
            sk.FloatParameter('colsample_bylevel', minimum=SMALLEST_NUMBER_ABOVE_ZERO, maximum=1),
            sk.FloatParameter('reg_lambda', minimum=0, maximum=1),
            sk.FloatParameter('reg_alpha', minimum=0, maximum=1),
            sk.FloatParameter('scale_pos_weight', minimum=0, maximum=1),
            sk.FloatParameter('base_score', minimum=0, maximum=1),
            sk.IntParameter('n_estimators', minimum=5, maximum=1000),
        ]
        return parameters, []
