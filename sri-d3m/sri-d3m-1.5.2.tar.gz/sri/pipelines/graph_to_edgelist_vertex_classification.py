from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline

from sri.pipelines.base import BasePipeline
from sri.graph.graph_to_edgelist import GraphToEdgeList
from sri.graph.vertex_classification import VertexClassificationParser

DATASETS = {
    'LL1_EDGELIST_net_nomination_seed',
    'LL1_VTXC_1343_cora',
    'LL1_VTXC_1369_synthetic',
    'LL1_net_classification_seed',
}

class GraphToEdgeListVertexClassificationPipeline(BasePipeline):
    def __init__(self):
        super().__init__(DATASETS, False)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = VertexClassificationParser.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        step_1 = meta_pipeline.PrimitiveStep(primitive_description = GraphToEdgeList.metadata.query())
        step_1.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'steps.0.produce'
        )
        step_1.add_output('produce')
        pipeline.add_step(step_1)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'EdgeLists', data_reference = 'steps.1.produce')

        return pipeline
