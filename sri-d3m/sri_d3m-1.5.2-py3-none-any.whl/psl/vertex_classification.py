import math
import os
import typing

import pandas
from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.metadata import params as meta_params
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import unsupervised_learning as pi_unsupervised_learning
from sklearn.metrics.pairwise import cosine_similarity

from sri.common import config
from sri.common import constants
from sri.common import util
from sri.graph import vertex_classification as vertex_classification_parser
from sri.psl import hyperparams
from sri.psl import psl

Inputs = container.DataFrame  # The output from data_transformation.vertex_classification_parser.VertexClassificationParser.
Outputs = container.DataFrame  # Predictions

PSL_MODEL = 'vertex_classification'

LOCAL_SIM_FILENAME = 'local_sim_obs.txt'
LINK_FILENAME = 'link_obs.txt'
LABEL_OBS_FILENAME = 'label_obs.txt'
LABEL_TARGET_FILENAME = 'label_target.txt'

class VertexClassificationHyperparams(hyperparams.PSLHyperparams):
    pass

class VertexClassificationParams(meta_params.Params):
    debug_options: typing.Dict
    training_data: tuple

class VertexClassification(pi_unsupervised_learning.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, VertexClassificationParams, VertexClassificationHyperparams]):
    """
    Solve vertex classification with PSL.
    """

    def __init__(self, *, hyperparams: VertexClassificationHyperparams, random_seed: int = 0, _debug_options: typing.Dict = {}) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._set_debug_options(_debug_options)

        self._training_data = None

    def _set_debug_options(self, _debug_options):
        self._debug_options = _debug_options

        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def set_training_data(self, *, inputs: Inputs) -> None:
        self._training_data = self._validate_inputs(inputs)

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        return pi_base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        if (self._training_data is None):
            raise ValueError("produce() called before set_training_data().")

        training_nodelist, training_edgelist, training_labels = self._training_data
        test_nodelist, test_edgelist, test_labels = self._validate_inputs(inputs)

        out_dir = os.path.abspath(os.path.join(psl.PSL_TEMP_DIR, PSL_MODEL))
        os.makedirs(out_dir, exist_ok = True)

        labels_target = self._write_data(out_dir,
                training_nodelist, training_edgelist, training_labels,
                test_nodelist, test_edgelist, test_labels)

        psl_output = psl.run_model(
                PSL_MODEL,
                self.hyperparams,
                lazy = False,
                int_args = True,
                int_ids = True,
                data_path = out_dir
        )
        psl_output = psl_output['LABEL']

        output = self._build_output(labels_target, test_labels, psl_output)
        return pi_base.CallResult(output)

    # Predict the strongest label for each target.
    # Return: [[node, label], ...]
    def _build_output(self, labels_target, test_labels,  psl_output):
        # {id: (bestLabel, bestScore), ...}
        best_labels = {}

        columns = list(test_labels.columns)
        columns.remove(constants.D3M_INDEX)
        label_column = columns[0]

        d3m_indexes = list(test_labels[constants.D3M_INDEX])

        for (node, label) in labels_target:
            node = int(node)
            label = int(label)

            score = psl_output[(node, label)]

            if (node not in best_labels or score > best_labels[node][1]):
                best_labels[node] = (label, score)

        # We will probably predict more nodes than asked for.
        # Only return what was explicitly asked for.
        results = []

        for i in range(len(test_labels)):
            id = int(test_labels[constants.D3M_INDEX][i])
            results.append([id, best_labels[id][0]])

        frame = container.DataFrame(results, columns = [constants.D3M_INDEX, label_column], generate_metadata=True)
        return util.prep_predictions(frame, d3m_indexes, metadata_source = self, missing_value = 0)

    def _write_data(self, out_dir,
            training_nodelist, training_edgelist, training_labels,
            test_nodelist, test_edgelist, test_labels):
        links = self._normalize_links(training_edgelist, test_edgelist)
        local_sims = self._compute_local_sims(training_nodelist, test_nodelist)

        labels_obs, labels_target = self._normalize_labels(training_labels, test_labels)

        path = os.path.join(out_dir, LINK_FILENAME)
        util.write_tsv(path, links)

        path = os.path.join(out_dir, LOCAL_SIM_FILENAME)
        util.write_tsv(path, local_sims)

        path = os.path.join(out_dir, LABEL_OBS_FILENAME)
        util.write_tsv(path, labels_obs)

        path = os.path.join(out_dir, LABEL_TARGET_FILENAME)
        util.write_tsv(path, labels_target)

        return labels_target

    # Returns: [[node (d3mIndex), label], ...]
    # TODO(eriq): Using lazy here could possibly capture more connections (depending on the data).
    def _normalize_labels(self, training_labels, test_labels):
        labels_obs = []
        labels_target = []

        columns = list(training_labels.columns)
        columns.remove(constants.D3M_INDEX)
        label_column = columns[0]

        # Sometimes there are dup records in both training and test data.
        # For consistency when building output, we will consider these duplicates targets.
        target_ids = set(test_labels[constants.D3M_INDEX])

        seen_labels = set()

        for i in range(len(training_labels)):
            node = training_labels[constants.D3M_INDEX][i]
            label = training_labels[label_column][i]

            if (node not in target_ids):
                labels_obs.append([node, label])

            seen_labels.add(label)

        for i in range(len(test_labels)):
            node = test_labels[constants.D3M_INDEX][i]

            for potential_label in seen_labels:
                labels_target.append([node, potential_label])

        return labels_obs, labels_target

    # Retuns: [[id, id, sim], ...].
    # Compute the cosine similarity between all the nodes we have.
    def _compute_local_sims(self, training_nodelist, test_nodelist):
        sims = []

        nodelist = pandas.concat([training_nodelist, test_nodelist], ignore_index = True)
        nodelist = nodelist.drop_duplicates().reset_index(drop = True)

        # The first three columns are guarenteed, the rest are attributes.
        attribute_columns = list(nodelist.columns)[3:]
        attributes = nodelist[attribute_columns]

        if (len(attribute_columns) == 0):
            return sims

        raw_sims = cosine_similarity(attributes)

        for index1 in range(len(nodelist)):
            for index2 in range(index1 + 1, len(nodelist)):
                sim = (raw_sims[index1][index2] + 1.0) / 2.0
                sims.append([nodelist[constants.D3M_INDEX][index1], nodelist[constants.D3M_INDEX][index2], sim])
                sims.append([nodelist[constants.D3M_INDEX][index2], nodelist[constants.D3M_INDEX][index1], sim])

        return sims

    # Noramlize the edges (links) into [[source, dest, weight], ...].
    # Where weight in [0, 1].
    def _normalize_links(self, training_edgelist, test_edgelist):
        min_weight = None
        max_weight = None

        edgelist = pandas.concat([training_edgelist, test_edgelist], ignore_index = True)
        edgelist = edgelist.drop_duplicates().reset_index(drop = True)

        # [[source, dest, weight], ...]
        links = []

        # {(minId, maxId), ...}
        seen_links = set()

        for i in range(len(edgelist)):
            source = edgelist[vertex_classification_parser.OUTPUT_EDGELIST_COLUMN_SOURCE][i]
            dest = edgelist[vertex_classification_parser.OUTPUT_EDGELIST_COLUMN_DEST][i]
            weight = float(edgelist[vertex_classification_parser.OUTPUT_EDGELIST_COLUMN_WEIGHT][i])

            if (min_weight is None or weight < min_weight):
                min_weight = weight

            if (max_weight is None or weight > max_weight):
                max_weight = weight

            ids = tuple(sorted([source, dest]))
            if (ids in seen_links):
                continue
            seen_links.add(ids)

            links.append([source, dest, weight])
            links.append([dest, source, weight])

        # Normalize weights.
        for link in links:
            if (math.isclose(min_weight, max_weight)):
                link[2] = 1.0
            else:
                link[2] = (link[2] - min_weight) / (max_weight - min_weight)

        return links

    # Returns: [nodelist, edgelist, labels].
    def _validate_inputs(self, frame):
        if (len(frame) != 1):
            raise ValueError("Expected exactly one row, got %d." % (len(frame)))

        if (set(frame.columns) != set(vertex_classification_parser.OUTPUT_COLUMNS)):
            raise ValueError("Unexpected set of column names. Expected {%s}, got: {%s}." % (str(vertex_classification_parser.OUTPUT_COLUMNS), str(frame.columns)))

        nodelist = frame[vertex_classification_parser.OUTPUT_COLUMN_NODELIST][0]
        edgelist = frame[vertex_classification_parser.OUTPUT_COLUMN_EDGELIST][0]
        labels = frame[vertex_classification_parser.OUTPUT_COLUMN_LABELS][0]

        # The first three columns of the nodelist are guarenteed to be there.
        if (len(nodelist.columns) < 3):
            raise ValueError("Expecting at least three columns for the nodelist. Got: %s." % (str(nodelist.columns)))

        if (len(labels.columns) != 2):
            raise ValueError("Expecting exactly two columns for the labels, found %d." % (len(labels.columns)))

        if (constants.D3M_INDEX not in labels.columns):
            raise ValueError("Could not locate D3M index in labels. Found: %s" % (str(labels.columns)))

        return nodelist, edgelist, labels

    def get_params(self) -> VertexClassificationParams:
        return VertexClassificationParams({
            'debug_options': self._debug_options,
            'training_data': self._training_data,
        })

    def set_params(self, *, params: VertexClassificationParams) -> None:
        self._set_debug_options(params['debug_options'])
        self._training_data = params['training_data']

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': 'dca25a46-7a5f-48d9-ac9b-d14d4d671b0b',
        'version': config.VERSION,
        'name': 'Vertex Classification',
        'description': 'Solve vertex classification using PSL.',
        'python_path': 'd3m.primitives.classification.vertex_nomination.VertexClassification',
        'primitive_family': meta_base.PrimitiveFamily.VERTEX_CLASSIFICATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.MARKOV_RANDOM_FIELD,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'primitive', 'relational', 'general', 'collective classifiction', 'vertexClassification' ],
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
        ]
    })
