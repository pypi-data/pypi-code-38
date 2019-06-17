import heapq
import os
import typing

import numpy
import pandas
from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.metadata import params as meta_params
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import supervised_learning as pi_supervised_learning
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

from sri.common import config
from sri.common import constants
from sri.common import util
from sri.psl import hyperparams
from sri.psl import psl

Inputs = container.DataFrame
Outputs = container.DataFrame

PSL_MODEL = 'general_relational'
DEFAULT_CATEGORY = 0
# Don't bother trying to compute similarities if there
# are too many records.
SIM_BAIL_SIZE = 10e8

UNIFORM_PRIOR_FILENAME = 'uniform_prior_obs.txt'
LOCAL_SIMS_FILENAME = 'local_sim_obs.txt'
ID_FILENAME = 'id_obs.txt'
CATEGORY_FILENAME = 'category_obs.txt'

VALUE_OBS_FILENAME = 'value_obs.txt'
VALUE_TARGET_FILENAME = 'value_target.txt'

MODEL_SUB_LOCAL_SIM = '{local_similarity}'
MODEL_SUB_INVERSE_LOCAL_SIM = '{inverse_local_similarity}'
MODEL_SUB_FUNCTIONAL_CATS = '{functional_categories}'
MODEL_SUB_UNIFORM_PRIOR = '{uniform_prior}'
MODEL_SUB_NEGATIVE_PRIOR = '{negative_prior}'

# TODO(eriq): Check for categorical columns that are using ints (like binary).
# TODO(eriq): Figure out some sort of local classifier.
# TODO(eriq): Learn weights.

class GeneralRelationalHyperparams(hyperparams.PSLHyperparams):
    categorical = meta_hyperparams.UniformBool(
            description = 'True for classification problems. This will be inferred if the predictions are non-numeric',
            default = False,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    exclusive_categories = meta_hyperparams.UniformBool(
            description = 'True if this is classification problem where the labels are mutually exclusive.',
            default = True,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    min_similarity = meta_hyperparams.Uniform(
            description = 'The lower threshold for a similarity value. Anything below this will not be included.',
            default = 0.50,
            lower = 0.0,
            upper = 1.0,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/TuningParameter'])

    max_similarities_per_entity = meta_hyperparams.Bounded(
            description = 'The maximum number of similarities to include per entityr.',
            default = 5,
            lower = 0,
            upper = None,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/TuningParameter'])

    include_inverse_similarities = meta_hyperparams.UniformBool(
            description = 'True if inverse similarity rules are to be included in the model. These rules are more computationally complex and typically have limited impact.',
            default = False,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    include_target_similarities = meta_hyperparams.UniformBool(
            description = 'True if similarities between targets and other targets are to be computed. Otherwise, only similarities between targets and training samples will be computed.',
            default = False,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

class GeneralRelationalParams(meta_params.Params):
    debug_options: typing.Dict

    cat_to_id: typing.Dict
    id_to_cat: typing.Dict

    prediction_column: str
    categorical: bool

    mean_prediction: str
    min_prediction: float
    max_prediction: float

    uniform_prior: typing.Dict

    training_data: container.DataFrame

class GeneralRelational(pi_supervised_learning.SupervisedLearnerPrimitiveBase[Inputs, Outputs, GeneralRelationalParams, GeneralRelationalHyperparams]):
    """
    A primitive that attempts to build a generalized relational model using hyperparams to activate rule templates.
    """

    def __init__(self, *, hyperparams: GeneralRelationalHyperparams, random_seed: int = 0, _debug_options: typing.Dict = {}) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._set_debug_options(_debug_options)

        # A mapping of raw category names to an int id.
        # Using this, we can allow PSL to only use int ids.
        # The cat ids will only be translated to right before PSL.
        self._cat_to_id = None
        self._id_to_cat = None

        self._prediction_column = None
        self._categorical = None

        self._mean_prediction = None
        self._min_prediction = None
        self._max_prediction = None

        # Index by category.
        # Continuous problems (regression) will just have one category.
        self._uniform_prior = None

        self._training_data = None

    def _set_debug_options(self, _debug_options):
        self._debug_options = _debug_options

        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        # There should be two columns, and we don't want the d3m index.
        prediction_index = (1 + outputs.columns.get_loc(constants.D3M_INDEX)) % 2
        self._prediction_column = outputs.columns[prediction_index]

        self._compute_priors(inputs, outputs)

        train_data = inputs.merge(outputs, on = constants.D3M_INDEX, how = 'inner', suffixes = ('', '_output'))
        self._training_data = train_data

    def _compute_priors(self, inputs, outputs):
        self._categorical = self.hyperparams['categorical']

        self._uniform_prior = {}
        self._cat_to_id = {}
        self._id_to_cat = {}

        if (self._categorical):
            predictions = outputs[self._prediction_column]
        else:
            # TODO(eriq): We need to detect if a column is binary or otherwise
            # categorical using ints.
            try:
                predictions = pandas.to_numeric(outputs[self._prediction_column])
            except ValueError:
                predictions = outputs[self._prediction_column]
                self._categorical = True

        predictions = container.DataFrame(list(predictions), columns = [self._prediction_column], generate_metadata=True)

        if (self._categorical):
            best_count = None
            best_category = None

            counts = predictions.groupby([self._prediction_column]).size()

            for category in counts.index:
                cat_id = len(self._cat_to_id)
                self._cat_to_id[category] = cat_id
                self._id_to_cat[cat_id] = category

                value = counts[category] / float(len(predictions))
                self._uniform_prior[category] = value

                if (best_count is None or value > best_count):
                    best_count = value
                    best_category = category

            self._mean_prediction = best_category
        else:
            self._min_prediction = float(predictions.min())
            self._max_prediction = float(predictions.max())

            # average = float(predictions.mean())
            average = float(predictions.median())

            self._mean_prediction = average
            self._uniform_prior[DEFAULT_CATEGORY] = average

            self._cat_to_id[DEFAULT_CATEGORY] = DEFAULT_CATEGORY
            self._id_to_cat[DEFAULT_CATEGORY] = DEFAULT_CATEGORY

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        # Weight learning not yet supported.
        return pi_base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        targets = list(inputs[constants.D3M_INDEX])

        out_dir = os.path.abspath(os.path.join(psl.PSL_TEMP_DIR, PSL_MODEL))
        os.makedirs(out_dir, exist_ok = True)

        self._write_data(out_dir, targets, inputs)

        psl_output = self._run_psl(out_dir)
        output = self._build_output(targets, psl_output)

        return pi_base.CallResult(output)

    def _write_data(self, out_dir, targets, test_data):
        value_obs, value_target = self._compute_values(targets)

        local_sims = self._compute_local_sims(test_data)

        if (self._categorical):
            uniform_prior = [(self._cat_to_id[category], prior) for (category, prior) in self._uniform_prior.items()]
        else:
            uniform_prior = [(self._cat_to_id[category], self._normalize_value(prior)) for (category, prior) in self._uniform_prior.items()]

        # Scoping predicates.
        ids = [[id] for id in targets]
        categories = [[cat_id] for cat_id in self._id_to_cat.keys()]

        path = os.path.join(out_dir, UNIFORM_PRIOR_FILENAME)
        util.write_tsv(path, uniform_prior)

        path = os.path.join(out_dir, ID_FILENAME)
        util.write_tsv(path, ids)

        path = os.path.join(out_dir, CATEGORY_FILENAME)
        util.write_tsv(path, categories)

        path = os.path.join(out_dir, LOCAL_SIMS_FILENAME)
        util.write_tsv(path, local_sims)

        path = os.path.join(out_dir, VALUE_OBS_FILENAME)
        util.write_tsv(path, value_obs)

        path = os.path.join(out_dir, VALUE_TARGET_FILENAME)
        util.write_tsv(path, value_target)

    def _compute_values(self, targets):
        value_obs = []
        value_target = []

        # TODO(eriq): This does not work with non-exclusive targets.

        for (index, row) in self._training_data[[constants.D3M_INDEX, self._prediction_column]].iterrows():
            if (self._categorical):
                value_obs.append((row[0], self._cat_to_id[row[1]], 1.0))
            else:
                value_obs.append((row[0], self._cat_to_id[DEFAULT_CATEGORY], self._normalize_value(row[1])))

        for category in self._uniform_prior:
            for id in targets:
                value_target.append((id, self._cat_to_id[category]))

        return value_obs, value_target

    def _compute_local_sims(self, test_data):
        sims = []

        if (self.hyperparams['max_similarities_per_entity'] == 0):
            return sims

        # Bail if there are too many similaries to compute.
        train_size = len(self._training_data)
        test_size = len(test_data)
        if (train_size * test_size >= SIM_BAIL_SIZE or
                (self.hyperparams['include_target_similarities'] and train_size * (test_size + train_size) >= SIM_BAIL_SIZE)):
            return sims

        # Bail if there are no test or train records.
        if (train_size == 0 or test_size == 0):
            return sims

        train_data, train_ids = self._prep_numeric_columns(self._training_data)
        test_data, test_ids = self._prep_numeric_columns(test_data)

        # Bail out if there are no numeric columns.
        if (len(test_data.columns) == 0 or len(train_data.columns)):
            return sims

        if (self.hyperparams['include_target_similarities']):
            train_data = pandas.concat([train_data, test_data], copy = False)
            train_ids = train_ids + test_ids

        raw_sims = cosine_similarity(test_data, train_data)

        # {test_id: heapq((sim, train_id)), ...}
        sorted_sims = {}
        for test_id in test_ids:
            sorted_sims[test_id] = []

        for test_index in range(len(test_ids)):
            test_id = test_ids[test_index]

            for train_index in range(len(train_ids)):
                train_id = train_ids[train_index]
                sim = raw_sims[test_index, train_index]

                if (sim < self.hyperparams['min_similarity']):
                    continue

                heap = sorted_sims[test_id]

                # If this sim is smaller than the smallest value in the heap,
                # don't even bother adding it.
                if (len(heap) > 0 and sim < heap[0][0]):
                    continue

                heapq.heappush(heap, (sim, train_id))
                if (len(heap) > self.hyperparams['max_similarities_per_entity']):
                    heapq.heappop(heap)

        # Now iterate throught the similarity heaps and add the values.
        for (test_id, heap) in sorted_sims.items():
            for (sim, train_id) in heap:
                sims.append([test_id, train_id, sim])

        return sims

    def _run_psl(self, out_dir):
        # Just pass comments for rules that we do not want.
        model_subs = {
            MODEL_SUB_LOCAL_SIM: '',
            MODEL_SUB_INVERSE_LOCAL_SIM: '# ',
            MODEL_SUB_FUNCTIONAL_CATS: '# ',
            MODEL_SUB_UNIFORM_PRIOR: '',
            MODEL_SUB_NEGATIVE_PRIOR: '',
        }

        if (self._categorical and self.hyperparams['exclusive_categories']):
            model_subs[MODEL_SUB_FUNCTIONAL_CATS] = ''

        if (self.hyperparams['include_inverse_similarities']):
            model_subs[MODEL_SUB_FUNCTIONAL_CATS] = ''

        psl_output = psl.run_model(
                PSL_MODEL,
                self.hyperparams,
                lazy = False,
                int_ids = True,
                model_template_subs = model_subs,
                data_path = out_dir,
        )

        # We only care about the Value predicate.
        psl_output = psl_output['VALUE']

        return psl_output

    def _build_output(self, d3m_indexes, psl_output):
        # Build up the result.
        output = []

        for d3m_index in d3m_indexes:
            prediction = None

            if (self._categorical):
                # TODO(eriq): Handle non-exclusive categories.

                prediction = self._mean_prediction
                best_score = None

                for category in self._uniform_prior:
                    cat_id = self._cat_to_id[category]

                    if ((d3m_index, cat_id) in psl_output):
                        category = self._id_to_cat[cat_id]
                        score = psl_output[(d3m_index, cat_id)]

                        if (best_score is None or score > best_score):
                            best_score = score
                            prediction = category
            else:
                prediction = self._mean_prediction
                if ((d3m_index, DEFAULT_CATEGORY) in psl_output):
                    prediction = psl_output[(d3m_index, DEFAULT_CATEGORY)]

                prediction = self._denormalize_value(prediction)

            output.append([int(d3m_index), prediction])

        frame = container.DataFrame(output, columns = [constants.D3M_INDEX, self._prediction_column], generate_metadata=True)
        return util.prep_predictions(frame, d3m_indexes, metadata_source = self, missing_value = self._mean_prediction)

    def _normalize_value(self, value):
        return (float(value) - self._min_prediction) / (self._max_prediction - self._min_prediction)

    def _denormalize_value(self, value):
        return float(value) * (self._max_prediction - self._min_prediction) + self._min_prediction

    def _prep_numeric_columns(self, data):
        '''
        Get a frame that only has numeric columns
        (and the D3M ids associated with the numeric data).
        '''

        # Drop any target columns.
        data = data.drop(columns = [self._prediction_column], errors = 'ignore')

        # Pull out just the numeric columns.
        data = data.apply(pandas.to_numeric, errors = 'ignore')
        data = data.select_dtypes(include = [numpy.number])

        # Pull out the ids
        ids = list(data[constants.D3M_INDEX])
        data = data.drop(columns = [constants.D3M_INDEX])

        # Bail out if there are no numeric columns.
        if (len(data.columns) == 0):
            return data, ids

        # Remove NaNs and normalize.
        data = data.fillna(0)
        data = data.astype('float64')
        data.loc[:,:] = MinMaxScaler().fit_transform(data)

        return data, ids

    def get_params(self) -> GeneralRelationalParams:
        min_prediction = self._min_prediction
        if (min_prediction is None):
            min_prediction = 0

        max_prediction = self._max_prediction
        if (max_prediction is None):
            max_prediction = 0

        return GeneralRelationalParams({
            'debug_options': self._debug_options,
            'cat_to_id': self._cat_to_id,
            'id_to_cat': self._id_to_cat,
            'prediction_column': self._prediction_column,
            'categorical': self._categorical,
            'mean_prediction': str(self._mean_prediction),
            'min_prediction': min_prediction,
            'max_prediction': max_prediction,
            'uniform_prior': self._uniform_prior,
            'training_data': self._training_data,
        })

    def set_params(self, *, params: GeneralRelationalParams) -> None:
        self._set_debug_options(params['debug_options'])

        self._cat_to_id = params['cat_to_id']
        self._id_to_cat = params['id_to_cat']
        self._prediction_column = params['prediction_column']
        self._categorical = params['categorical']
        self._min_prediction = params['min_prediction']
        self._max_prediction = params['max_prediction']
        self._uniform_prior = params['uniform_prior']
        self._training_data = params['training_data']

        if (self._categorical):
            self._mean_prediction = params['mean_prediction']
        else:
            self._mean_prediction = float(params['mean_prediction'])

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '03b1288c-d4f5-4fa8-9a49-32e82c5efaf2',
        'version': config.VERSION,
        'name': 'General Relational',
        'description': 'Builds generalized relationsl models that utilize templates activated by hyperparams.',
        'python_path': 'd3m.primitives.classification.general_relational_dataset.GeneralRelational',
        'primitive_family': meta_base.PrimitiveFamily.CLASSIFICATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.MARKOV_RANDOM_FIELD,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'primitive', 'relational', 'general', 'collective classifiction'],
        'installation': [
            config.INSTALLATION,
            config.INSTALLATION_JAVA,
            # TODO: revert (Issue 139)
            # config.INSTALLATION_POSTGRES
        ],
        'location_uris': [],
        'preconditions': [ meta_base.PrimitiveEffect.NO_NESTED_VALUES ],
        'effects': [
            meta_base.PrimitiveEffect.NO_MISSING_VALUES,
            meta_base.PrimitiveEffect.NO_NESTED_VALUES
        ],
        'hyperparms_to_tune': [
            'categorical',
            'exclusive_categories',
            'min_similarity',
            'max_similarities_per_entity',
            'include_inverse_similarities',
        ]
    })
