import operator
import random
import re
import typing

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import transformer as pi_transformer
from sklearn import feature_extraction
from sklearn import metrics

from sri.common import config
from sri.common import constants
from sri.common import util
from sri.graph.networkx import Graph
from sri.graph.networkx import DiGraph

# TODO(eriq): Change the output to just a graph once there is officially metadata on it.
Inputs = container.List
Outputs = container.List

# TODO(eriq): We need a way to cut down these graphs, they can get pretty big.
#   Maybe we can sample around the explicit targets?

# TODO(eriq): More through explaniation of input and output annotations.
"""
We expect two or three graphs as input:
- A graph describing the source nodes for the downstream link prediction problem.
- A graph describing the target nodes for the downstream link prediction problem.
- An optional graph describing existing links bewteen these two graphs.
The nodes in the source graph will maintain their "nodeID" and will get an additional attribute: SOURCE_GRAPH_KEY
indicating if thise node came from the source graph (NODE_MODIFIER_SOURCE) or target graph (NODE_MODIFIER_TARGET).
The label for these nodes will additionally become: (nodeID + 1) * SOURCE_GRAPH_KEY.
This is because nodeIDs can overlap between graphs.
The +1 is because zero is a valid nodeID, but they are non-negative.
"""

DEBUG_BAIL_COUNT = 100

class GraphTransformerHyperparams(meta_hyperparams.Hyperparams):
    feature_pattern = meta_hyperparams.Hyperparameter(
            default = r'f\d+',
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    max_links_per_node = meta_hyperparams.Hyperparameter(
            default = 10,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    max_edges_per_node = meta_hyperparams.Hyperparameter(
            default = 10,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    min_cosine_sim = meta_hyperparams.Hyperparameter[float](
            default = 0.60,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    max_cross_edge_exploration = meta_hyperparams.Hyperparameter(
            default = 10,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

class GraphTransformer(pi_transformer.TransformerPrimitiveBase[Inputs, Outputs, GraphTransformerHyperparams]):
    """
    A primitive that transforms multiple graphs into a single annotated graph that can be consumed by PSL.
    """

    def __init__(self, *, hyperparams: GraphTransformerHyperparams, _debug_options: typing.Dict = {}, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._rand = random.Random()
        self._rand.seed(random_seed)

        self._logger = util.get_logger(__name__)
        # TODO(eriq): Work on this.
        self._debug_run_fast = True

        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        if (constants.DEBUG_OPTION_RUN_FAST in _debug_options):
            self._debug_run_fast = _debug_options[constants.DEBUG_OPTION_RUN_FAST]

        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        input_source_graph, input_target_graph, link_graph = self._validate_inputs(inputs)

        result = self._process_data(input_source_graph, input_target_graph, link_graph)

        outputs: container.List = container.List([result])

        metaInfo = {
            'schema': meta_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': type(outputs),
            'dimension': {
                'length': len(outputs)
            }
        }
        metadata = meta_base.DataMetadata(metaInfo).generate(outputs)
        metadata = metadata.update((meta_base.ALL_ELEMENTS,), {'structural_type': Graph})
        outputs.metadata = metadata

        return pi_base.CallResult(outputs)

    def _validate_inputs(self, inputs: Inputs):
        if (len(inputs) < 2):
            raise ValueError("Not enough values for input. Need at least 2, found %d." % (len(inputs)))

        if (len(inputs) > 3):
            raise ValueError("Too many values for input. Need at most 3, found %d." % (len(inputs)))

        input_source_graph = inputs[0]
        input_target_graph = inputs[1]

        link_graph = None
        if (len(inputs) == 3):
            link_graph = inputs[2]

        if (not isinstance(input_source_graph, Graph)):
            raise ValueError("Expecting a graph at \"'0'\", found a %s" % (type(input_source_graph).__name__))

        if (not isinstance(input_target_graph, Graph)):
            raise ValueError("Expecting a graph at \"'1'\", found a %s" % (type(input_target_graph).__name__))

        if (link_graph is not None and not isinstance(link_graph, DiGraph)):
            raise ValueError("Expecting a directed graph at \"'2'\", found a %s" % (type(link_graph).__name__))

        return input_source_graph, input_target_graph, link_graph

    def _process_data(self, input_source_graph, input_target_graph, link_graph):
        self._logger.debug("Processing data")

        output_graph = Graph()

        hints = self._check_hints(input_source_graph, input_target_graph, link_graph)

        self._logger.debug("Build a graph with hints: %s.", hints)

        self._process_graph(output_graph, input_source_graph)
        self._process_graph(output_graph, input_target_graph)

        explicit_targets = []
        if (link_graph is not None):
            explicit_targets = self._process_links(output_graph, link_graph)

        if (hints[constants.GRAPH_HINT_LINK_LOCAL_SIM]):
            self._compute_local_sim_link_weights(output_graph, input_source_graph, input_target_graph, explicit_targets)

        if (hints[constants.GRAPH_HINT_LINK_MEAN]):
            self._compute_mean_link_weights(output_graph, input_source_graph, input_target_graph, explicit_targets)

        if (hints[constants.GRAPH_HINT_EDGE_COSINE][0]):
            self._compute_cosine_edge_weights(output_graph, input_source_graph, explicit_targets)

        if (hints[constants.GRAPH_HINT_EDGE_COSINE][1]):
            self._compute_cosine_edge_weights(output_graph, input_target_graph, explicit_targets)

        # Ensure that explicit targets are included.
        self._logger.debug("Adding explicit targets (%d).", len(explicit_targets))

        for (source_label, target_label) in explicit_targets:
            if (output_graph.has_edge(source_label, target_label)):
                # Ensure some edge properties exist.
                output_graph[source_label][target_label][constants.EDGE_TYPE_KEY] = constants.EDGE_TYPE_LINK
                output_graph[source_label][target_label][constants.TARGET_KEY] = True
                output_graph[source_label][target_label][constants.OBSERVED_KEY] = False
                output_graph[source_label][target_label][constants.D3M_INDEX] = link_graph[source_label][target_label][constants.D3M_INDEX]
            else:
                attributes = {
                    constants.EDGE_TYPE_KEY: constants.EDGE_TYPE_LINK,
                    constants.TARGET_KEY: True,
                    constants.OBSERVED_KEY: False,
                    constants.D3M_INDEX: link_graph[source_label][target_label][constants.D3M_INDEX]
                }
                output_graph.add_edge(source_label, target_label, **attributes)

        # Attached the used hints as metadata in the output graph.
        output_graph.metadata = output_graph.metadata.update([], {
            'schema': meta_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': Graph,
            'hints': hints
        })

        return output_graph

    # Add the nodes and edges from a single graph.
    def _process_graph(self, output_graph, input_graph):
        # First add all the nodes.
        for (label, data) in input_graph.nodes(data = True):
            attributes = {
                constants.SOURCE_GRAPH_KEY: data[constants.SOURCE_GRAPH_KEY],
                constants.NODE_ID_LABEL: data[constants.NODE_ID_LABEL],
            }
            output_graph.add_node(label, **attributes)

        # Now add all the edges.
        for (source_label, target_label) in input_graph.edges():
            # Disallow self edges.
            if (source_label == target_label):
                continue

            weight = 1.0
            if (constants.WEIGHT_KEY in input_graph[source_label][target_label]):
                weight = input_graph[source_label][target_label][constants.WEIGHT_KEY]

            attributes = {
                constants.WEIGHT_KEY: weight,
                constants.EDGE_TYPE_KEY: constants.EDGE_TYPE_EDGE,
                constants.OBSERVED_KEY: True
            }
            output_graph.add_edge(source_label, target_label, **attributes)

    # Add observed links and check for explicit targets.
    def _process_links(self, output_graph, link_graph):
        targets = []

        # All the nodes should already exist in each respective graph.
        for (source_label, target_label, data) in link_graph.edges(data = True):
            if (constants.TARGET_KEY in data and data[constants.TARGET_KEY]):
                # This link is an explicit target, make sure to include it in targets.
                targets.append((source_label, target_label))
            else:
                # This link is observed.
                weight = 1.0
                if (constants.WEIGHT_KEY in link_graph[source_label][target_label] and link_graph[source_label][target_label][constants.WEIGHT_KEY] is not None):
                    weight = float(link_graph[source_label][target_label][constants.WEIGHT_KEY])

                attributes = {
                    constants.WEIGHT_KEY: weight,
                    constants.EDGE_TYPE_KEY: constants.EDGE_TYPE_LINK,
                    constants.OBSERVED_KEY: True
                }

                output_graph.add_edge(source_label, target_label, **attributes)

        return targets

    # Looks for hints and reconcile them with any additional options.
    def _check_hints(self, *graphs):
        hints = {
            constants.GRAPH_HINT_LINK_LOCAL_SIM: False,
            constants.GRAPH_HINT_LINK_MEAN: False,
            # We can get different hints about each input graph.
            constants.GRAPH_HINT_EDGE_COSINE: [False, False],
        }

        # First check for hints from each graph.
        for i in range(len(graphs)):
            graph_hints = graphs[i].metadata.query([])['hints']

            if (not graph_hints):
                continue

            if (constants.GRAPH_HINT_LINK_LOCAL_SIM in graph_hints):
                hints[constants.GRAPH_HINT_LINK_LOCAL_SIM] = hints[constants.GRAPH_HINT_LINK_LOCAL_SIM] or graph_hints[constants.GRAPH_HINT_LINK_LOCAL_SIM]

            if (constants.GRAPH_HINT_LINK_MEAN in graph_hints):
                hints[constants.GRAPH_HINT_LINK_MEAN] = hints[constants.GRAPH_HINT_LINK_MEAN] or graph_hints[constants.GRAPH_HINT_LINK_MEAN]

            if (constants.GRAPH_HINT_EDGE_COSINE in graph_hints and i < 2):
                hints[constants.GRAPH_HINT_EDGE_COSINE][i] = graph_hints[constants.GRAPH_HINT_EDGE_COSINE]

        return hints

    # Look for node attributes that look like features get the distance (normalized into similarity) between them.
    # TODO(eriq): Make blocking tunable.
    # TODO(eriq): Where are some target links that we want to make sure are included.
    def _compute_local_sim_link_weights(self, output_graph, input_source_graph, input_target_graph, explicit_targets):
        self._logger.debug("Computing local link similarity")

        features = self._discoverFeatures(input_source_graph, input_target_graph)

        # {source_label: {target_label: [distance, ...], ...}, ...}
        distances = {}

        debug_break_count = int(self.hyperparams['max_links_per_node'] / 2)

        for feature in features:
            min_val = None
            max_val = None

            for source_label in input_source_graph.nodes():
                count = 0
                for target_label in input_target_graph.nodes():
                    # Only calcualte distance for links not already observed in the output graph.
                    if (output_graph.has_edge(source_label, target_label) and output_graph[source_label][target_label][constants.OBSERVED_KEY]):
                        continue

                    distance = abs(input_source_graph.node[source_label][feature] - input_target_graph.node[target_label][feature])

                    if (min_val is None or distance < min_val):
                        min_val = distance

                    if (max_val is None or distance > max_val):
                        max_val = distance

                    if (source_label not in distances):
                        distances[source_label] = {}

                    if (target_label not in distances[source_label]):
                        distances[source_label][target_label] = []

                    distances[source_label][target_label].append(distance)

                    count += 1
                    if (self._debug_run_fast and count == debug_break_count):
                        break

            # Just do a min/max normalization into a similarity.
            # TODO(eriq): Better normalization here can go a long way.
            range_val = float(max_val - min_val)
            for (source_label, id2Distances) in distances.items():
                for (target_label, pairDistances) in id2Distances.items():
                    distance = pairDistances[-1]
                    pairDistances[-1] = (1.0 - min(1.0, max(0.0, float(distance - min_val) / range_val)))

        # Just get the mean or the normalized values, but we could also do
        # something like a logistic regression on the raw values.
        # now distances = {source_label: {target_label: nomral distance, ...}, ...}
        for (source_label, target_sims) in distances.items():
            for (target_label, pairSims) in target_sims.items():
                distances[source_label][target_label] = float(sum(pairSims)) / len(pairSims)

        # For blocking purposes, choose the top N similarities for each node.
        blockedSims = {}

        ''' TODO(eriq): This is pretty costly (750k in test data). Can we make it cheaper?
        # Before we block, include all information from both sides of explicit targets.
        include_sources = {explicit_target[0] for explicit_target in explicit_targets}
        include_targets = {explicit_target[1] for explicit_target in explicit_targets}
        for (source_label, target_sims) in distances.items():
            node_id_1 = input_source_graph.node[source_label][NODE_ID_LABEL]

            blockedSims[source_label] = {}
            for (target_label, sim) in target_sims.items():
                node_id_2 = input_target_graph.node[target_label][NODE_ID_LABEL]

                if (node_id_1 in include_sources or node_id_2 in include_targets):
                    blockedSims[source_label][target_label] = sim
        '''

        max_links_per_node = self.hyperparams['max_links_per_node']
        self._logger.debug("Taking top %d link similarity", max_links_per_node)
        for (source_label, sims) in distances.items():
            sims = list(sims.items())
            sims.sort(reverse = True, key = operator.itemgetter(1))
            blockedSims[source_label] = dict(sims[0:max_links_per_node])

        for (source_label, target_sims) in blockedSims.items():
            for (target_label, sim) in target_sims.items():
                attributes = {
                    constants.WEIGHT_KEY: sim,
                    constants.EDGE_TYPE_KEY: constants.EDGE_TYPE_LINK,
                    constants.SOURCE_GRAPH_KEY: constants.COMPUTED_SOURCE_LOCAL_SIM,
                    constants.OBSERVED_KEY: False
                }

                output_graph.add_edge(source_label, target_label, **attributes)

    # Put a computed edge over every pair of nodes
    # (that do not already have one).
    # First get the mean of all observed link a source/target is
    # already involved in.
    # Then get every pair without an observed label and assign it the
    # mean of the source and target mean.
    def _compute_mean_link_weights(self, output_graph, input_source_graph, input_target_graph, explicit_targets):
        self._logger.debug("Computing mean link weights")

        # {label: [running sum, count], ...}
        source_weights = {}
        target_weights = {}

        # Sum up all the link weights.
        for (source_label, target_label, data) in output_graph.edges(data = True):
            if (data[constants.EDGE_TYPE_KEY] != constants.EDGE_TYPE_LINK or not data[constants.OBSERVED_KEY]):
                continue

            if (constants.WEIGHT_KEY not in data):
                raise ValueError("No weight for (%s, %s)." % (source_label, target_label))

            if (source_label not in source_weights):
                source_weights[source_label] = [0.0, 0]

            if (target_label not in target_weights):
                target_weights[target_label] = [0.0, 0]

            source_weights[source_label][0] += data[constants.WEIGHT_KEY]
            source_weights[source_label][1] += 1

            target_weights[target_label][0] += data[constants.WEIGHT_KEY]
            target_weights[target_label][1] += 1

        # Average the weights out.
        for source_label in source_weights:
            source_weights[source_label] = source_weights[source_label][0] / source_weights[source_label][1]

        for target_label in target_weights:
            target_weights[target_label] = target_weights[target_label][0] / target_weights[target_label][1]

        # Assign a link to every pair that does not already have one.
        for source_label in input_source_graph.nodes():
            count = 0
            for target_label in input_target_graph.nodes():
                if (output_graph.has_edge(source_label, target_label) and output_graph[source_label][target_label][constants.OBSERVED_KEY]):
                    continue

                weight = None
                if (source_label in source_weights):
                    weight = source_weights[source_label]

                if (target_label in target_weights):
                    if (weight is None):
                        weight = target_weights[target_label]
                    else:
                        weight = (weight + target_weights[target_label]) / 2.0

                if (weight is None):
                    continue

                attributes = {
                    constants.WEIGHT_KEY: weight,
                    constants.EDGE_TYPE_KEY: constants.EDGE_TYPE_LINK,
                    constants.SOURCE_GRAPH_KEY: constants.COMPUTED_SOURCE_MEAN,
                    constants.OBSERVED_KEY: False
                }
                output_graph.add_edge(source_label, target_label, **attributes)

                count += 1
                if (self._debug_run_fast and count == self.hyperparams['max_links_per_node']):
                    break

    # Calclate the cosine similarity between two nodes in the same graph
    # (which means we will be inserting an edge).
    # Use the weights of observed links as the vectors to compare.
    # We will only calculate one diagonal since these edges are undirected.
    # Remember that this is within one graph, so "source" and "target" here
    # refer to the terminal nodes of an edge (not link).
    def _compute_cosine_edge_weights(self, output_graph, input_graph, explicit_targets):
        self._logger.debug("Computing cosine edge weights")

        # First, build the sparse vectors of obsereved edge weights.
        # [source_label, ...] (1-1 with graph_weights).
        graph_ids = []
        # [{target_label: weight, ...}, ...]
        graph_weights = []

        for source_label in input_graph.nodes():
            weights = {}

            for target_label in output_graph[source_label]:
                data = output_graph[source_label][target_label]

                if (data[constants.EDGE_TYPE_KEY] == constants.EDGE_TYPE_LINK and data[constants.OBSERVED_KEY] and constants.WEIGHT_KEY in data):
                    weights[target_label] = data[constants.WEIGHT_KEY]

            graph_ids.append(source_label)
            graph_weights.append(weights)

        # Turn the mappings into sparse vectors.
        graph_vectors = feature_extraction.DictVectorizer().fit_transform(graph_weights)

        used_indexes = set()

        # Calculate the pairwise cosine similarities.
        outter_loop_count = 0
        for index1 in range(len(graph_ids)):
            outter_loop_count += 1
            if (self._debug_run_fast and outter_loop_count >= DEBUG_BAIL_COUNT):
                break

            source_label = graph_ids[index1]
            added_count = 0
            inner_loop_count = 0

            # Because we may stop early, randomly choose indexes.
            # (shuffling is too expensive).
            used_indexes.clear()

            while (len(used_indexes) < (len(graph_ids) - index1 - 1)):
                index2 = self._rand.randrange(index1 + 1, len(graph_ids))
                while (index2 in used_indexes):
                    index2 = self._rand.randrange(index1 + 1, len(graph_ids))
                used_indexes.add(index2)

                target_label = graph_ids[index2]

                inner_loop_count += 1
                if (self._debug_run_fast and inner_loop_count >= DEBUG_BAIL_COUNT):
                    break

                # Skip if we already have an edge.
                if (output_graph.has_edge(source_label, target_label)):
                    continue

                if (graph_vectors[index1].getnnz() == 0):
                    continue

                # Only explore so much.
                if (self.hyperparams['max_cross_edge_exploration'] != -1 and inner_loop_count >= self.hyperparams['max_cross_edge_exploration']):
                    break

                cosine_sim = metrics.pairwise.cosine_similarity(graph_vectors[index1], graph_vectors[index2])[0][0]

                if (cosine_sim < self.hyperparams['min_cosine_sim']):
                    continue

                attributes = {
                    constants.WEIGHT_KEY: cosine_sim,
                    constants.EDGE_TYPE_KEY: constants.EDGE_TYPE_EDGE,
                    constants.SOURCE_GRAPH_KEY: constants.COMPUTED_SOURCE_COSINE,
                    constants.OBSERVED_KEY: False
                }
                output_graph.add_edge(source_label, target_label, **attributes)

                # Keep the size reasonable.
                # TODO(eriq): Later, we may want to bucket the results into good/neutral/bad and put a limit on those sizes instead.
                if (added_count > self.hyperparams['max_edges_per_node']):
                    break

                added_count += 1
                if (self._debug_run_fast and added_count >= int(self.hyperparams['max_links_per_node'] / 2)):
                    break

    # Just check the first node on each graph and make sure they match.
    def _discoverFeatures(self, *graphs):
        features = []

        if (len(graphs) == 0):
            return features

        # Fetch the initial features.
        feature_pattern = self.hyperparams['feature_pattern']
        for id, data in graphs[0].nodes(data = True):
            for key in data:
                if (re.match(feature_pattern, key)):
                    features.append(key)
            break

        features.sort()

        # Ensure that all the features are in the other graph.
        for graph in graphs[1:]:
            for id, data in graph.nodes(data = True):
                for feature in features:
                    if (feature not in data):
                        raise ValueError("Features are not consistent across graphs.")
                break

        return features

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': 'da0405b0-2d6f-4107-94f6-658913c7cc70',
        'version': config.VERSION,
        'name': 'Graph Transformer',
        'description': 'Take in some graphs respectivley describing two graphs and (optinally) targets between those graphs, and produce a single unified graph with potentially more computed edges.',
        'python_path': 'd3m.primitives.data_transformation.graph_transformer.GraphTransformer',
        'primitive_family': meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.COMPUTER_ALGEBRA,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'transformer' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'preconditions': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
