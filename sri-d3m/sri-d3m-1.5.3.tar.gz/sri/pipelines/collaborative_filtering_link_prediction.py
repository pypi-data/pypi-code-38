from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline

from sri.pipelines.base import BasePipeline
from sri.psl.collaborative_filtering_link_prediction import CollaborativeFilteringLinkPrediction

DATASETS = {
    '60_jester'
}


class CollaborativeFilteringLinkPredictionPipeline(BasePipeline):

    CHALLENGE_PROBLEMS = ['59_LP_karate']

    def __init__(self):
        problems = DATASETS
        super().__init__(problems, True)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = CollaborativeFilteringLinkPrediction.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'Predictions', data_reference = 'steps.0.produce')

        return pipeline
