ENTRYPOINTS = {
    'd3m.primitives': {
        'data_transformation.conditioner.Conditioner': 'sri.autoflow.conditioner:Conditioner',
        'data_preprocessing.dataset_text_reader.DatasetTextReader': 'sri.autoflow.dataset_text_reader:DatasetTextReader',
        'data_transformation.conditioner.StaticEnsembler': 'sri.autoflow.static_ensembler:StaticEnsembler',
        'classification.gaussian_classification.MeanBaseline': 'sri.baseline.mean:MeanBaseline',
        'data_transformation.collaborative_filtering_parser.CollaborativeFilteringParser': 'sri.graph.collaborative_filtering:CollaborativeFilteringParser',
        'community_detection.community_detection_parser.CommunityDetectionParser': 'sri.graph.community_detection:CommunityDetectionParser',
        'data_transformation.graph_matching_parser.GraphMatchingParser': 'sri.graph.graph_matching:GraphMatchingParser',
        'data_transformation.graph_transformer.GraphTransformer': 'sri.graph.transform:GraphTransformer',
        'data_transformation.vertex_nomination_parser.VertexNominationParser': 'sri.graph.vertex_nomination:VertexNominationParser',
        'link_prediction.collaborative_filtering_link_prediction.CollaborativeFilteringLinkPrediction': 'sri.psl.collaborative_filtering_link_prediction:CollaborativeFilteringLinkPrediction',
        'classification.community_detection.CommunityDetection': 'sri.psl.community_detection:CommunityDetection',
        # Until we have preprocessing code to prepare the data, do not expose this entrypoint.
        # 'sri.psl.GeneralRelational': 'sri.psl.general_relational:GeneralRelational',
        'classification.general_relational_dataset.GeneralRelationalDataset': 'sri.psl.general_relational_dataset:GeneralRelationalDataset',
        'link_prediction.graph_matching_link_prediction.GraphMatchingLinkPrediction': 'sri.psl.graph_matching_link_prediction:GraphMatchingLinkPrediction',
        'link_prediction.link_prediction.LinkPrediction': 'sri.psl.link_prediction:LinkPrediction',
        'time_series_forecasting.time_series_to_list.RelationalTimeseries': 'sri.psl.relational_timeseries:RelationalTimeseries',
        'classification.vertex_nomination.VertexNomination': 'sri.psl.vertex_nomination:VertexNomination',
        'data_transformation.stacking_operator.StackingOperator': 'sri.tpot.stacking:StackingOperator',
        'data_transformation.zero_count.ZeroCount': 'sri.tpot.zerocount:ZeroCount',

        # TODO(eriq): Will be moved to common primitives when actually implemented.
        'data_transformation.graph_node_splitter.GraphNodeSplitter': 'sri.graph.node_splitter:GraphNodeSplitter',
        'data_transformation.graph_to_edge_list.GraphToEdgeList': 'sri.graph.graph_to_edgelist:GraphToEdgeList',
        'data_transformation.edge_list_to_graph.EdgeListToGraph': 'sri.graph.edgelist_to_graph:EdgeListToGraph',
    }
}

def get_entrypoints_definition():
    all_entrypoints = {}

    for (top_level, entrypoints) in ENTRYPOINTS.items():
        points = []

        for (entrypoint, target) in entrypoints.items():
            points.append("%s = %s" % (entrypoint, target))

        all_entrypoints[top_level] = points

    return all_entrypoints

# Get all the entrypoints.
def main():
    for (top_level, entrypoints) in ENTRYPOINTS.items():
        for entrypoint in entrypoints:
            print("%s.%s" % (top_level, entrypoint))

if __name__ == '__main__':
    main()
