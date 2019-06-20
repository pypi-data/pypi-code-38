import typing

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import transformer as pi_transformer
from networkx import Graph as nx_Graph # type: ignore

from sri.common import config
from sri.common import constants
from sri.common import util
from sri.graph.networkx import Graph
from sri.graph.networkx import DiGraph

Inputs = container.Dataset
Outputs = container.List

class GraphMatchingParserHyperparams(meta_hyperparams.Hyperparams):
    pass

class GraphMatchingParser(pi_transformer.TransformerPrimitiveBase[Inputs, Outputs, GraphMatchingParserHyperparams]):
    """
    A primitive that takes in a "Graph Matching" dataset and converts it into several graphs for later processing.
    The output is a list of three graphs:

     1. The source graph in this graph matching problem.
     2. The destination graph in this graph matching problem.
     3. A directed bipartite graph that holds the observed and target edges.
        Observed edges have a weight, while targets have no weight.

    Node attributes:

     - constants.SOURCE_GRAPH_KEY: Either constants.NODE_MODIFIER_SOURCE or constants.NODE_MODIFIER_TARGET.
     - constants.NODE_ID_LABEL: An ID consistent amongst all three graphs.

    Edge attributes:

     - constants.OBSERVED_KEY: True/False depending on if the edge is observed (True) or a target (False).
     - constants.TARGET_KEY: True if this link is a target.
     - constants.D3M_INDEX: The D3M index value.
     - constants.EDGE_TYPE_KEY: constants.EDGE_TYPE_EDGE for edges between nodes in the same graph,
        and constants.EDGE_TYPE_LINK for nodes in different graphs.
     - 'weight': 'weight' is already a standard NetworkX key, but observed edges will have weights representing the observed value.

    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: GraphMatchingParserHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)

        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        graph1, graph2, observedLinks = self._validate_inputs(inputs)
        result = self._process_data(graph1, graph2, observedLinks)

        outputs: container.List = container.List(result, generate_metadata=True)

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
        if (len(inputs) != 3):
            raise ValueError("Dataset does not have three elements. Found %s." % (len(inputs)))

        graph_keys = util.get_graph_keys(inputs)
        if (len(graph_keys) != 2):
            raise ValueError("Expected exactly two graphs in the dataset, found: %d." % (len(graph_keys)))

        graph1 = inputs[graph_keys[0]]
        graph2 = inputs[graph_keys[1]]
        observedLinks = inputs[constants.D3M_TABLE_KEY]

        if (not isinstance(graph1, nx_Graph)):
            raise ValueError("Expecting a graph at \"%s\", found a %s" % (graph_keys[0], type(graph1).__name__))

        if (not isinstance(graph2, nx_Graph)):
            raise ValueError("Expecting a graph at \"%s\", found a %s" % (graph_keys[1], type(graph2).__name__))

        # Panda's Index, D3M Index, G1 nodeID, G2 nodeID, match

        count = 0
        for row in observedLinks.itertuples():
            # One extra column for the index.
            if (len(row) != 5):
                raise ValueError("Row %d in the tabular data that does not have four columns, found: (%s)." % (count, row))

            # We can't assign back into our Panda's frame, but we can check a failed conversion.
            int(row[2])
            # This used to be an int but it was changed to an alphanumeric value. Commenting out this check in case
            # there are datasets that still have node ids in integer form
            # str(row[3])

            if (row[4] != ''):
                val = float(row[4])
                if (val < 0.0 or val > 1.0):
                    raise ValueError("Row %d is out of range, found: (%s)." % (count, val))

            count += 1

        return Graph(graph1), Graph(graph2), observedLinks

    # Return a new graph with properly labeled nodes.
    def _relabel(self, input_graph, node_modifier):
        output_graph = Graph()

        # First add all the nodes.
        for (id, data) in input_graph.nodes(data = True):
            label = util.computeNodeLabel(data[constants.NODE_ID_LABEL], node_modifier)

            data[constants.SOURCE_GRAPH_KEY] = node_modifier
            data[constants.NODE_ID_LABEL] = data[constants.NODE_ID_LABEL]

            output_graph.add_node(label, **data)

        # Now add all the edges.
        for (source, target, data) in input_graph.edges(data = True):
            source_id = input_graph.node[source][constants.NODE_ID_LABEL]
            target_id = input_graph.node[target][constants.NODE_ID_LABEL]

            # Disallow self edges.
            if (source == target or source_id == target_id):
                continue

            weight = 1.0
            if (constants.WEIGHT_KEY in data):
                weight = data[constants.WEIGHT_KEY]

            # Remember, these edges are within the same input graph.
            source_label = util.computeNodeLabel(source_id, node_modifier)
            target_label = util.computeNodeLabel(target_id, node_modifier)

            data[constants.WEIGHT_KEY] = weight
            data[constants.EDGE_TYPE_KEY] = constants.EDGE_TYPE_EDGE
            data[constants.OBSERVED_KEY] = True

            output_graph.add_edge(source_label, target_label, **data)

        return output_graph

    def _process_data(self, graph1, graph2, observedLinks):
        self._logger.debug("Processing data")

        graph1 = self._relabel(graph1, constants.NODE_MODIFIER_SOURCE)
        graph2 = self._relabel(graph2, constants.NODE_MODIFIER_TARGET)

        # Panda's Index, D3M Index, G1 nodeID, G2 nodeID, match

        # Build up the graph of observed links.
        observedGraph = DiGraph()
        for row in observedLinks.itertuples():
            d3mIndex = int(row[1])
            source = int(row[2])
            # If the target node id is an alphanumeric we convert it to a base 36 integer
            if not isinstance(row[3], int):
                target = int(row[3], 36)
            else:
                target = int(row[3])

            weight = None
            if (row[4] != ''):
                weight = float(row[4])

            sourceLabel = util.computeNodeLabel(source, constants.NODE_MODIFIER_SOURCE)
            targetLabel = util.computeNodeLabel(target, constants.NODE_MODIFIER_TARGET)

            attributes = {
                constants.SOURCE_GRAPH_KEY: constants.NODE_MODIFIER_SOURCE,
                constants.NODE_ID_LABEL: source,
            }
            observedGraph.add_node(sourceLabel, **attributes)

            attributes = {
                constants.SOURCE_GRAPH_KEY: constants.NODE_MODIFIER_TARGET,
                constants.NODE_ID_LABEL: target,
            }
            observedGraph.add_node(targetLabel, **attributes)

            attributes = {
                constants.EDGE_TYPE_KEY: constants.EDGE_TYPE_LINK,
                constants.D3M_INDEX: d3mIndex,
            }

            # If we have a weight, then this is an observed link.
            # Otherwise, this is a target.
            if (weight is not None):
                attributes[constants.OBSERVED_KEY] = True
                attributes['weight'] = weight
            else:
                attributes[constants.TARGET_KEY] = True
                attributes[constants.OBSERVED_KEY] = False

            observedGraph.add_edge(sourceLabel, targetLabel, **attributes)

        # Add in some hints
        # We know that it makes sense to compute the local feature based similarity of the links.
        for graph in [graph1, graph2, observedGraph]:
            graph.metadata = graph.metadata.update([], {
                'schema': meta_base.CONTAINER_SCHEMA_VERSION,
                'structural_type': Graph,
                'hints': {
                    constants.GRAPH_HINT_LINK_LOCAL_SIM: True
                }
            })

        return [graph1, graph2, observedGraph]

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '3c4a1c2a-0f88-4fb1-a1b5-23226a38741b',
        'version': config.VERSION,
        'name': 'Graph Matching Parser',
        'description': 'Take in a "Graph Matching" dataset and convert it three different graphs: source graph, target graph, and inter-graph links.',
        'python_path': 'd3m.primitives.data_transformation.graph_matching_parser.GraphMatchingParser',
        'primitive_family': meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.DATA_CONVERSION,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'dataset', 'transformer', 'graphMatching'],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'preconditions': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
