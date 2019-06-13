from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline

from sri.pipelines.base import BasePipeline
from sri.psl.graph_matching_link_prediction import GraphMatchingLinkPrediction
from sri.psl.link_prediction import LinkPredictionHyperparams

DATASETS = {
    '49_facebook'
}

class GraphMatchingLinkPredictionPipeline(BasePipeline):
    def __init__(self):
        super().__init__(DATASETS, True)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        defaults = LinkPredictionHyperparams.defaults()
        hyperparams = LinkPredictionHyperparams(defaults, truth_threshold = 0.0000001)

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = GraphMatchingLinkPrediction.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_hyperparameter(
                name = 'link_prediction_hyperparams',
                argument_type = meta_base.ArgumentType.VALUE,
                data = hyperparams
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'Predictions', data_reference = 'steps.0.produce')

        return pipeline
