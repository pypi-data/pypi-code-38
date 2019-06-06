import os
import typing

import pandas
from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.metadata import params as meta_params
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import supervised_learning as pi_supervised_learning

from sri.common import config
from sri.common import constants
from sri.common import util
from sri.psl import hyperparams
from sri.psl import psl

Inputs = container.DataFrame
Outputs = container.DataFrame

PSL_MODEL = 'relational_timeseries'

NEXT_TIME_FILENAME = 'next_time_obs.txt'
NEXT_PERIOD_FILENAME = 'next_period_obs.txt'
PRIOR_FILENAME = 'prior_obs.txt'

VALUE_OBS_FILENAME = 'value_obs.txt'
VALUE_TARGET_FILENAME = 'value_target.txt'

# TODO(eriq): Right now we only support a single period, but often timeseries show multiple.
# TODO(eriq): Learn weights.

class RelationalTimeseriesHyperparams(hyperparams.PSLHyperparams):
    period = meta_hyperparams.Hyperparameter[int](
            default = 7,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    time_indicator_column = meta_hyperparams.Hyperparameter[str](
            default = 'time',
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

class RelationalTimeseriesParams(meta_params.Params):
    debug_options: typing.Dict
    prediction_column: str
    mean_prediction: float
    min_prediction: float
    max_prediction: float
    training_data: container.DataFrame
    time_indicator_column: str

class RelationalTimeseries(pi_supervised_learning.SupervisedLearnerPrimitiveBase[Inputs, Outputs, RelationalTimeseriesParams, RelationalTimeseriesHyperparams]):
    """
    A primitive that looks at a timeseries as a Markov model.
    """

    def __init__(self, *, hyperparams: RelationalTimeseriesHyperparams, random_seed: int = 0, _debug_options: typing.Dict = {}) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._set_debug_options(_debug_options)

        self._prediction_column = None
        self._mean_prediction = None
        self._min_prediction = None
        self._max_prediction = None
        self._training_data = None
        self._time_indicator_column = None

    def _set_debug_options(self, _debug_options):
        self._debug_options = _debug_options

        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        # 56_sunspots is irregular.
        outputs = outputs.drop(columns = ['sunspot.month'], errors = 'ignore')

        # There should be two columns, and we don't want the d3m index.
        prediction_index = (1 + outputs.columns.get_loc(constants.D3M_INDEX)) % 2
        self._prediction_column = outputs.columns[prediction_index]

        predictions = pandas.to_numeric(outputs[self._prediction_column])

        # self._mean_prediction = float(predictions.mean())
        self._mean_prediction = float(predictions.median())

        self._min_prediction = float(predictions.min())
        self._max_prediction = float(predictions.max())

        # Check for the time indicator column.
        self._time_indicator_column = self.hyperparams['time_indicator_column']
        if (self.hyperparams['time_indicator_column'] not in inputs.columns):
            # Fallback to the d3m index.
            if (constants.D3M_INDEX not in inputs.columns):
                raise ValueError("Could not find a sutible time indicator column among: %s." % (inputs.columns))
            self._time_indicator_column = constants.D3M_INDEX

        train_data = inputs.merge(outputs, on = constants.D3M_INDEX, how = 'inner', suffixes = ('', '_output'))
        self._training_data = train_data[[self._time_indicator_column, self._prediction_column]]

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        # Weight learning not yet supported.
        return pi_base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        # First select out only the data we need.
        inputs = inputs[[constants.D3M_INDEX, self._time_indicator_column]]

#        out_dir = os.path.abspath(os.path.join(self.hyperparams['psl_temp_dir'], PSL_MODEL))
        out_dir = os.path.abspath(os.path.join(psl.PSL_TEMP_DIR, PSL_MODEL))
        os.makedirs(out_dir, exist_ok = True)

        self._write_data(inputs, out_dir)
        psl_output = self._run_psl(out_dir)
        output = self._build_output(inputs, psl_output)

        return pi_base.CallResult(output)

    def _write_data(self, targets, out_dir):
        time_col = self._time_indicator_column

        times = set(pandas.to_numeric(self._training_data[time_col]))
        times |= set(pandas.to_numeric(targets[time_col].iloc[:,0]))
        times = sorted(list(times))

        next_times = [(time, time + 1) for time in times]
        next_period = [(time, time + self.hyperparams['period']) for time in times]
        prior = [(0, self._normalize_value(self._mean_prediction))]

        value_obs = []
        for (index, row) in self._training_data.iterrows():
            value_obs.append((row[time_col], self._normalize_value(row[self._prediction_column])))

        value_target = [(row[time_col],) for (index, row) in targets.iterrows()]
        
        path = os.path.join(out_dir, NEXT_TIME_FILENAME)
        util.write_tsv(path, next_times)
        
        path = os.path.join(out_dir, NEXT_PERIOD_FILENAME)
        util.write_tsv(path, next_period)
        
        path = os.path.join(out_dir, PRIOR_FILENAME)
        util.write_tsv(path, prior)
        
        path = os.path.join(out_dir, VALUE_OBS_FILENAME)
        util.write_tsv(path, value_obs)

        path = os.path.join(out_dir, VALUE_TARGET_FILENAME)
        util.write_tsv(path, value_target)

    def _normalize_value(self, value):
        return (float(value) - self._min_prediction) / (self._max_prediction - self._min_prediction)

    def _denormalize_value(self, value):
        return float(value) * (self._max_prediction - self._min_prediction) + self._min_prediction

    def _run_psl(self, out_dir):
        psl_output = psl.run_model(
                PSL_MODEL,
                self.hyperparams,
                lazy = True,
                data_path = out_dir,
        )

        # We only care about the Value predicate.
        psl_output = psl_output['VALUE']

        for args in psl_output:
            psl_output[args] = self._denormalize_value(psl_output[args])

        return psl_output

    def _build_output(self, inputs, psl_output):
        d3m_indexes = list(inputs[constants.D3M_INDEX])

        # Build up the result.
        output = []

        for (index, row) in inputs.iterrows():
            d3mIndex = row[constants.D3M_INDEX]
            # TODO(eriq): This may not always be safe.
            time = int(row[self._time_indicator_column])

            prediction = self._mean_prediction
            if ((time,) in psl_output):
                prediction = psl_output[(time,)]

            output.append([int(d3mIndex), prediction])

        frame = container.DataFrame(output, columns = [constants.D3M_INDEX, self._prediction_column], generate_metadata=True)
        return util.prep_predictions(frame, d3m_indexes, metadata_source = self, missing_value = self._mean_prediction)

    def get_params(self) -> RelationalTimeseriesParams:
        return RelationalTimeseriesParams({
            'debug_options': self._debug_options,
            'prediction_column': self._prediction_column,
            'mean_prediction': self._mean_prediction,
            'min_prediction': self._min_prediction,
            'max_prediction': self._max_prediction,
            'training_data': self._training_data,
            'time_indicator_column': self._time_indicator_column,
        })

    def set_params(self, *, params: RelationalTimeseriesParams) -> None:
        self._set_debug_options(params['debug_options'])
        self._prediction_column = params['prediction_column']
        self._mean_prediction = params['mean_prediction']
        self._min_prediction = params['min_prediction']
        self._max_prediction = params['max_prediction']
        self._training_data = params['training_data']
        self._time_indicator_column = params['time_indicator_column']

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '03b1288c-d4f5-4fa8-9a49-32e82c5efaf2',
        'version': config.VERSION,
        'name': 'Relational Timeseries',
        'description': 'Perform collective timeseries prediction.',
        'python_path': 'd3m.primitives.time_series_forecasting.time_series_to_list.RelationalTimeseries',
        'primitive_family': meta_base.PrimitiveFamily.TIME_SERIES_FORECASTING,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.MARKOV_RANDOM_FIELD,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'primitive', 'relational', 'timeseries', 'collective classifiction', 'timeSeriesForecasting' ],
        'installation': [
            config.INSTALLATION,
            config.INSTALLATION_JAVA,
#           Todo: revert (Issue 139)
#            config.INSTALLATION_POSTGRES
        ],
        'location_uris': [],
        'preconditions': [ meta_base.PrimitiveEffect.NO_NESTED_VALUES ],
        'effects': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES, meta_base.PrimitiveEffect.NO_NESTED_VALUES ],
        'hyperparms_to_tune': ['period']
    })
