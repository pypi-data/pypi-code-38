from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline
from d3m.primitives.data_transformation.construct_predictions import DataFrameCommon as ConstructPredictions
# from d3m.primitives.data import ConstructPredictions

from sri.pipelines.base import BasePipeline
from sri.graph.graph_matching import GraphMatchingParser
from sri.graph.transform import GraphTransformer
from sri.psl.link_prediction import LinkPrediction

DATASETS = {
    '49_facebook'
}

class GraphMatchingTransformLPPipeline(BasePipeline):

    CHALLENGE_PROBLEMS = ['LL1_DIC28_net']

    def __init__(self):
        problems = DATASETS
        super().__init__(problems, True)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = GraphMatchingParser.metadata.query())
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
                data = 'match',
        )
        step_2.add_hyperparameter(
                name = 'truth_threshold',
                argument_type = meta_base.ArgumentType.VALUE,
                data = 0.0000001,
        )
        step_2.add_output('produce')
        pipeline.add_step(step_2)

        step_3 = meta_pipeline.PrimitiveStep(primitive_description = ConstructPredictions.metadata.query())
        step_3.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'steps.2.produce'
        )
        step_3.add_argument(
                name = 'reference',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'steps.2.produce'
        )
        step_3.add_hyperparameter(
                name = 'use_columns',
                argument_type = meta_base.ArgumentType.VALUE,
                data = [0, 1],
        )
        step_3.add_output('produce')
        pipeline.add_step(step_3)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'Links', data_reference = 'steps.3.produce')

        return pipeline
