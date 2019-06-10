from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline

import sri.pipelines.datasets as datasets
from sri.pipelines.base import BasePipeline
from sri.graph.node_splitter import GraphNodeSplitter, GraphNodeSplitterHyperparams

# TODO(eriq): This pipeline will not pass until we can set arguments. Maybe we need a wrapper primitive for testing?

class GraphNodeSplitterPipeline(BasePipeline):
    def __init__(self):
        super().__init__(datasets.get_graph_dataset_names(), False)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = GraphNodeSplitter.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.VALUE,
                # This will not work. Arguments have to be glued to other parts of the pipeline.
                data = container.List([1, 3], generate_metadata=True),
        )
        step_0.add_output('produce')
        step_0.add_output('produce_test')
        pipeline.add_step(step_0)

        pipeline.add_output(name = 'Train Splits', data_reference = 'steps.0.produce')
        pipeline.add_output(name = 'Test Splits', data_reference = 'steps.0.produce_test')

        return pipeline
