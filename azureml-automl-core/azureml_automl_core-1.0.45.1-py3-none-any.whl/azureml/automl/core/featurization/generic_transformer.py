# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Generic transformer."""
from typing import Optional, Dict, List
import logging
from ..featurizer.transformer.automltransformer import AutoMLTransformer
from ..featurizer.transformer.generic.generic_featurizers import GenericFeaturizers
from .._engineered_feature_names import \
    _GenerateEngineeredFeatureNames, _FeatureTransformers, _TransformationFunctionNames, \
    _Transformer, _OperatorNames, FeatureTypeRecognizer
from automl.client.core.common.types import TransformerType


class GenericTransformer(AutoMLTransformer):
    """Class for generic transformer."""
    def __init__(self, logger: Optional[logging.Logger] = None, is_onnx_compatible: bool = False):
        """
        Construct the GenericTransformer.
        :param logger: Logger to be injected to usage in this class.
        :param is_onnx_compatible: if works in onnx compatible mode
        """
        super().__init__()
        self.logger = logger or logging.getLogger(__name__)     # type: logging.Logger
        self.is_onnx_compatible = is_onnx_compatible

    def get_transforms(self,
                       column_groups: Dict[str, List[str]],
                       engineering_feature_name_class: _GenerateEngineeredFeatureNames) -> \
            List[TransformerType]:
        """
        Create a list of transforms for generic transforms.
        :param column_groups: Dictionary of column purpose and list of column labels for that purpose.
        :param engineering_feature_name_class: Existing engineered feature names.
        :return: Generic Transformations to use in a list.
        """
        return self.get_minibatchkmeans_transforms(column_groups, engineering_feature_name_class)

    def get_minibatchkmeans_transforms(self,
                                       column_groups: Dict[str, List[str]],
                                       engineering_feature_name_class: _GenerateEngineeredFeatureNames) -> \
            List[TransformerType]:
        """
        Create a list of transforms for minibatch kmeans.
        :param column_groups: Dictionary of column purpose and list of column labels for that purpose.
        :param engineering_feature_name_class: Existing engineered feature names.
        :return: MiniBatch Kmeans Transformations to use in a list.
        """
        # Check if this needs to be revisited once it is Onnx compatible
        tr = []  # type: List[TransformerType]
        if self.is_onnx_compatible:
            self.logger.info("MiniBatchKMeans is not onnx_commpatbile")
            return tr
        # do not apply if only one numeric column
        if FeatureTypeRecognizer.Numeric in column_groups and len(column_groups[FeatureTypeRecognizer.Numeric]) < 2:
            self.logger.info(
                "MiniBatchKMeans transformer not applied as dataset does not contain 2 or more Numeric features")
            return tr
        minibatchkmeans_transformer = GenericFeaturizers.minibatchkmeans_featurizer()
        clusters = minibatchkmeans_transformer.n_clusters
        features = ":".join([str(col) for col in column_groups[FeatureTypeRecognizer.Numeric]])
        CNAME = "MiniBatchKMeans_" + str(clusters) + ":" + features
        numeric_transformer = _Transformer(
            parent_feature_list=[str(CNAME)],
            transformation_fnc=_TransformationFunctionNames.Imputer,
            operator=_OperatorNames.Mean,
            feature_type=FeatureTypeRecognizer.Numeric,
            should_output=True)
        numeric_maxabsscaler_transformer = _Transformer(
            parent_feature_list=[1],
            transformation_fnc=_TransformationFunctionNames.MaxAbsScaler,
            operator=None,
            feature_type=FeatureTypeRecognizer.Numeric,
            should_output=False)
        generic_minibatchkmeans_transformer = _Transformer(
            parent_feature_list=[2],
            transformation_fnc=_TransformationFunctionNames.MiniBatchKMeans,
            operator=None,
            feature_type=FeatureTypeRecognizer.Numeric,
            should_output=True)
        feature_transformers = \
            _FeatureTransformers(
                [numeric_transformer, numeric_maxabsscaler_transformer, generic_minibatchkmeans_transformer])
        json_obj = feature_transformers.encode_transformations_from_list()
        alias_column_name = engineering_feature_name_class.get_raw_feature_alias_name(json_obj)
        tr = [(
            column_groups[FeatureTypeRecognizer.Numeric],
            [
                GenericFeaturizers.imputer(),
                GenericFeaturizers.maxabsscaler(),
                minibatchkmeans_transformer
            ],
            {'alias': alias_column_name}
        )]
        return tr
