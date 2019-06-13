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
Outputs = container.DataFrame # [nodelist (dataframe), edgelist (dataframe), labels (dataframe)]

OUTPUT_COLUMN_NODELIST = 'nodelist'
OUTPUT_COLUMN_EDGELIST = 'edgelist'
OUTPUT_COLUMN_LABELS = 'labels'
OUTPUT_COLUMNS = [OUTPUT_COLUMN_NODELIST, OUTPUT_COLUMN_EDGELIST, OUTPUT_COLUMN_LABELS]

OUTPUT_EDGELIST_COLUMN_SOURCE = constants.SOURCE_KEY
OUTPUT_EDGELIST_COLUMN_DEST = constants.DEST_KEY
OUTPUT_EDGELIST_COLUMN_WEIGHT = constants.WEIGHT_KEY
OUTPUT_EDGELIST_COLUMNS = [OUTPUT_EDGELIST_COLUMN_SOURCE, OUTPUT_EDGELIST_COLUMN_DEST, OUTPUT_EDGELIST_COLUMN_WEIGHT]

TEMP_KEY_EDGE_INDEX = 'edgeIndex'
TEMP_KEY_SOURCE = 'node1'
TEMP_KEY_DEST = 'node2'
TEMP_KEY_WEIGHT = 'weight'

class VertexClassificationParserHyperparams(meta_hyperparams.Hyperparams):
    pass

class VertexClassificationParser(pi_transformer.TransformerPrimitiveBase[Inputs, Outputs, VertexClassificationParserHyperparams]):
    """
    Pull all the graph data out of a 'vertex classification' style problem.
    In the output edgelist, there may be nodes that are not in the nodelist.
    This is because not all nodes have features associated with them.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: VertexClassificationParserHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        graph_id, table_id, is_edgelist, node_column_index, target_column_index, attribute_column_indexs = self._validate_inputs(inputs)

        if (is_edgelist):
            raw_edgelist = inputs[graph_id]
            raw_feature_table = inputs[table_id]

            source_node_index, target_node_index, weight_column_index = self._validate_edgelist(inputs, graph_id)
        else:
            edgelist_info, feature_table_info = self._deconstruct_graph(inputs[graph_id], inputs[table_id], node_column_index, target_column_index)

            raw_edgelist, source_node_index, target_node_index, weight_column_index = edgelist_info
            raw_feature_table, node_column_index, target_column_index, attribute_column_indexs = feature_table_info

        nodelist, labels, id_mapping = self._clean_nodes(raw_feature_table, node_column_index, target_column_index, attribute_column_indexs)
        edgelist = self._clean_edges(raw_edgelist, is_edgelist, source_node_index, target_node_index, weight_column_index, id_mapping)

        result = container.DataFrame([[nodelist, edgelist, labels]], columns = OUTPUT_COLUMNS, generate_metadata = True)
        return pi_base.CallResult(result)

    # We expect a dataset with a single "graph" and a single table (that indexes into the graph).
    def _validate_inputs(self, dataset):
        is_edgelist = False

        num_data_elements = int(dataset.metadata.query([])['dimension']['length'])

        if (num_data_elements != 2):
            raise ValueError("Vertex Classification-style problems only have 2 data elements, found %d." % (num_data_elements))

        graph_ids = util.get_graph_keys(dataset)
        if (len(graph_ids) > 1):
            raise ValueError("Found multiple graph elements, expecting only one.")

        if (len(graph_ids) == 0):
            # May be an edhelist.
            graph_ids = util.get_edge_list_keys(dataset)
            if (len(graph_ids) == 0):
                raise ValueError("Failed to find the graph resource.")

            if (len(graph_ids) > 1):
                raise ValueError("Found multiple edgelist elements, expecting only one.")

            is_edgelist = True

        graph_id = graph_ids[0]

        table_id = util.get_learning_data_key(dataset)
        target_column_index = util.get_target_column(dataset, table_id)
        attribute_column_indexs = util.get_attribute_columns(dataset, table_id)

        node_column_indexs = util.get_node_columns(dataset, table_id, graph_id)
        if (len(node_column_indexs) == 0):
            raise ValueError("Failed to find node references in the learning data")

        if (len(node_column_indexs) > 1):
            raise ValueError("Expected a single column with node references, but found multiple")

        node_column_index = node_column_indexs[0]

        return graph_id, table_id, is_edgelist, node_column_index, target_column_index, attribute_column_indexs

    # We expect a dataset with a single graph and a single table (that indexes into the graph).
    def _validate_edgelist(self, dataset, graph_id):
        source_column_index = util.get_edgelist_source_column(dataset, graph_id)
        target_column_index = util.get_edgelist_target_column(dataset, graph_id)
        weight_column_index = util.get_edgelist_weight_column(dataset, graph_id)
        return source_column_index, target_column_index, weight_column_index

    # Convert the graph and table into the more standard edge and feature lists.
    # The new indexes into these tables will be returned: node_column_index, target_column_index, attribute_column_indexs.
    # Returns: [edgelist_info, feature_table_info].
    # Where: edgelist_info = (edgelist, source_index, target_index, weight_index).
    # Where: feature_table_info = (feature_table, node_column_index, target_column_index, attribute_column_indexs).
    def _deconstruct_graph(self, graph, table, node_column_index, target_column_index):
        node_column = table.columns[node_column_index]
        target_column = table.columns[target_column_index]

        # Build the edgelist.
        edges = []

        for (source_id, dest_id, data) in graph.edges.data():
            weight = 1
            if (constants.WEIGHT_KEY in data):
                weight = data[constants.WEIGHT_KEY]

            edges.append([len(edges), source_id, dest_id, weight])

        edgelist = container.DataFrame(edges, columns = [TEMP_KEY_EDGE_INDEX, TEMP_KEY_SOURCE, TEMP_KEY_DEST, TEMP_KEY_WEIGHT])
        edgelist_info = (edgelist, 1, 2, 3)

        # Build the feature table.
        features = []

        feature_columns = [constants.D3M_INDEX, node_column, target_column]
        added_features = False
        attribute_column_indexs = []

        for i in range(len(table)):
            d3m_index = int(table[constants.D3M_INDEX][i])
            node_id = int(table[node_column][i])
            label = table[target_column][i]

            node = graph.node[node_id]

            # If we have not yet, find all the feature columns.
            if (len(attribute_column_indexs) == 0):
                for key in node:
                    if (key in {'id', 'label', 'nodeID', node_column}):
                        continue

                    attribute_column_indexs.append(3 + len(attribute_column_indexs))
                    feature_columns.append(key)

            row = [d3m_index, node_id, label]

            for attribute_column_index in attribute_column_indexs:
                row.append(node[feature_columns[attribute_column_index]])

            features.append(row)

        feature_table = container.DataFrame(features, columns = feature_columns)
        feature_table_info = (feature_table, 1, 2, attribute_column_indexs)

        return (edgelist_info, feature_table_info)

    # Pull all the info out of the feature table.
    # Returns: [nodelist, labels, mapping{node_id: d3m_index}].
    def _clean_nodes(self, feature_table, node_column_index, target_column_index, attribute_column_indexs):
        # {node_id: d3m_index, ...}
        id_mapping = {}

        node_column = feature_table.columns[node_column_index]
        target_column = feature_table.columns[target_column_index]
        attribute_columns = [feature_table.columns[index] for index in attribute_column_indexs]

        for i in range(len(feature_table)):
            id_mapping[feature_table[node_column][i]] = int(feature_table[constants.D3M_INDEX][i])

        # Extract the labels.
        labels = feature_table[[constants.D3M_INDEX, target_column]]

        # Drop the node id and labels.
        nodelist = feature_table.drop(columns = [node_column, target_column])

        return nodelist, labels, id_mapping

    # Extract all the edges and translate them into d3m_indexes.
    # Note that we may discover nodes not in id_mapping (the feature table).
    # Not all nodes have features, so we will just give them a unique id in another number space and carry on.
    def _clean_edges(self, raw_graph, is_edgelist, source_node_index, target_node_index, weight_column_index, id_mapping):
        raw_edgelist = []

        source_node = raw_graph.columns[source_node_index]
        target_node = raw_graph.columns[target_node_index]
        weight_column = raw_graph.columns[weight_column_index]

        for i in range(len(raw_graph)):
            weight = 1
            if (weight_column_index is not None):
                weight = raw_graph[weight_column][i]

            source_node_id = raw_graph[source_node][i]
            dest_node_id = raw_graph[target_node][i]

            source_id = self._convert_node_id(source_node_id)
            if (source_node_id in id_mapping):
                source_id = id_mapping[source_node_id]

            dest_id = self._convert_node_id(dest_node_id)
            if (dest_node_id in id_mapping):
                dest_id = id_mapping[dest_node_id]

            raw_edgelist.append([source_id, dest_id, weight])

        return container.DataFrame(raw_edgelist, columns = OUTPUT_EDGELIST_COLUMNS, generate_metadata = True)

    # Convert a node id into a space that does not overlap with d3m indexes.
    def _convert_node_id(self, id):
        if (isinstance(id, int)):
            return -id

        if (not isinstance(id, str)):
            return id

        if (not id.isdigit()):
            return id

        return -1 * int(id)

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': 'a22f9bd3-818e-44e9-84a3-9592c5a85408',
        'version': config.VERSION,
        'name': 'Vertex Classification Parser',
        'description': 'Transform "vertex classification"-like problems into three tables: nodes, edges, and labels.',
        'python_path': 'd3m.primitives.data_transformation.vertex_classification_parser.VertexClassificationParser',
        'primitive_family': meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.DATA_CONVERSION,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'dataset', 'transformer', 'vertexClassification' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'preconditions': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
