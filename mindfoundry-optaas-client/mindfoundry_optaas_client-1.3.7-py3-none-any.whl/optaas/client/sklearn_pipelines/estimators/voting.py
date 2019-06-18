from typing import List

from sklearn.ensemble import VotingClassifier as BaseVotingClassifier

from mindfoundry.optaas.client.parameter import Parameter, GroupParameter
from mindfoundry.optaas.client.sklearn_pipelines.mixin import OptimizableBaseEstimator
from mindfoundry.optaas.client.sklearn_pipelines.parameter_maker import SklearnParameterMaker
from mindfoundry.optaas.client.sklearn_pipelines.utils import _get_all_parameters_and_constraints, \
    ParametersAndConstraints


class VotingClassifier(BaseVotingClassifier, OptimizableBaseEstimator):
    def make_parameters_and_constraints(self, sk: SklearnParameterMaker, **kwargs) -> ParametersAndConstraints:
        """Generates :class:`Parameters <.Parameter>` and :class:`Constraints <.Constraint>` to optimize a :class:`.VotingClassifier`."""

        grouped_parameters, constraints = _get_all_parameters_and_constraints(self.estimators, sk.prefix, **kwargs)

        parameters: List[Parameter] = []
        for group in grouped_parameters:
            if not isinstance(group, GroupParameter):
                raise ValueError('VotingClassifier does not support Choices')
            for parameter in group.items:
                parameter.name = group.name + '__' + parameter.name
            parameters.extend(group.items)

        parameters.extend([
            sk.CategoricalParameter('voting', values=['hard', 'soft']),
            sk.GroupParameter('weights', optional=True, items=[
                sk.FloatParameter(f'weight_{estimator_name}', minimum=0, maximum=1)
                for estimator_name, _ in self.estimators
            ])
        ])
        return parameters, constraints
