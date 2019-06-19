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

Inputs = container.DataFrame  # container.DataFrame[container.DataFrame]
Outputs = container.DataFrame  # container.DataFrame[networkx.Graph]

class EdgeListToGraphHyperparams(meta_hyperparams.Hyperparams):
    pass

class EdgeListToGraph(pi_transformer.TransformerPrimitiveBase[Inputs, Outputs, EdgeListToGraphHyperparams]):
    """
    Convert edge lists to graphs.
    This is a inverse to the GraphToEdgeList primitive.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: EdgeListToGraphHyperparams, random_seed: int = 0) -> None:
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

        graphs = []
        for edgelist in inputs[inputs.columns[0]]:
            graphs.append([self._convert_edgelist(edgelist)])

        return pi_base.CallResult(container.DataFrame(graphs, columns = ['graph'], generate_metadata=True))

    def _convert_edgelist(self, edgelist):
        for required_col in ['source', 'dest']:
            if (required_col not in edgelist.columns):
                raise ValueError("Missing required column: '%s'." % (required_col))

        data_columns = set(edgelist.columns).difference({'source', 'dest', 'directed', 'weight'})

        if (len(edgelist) == 0):
            return networkx.Graph()

        if (edgelist['directed'][0]):
            graph = networkx.DiGraph()
        else:
            graph = networkx.Graph()

        for (index, edge) in edgelist.iterrows():
            source = edge['source']
            dest = edge['dest']

            edge_data = {}
            source_data = {}
            dest_data = {}

            for data_column in data_columns:
                value = edge[data_column]
                if (isinstance(value, list)):
                    # This must be a node attribute.
                    if (len(value) != 2):
                        raise ValueError("Expecting node attributes to always be of size 2, got %d." % (len(value)))

                    source_data[data_column] = value[0]
                    dest_data[data_column] = value[1]
                else:
                    edge_data[data_column] = edge[data_column]

            # networkx is super picky about additional attributes (can't pass an empty dict).
            # So splat the args.
            extra_args = {}

            if ('weight' in edge and edge['weight'] is not None):
                extra_args['weight'] = edge['weight']

            if (len(edge_data) > 0):
                extra_args['data'] = edge_data

            graph.add_edge(source, dest, **extra_args)

            # We will continually write over a node's data if we have seen it before.
            if (len(source_data) > 0):
                graph.node[source].update(source_data)
                graph.node[dest].update(dest_data)

        return graph

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '30f51c3a-d5fc-4bc1-b6bf-ab62b89489fd',
        'version': config.VERSION,
        'name': 'Edge List to Graph',
        'description': "Convert edge lists to graphs. This is a inverse to the GraphToEdgeList primitive.",
        'python_path': 'd3m.primitives.data_transformation.edge_list_to_graph.EdgeListToGraph',
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
