from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline

from sri.pipelines.base import BasePipeline
from sri.graph.collaborative_filtering import CollaborativeFilteringParser
from sri.graph.transform import GraphTransformer
from sri.psl.link_prediction import LinkPrediction

DATASETS = {
    '60_jester'
}

class CollaborativeFilteringTransformLPPipeline(BasePipeline):
    def __init__(self):
        super().__init__(DATASETS, True)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = CollaborativeFilteringParser.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        step_1 = meta_pipeline.PrimitiveStep(primitive_description = GraphTransformer.metadata.query())
        step_1.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'steps.0.produce'
        )
        step_1.add_output('produce')
        pipeline.add_step(step_1)

        step_2 = meta_pipeline.PrimitiveStep(primitive_description = LinkPrediction.metadata.query())
        step_2.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'steps.1.produce'
        )
        step_2.add_hyperparameter(
                name = 'prediction_column',
                argument_type = meta_base.ArgumentType.VALUE,
                data = 'rating',
        )
        step_2.add_output('produce')
        pipeline.add_step(step_2)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'Links', data_reference = 'steps.2.produce')

        return pipeline
