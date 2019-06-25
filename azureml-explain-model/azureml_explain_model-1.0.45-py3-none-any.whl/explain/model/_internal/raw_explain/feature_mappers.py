# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Binarizer, KernelCenterer, LabelEncoder, MaxAbsScaler, MinMaxScaler, Normalizer, \
    OneHotEncoder, QuantileTransformer, RobustScaler, StandardScaler


def get_feature_mapper_for_pipeline(pipeline_obj):
    """Get FeatMapper object from a sklearn.pipeline.Pipeline object.

    :param pipeline_obj: pipeline object
    :type pipeline_obj: sklearn.pipeline.Pipeline
    :return: feat mapper for pipeline
    :rtype: PipelineFeatureMapper
    """
    """Get feat mapper for a pipeline, iterating over the transformers."""

    steps = []
    count = 0
    for _, transformer in pipeline_obj.steps:
        transformer_type = type(transformer)
        if transformer_type in encoders_to_mappers_dict:
            steps.append((str(count), encoders_to_mappers_dict[transformer_type](transformer)))
            count += 1
        elif transformer_type == Pipeline:
            steps.append((str(count), get_feature_mapper_for_pipeline(transformer)))
        else:
            steps.append((str(count), ManytoManyMapper(transformer)))

    return PipelineFeatureMapper(Pipeline(steps))


class FeatureMapper(object):
    """A class that supports both feature map from raw to engineered as well as a transform method."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, transformer):
        """

        :param transformer: object that has a .transform method
        :type transformer: class that has a .transform method
        """
        self._transformer = transformer
        self._feature_map = None
        self._feature_map_weights = None

    @property
    def transformer(self):
        return self._transformer

    @abstractmethod
    def transform(self, x):
        """

        :param x: input data
        :type x: pandas.DataFrame or numpy.array
        :rtype: transformed data
        :rtype: numpy.array or scipy.sparse matrix
        """
        pass

    @property
    def feature_map(self):
        """

        :return: feature map from raw to generated
        :rtype: list[list[int]]
        """
        if self._feature_map is None:
            raise ValueError("transform not called")
        return self._feature_map

    @property
    def feature_map_weights(self):
        """Weights associated with each generated feature importance.

        :return: weights associated with the feature map
        :rtype: list[list[float]]
        """
        if self._feature_map_weights is None:
            raise ValueError("transform not called")
        return self._feature_map_weights

    def set_feature_map(self, feature_map):
        """

        :param feature_map: feature map associated with the FeatureMapper
        :type feature_map list[[int]]
        """
        self._feature_map = feature_map

    def set_feature_map_weights(self, weights):
        """Set feature map weights associated with this FeatureMapper.

        :param weights: weights associated with feature map
        :type weights: list[[float]]
        """
        self._feature_map_weights = weights

    def fit(self, x):
        """Dummy fit so that this can go in an sklearn.pipeline.Pipeline.

        :param x: input data
        :type x: numpy.array or pandas.DataFrame
        :return: self
        :rtype: FeatureMapper
        """
        return self


class IdentityMapper(FeatureMapper):
    """FeatMapper for one to one mappings."""

    def __init__(self, transformer):
        """

        :param transformer: object that has a .transform method
        :type transformer: class that has a .transform method
        """
        super(IdentityMapper, self).__init__(transformer)

    def _build_feature_map(self, num_cols):
        """Build a feature map for one to one mappings from raw to generated.

        :param num_cols: number of columns in input.
        :type num_cols: int
        """
        self.set_feature_map([[i] for i in range(num_cols)])
        self.set_feature_map_weights([[1]] * num_cols)

    def transform(self, x):
        """Transform input data.

        :param x: input data
        :type x: numpy.array or pandas.DataFrame
        :return: transformed data
        :rtype: numpy.array
        """
        result = self.transformer.transform(x)
        if self._feature_map is None:
            self._build_feature_map(result.shape[1])

        return result


class PassThroughMapper(FeatureMapper):
    """FeatureMapper to use when only one column is the input."""

    def __init__(self, transformer):
        """

        :param transformer: object that has a .transform method
        :type transformer: class that has a .transform method
        """
        super(PassThroughMapper, self).__init__(transformer)

    def _build_feature_map(self, num_cols):
        """Build a feature map for mappings from raw to generated when the input column is just one.

        :param num_cols: number of input columns
        :type num_cols: [int]
        """
        self.set_feature_map([list(range(num_cols))])
        self.set_feature_map_weights([[1] * num_cols])

    def transform(self, x):
        """

        :param x: input data
        :type x: numpy.array or pandas.DataFrame
        :return: transformed data
        :rytpe: numpy.array or scipy.sparse matrix
        """
        x_transformed = self.transformer.transform(x)
        if self._feature_map is None:
            self._build_feature_map(x_transformed.shape[1])

        return x_transformed


class PipelineFeatureMapper(FeatureMapper):
    """FeatureMapper for a sklearn pipeline of feat mappers"""

    def __init__(self, transformer):
        """

        :param transformer: object that has a .transform method
        :type transformer: class that has a .transform method
        """
        super(PipelineFeatureMapper, self).__init__(transformer)

    def _get_next_step_feature_map_weights(self, from_map=None, from_weights=None, to_map=None, to_weights=None):
        """For two transform steps "from" (represented by from_map and from_weights) and "to" {represented by to_map
         and to_weights) in a pipeline, get the map in terms of the features of the step after "to" step and weights
         that apply to the features that result after "to" step.

        :param from_map: list of list representing indices of the generated features after "from" step
        :type from_map: list[list[int]]
        :param from_weights: list of list of weights to be applied to the generated features after "from" step
        :type from_weights: list[list[float]]
        :param to_map: list of list representing indices of the generated features after "to" step
        :type to_map: list[list[int]]
        :param to_weights: list of list of weights to be applied to the generated features after "to" step
        :type to_weights: list[list[float]]
        :return: tuple of feature map from the features before from_map to features after to_map
        :rtype: tuple[list[list[int]], list[list[float]]]
        """
        new_map = []
        new_weights = []
        # iterate over feature indices array associated with each raw feature in from_map and the associated weights
        for from_map_i, from_weights_i in zip(from_map, from_weights):
            # Each raw feature in from_map is represented by an array of indices to generated features. from_weights
            # carries the associated weights to be applied to the feature importances.
            feature_weights_dict = OrderedDict()
            for feature_index, feature_weight in zip(from_map_i, from_weights_i):
                # feature_index is a feature in to_map. Which in to_map is itself represented by an array of indices to
                # the features that are generated by to_map.
                to_index_weight_pairs = zip(to_map[feature_index], to_weights[feature_index])
                for to_generated_index, to_generated_weight in to_index_weight_pairs:
                    feature_weights_dict[to_generated_index] = feature_weight * to_generated_weight + \
                        feature_weights_dict.get(to_generated_index, 0)
            new_map.append(list(feature_weights_dict.keys()))
            new_weights.append(list(feature_weights_dict.values()))

        return new_map, new_weights

    def _build_feature_map(self, feature_mappers):
        """Build a feature map for mappings from raw to generated for a pipeline of FeatMapper's.

        :param feature_mappers: list of feat mappers
        :type feature_mappers: [FeatureMapper]
        """

        curr_map = feature_mappers[0].feature_map
        curr_weights = feature_mappers[0].feature_map_weights
        for i in range(1, len(feature_mappers)):
            curr_map, curr_weights = self._get_next_step_feature_map_weights(
                from_map=curr_map, from_weights=curr_weights, to_map=feature_mappers[i].feature_map,
                to_weights=feature_mappers[i].feature_map_weights)

        self.set_feature_map(curr_map)
        self.set_feature_map_weights(curr_weights)

    def transform(self, x):
        """

        :param x: input data
        :type x: numpy.array or pandas.DataFrame
        :return: transformed data
        :rtype: numpy.array or scipy.sparse matrix
        """
        ret = self.transformer.transform(x)
        if self._feature_map is None:
            self._build_feature_map([s[1] for s in self._transformer.steps])

        return ret


class OneHotEncoderMapper(FeatureMapper):
    """OneHotEncoder FeatureMapper"""
    def __init__(self, transformer):
        """Build a feature map for OneHotEncoder.

        :param transformer: object of type onehotencoder
        :type transformer: sklearn.preprocessing.OneHotEncoder
        """
        super(OneHotEncoderMapper, self).__init__(transformer)

    def _build_feature_map(self):
        """Build feature map when transformer is a one hot encoder."""
        feat_map = []
        feat_weights = []
        last_num_cols = 0
        for cat in self.transformer.categories_:
            feat_map.append([i + last_num_cols for i in range(len(cat))])
            feat_weights.append([1] * len(cat))
            last_num_cols += len(cat)

        self.set_feature_map(feat_map)
        self.set_feature_map_weights(feat_weights)

    def transform(self, x):
        """

        :param x: input data
        :type x: numpy.array
        :return: transformed data
        :rtype x: numpy.array
        """
        ret = self.transformer.transform(x)
        if self._feature_map is None:
            self._build_feature_map()

        return ret


class ManytoManyMapper(FeatureMapper):
    def __init__(self, transformer):
        """Build a feature map for a many to many transformer.

        :param transformer: object that has a .transform method
        :type transformer: class that has a .transform method
        """
        super(ManytoManyMapper, self).__init__(transformer)
        self._transformer = transformer

    def _build_feature_map(self, in_feature_len=None, out_feature_len=None):
        """Generate a feature map so that weights of generated features are equally divided between parents and every
        parent feature map has every generated feature.

        :param in_feature_len: number of input features
        :type in_feature_len: int
        :param out_feature_len: number of output features
        :type out_feature_len: int
        """
        self.set_feature_map([list(range(out_feature_len)) for _ in range(in_feature_len)])
        self.set_feature_map_weights([[1.0 / in_feature_len] * out_feature_len] * in_feature_len)

    def transform(self, x):
        """Get transformed data from input.

        :param x: input data
        :type x: numpy.array or pandas.DataFrame
        :return: transformed data
        :rtype: numpy.array or scipy.sparse matrix
        """
        x_transformed = self._transformer.transform(x)
        if self._feature_map is None:
            self._build_feature_map(in_feature_len=x.shape[1], out_feature_len=x_transformed.shape[1])

        return x_transformed


class FuncTransformer:
    def __init__(self, func):
        """

        :param func: function that transforms the data
        :type func: function that takes in numpy.array/pandas.Dataframe and outputs numpy.array or scipy.sparse matrix
        """
        self._func = func

    def transform(self, x):
        """

        :param x: input data
        :type x: numpy.array or pandas.DataFrame
        :return: transformed data
        :rtype: numpy.array or scipy.sparse matrix
        """
        return self._func(x)


# dictionary containing currently identified preprocessors/transformers that result in one to many maps.
encoders_to_mappers_dict = {
    Binarizer: IdentityMapper,
    KernelCenterer: IdentityMapper,
    LabelEncoder: IdentityMapper,
    MaxAbsScaler: IdentityMapper,
    MinMaxScaler: IdentityMapper,
    Normalizer: IdentityMapper,
    QuantileTransformer: IdentityMapper,
    RobustScaler: IdentityMapper,
    StandardScaler: IdentityMapper,
    OneHotEncoder: OneHotEncoderMapper,
}

try:
    from sklearn.impute import MissingIndicator, SimpleImputer
    from sklearn.preprocessing import KBinsDiscretizer, OrdinalEncoder, PowerTransformer

    encoders_to_mappers_dict.update([
        (SimpleImputer, IdentityMapper),
        (KBinsDiscretizer, IdentityMapper),
        (MissingIndicator, IdentityMapper),
        (OrdinalEncoder, IdentityMapper),
        (PowerTransformer, IdentityMapper)
    ])
except ImportError:
    # sklearn version earlier than 0.20.0
    pass
