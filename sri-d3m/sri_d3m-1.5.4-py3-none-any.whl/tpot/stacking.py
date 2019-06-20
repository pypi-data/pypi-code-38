from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.metadata import params as meta_params
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import supervised_learning as pi_supervised_learning
from d3m.primitives.classification.gradient_boosting import SKlearn as SKGradientBoostingClassifier
import numpy as np
from pandas import concat

from sri.common import config

Inputs = container.DataFrame
Outputs = container.DataFrame

class StackingOperatorEstimatorHyperparam(meta_hyperparams.Hyperparameter[pi_supervised_learning.SupervisedLearnerPrimitiveBase]):
    structural_type = pi_supervised_learning.SupervisedLearnerPrimitiveBase
    def __init__(self):
        self.structural_type = pi_supervised_learning.SupervisedLearnerPrimitiveBase

        super().__init__(
            default = SKGradientBoostingClassifier(
                hyperparams = SKGradientBoostingClassifier.metadata.query()['primitive_code']['class_type_arguments']['Hyperparams'].defaults()
            ),
            semantic_types = [ 'https://metadata.datadrivendiscovery.org/types/ControlParameter' ]
        )

class StackingOperatorHyperparams(meta_hyperparams.Hyperparams):
    estimator = StackingOperatorEstimatorHyperparam()

class StackingOperatorParams(meta_params.Params):
    fitted: bool

class StackingOperator(pi_supervised_learning.SupervisedLearnerPrimitiveBase[Inputs, Outputs, StackingOperatorParams, StackingOperatorHyperparams]):
    """
The StackingOperator applies a supervised learner primitive to a dataframe, appending the learner's
predictions as an additional column.

Hyperparameters:
* **estimator**:  The learner to invoke for stacking purposes.  Must be an instance of SupervisedLearnerPrimitiveBase.
    """

    def __init__(self, *, hyperparams: StackingOperatorHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)
        self._prim = hyperparams['estimator']
        self._fitted = False

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        self._inputs = inputs
        self._outputs = outputs
        self._prim.set_training_data(inputs = inputs, outputs = outputs)
        self._fitted = False

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        if not self._fitted:
            self._prim.fit(timeout = timeout, iterations = iterations)
            self._fitted = True
        return pi_base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        preds = self._prim.produce(inputs=inputs, timeout=timeout, iterations=iterations).value
        preds = preds.astype(float)
        output = inputs.copy()
        output = np.hstack((np.reshape(preds, (-1, 1)), output))
        return pi_base.CallResult(output)

    def get_params(self) -> StackingOperatorParams:
        return StackingOperatorParams({
            'fitted': self._fitted,
        })

    def set_params(self, *, params: StackingOperatorParams) -> None:
        self._fitted = params['fitted']

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '39082f18-4d35-4582-94a0-83ee22099adf',
        'version': config.VERSION,
        'name': 'Stacking Operator',
        'description': "Appends a second primitive's predictions to its input.",
        'python_path': 'd3m.primitives.data_transformation.stacking_operator.StackingOperator',
        'primitive_family': meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.ENSEMBLE_LEARNING
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'dataset', 'transformer' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'preconditions': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
