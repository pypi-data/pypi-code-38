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

Inputs = container.DataFrame  # container.DataFrame[networkx.Graph]
Outputs = container.DataFrame  # container.DataFrame[container.DataFrame]

class GraphToEdgeListHyperparams(meta_hyperparams.Hyperparams):
    include_edge_attributes = meta_hyperparams.Hyperparameter[bool](
            description = 'If true, any edge attributes will be include in the output.',
            default = False,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter']
    )

    include_node_attributes = meta_hyperparams.Hyperparameter[bool](
            description = 'If true, any node attributes will be include in the output. Node attributes will be included as a container.List of (source, target).',
            default = False,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter']
    )

class GraphToEdgeList(pi_transformer.TransformerPrimitiveBase[Inputs, Outputs, GraphToEdgeListHyperparams]):
    """
    Convert graphs into edge lists (in the form of a DataFrame).
    Four columns will always be returned in the edge list: 'source', 'dest', 'directed', 'weight'.
    More columns may be returned based on the hyperparams.
    This is a inverse to the EdgeListToGraph primitive.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: GraphToEdgeListHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = util.get_logger(__name__)
        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        if (constants.DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            util.set_logging_level(_debug_options[constants.DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        if (len(inputs.columns) == 0):
            raise ValueError("Not enough columns.")

        edge_lists = []
        for graph in inputs[inputs.columns[0]]:
            edge_lists.append([self._convert_graph(graph)])

        return pi_base.CallResult(container.DataFrame(edge_lists, columns = ['edgelist']))

    # TODO(eriq): Name collisions with attributes are possible here.
    def _convert_graph(self, graph):
        # Columns that we will always include.
        base_columns = ['source', 'dest', 'directed', 'weight']
        additional_columns = set()

        edges = []

        directed = False
        if (networkx.is_directed(graph)):
            directed = True

        for (source, dest, data) in graph.edges(data = True):
            data['source'] = source
            data['dest'] = dest
            data['directed'] = directed

            if (self.hyperparams['include_edge_attributes']):
                additional_columns.union(data.keys())

            if (self.hyperparams['include_node_attributes']):
                source_data = graph.nodes[source]
                dest_data = graph.nodes[dest]

                for key in (set(source_data.keys()).union(set(dest_data.keys()))):
                    source_val = None
                    if (key in source_data):
                        source_val = source_data[key]

                    dest_val = None
                    if (key in dest_data):
                        dest_val = dest_data[key]

                    additional_columns.add(key)
                    # TODO(eriq): I would prefer this be a tuple, but d3m data types disallow it.
                    data[key] = container.List([source_val, dest_val])

            edges.append(data)

        if ('weight' in additional_columns):
            additional_columns.remove('weight')

        edge_list = []
        columns = base_columns + list(additional_columns)

        for edge in edges:
            attributes = []
            for column in columns:
                if (column not in edge):
                    attributes.append(None)
                else:
                    attributes.append(edge[column])

            edge_list.append(attributes)

        return container.DataFrame(edge_list, columns = columns)

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '5f565b7a-9cb7-48c3-ae4d-84a57eb790af',
        'version': config.VERSION,
        'name': 'Graph to Edge List',
        'description': "Convert graphs into edge lists (in the form of a DataFrame). Four columns will always be returned in the edge list: 'source', 'dest', 'directed', 'weight'. More columns may be returned based on the hyperparams.",
        'python_path': 'd3m.primitives.data_transformation.graph_to_edge_list.GraphToEdgeList',
        'primitive_family': meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.DATA_CONVERSION,
        ],
        'source': config.SOURCE,

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'dataset', 'transformer' 'edge list' ],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'preconditions': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffect.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
