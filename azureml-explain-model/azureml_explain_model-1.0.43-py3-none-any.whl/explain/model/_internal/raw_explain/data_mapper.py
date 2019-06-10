# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import numpy as np
import pandas
import scipy.sparse as sparse
from sklearn.pipeline import Pipeline

from .feature_mappers import encoders_to_mappers_dict, get_feature_mapper_for_pipeline, IdentityMapper, \
    PassThroughMapper, FuncTransformer

from .data_mapper_utils import extract_column, get_transformer_config_tuples_from_column_transformer, \
    get_transformer_config_tuples_from_transformations_list

try:
    from sklearn.compose import ColumnTransformer
    column_transformer_exists = True
except ImportError:
    column_transformer_exists = False


class TransformationsListTransformer:
    """Computes transformations on input data from a list of columns and pre-trained transformers in the same format
    that sklearn-pandas' DataFrameMapper expects."""
    def __init__(self, transformer_config_tuples):
        """

        :param transformer_config_tuples: transformer, transformer config associated with the transformer
        :type transformer_config_tuples: [(transformer, TransformerConfig)] where transformer is an object with a
        .transform method.
        """
        self._transformer_config_tuples = transformer_config_tuples

    def transform(self, x):
        """Transform data when the user provides a list of transformations in sklearn-pandas format.

        :param x: input data
        :type x: numpy.array or scipy.sparse matrix
        :return: transformed data
        """
        results = []
        for tr, tr_config in self._transformer_config_tuples:
            x_column = extract_column(x, tr_config)
            if tr is None:
                # The column is used as if transformer is None
                results.append(x_column)
            else:
                results.append(tr.transform(x_column))

        if any(map(sparse.issparse, results)):
            return sparse.hstack(results).tocsr()
        else:
            return np.hstack(tuple(results))


class DataMapper(object):
    """Class to transform raw features to engineered features using list of transformations."""

    def __init__(self, transformations=None):
        """Initialize DataMapper object.

        :param transformations: List of (column_name, transformer) tuples or sklearn.compose.ColumnTransformer
        :type transformations: list[tuple(str, (class containing .transform method))]
        :param examples: DataFrame or numpy array of input
        :type examples: pandas.DataFrame or numpy.array
        """
        self._transformer_config_tuples = self._get_transformer_config_tuples(transformations)
        self._feature_mappers_pipeline = self._build_feature_mappers_pipeline(self._transformer_config_tuples)
        self._transform = self._get_transform_func(transformations)
        self._feature_map = None

    @property
    def feature_map(self):
        """Feature map from raw to generated.

        :return: mapping from raw to generated features
        :rtype: list[list[int]]
        """
        if not self._feature_map:
            raise ValueError("feat map not built. Run Transform first.")
        return self._feature_map

    def _get_transform_func(self, transformations):
        """Gets the transform function that produces transformed data.

        :param transformations: list of transformations in sklearn-pandas format or sklearn.compose.ColumnTransformer
        object
        :type transformations: list[tuple] or sklearn.compose.ColumnTransformer
        :return: function that maps input data to transformed data.
        """
        if isinstance(transformations, list):
            return TransformationsListTransformer(self._transformer_config_tuples).transform
        elif column_transformer_exists and isinstance(transformations, ColumnTransformer):
            return transformations.transform
        else:
            raise Exception("{} not supported as transformations argument".format(type(transformations)))

    def _get_transformer_config_tuples(self, transformations):
        """Get input transformations in the form of transformer, TransformerConfig tuples

        :param transformations: list of transformations in sklearn-pandas format or sklearn.compose.ColumnTransformer
        object
        :type transformations: list[tuple] or sklearn.compose.ColumnTransformer
        :return: list of tuples of the type (transformer, TransformerConfig)
        """

        if isinstance(transformations, list):
            return get_transformer_config_tuples_from_transformations_list(transformations)
        elif column_transformer_exists and isinstance(transformations, ColumnTransformer):
            return get_transformer_config_tuples_from_column_transformer(transformations)

        raise Exception("Non-supported transformations argument passed.")

    def _build_feature_mappers_pipeline(self, transformations):
        """Generate a list of FeatureMappers that can transform as well as contain a featmap property

        :param transformations: from a list of transformer, TransformerConfig tuples, generate featuremappers.
        :type transformations: list[tuple]
        :return: list of tuples of TransformerConfig and FeatureMapper
        :rtype: list[tuple(TransformerConfig, FeatureMapper)]
        """
        result = []
        for transformer, config in transformations:
            result.append((config, self._get_feature_mapper(transformer, config)))

        return result

    def _get_feature_mapper(self, transformer, transformer_config):
        """Get FeatureMapper from transformer and columns list that can also get the associated featmap.

        :param transformer: object that has a transform method
        :type transformer: class that has a transform method
        :param transformer_config: TransformerConfig needed to get the right shape of input data for transformer
        :type transformer_config: TransformerConfig
        :return: feature mapper associated with the transformer
        :rtype: FeatureMapper
        """
        # if there is only one column, we can just look at the shape of final transformers and get result
        if len(transformer_config.columns) == 1:
            if transformer is None:
                if transformer_config.one_dimensional:
                    return IdentityMapper(FuncTransformer(lambda x: x))
                else:
                    return IdentityMapper(FuncTransformer(lambda x: x.reshape(-1, 1)))
            else:
                return PassThroughMapper(transformer)

        # if it is one of the supported transformations
        transformer_type = type(transformer)
        if transformer_type in encoders_to_mappers_dict:
            return encoders_to_mappers_dict[transformer_type](transformer)

        if isinstance(transformer, Pipeline):
            return get_feature_mapper_for_pipeline(transformer)

        # its a many to many or many to one map if we end up here
        raise ValueError("Many to many or many to one transformers not supported in raw explanations.")

    def _add_num_to_list_of_lists(self, num, list_of_list):
        """For a sequence of transformers in DataMappers, feature mapping from transformers need to add the number of
        columns generated from the previous set of transformers to their mapping in order to get the correct index of
        generated column. This helper function adds an integer to the integers in the list of lists which is the
        feature mapping.

        :param num: number to be added to the integers in list_of_list
        :type num: int
        :param list_of_list: feature map
        :type list_of_list: list[list[int]]
        :return: list of lists
        :rtype: list[list[int]]
        """
        result = []
        for lst in list_of_list:
            result.append([num + i for i in lst])
        return result

    def _build_feature_map(self, x, columns):
        """Build the feature map from the feature maps of list of transformation wrappers in DataMapper.

        :param columns: input columns either as string names for dataframe or list of integers for numpy array
        :type columns: list[str] or list[int]
        """
        # run all transform methods in feature mappers so that we have column counts filled in
        self._run_feature_mappers_transform(x)

        raw_to_engineered_map = {}
        last_num_cols = 0
        for transformer_config, feature_mapper in self._feature_mappers_pipeline:
            column_names = transformer_config.columns
            raw_to_engineered = self._add_num_to_list_of_lists(last_num_cols, feature_mapper.feature_map)

            for i, col in enumerate(column_names):
                if col not in raw_to_engineered_map:
                    raw_to_engineered_map[col] = []
                raw_to_engineered_map[col].extend(raw_to_engineered[i])

            # number of cols in engineered until this transformation
            last_num_cols += sum([len(x) for x in raw_to_engineered])

        feature_map = []
        # return the results in the order the columns are in the input
        for col in columns:
            feature_map.append(raw_to_engineered_map.get(col, []))

        self._feature_map = feature_map

    def _run_feature_mappers_transform(self, x):
        """Run the transform methods associated with each feature_mapper. This will set the featmaps.

        :param x: input data
        :type x: numpy array or DataFrame
        :return: numpy.array or sparse matrix
        """
        for transformer_config, feature_mapper in self._feature_mappers_pipeline:
            feature_mapper.transform(extract_column(x, transformer_config))

    def transform(self, x):
        """Transform input data given the transformations.

        :param x: input data
        :type x: pandas.DataFrame or numpy array
        :return: transformed data
        :rtype: numpy.array or scipy.sparse matrix
        """

        if self._feature_map is None:
            # pass a single example through the transformations list to build feature map
            columns = x.columns if isinstance(x, pandas.DataFrame) else list(range(x.shape[1]))
            self._build_feature_map(x[:1], columns)

        return self._transform(x)
