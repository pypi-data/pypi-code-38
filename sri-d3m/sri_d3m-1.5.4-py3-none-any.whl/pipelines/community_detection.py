from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline

from sri.pipelines import datasets
from sri.pipelines.base import BasePipeline
from sri.graph.community_detection import CommunityDetectionParser

from d3m.primitives.data_transformation.denormalize import Common as Denormalize
from d3m.primitives.data_transformation.normalize_graphs import Common as NormalizeGraphs

DATASETS = { '6_70_com_amazon' }


class CommunityDetectionParserNormalizedPipeline(BasePipeline):
    # Problems nominated as part of the Phase 2 TA1 evaluation
    # Some of these choices are obviously bizarre for this pipeline
    CHALLENGE_PROBLEMS = ['6_86_com_DBLP', 'LL1_bn_fly_drosophila_medulla_net', '38_sick', '1567_poker_hand']

    def __init__(self):
        super().__init__(datasets.get_dataset_names_by_task('communityDetection'), False)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = NormalizeGraphs.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        step_1 = meta_pipeline.PrimitiveStep(primitive_description = Denormalize.metadata.query())
        step_1.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'produce.0'
        )
        step_1.add_output('produce')
        pipeline.add_step(step_1)

        step_2 = meta_pipeline.PrimitiveStep(primitive_description = CommunityDetectionParser.metadata.query())
        step_2.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'produce.1'
        )
        step_2.add_output('produce')
        pipeline.add_step(step_2)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'Graphs', data_reference = 'steps.2.produce')

        return pipeline


class CommunityDetectionParserPipeline(BasePipeline):
    # Problems nominated as part of the Phase 2 TA1 evaluation
    # Some of these choices are obviously bizarre for this pipeline
    CHALLENGE_PROBLEMS = ['6_86_com_DBLP', 'LL1_bn_fly_drosophila_medulla_net', '38_sick', '1567_poker_hand']

    def __init__(self):
        super().__init__(datasets.get_dataset_names_by_task('communityDetection'), False)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = CommunityDetectionParser.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'Graphs', data_reference = 'steps.0.produce')

        return pipeline
