import os
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
from sri.graph.networkx import Graph
from sri.psl import hyperparams
from sri.psl import psl

# We can take just the annotated graph.
Inputs = container.List
Outputs = container.DataFrame

# TODO(eriq): Include all edges in targets? (param)
# TODO(eriq): Use the training data for weight learning?

PSL_MODEL = 'link_prediction'

class LinkPredictionHyperparams(hyperparams.PSLHyperparams):
    truth_threshold = meta_hyperparams.Hyperparameter[float](
            default = 0.50,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
    )

    prediction_column = meta_hyperparams.Hyperparameter[str](
            default = 'link',
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'],
            description = 'The name of the column for the predictions made.',
    )

class LinkPredictionParams(meta_params.Params):
    debug_options: typing.Dict

class LinkPrediction(pi_unsupervised_learning.UnsupervisedLearnerPrimitiveBase[Inputs, Outputs, LinkPredictionParams, LinkPredictionHyperparams]):
    """
    A primitive that performs link prediction on an annotated graph.

    Note: this is unsupervised because we take the dataset itself and set_training_data() does not want an output argument.
    """

    def __init__(self, *, hyperparams: LinkPredictionHyperparams, random_seed: int = 0, _debug_options: typing.Dict = {}) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._training_data = None

        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        self._debug_options = _debug_options

        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        # Unsupervised learners get produce called for both the train and target data.
        # We already stored the train data, so skip the produce call with it.
        if (self._training_data == inputs):
            return pi_base.CallResult(self._build_fit_predictions(inputs[0]))

        self._logger.debug("Starting produce")

        annotatedGraph = self._validateInputs(inputs)
        result = self._link_prediction(annotatedGraph)

        return pi_base.CallResult(result)

    def _link_prediction(self, graph):
#        out_dir = os.path.abspath(os.path.join(self.hyperparams['psl_temp_dir'], PSL_MODEL))
        out_dir = os.path.abspath(os.path.join(psl.PSL_TEMP_DIR, PSL_MODEL))
        os.makedirs(out_dir, exist_ok = True)

        self._write_psl_data(graph, out_dir)
        pslOutput = psl.run_model(
                PSL_MODEL,
                self.hyperparams,
                int_args = True,
                data_path = out_dir,
        )

        return self._build_output_predictions(pslOutput[constants.LINK_PREDICATE], graph)

    def _validateInputs(self, inputs: Inputs):
        if (len(inputs) != 1):
            raise ValueError("Not exactly one input, found %d." % (len(inputs)))

        graph = inputs[0]

        if (not isinstance(graph, Graph)):
            raise ValueError("Expecting a graph, found a %s" % (type(graph).__name__))

        return graph

    def set_training_data(self, *, inputs: Inputs) -> None:
        # Weight learning not yet supported.
        self._training_data = inputs

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        # Weight learning not yet supported.
        return pi_base.CallResult(None)

    def get_params(self) -> LinkPredictionParams:
        return LinkPredictionParams({
            'debug_options': self._debug_options
        })

    def set_params(self, *, params: LinkPredictionParams) -> None:
        self._set_debug_options(params['debug_options'])

    # PSL specific functionality.

    def _write_psl_data(self, graph, base_path, include_all_edges = False):
        """
        Decompose the graph into data for a PSL link prediction model.
        Every unobserved link (where a link exists, but has the property: 'observed': False) is a target.
        """
        self._logger.debug("Writing PSL data into '%s'", base_path)

        self._write_predicate_graph(graph, os.path.join(base_path, constants.GRAPH1_PREDICATE_FILENAME), constants.NODE_MODIFIER_SOURCE)
        self._write_predicate_graph(graph, os.path.join(base_path, constants.GRAPH2_PREDICATE_FILENAME), constants.NODE_MODIFIER_TARGET)
        self._write_predicate_edge(graph, os.path.join(base_path, constants.EDGE1_PREDICATE_FILENAME), constants.NODE_MODIFIER_SOURCE)
        self._write_predicate_edge(graph, os.path.join(base_path, constants.EDGE2_PREDICATE_FILENAME), constants.NODE_MODIFIER_TARGET)
        self._write_predicate_link_prior(graph, os.path.join(base_path, constants.LINK_PRIOR_PREDICATE_FILENAME))
        self._write_predicate_link_observed(graph, os.path.join(base_path, constants.LINK_PREDICATE_OBS_FILENAME))

        if (include_all_edges):
            self._write_predicate_link_target_all(graph, os.path.join(base_path, constants.LINK_PREDICATE_TARGET_FILENAME))
        else:
            self._write_predicate_link_target(graph, os.path.join(base_path, constants.LINK_PREDICATE_TARGET_FILENAME))

        self._write_predicate_block(graph, os.path.join(base_path, constants.BLOCK_PREDICATE_FILENAME))

    # predicate_values should be {[atom arg, ...]: link value, ...}
    def _build_output_predictions(self, predicate_values, in_graph):
        d3m_indexes = []
        predictions = []
        confidences = []

        for link in predicate_values:
            if (len(link) != 2):
                raise ValueError("Expecting links of length 2, got %s: (%s)." % (len(link), link))

            # TODO(eriq): Double check int/string consistency
            # source_id, target_id = str(link[0]), str(link[1])
            source_id, target_id = link[0], link[1]

            edge = in_graph[source_id][target_id]

            # We only care about prediction edges.
            if (constants.TARGET_KEY not in edge or not edge[constants.TARGET_KEY]):
                continue

            d3m_indexes.append(int(edge[constants.D3M_INDEX]))
            confidences.append(predicate_values[link])

            if (predicate_values[link] >= self.hyperparams['truth_threshold']):
                predictions.append(1)
            else:
                predictions.append(0)

        frame = container.DataFrame(
                columns = [constants.D3M_INDEX, self.hyperparams['prediction_column'], constants.CONFIDENCE_COLUMN],
                data = {constants.D3M_INDEX: d3m_indexes, self.hyperparams['prediction_column']: predictions, constants.CONFIDENCE_COLUMN: confidences},
                generate_metadata = True
        )

        # We have lost all ordering information on the d3m indexes, so just sort them naturally.
        return util.prep_predictions(frame, sorted(d3m_indexes), metadata_source = self, missing_value = 0)

    # Build up some fake predictions for the produce() called during fitting.
    def _build_fit_predictions(self, graph):
        d3m_indexes = []
        predictions = []
        confidences = []

        for (source, dest, data) in graph.edges(data = True):
            # We only care about observed links.
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_LINK or not data[constants.OBSERVED_KEY]):
                continue

            d3m_indexes.append(len(d3m_indexes))
            confidences.append(1.0)
            predictions.append(int(data[constants.WEIGHT_KEY]))

        frame = container.DataFrame(
                columns = [constants.D3M_INDEX, self.hyperparams['prediction_column'], constants.CONFIDENCE_COLUMN],
                data = {constants.D3M_INDEX: d3m_indexes, self.hyperparams['prediction_column']: predictions, constants.CONFIDENCE_COLUMN: confidences},
                generate_metadata = True
        )

        return util.prep_predictions(frame, sorted(d3m_indexes), metadata_source = self, missing_value = 0)

    def _write_predicate_graph(self, graph, path, graphId):
        rows = []

        for (id, data) in graph.nodes(data = True):
            if (data[constants.SOURCE_GRAPH_KEY] != graphId):
                continue
            rows.append([str(id)])

        util.write_tsv(path, rows)

    def _write_predicate_edge(self, graph, path, graphId):
        rows = []

        for (source, target, data) in graph.edges(data = True):
            # Skip links.
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_EDGE):
                continue

            # Skip edges that do not come from out target graph.
            if (graph.node[source][constants.SOURCE_GRAPH_KEY] != graphId):
                continue

            # Edges are undirected.
            rows.append([str(source), str(target), str(data[constants.WEIGHT_KEY])])
            rows.append([str(target), str(source), str(data[constants.WEIGHT_KEY])])

        util.write_tsv(path, rows)

    def _write_predicate_link_observed(self, graph, path):
        rows = []

        for (source, target, data) in graph.edges(data = True):
            # Skip edges.
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_LINK):
                continue

            # Skip links that are not observed.
            if (not data[constants.OBSERVED_KEY]):
                continue

            # Make sure graph 1 comes first.
            if (source > target):
                source, target = target, source

            rows.append([str(source), str(target), str(data[constants.WEIGHT_KEY])])

        util.write_tsv(path, rows)

    def _write_predicate_link_prior(self, graph, path):
        rows = []

        for (source, target, data) in graph.edges(data = True):
            # Skip edges.
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_LINK):
                continue

            # Skip observed links.
            # Since observed links are not targets, they have no prior.
            if (constants.OBSERVED_KEY in data and data[constants.OBSERVED_KEY]):
                continue

            if (constants.WEIGHT_KEY not in data):
                continue

            # Make sure graph 1 comes first.
            if (source > target):
                source, target = target, source

            rows.append([str(source), str(target), str(data[constants.WEIGHT_KEY])])

        util.write_tsv(path, rows)

    def _write_predicate_link_target(self, graph, path):
        rows = []

        for (source, target, data) in graph.edges(data = True):
            # Skip edges.
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_LINK):
                continue

            # Skip observed links.
            if (data[constants.OBSERVED_KEY]):
                continue

            # Make sure graph 1 comes first.
            # TODO(eriq): This should be unnecessary.
            if (source > target):
                source, target = target, source

            rows.append([str(source), str(target)])

        util.write_tsv(path, rows)

    def _write_predicate_block(self, graph, path):
        rows = []

        for (source, target, data) in graph.edges(data = True):
            # Skip edges.
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_LINK):
                continue

            # Skip observed links.
            if (data[constants.OBSERVED_KEY]):
                continue

            # Make sure graph 1 comes first.
            # TODO(eriq): This should be unnecessary.
            if (source > target):
                source, target = target, source

            rows.append([str(source), str(target)])

        util.write_tsv(path, rows)

    # Write every possible link that has not been observed.
    def _write_predicate_link_target_all(self, graph, path):
        for (id1, data1) in graph.nodes(data = True):
            if (data1[constants.SOURCE_GRAPH_KEY] != 1):
                continue

            for (id2, data2) in graph.nodes(data = True):
                if (data2[constants.SOURCE_GRAPH_KEY] != 2):
                    continue

                # Skip any observed links
                if (graph.has_edge(id1, id2) and graph[id1][id2][constants.OBSERVED_KEY]):
                    continue

                rows.append([str(id1), str(id2)])

        util.write_tsv(path, rows)

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': 'd83aa8fe-0433-4462-be54-b4074959b6fc',
        'version': config.VERSION,
        'name': 'Link Prediction',
        'description': 'Perform collective link prediction.',
        'python_path': 'd3m.primitives.link_prediction.link_prediction.LinkPrediction',
        'primitive_family': meta_base.PrimitiveFamily.LINK_PREDICTION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.MARKOV_RANDOM_FIELD,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'primitive', 'graph', 'link prediction', 'collective classifiction'],
        'installation': [
            config.INSTALLATION,
            config.INSTALLATION_JAVA,
#           Todo: revert (Issue 139)
#            config.INSTALLATION_POSTGRES
        ],
        'location_uris': [],
        'preconditions': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
