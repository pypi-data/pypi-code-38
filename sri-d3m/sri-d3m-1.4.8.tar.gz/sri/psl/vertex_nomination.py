import math
import os
import typing

import networkx
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
from sri.graph import vertex_nomination as vertex_nomination_parser
from sri.psl import hyperparams
from sri.psl import psl

Inputs = container.DataFrame  # A single graph
Outputs = container.DataFrame  # Predictions

PSL_MODEL = 'vertex_nomination'

LOCAL_SIM_FILENAME = 'local_sim_obs.txt'
LINK_FILENAME = 'link_obs.txt'
LABEL_OBS_FILENAME = 'label_obs.txt'
LABEL_TARGET_FILENAME = 'label_target.txt'

class VertexNominationHyperparams(hyperparams.PSLHyperparams):
    pass

class VertexNominationParams(meta_params.Params):
    debug_options: typing.Dict
    training_graph: networkx.Graph

class VertexNomination(pi_unsupervised_learning.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, VertexNominationParams, VertexNominationHyperparams]):
    """
    Solve vertex nomination with PSL.
    """

    def __init__(self, *, hyperparams: VertexNominationHyperparams, random_seed: int = 0, _debug_options: typing.Dict = {}) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._set_debug_options(_debug_options)

        self._training_graph = None

    def _set_debug_options(self, _debug_options):
        self._debug_options = _debug_options

        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def set_training_data(self, *, inputs: Inputs) -> None:
        self._training_graph, _ = self._validate_inputs(inputs)

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        return pi_base.CallResult(None)

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        if (self._training_graph is None):
            raise ValueError("produce() called before set_training_data().")

        graph, d3m_indexes = self._validate_inputs(inputs)

#        out_dir = os.path.abspath(os.path.join(self.hyperparams['psl_temp_dir'], PSL_MODEL))
        out_dir = os.path.abspath(os.path.join(psl.PSL_TEMP_DIR, PSL_MODEL))
        os.makedirs(out_dir, exist_ok = True)

        labels_target = self._write_data(graph, out_dir)

        psl_output = psl.run_model(
                PSL_MODEL,
                self.hyperparams,
                lazy = False,
                int_args = True,
                int_ids = True,
                data_path = out_dir
        )
        psl_output = psl_output['LABEL']

        output = self._build_output(labels_target, graph, psl_output, d3m_indexes)

        return pi_base.CallResult(output)

    # Predict the strongest label for each target.
    def _build_output(self, labels_target, graph, psl_output, d3m_indexes):
        # {id: (bestLabel, bestScore), ...}
        best_labels = {}

        for (node, label) in labels_target:
            node = int(node)
            label = int(label)

            score = psl_output[(node, label)]

            if (node not in best_labels or score > best_labels[node][1]):
                best_labels[node] = (label, score)

        results = []
        for (node, (best_label, best_score)) in best_labels.items():
            # We may predict more nodes than actually asked for.
            # These can be identified by their lack of d3m index.
            if (constants.D3M_INDEX in graph.node[node]):
                d3m_index = graph.node[node][constants.D3M_INDEX]
                results.append([int(d3m_index), best_label])

        frame = container.DataFrame(results, columns = [constants.D3M_INDEX, vertex_nomination_parser.COLUMN_LABEL], generate_metadata=True)
        return util.prep_predictions(frame, d3m_indexes, metadata_source = self, missing_value = 0)

    def _write_data(self, graph, out_dir):
        links = self._get_links(self._training_graph)
        local_sims = self._get_local_sims(self._training_graph)
        labels_obs, labels_target = self._get_labels(self._training_graph)

        path = os.path.join(out_dir, LINK_FILENAME)
        util.write_tsv(path, links)

        path = os.path.join(out_dir, LOCAL_SIM_FILENAME)
        util.write_tsv(path, local_sims)

        path = os.path.join(out_dir, LABEL_OBS_FILENAME)
        util.write_tsv(path, labels_obs)

        path = os.path.join(out_dir, LABEL_TARGET_FILENAME)
        util.write_tsv(path, labels_target)

        # Pass back the targets so we can easily build predictions
        return labels_target

    def _get_labels(self, graph):
        all_labels = set()
        for (node, data) in graph.nodes(data = True):
            if (vertex_nomination_parser.COLUMN_LABEL in data):
                all_labels.add(data[vertex_nomination_parser.COLUMN_LABEL])

        labels_obs = []
        labels_target = []

        for (node, data) in graph.nodes(data = True):
            if (vertex_nomination_parser.COLUMN_LABEL in data):
                labels_obs.append([node, data[vertex_nomination_parser.COLUMN_LABEL]])
            else:
                for label in all_labels:
                    labels_target.append([node, label])

        return labels_obs, labels_target

    def _get_local_sims(self, graph):
        sims = []

        skip_attributes = {'id', 'label', vertex_nomination_parser.COLUMN_LABEL, vertex_nomination_parser.GRAPH_NODE_ID_ATTRIBUTE, vertex_nomination_parser.NODE_ID, constants.D3M_INDEX}
        sim_attributes = []

        for (node, data) in graph.nodes(data = True):
            sim_attributes = list(set(data.keys()).difference(skip_attributes))
            break

        if (len(sim_attributes) == 0):
            return sims

        ids = []
        attributes = []

        for (node, data) in graph.nodes(data = True):
            has_all_attributes = True
            for attribute in sim_attributes:
                if (attribute not in data):
                    has_all_attributes = False
                    break

            if (not has_all_attributes):
                continue

            ids.append(node)
            attributes.append([data[key] for key in sim_attributes])

        raw_sims = cosine_similarity(attributes)

        for index1 in range(len(ids)):
            for index2 in range(index1 + 1, len(ids)):
                sim = (raw_sims[index1][index2] + 1.0) / 2.0
                sims.append([ids[index1], ids[index2], sim])
                sims.append([ids[index2], ids[index1], sim])

        return sims

    def _get_links(self, graph):
        min_weight = None
        max_weight = None

        # [[source, dest, weight], ...]
        links = []

        for (source, dest, data) in graph.edges(data = True):
            weight = 1.0
            if ('weight' in data):
                weight = float(data['weight'])

            if (min_weight is None or weight < min_weight):
                min_weight = weight

            if (max_weight is None or weight > max_weight):
                max_weight = weight

            links.append([source, dest, weight])
            links.append([dest, source, weight])

        # Normalize weights.
        for link in links:
            if (math.isclose(min_weight, max_weight)):
                link[2] = 1.0
            else:
                link[2] = (link[2] - min_weight) / (max_weight - min_weight)

        return links

    def _validate_inputs(self, frame):
        if (len(frame) != 1):
            raise ValueError("Expected exactly one row, got %d." % (len(frame)))

        if (vertex_nomination_parser.OUTPUT_COLUMN_GRAPH not in frame.columns):
            raise ValueError("Cannot find column for graph. Expecting '%s'," % (vertex_nomination_parser.OUTPUT_COLUMN_GRAPH))

        graph = frame[vertex_nomination_parser.OUTPUT_COLUMN_GRAPH][0]
        if (not isinstance(graph, networkx.Graph)):
            raise ValueError("Expected a graph, found %s" % (type(graph)))

        if (vertex_nomination_parser.OUTPUT_COLUMN_D3M_INDEXES not in frame.columns):
            raise ValueError("Cannot find column for d3m indexes. Expecting '%s'," % (vertex_nomination_parser.OUTPUT_COLUMN_D3M_INDEXES))

        d3m_indexes = frame[vertex_nomination_parser.OUTPUT_COLUMN_D3M_INDEXES][0]
        d3m_indexes = list(d3m_indexes[constants.D3M_INDEX])

        return graph, d3m_indexes

    def get_params(self) -> VertexNominationParams:
        return VertexNominationParams({
            'debug_options': self._debug_options,
            'training_graph': self._training_graph,
        })

    def set_params(self, *, params: VertexNominationParams) -> None:
        self._set_debug_options(params['debug_options'])
        self._training_graph = params['training_graph']

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': 'dca25a46-7a5f-48d9-ac9b-d14d4d671b0b',
        'version': config.VERSION,
        'name': 'Vertex Nomination',
        'description': 'Solve vertex nomination using PSL.',
        'python_path': 'd3m.primitives.classification.vertex_nomination.VertexNomination',
        'primitive_family': meta_base.PrimitiveFamily.CLASSIFICATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.MARKOV_RANDOM_FIELD,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'primitive', 'relational', 'general', 'collective classifiction', 'vertexNomination' ],
        'installation': [
            config.INSTALLATION,
            config.INSTALLATION_JAVA,
#           Todo: revert (Issue 139)
#            config.INSTALLATION_POSTGRES
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
