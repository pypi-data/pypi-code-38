import typing

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

COLUMN_LABEL = 'community'
NODE_ID = 'nodeID'
NODE_ID_COLUMNS = ['nodeID', 'G1.nodeID']

OUTPUT_COLUMN_GRAPH = 'graph'
OUTPUT_COLUMN_D3M_INDEXES = 'd3mIndexes'

# TODO(eriq): Lots of overlap with vertex nomination.

class CommunityDetectionParserHyperparams(meta_hyperparams.Hyperparams):
    pass

class CommunityDetectionParser(pi_transformer.TransformerPrimitiveBase[Inputs, Outputs, CommunityDetectionParserHyperparams]):
    """
    Pull all the graph data out of a 'community detection' style problem.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: CommunityDetectionParserHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        raw_graph, table = self._validate_inputs(inputs)
        graph = self._merge_data(raw_graph, table)

        d3m_indexes = container.DataFrame(list(table[constants.D3M_INDEX]), columns = [constants.D3M_INDEX])

        return pi_base.CallResult(container.DataFrame([[graph, d3m_indexes]], columns = [OUTPUT_COLUMN_GRAPH, OUTPUT_COLUMN_D3M_INDEXES]))

    # We expect a dataset with a single graph and a single table (that indexes into the graph).
    def _validate_inputs(self, dataset):
        graph_id = None
        table_id = None

        num_data_elements = int(dataset.metadata.query([])['dimension']['length'])

        if (num_data_elements != 2):
            raise ValueError("Community Detection-sytle problems only have 2 data elements, found %d." % (num_data_elements))

        for data_element in dataset.keys():
            if ('https://metadata.datadrivendiscovery.org/types/Graph' in dataset.metadata.query((data_element,))['semantic_types']):
                if (graph_id is not None):
                    raise ValueError("Found multiple graph elements, expecting only one.")
                graph_id = data_element
            else:
                if (table_id is not None):
                    raise ValueError("Found multiple table elements, expecting only one.")
                table_id = data_element

        return dataset[graph_id], dataset[table_id]

    def _merge_data(self, raw_graph, table):
        # Start with the raw graph and then just add the labels from the table.
        graph = raw_graph

        # Build an index of all the nodes by node id.
        # {nodeID: id, ...}
        node_ids = {}
        for (node, data) in graph.nodes(data = True):
            if (NODE_ID not in data):
                raise ValueError("Could not locate the node identifier for node %d (no '%s')." % (node, NODE_ID))
            node_ids[data[NODE_ID]] = node

        node_id_column = None
        for id_column in NODE_ID_COLUMNS:
            if (id_column in table.columns):
                node_id_column = id_column
                break

        if (node_id_column is None):
            raise ValueError("Could not locate node identifier column in table (none of %s)." % (NODE_ID_COLUMNS))

        for (index, row) in table.iterrows():
            node = node_ids[int(row[node_id_column])]

            new_data = {
                constants.D3M_INDEX: int(row[constants.D3M_INDEX]),
            }

            if (row[COLUMN_LABEL]):
                new_data[COLUMN_LABEL] = row[COLUMN_LABEL]

            graph.node[node].update(new_data)

        return graph

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': 'e149ba15-4004-4642-a00f-e7c833653a54',
        'version': config.VERSION,
        'name': 'Community Detection Parser',
        'description': 'Transform "community detection"-like problems into pure graphs.',
        'python_path': 'd3m.primitives.community_detection.community_detection_parser.CommunityDetectionParser',
        'primitive_family': meta_base.PrimitiveFamily.COMMUNITY_DETECTION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.DATA_CONVERSION,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'dataset', 'transformer', 'communityDetection' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'preconditions': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
