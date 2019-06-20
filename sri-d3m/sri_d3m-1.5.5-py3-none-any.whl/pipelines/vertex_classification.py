from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline

import sri.pipelines.datasets as datasets
from sri.pipelines.base import BasePipeline
from sri.graph.vertex_classification import VertexClassificationParser

class VertexClassificationParserPipeline(BasePipeline):
    def __init__(self):
        super().__init__(datasets.get_dataset_names_by_task('vertexClassification'), False)

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

        # Adding output step to the pipeline
        pipeline.add_output(name = 'Graphs', data_reference = 'steps.0.produce')

        return pipeline
