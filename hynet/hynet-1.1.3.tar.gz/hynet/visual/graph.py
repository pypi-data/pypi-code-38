"""
Visualization of network graphs.

*hynet* uses NetworkX to export graph data. NetworkX can export to various
popular formats, including the GraphViz DOT format and JSON.
"""

import copy
import json
import logging
from math import isnan, isinf

import networkx as nx
from networkx.readwrite import json_graph

from hynet.scenario.representation import Scenario
from hynet.model.steady_state import SystemModel
from hynet.opf.result import OPFResult

_log = logging.getLogger(__name__)


def create_networkx_graph(data):
    """
    Return a NetworkX graph object for the provided network graph.

    Buses and injectors are inserted as nodes. Branches and converters are
    inserted as edges between the buses, while injectors are connected via
    additional edges to their respective terminal bus. The scenario data and,
    if provided, the OPF result data of the individual entities is added as
    attributes to the respective graph elements. The returned NetworkX graph
    can be exported into various formats, please refer to the documentation of
    NetworkX.

    Parameters
    ----------
    data : Scenario or SystemModel or OPFResult
        ``Scenario`` object, ``SystemModel`` object, or ``OPFResult`` that
        contains the network graph information.

    Returns
    -------
    graph : nx.Graph
        NetworkX graph representation of the grid's network graph.

    See Also
    --------
    hynet.visual.graph.export_networkx_graph_to_json
    """
    graph = nx.Graph()
    if isinstance(data, Scenario):
        scenario = data
    elif isinstance(data, (SystemModel, OPFResult)):
        scenario = data.scenario
    else:
        raise ValueError(("The argument 'data' must be a Scenario object, "
                          "a SystemModel object, or an OPF result."))

    bus_node = 'Bus {0}'
    injector_node = 'Injector {0}'

    buses = _restore_index(scenario.bus)
    branches = _restore_index(scenario.branch)
    converters = _restore_index(scenario.converter)
    injectors = _restore_index(scenario.injector)

    if isinstance(data, OPFResult):
        buses = buses.join(data.bus, rsuffix='_opf')
        branches = branches.join(data.branch, rsuffix='_opf')
        converters = converters.join(data.converter, rsuffix='_opf')
        injectors = injectors.join(data.injector, rsuffix='_opf')

    buses = buses.to_dict(orient='records')
    branches = branches.to_dict(orient='records')
    converters = converters.to_dict(orient='records')
    injectors = injectors.to_dict(orient='records')

    for bus in buses:
        bus['graph_type'] = 'bus'
        graph.add_node(bus_node.format(bus['id']), attr_dict=bus)

    for branch in branches:
        branch['graph_type'] = 'branch'
        graph.add_edge(bus_node.format(branch['src']),
                       bus_node.format(branch['dst']),
                       attr_dict=branch)

    for converter in converters:
        converter['graph_type'] = 'converter'
        graph.add_edge(bus_node.format(converter['src']),
                       bus_node.format(converter['dst']),
                       attr_dict=converter)

    for injector in injectors:
        injector['graph_type'] = 'injector'
        graph.add_node(injector_node.format(injector['id']),
                       attr_dict=injector)
        graph.add_edge(injector_node.format(injector['id']),
                       bus_node.format(injector['bus']),
                       attr_dict={'graph_type': 'terminal',
                                  'injector': injector['id'],
                                  'bus': injector['bus']})

    return graph


def export_networkx_graph_to_json(graph, output_file):
    """
    Exports a NetworkX graph object to a JSON file.

    The specified network graph is exported to the JSON format, which is
    supported by D3 [1]_.

    **Remark:** As a simple tool to visualize the graph, this subpackage
    includes the web page ``show_graph.html`` in the subdirectory
    ``rendering``. To use it, store the graph object to the file
    ``network_graph.json`` and open the aforementioned HTML file.

    Parameters
    ----------
    graph: nx.Graph
        The graph that shall be exported to the JSON format.
    output_file: str
        The file name to which the JSON data shall be exported.

    See Also
    --------
    hynet.visual.graph.create_networkx_graph

    References
    ----------
    .. [1] https://github.com/d3/d3
    """
    json_output = json_graph.node_link_data(graph)
    json_output = _clear_invalid_json_values(json_output)

    with open(output_file, 'w') as file:
        json.dump(json_output, file,
                  default=lambda x: x.__str__(),
                  allow_nan=False)


def _clear_invalid_json_values(dictionary):
    """
    Convert all ``nan`` and ``inf`` values in the dictionary to ``None``.

    This function ensures that there are no not-a-number and infinity values
    in the input dictionary, recursively. This avoids that some parsers throw
    errors when attempting to import the data.

    Parameters
    ----------
    dictionary: dict
        A dictionary, potentially containing invalid JSON values.

    Returns
    -------
    dictionary: dict
        A dictionary that has all invalid JSON values replaced by ``None``.
    """
    for k, v in dictionary.items():
        if isinstance(v, dict):
            _clear_invalid_json_values(v)
        if isinstance(v, list):
            for x in v:
                _clear_invalid_json_values(x)
        elif isinstance(v, float):
            if isnan(v) or isinf(v):
                dictionary[k] = None
    return dictionary


def _restore_index(dataframe):
    """
    Returns a copy of the data frame with its index in the column ``id``.

    Parameters
    ----------
    dataframe: pd.DataFrame
        Input data frame.

    Returns
    -------
    dataframe_copy: pd.DataFrame
        Deep copy of the data frame with an additional column ``id`` that
        contains the data frame's index.
    """
    dataframe_copy = copy.deepcopy(dataframe)
    dataframe_copy['id'] = dataframe_copy.index
    return dataframe_copy
