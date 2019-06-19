from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline
#from d3m.primitives.datasets import DatasetToDataFrame
from d3m.primitives.data_transformation.dataset_to_dataframe import Common as DatasetToDataFrame
#from d3m.primitives.data import ExtractColumnsBySemanticTypes
from d3m.primitives.data_transformation.extract_columns_by_semantic_types import DataFrameCommon as ExtractColumnsBySemanticTypes

from sri.pipelines import datasets
from sri.pipelines.base import BasePipeline
from sri.psl.relational_timeseries import RelationalTimeseries

SKIP_DATASETS = {
    # Cannot be read by DataSetToDataFrame
    'LL1_736_stock_market',
}

class RelationalTimeseriesPipeline(BasePipeline):

    CHALLENGE_PROBLEMS = ['LL1_736_population_spawn', 'LL1_736_population_spawn_simpler', 'LL1_736_stock_market',
                          '56_sunspots_monthly']

    def __init__(self):
        problems = set(datasets.get_dataset_names_by_task('timeSeriesForecasting')) - SKIP_DATASETS
        super().__init__(problems, True)

    def _gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = DatasetToDataFrame.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        step_1 = meta_pipeline.PrimitiveStep(primitive_description = ExtractColumnsBySemanticTypes.metadata.query())
        step_1.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'steps.0.produce'
        )
        step_1.add_hyperparameter(
                name = 'semantic_types',
                argument_type = meta_base.ArgumentType.VALUE,
                data = [
                    'https://metadata.datadrivendiscovery.org/types/PrimaryKey',
                    'https://metadata.datadrivendiscovery.org/types/Attribute',
                ]
        )
        step_1.add_output('produce')
        pipeline.add_step(step_1)

        step_2 = meta_pipeline.PrimitiveStep(primitive_description = ExtractColumnsBySemanticTypes.metadata.query())
        step_2.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'steps.0.produce'
        )
        step_2.add_hyperparameter(
                name = 'semantic_types',
                argument_type = meta_base.ArgumentType.VALUE,
                data = [
                    'https://metadata.datadrivendiscovery.org/types/PrimaryKey',
                    'https://metadata.datadrivendiscovery.org/types/TrueTarget',
                ]
        )
        step_2.add_output('produce')
        pipeline.add_step(step_2)

        step_3 = meta_pipeline.PrimitiveStep(primitive_description = RelationalTimeseries.metadata.query())
        step_3.add_argument(
                name = 'inputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'steps.1.produce'
        )
        step_3.add_argument(
                name = 'outputs',
                argument_type = meta_base.ArgumentType.CONTAINER,
                data_reference = 'steps.2.produce'
        )
        step_3.add_output('produce')
        pipeline.add_step(step_3)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'Results', data_reference = 'steps.3.produce')

        return pipeline
