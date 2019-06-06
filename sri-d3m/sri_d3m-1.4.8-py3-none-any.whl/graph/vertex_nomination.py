import typing

import networkx
from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import transformer as pi_transformer

from sri.common import config
from sri.common import constants
from sri.common import util

Inputs = container.Dataset
Outputs = container.DataFrame  # ['graph', 'd3mIndexes']

COLUMN_NODE_ID = 'G1.nodeID'
COLUMN_LABEL = 'classLabel'
GRAPH_NODE_ID_ATTRIBUTE = 'name'
NODE_ID = 'nodeID'

EDGE_LIST_NODE_ID1 = 'V1_nodeID'
EDGE_LIST_NODE_ID2 = 'V2_nodeID'
EDGE_LIST_WEIGHT = 'edge_weight'

OUTPUT_COLUMN_GRAPH = 'graph'
OUTPUT_COLUMN_D3M_INDEXES = 'd3mIndexes'

class VertexNominationParserHyperparams(meta_hyperparams.Hyperparams):
    pass

class VertexNominationParser(pi_transformer.TransformerPrimitiveBase[Inputs, Outputs, VertexNominationParserHyperparams]):
    """
    Pull all the graph data out of a 'vertex nomination' style problem.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: VertexNominationParserHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        raw_graph, table, is_edgelist = self._validate_inputs(inputs)

        if (is_edgelist):
            graph = self._merge_data_edgelist(raw_graph, table)
        else:
            graph = self._merge_data_graph(raw_graph, table)

        d3m_indexes = container.DataFrame(list(table[constants.D3M_INDEX]), columns = [constants.D3M_INDEX], generate_metadata = True)

        return pi_base.CallResult(container.DataFrame([[graph, d3m_indexes]], columns = [OUTPUT_COLUMN_GRAPH, OUTPUT_COLUMN_D3M_INDEXES], generate_metadata = True))

    # We expect a dataset with a single graph and a single table (that indexes into the graph).
    def _validate_inputs(self, dataset):
        graph_id = None
        table_id = None
        is_edgelist = False

        num_data_elements = int(dataset.metadata.query([])['dimension']['length'])

        if (num_data_elements != 2):
            raise ValueError("Vertex Nomination-sytle problems only have 2 data elements, found %d." % (num_data_elements))

        for data_element in dataset.keys():
            if ('https://metadata.datadrivendiscovery.org/types/EdgeList' in dataset.metadata.query((data_element,))['semantic_types']):
                if (graph_id is not None):
                    raise ValueError("Found multiple graph elements, expecting only one.")
                graph_id = data_element
                is_edgelist = True
            elif ('https://metadata.datadrivendiscovery.org/types/Graph' in dataset.metadata.query((data_element,))['semantic_types']):
                if (graph_id is not None):
                    raise ValueError("Found multiple graph elements, expecting only one.")
                graph_id = data_element
            else:
                if (table_id is not None):
                    raise ValueError("Found multiple table elements, expecting only one.")
                table_id = data_element

        return dataset[graph_id], dataset[table_id], is_edgelist

    def _merge_data_graph(self, raw_graph, table):
        # Start with the raw graph and then just add the labels from the table.
        graph = raw_graph

        # Build an index of all the nodes by node id (which may be refered to as GRAPH_NODE_ID_ATTRIBUTE in the graph).
        # {nodeName: id, ...}
        node_ids = {}
        for (node, data) in graph.nodes(data = True):
            if (GRAPH_NODE_ID_ATTRIBUTE in data):
                node_ids[int(data[GRAPH_NODE_ID_ATTRIBUTE])] = node
            elif (NODE_ID in data):
                node_ids[int(data[NODE_ID])] = node
            else:
                raise ValueError("Could not locate the node identifier for node %d (no '%s' or '%s')." % (node, GRAPH_NODE_ID_ATTRIBUTE, NODE_ID))

        for (index, row) in table.iterrows():
            node = node_ids[int(row[COLUMN_NODE_ID])]

            new_data = {
                # Duplicate the "name" as "nodeId" so it is consistet.
                NODE_ID: int(row[COLUMN_NODE_ID]),
                constants.D3M_INDEX: int(row[constants.D3M_INDEX]),
            }

            if (row[COLUMN_LABEL]):
                new_data[COLUMN_LABEL] = row[COLUMN_LABEL]

            graph.node[node].update(new_data)

        return graph

    def _merge_data_edgelist(self, edgelist, table):
        # Start with a new graph.
        graph = networkx.Graph()

        # First fill in the nodes because they have attributes.
        attribute_cols = set(table.columns) - {constants.D3M_INDEX, NODE_ID, COLUMN_LABEL}

        for (index, row) in table.iterrows():
            node_id = int(row[NODE_ID])

            data = {
                NODE_ID: node_id,
                constants.D3M_INDEX: int(row[constants.D3M_INDEX]),
            }

            if (row[COLUMN_LABEL]):
                data[COLUMN_LABEL] = row[COLUMN_LABEL]

            for attribute_col in attribute_cols:
                try:
                    data[attribute_col] = float(row[attribute_col])
                except ValueError:
                    data[attribute_col] = row[attribute_col]

            graph.add_node(node_id, **data)

        # Now add the edges.
        for (index, row) in edgelist.iterrows():
            source_node = int(row[EDGE_LIST_NODE_ID1])
            target_node = int(row[EDGE_LIST_NODE_ID2])
            weight = float(row[EDGE_LIST_WEIGHT])

            graph.add_edge(source_node, target_node, weight = weight)

        return graph

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': 'a22f9bd3-818e-44e9-84a3-9592c5a85408',
        'version': config.VERSION,
        'name': 'Vertex Nomination Parser',
        'description': 'Transform "vertex nomination"-like problems into pure graphs.',
        'python_path': 'd3m.primitives.data_transformation.vertex_nomination_parser.VertexNominationParser',
        'primitive_family': meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.DATA_CONVERSION,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'dataset', 'transformer', 'vertexNomination' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'preconditions': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
