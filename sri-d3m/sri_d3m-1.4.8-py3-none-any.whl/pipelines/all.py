# Information on all pipelines and which primitives are used.

import json

from sri.pipelines.base import BasePipeline
from sri.pipelines.baseline_mean import MeanBaselinePipeline
from sri.pipelines.collaborative_filtering import CollaborativeFilteringParserPipeline
from sri.pipelines.collaborative_filtering_link_prediction import CollaborativeFilteringLinkPredictionPipeline
from sri.pipelines.collaborative_filtering_transform import CollaborativeFilteringTransformPipeline
from sri.pipelines.collaborative_filtering_transform_lp import CollaborativeFilteringTransformLPPipeline
from sri.pipelines.community_detection import CommunityDetectionParserPipeline
from sri.pipelines.community_detection_psl import CommunityDetectionPSLPipeline
from sri.pipelines.edgelist_to_graph_vertex_nomination import EdgeListToGraphVertexNominationPipeline
from sri.pipelines.general_relational_dataset import GeneralRelationalDatasetPipeline
from sri.pipelines.graph_matching import GraphMatchingParserPipeline
from sri.pipelines.graph_matching_link_prediction import GraphMatchingLinkPredictionPipeline
from sri.pipelines.graph_matching_transform import GraphMatchingTransformPipeline
from sri.pipelines.graph_matching_transform_lp import GraphMatchingTransformLPPipeline
from sri.pipelines.graph_node_splitter import GraphNodeSplitterPipeline
from sri.pipelines.graph_to_edgelist_vertex_nomination import GraphToEdgeListVertexNominationPipeline
from sri.pipelines.relational_timeseries import RelationalTimeseriesPipeline
from sri.pipelines.vertex_nomination import VertexNominationParserPipeline
from sri.pipelines.vertex_nomination_psl import VertexNominationPSLPipeline
from sri.pipelines.zero_count import ZeroCountPipeline
from sri.pipelines.conditioner import ConditionerPipeline
from sri.pipelines.dataset_text_reader import DatasetTextReaderPipeline

from sri.baseline.mean import MeanBaseline
from sri.graph.collaborative_filtering import CollaborativeFilteringParser
from sri.graph.community_detection import CommunityDetectionParser
from sri.graph.edgelist_to_graph import EdgeListToGraph
from sri.graph.graph_matching import GraphMatchingParser
from sri.graph.graph_to_edgelist import GraphToEdgeList
from sri.graph.transform import GraphTransformer
from sri.graph.node_splitter import GraphNodeSplitter
from sri.graph.vertex_nomination import VertexNominationParser
from sri.psl.collaborative_filtering_link_prediction import CollaborativeFilteringLinkPrediction
from sri.psl.community_detection import CommunityDetection
from sri.psl.general_relational_dataset import GeneralRelationalDataset
from sri.psl.graph_matching_link_prediction import GraphMatchingLinkPrediction
from sri.psl.link_prediction import LinkPrediction
from sri.psl.relational_timeseries import RelationalTimeseries
from sri.psl.vertex_nomination import VertexNomination

PIPELINES_BY_PRIMITIVE = {
    'd3m.primitives.data_transformation.graph_node_splitter.GraphNodeSplitter': [
        # TODO(eriq): Disabled until other pipeline support (see file).
        # GraphNodeSplitterPipeline,
    ],
    'd3m.primitives.data_transformation.graph_to_edge_list.GraphToEdgeList': [
        EdgeListToGraphVertexNominationPipeline,
        GraphToEdgeListVertexNominationPipeline,
    ],
    'd3m.primitives.data_transformation.edge_list_to_graph.EdgeListToGraph': [
        EdgeListToGraphVertexNominationPipeline,
    ],
    'd3m.primitives.classification.gaussian_classification.MeanBaseline': [
        MeanBaselinePipeline,
    ],
    'd3m.primitives.data_transformation.collaborative_filtering_parser.CollaborativeFilteringParser': [
        CollaborativeFilteringParserPipeline,
        CollaborativeFilteringTransformPipeline,
        CollaborativeFilteringTransformLPPipeline,
    ],
    'd3m.primitives.community_detection.community_detection_parser.CommunityDetectionParser': [
        CommunityDetectionParserPipeline,
        CommunityDetectionPSLPipeline,
    ],
    'd3m.primitives.data_transformation.graph_matching_parser.GraphMatchingParser': [
        GraphMatchingParserPipeline,
        GraphMatchingTransformPipeline,
        GraphMatchingTransformLPPipeline,
    ],
    'd3m.primitives.data_transformation.graph_transformer.GraphTransformer': [

        CollaborativeFilteringTransformPipeline,
        CollaborativeFilteringTransformLPPipeline,
        # See https://jira.sri.com/browse/D3M-202
        # GraphMatchingTransformPipeline,
        # GraphMatchingTransformLPPipeline,
    ],
    'd3m.primitives.data_transformation.vertex_nomination_parser.VertexNominationParser': [
        EdgeListToGraphVertexNominationPipeline,
        GraphToEdgeListVertexNominationPipeline,
        VertexNominationParserPipeline,
        VertexNominationPSLPipeline,
    ],
    'd3m.primitives.link_prediction.collaborative_filtering_link_prediction.CollaborativeFilteringLinkPrediction': [
        CollaborativeFilteringLinkPredictionPipeline,
    ],
    'd3m.primitives.classification.community_detection.CommunityDetection': [
        CommunityDetectionPSLPipeline,
    ],
    'd3m.primitives.classification.general_relational_dataset.GeneralRelational': [
    ],
    'd3m.primitives.classification.general_relational_dataset.GeneralRelationalDataset': [
        GeneralRelationalDatasetPipeline,
    ],
    'd3m.primitives.link_prediction.graph_matching_link_prediction.GraphMatchingLinkPrediction': [
        GraphMatchingLinkPredictionPipeline,
    ],
    'd3m.primitives.link_prediction.link_prediction.LinkPrediction': [
        CollaborativeFilteringTransformLPPipeline,
        GraphMatchingTransformLPPipeline,
    ],
    'd3m.primitives.time_series_forecasting.time_series_to_list.RelationalTimeseries': [
        RelationalTimeseriesPipeline,
    ],
    'd3m.primitives.classification.vertex_nomination.VertexNomination': [
        VertexNominationPSLPipeline,
    ],
    'd3m.primitives.data_transformation.zero_count.ZeroCount' : [
        ZeroCountPipeline,
    ],
    'd3m.primitives.data_transformation.conditioner.Conditioner' : [
        ConditionerPipeline,
    ],
    'd3m.primitives.data_preprocessing.dataset_text_reader.DatasetTextReader' : [
        DatasetTextReaderPipeline,
    ]
}

def get_primitives():
    return PIPELINES_BY_PRIMITIVE.keys()

def get_pipelines(primitive = None):
    if (primitive is not None):
        if (primitive not in PIPELINES_BY_PRIMITIVE):
            return []
        return PIPELINES_BY_PRIMITIVE[primitive]

    pipelines = set()
    for primitive_pipelines in PIPELINES_BY_PRIMITIVE.values():
        pipelines = pipelines | set(primitive_pipelines)
    return pipelines

if __name__ == '__main__':
    output = PIPELINES_BY_PRIMITIVE.copy()
    for key in output:
        output[key] = [pipeline.__name__ for pipeline in output[key]]
    print(json.dumps(output, indent = 4))
