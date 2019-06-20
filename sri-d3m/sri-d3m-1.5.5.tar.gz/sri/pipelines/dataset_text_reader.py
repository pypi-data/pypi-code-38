from d3m.metadata import base as meta_base
from d3m.metadata import pipeline as meta_pipeline

from d3m.primitives.data_transformation.column_parser import DataFrameCommon as ColumnParser
from d3m.primitives.data_transformation.extract_columns_by_semantic_types import DataFrameCommon as ExtractColumnsBySemanticTypes
from d3m.primitives.data_transformation.dataset_to_dataframe import Common as DatasetToDataFrame
from d3m.primitives.data_transformation.conditioner import Conditioner
from d3m.primitives.data_preprocessing.dataset_text_reader import DatasetTextReader
from d3m.primitives.feature_selection.select_percentile import SKlearn as SelectPercentile
from d3m.primitives.classification.bernoulli_naive_bayes import SKlearn as BernoulliNaiveBayes
from d3m.primitives.data_transformation.construct_predictions import DataFrameCommon as ConstructPredictions

from sri.pipelines import datasets
from sri.pipelines.base import BasePipeline, ATTR_TYPE, TARG_TYPE

class DatasetTextReaderPipeline(BasePipeline):
    def __init__(self):
        super().__init__(('30_personae',), True)

    def _gen_pipeline(self):

        # Create pipeline elements
        tr = DatasetTextReader(hyperparams={})
        todf = DatasetToDataFrame(hyperparams=dict(dataframe_resource=None))
        cp = ColumnParser(hyperparams={})
        ext_attr = ExtractColumnsBySemanticTypes(hyperparams=dict(semantic_types=(ATTR_TYPE,)))
        ext_targ = ExtractColumnsBySemanticTypes(hyperparams=dict(semantic_types=(TARG_TYPE,)))
        cond = Conditioner(hyperparams=dict(ensure_numeric=True, maximum_expansion=30))
        bnb = BernoulliNaiveBayes(hyperparams=dict(
            alpha=10.0,
            binarize=0,
            fit_prior=False
        ))
        construct_pred = ConstructPredictions(hyperparams={})

        # Create pipeline instance
        pipeline = meta_pipeline.Pipeline()
        pipeline.add_input(name = 'inputs')

        # Add pipeline steps
        node = self._add_pipeline_step(pipeline, tr, inputs="inputs.0")
        input_node = self._add_pipeline_step(pipeline, todf, inputs=node)
        tnode = self._add_pipeline_step(pipeline, ext_targ, inputs=input_node)
        node = self._add_pipeline_step(pipeline, cp, inputs=input_node)
        node = self._add_pipeline_step(pipeline, ext_attr, inputs=node)
        node = self._add_pipeline_step(pipeline, cond, inputs=node)
        node = self._add_pipeline_step(pipeline, bnb, inputs=node, outputs=tnode)
        node = self._add_pipeline_step(pipeline, construct_pred, inputs=node, reference=input_node)


        # Add pipeline output
        pipeline.add_output(name="Results", data_reference=node)

        return pipeline
