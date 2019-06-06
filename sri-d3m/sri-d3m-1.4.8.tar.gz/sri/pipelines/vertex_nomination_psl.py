from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline

import sri.pipelines.datasets as datasets
from sri.pipelines.base import BasePipeline
from sri.graph.vertex_nomination import VertexNominationParser
from sri.psl.vertex_nomination import VertexNomination

SKIP_DATASETS = {
    # Unsupervised, but not labeled as such.
    'DS01876',
}

class VertexNominationPSLPipeline(BasePipeline):
    def __init__(self):
        super().__init__(set(datasets.get_dataset_names_by_task('vertexNomination')) - SKIP_DATASETS, True)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = VertexNominationParser.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        step_1 = meta_pipeline.PrimitiveStep(primitive_description = VertexNomination.metadata.query())
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
