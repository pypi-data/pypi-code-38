from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline

import sri.pipelines.datasets as datasets
from sri.pipelines.base import BasePipeline
from sri.graph.vertex_classification import VertexClassificationParser
from sri.psl.vertex_classification import VertexClassification


class VertexClassificationPSLPipeline(BasePipeline):

    CHALLENGE_PROBLEMS = ['LL1_EDGELIST_net_nomination_seed', 'LL1_net_nomination_seed',
                          'LL1_VTXC_1343_cora', 'LL1_VTXC_1369_synthetic']

    def __init__(self):
        problems = datasets.get_dataset_names_by_task('vertexClassification')
        super().__init__(problems, True)

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

        step_1 = meta_pipeline.PrimitiveStep(primitive_description = VertexClassification.metadata.query())
        step_1.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'steps.0.produce'
        )
        step_1.add_output('produce')
        pipeline.add_step(step_1)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'Results', data_reference = 'steps.1.produce')

        return pipeline
