import numpy as np
import pandas as pd
from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import transformer as pi_transformer
from sklearn.utils import check_array

from sri.common import config

Inputs = container.DataFrame
Outputs = container.DataFrame

class ZeroCountHyperparams(meta_hyperparams.Hyperparams):
    pass

class ZeroCount(pi_transformer.TransformerPrimitiveBase[Inputs, Outputs, ZeroCountHyperparams]):
    """
    ZeroCount appends two integer columns to the input dataframe, one containing the count
    of zero columns in each row, the other containing the count of non-zero columns.

    This simple transformer takes no hyperparameters.
    """

    def produce_old(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        X = inputs.values
        X = check_array(X)
        n_features = X.shape[1]

        X_transformed = np.copy(X)

        non_zero_vector = np.count_nonzero(X_transformed, axis=1)
        non_zero = np.reshape(non_zero_vector, (-1, 1))
        zero_col = np.reshape(n_features - non_zero_vector, (-1, 1))

        X_transformed = np.hstack((non_zero, X_transformed))
        X_transformed = np.hstack((zero_col, X_transformed))

        return pi_base.CallResult(container.DataFrame(X_transformed, generate_metadata=True))

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        n_features = inputs.shape[1]
        X_transformed = inputs.copy()

        non_zero_vector = X_transformed.astype(bool).sum(axis=1)
        zero_vector = n_features - non_zero_vector
        X_transformed = pd.concat([X_transformed, non_zero_vector, zero_vector], axis=1, ignore_index=True)

        return pi_base.CallResult(container.DataFrame(X_transformed, generate_metadata=True))


    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '4ae75c66-e8d1-41ec-9d6e-5074e081fbe6',
        'version': config.VERSION,
        'name': 'Zero Count',
        'description': 'Adds features indicating number of zeroes and non-zeroes in row',
        'python_path': 'd3m.primitives.data_transformation.zero_count.ZeroCount',
        'primitive_family': meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.COMPUTER_ALGEBRA,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'dataset', 'transformer'],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'preconditions': [ meta_base.PrimitiveEffect.NO_NESTED_VALUES ],
        'effects': [ meta_base.PrimitiveEffect.NO_NESTED_VALUES ],
        'hyperparms_to_tune': []
    })
