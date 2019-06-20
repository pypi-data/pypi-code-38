import typing

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.metadata import params as meta_params
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import unsupervised_learning as pi_unsupervised_learning

from sri.common import config
from sri.common import constants
from sri.common import util

Inputs = container.Dataset
Outputs = container.DataFrame

class MeanBaselineHyperparams(meta_hyperparams.Hyperparams):
    pass

class MeanBaselineParams(meta_params.Params):
    debug_options: typing.Dict
    target_name: str
    target_data_element: str
    categorical_prediction: bool
    prediction: str

class MeanBaseline(pi_unsupervised_learning.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, MeanBaselineParams, MeanBaselineHyperparams]):
    """
    A simple baseline that just predicts the mean/plurality.
    This is not meant to be used in production, just a way to get quick and reasonable answers for debugging.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: MeanBaselineHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._target_name = None
        self._target_data_element = None
        self._categorical_prediction = None
        self._prediction = None

        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        self._debug_options = _debug_options

        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def set_training_data(self, *, inputs: Inputs) -> None:
        labels, average, target_name, target_data_element = self._validate_training_input(inputs)
        self._target_name = target_name
        self._target_data_element = target_data_element
        self._prediction, self._categorical_prediction = self._process_data(labels, average)

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        return pi_base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        ids = self._validate_test_input(inputs)
        ids = [int(id) for id in ids]

        predictions = [self._prediction for id in ids]

        results = container.DataFrame(
            data = {constants.D3M_INDEX: ids, self._target_name: predictions},
            columns = [constants.D3M_INDEX, self._target_name],
            generate_metadata = True,
        )

        results = util.prep_predictions(results, ids, metadata_source = self, missing_value = self._prediction)

        self._logger.debug("Produce complete")

        return pi_base.CallResult(results)

    def get_params(self) -> MeanBaselineParams:
        return MeanBaselineParams({
            'debug_options': self._debug_options,
            'target_name': self._target_name,
            'target_data_element': self._target_data_element,
            'categorical_prediction': self._categorical_prediction,
            'prediction': str(self._prediction),
        })

    def set_params(self, *, params: MeanBaselineParams) -> None:
        self._set_debug_options(params['debug_options'])
        self._target_name = params['target_name']
        self._target_data_element = params['target_data_element']
        self._categorical_prediction = params['categorical_prediction']

        if (self._categorical_prediction):
            self._prediction = params['prediction']
        else:
            self._prediction = float(params['prediction'])

    def _validate_training_input(self, inputs: Inputs):
        target_data_element = None
        target_column = None
        average = False

        for data_element in inputs.keys():
            # Skip types without columns.
            if ('https://metadata.datadrivendiscovery.org/types/Graph' in inputs.metadata.query((data_element,))['semantic_types']):
                continue

            numCols = int(inputs.metadata.query((data_element, meta_base.ALL_ELEMENTS))['dimension']['length'])
            for i in range(numCols):
                column_info = inputs.metadata.query((data_element, meta_base.ALL_ELEMENTS, i))

                if ('https://metadata.datadrivendiscovery.org/types/TrueTarget' not in column_info['semantic_types']):
                    continue

                target_data_element = data_element
                target_column = column_info['name']
                average = ('http://schema.org/Float' in column_info['semantic_types'])
                break

            if (target_column is not None):
                break

        if (target_column is None):
            raise ValueError("Could not figure out target column.")

        labels = list(inputs[data_element][target_column])

        if (average):
            labels = [float(value) for value in labels]

        return labels, average, target_column, target_data_element

    # Just get the d3mIndexes
    def _validate_test_input(self, inputs: Inputs):
        return list(inputs[self._target_data_element]['d3mIndex'])

    def _process_data(self, labels, average):
        self._logger.debug("Processing data")

        predicted_value = None
        categorical_prediction = None

        if (average):
            predicted_value = self._calc_mean(labels)
            categorical_prediction = False
        else:
            predicted_value = self._calc_plurality(labels)
            categorical_prediction = True

        self._logger.debug("Data processing complete")

        return predicted_value, categorical_prediction

    def _calc_mean(self, labels):
        mean = 0.0
        for label in labels:
            mean += label
        mean /= len(labels)

        return mean

    def _calc_plurality(self, labels):
        counts = {}

        for label in labels:
            if (label not in counts):
                counts[label] = 0
            counts[label] += 1

        best_count = 0
        best_label = None

        for (label, count) in counts.items():
            if (count > best_count):
                best_count = count
                best_label = label

        return best_label

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '36d5472c-e0a4-4ed6-a1d0-2665feacff39',
        'version': config.VERSION,
        'name': 'Mean Baseline',
        'description': 'A baseline primitive that just predicate the mean/plurality. Not indented for production, only debugging.',
        'python_path': 'd3m.primitives.classification.gaussian_classification.MeanBaseline',
        'primitive_family': meta_base.PrimitiveFamily.CLASSIFICATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.COMPUTER_ALGEBRA,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'dataset'],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'preconditions': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
