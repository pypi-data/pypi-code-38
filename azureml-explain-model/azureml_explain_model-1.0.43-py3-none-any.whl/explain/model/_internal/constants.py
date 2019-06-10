# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Defines constants for explain model."""

from enum import Enum


class BackCompat(object):
    """Constants necessary for supporting old versions of our product"""
    FEATURE_NAMES = 'feature_names'
    NAME = 'name'
    OLD_NAME = 'old_name'
    OVERALL_FEATURE_ORDER = 'overall_feature_order'
    OVERALL_IMPORTANCE_ORDER = 'overall_importance_order'
    OVERALL_SUMMARY = 'overall_summary'
    PER_CLASS_FEATURE_ORDER = 'per_class_feature_order'
    PER_CLASS_IMPORTANCE_ORDER = 'per_class_importance_order'
    PER_CLASS_SUMMARY = 'per_class_summary'
    SHAP_VALUES = 'shap_values'


class ExplainerArgs(object):
    """Constants for explainer arguments"""
    TRANSFORMATIONS = "transformations"


class ExplanationParams(object):
    """Constants for explanation parameters"""
    EXPECTED_VALUES = 'expected_values'
    CLASSES = 'classes'
    EXPLANATION = 'explanation'
    SCORING_EXPLAINER = 'scoring_explainer'


class History(object):
    """Constants related to uploading assets to run history"""
    BLOCK_SIZE = 'block_size'
    CLASSES = 'classes'
    UPLOAD_TIME = 'upload_time'
    EXPECTED_VALUES = 'expected_values'
    EXPLANATION = 'explanation'
    EXPLANATION_ASSET = 'explanation_asset'
    EXPLANATION_ASSET_TYPE_V1 = 'azureml.v1.model.explanation'
    EXPLANATION_ASSET_TYPE_V2 = 'azureml.v2.model.explanation'
    EXPLANATION_ASSET_TYPE_V3 = 'azureml.v3.model.explanation'
    EXPLANATION_ASSET_TYPE_V4 = 'azureml.v4.model.explanation'
    EXPLANATION_ID = 'explanation_id'
    FEATURES = 'features'
    GLOBAL_IMPORTANCE_NAMES = 'global_importance_names'
    GLOBAL_IMPORTANCE_RANK = 'global_importance_rank'
    GLOBAL_IMPORTANCE_VALUES = 'global_importance_values'
    ID = 'id'
    LOCAL_IMPORTANCE_RANK = 'local_importance_rank'
    LOCAL_IMPORTANCE_VALUES = 'local_importance_values'
    MAX_NUM_BLOCKS = 'max_num_blocks'
    METADATA_ARTIFACT = 'metadata_artifact_path'
    METHOD = 'method'
    NAME = 'name'
    NUM_BLOCKS = 'num_blocks'
    NUM_CLASSES = 'num_classes'
    NUM_FEATURES = 'num_features'
    ORDERED_LOCAL_IMPORTANCE_VALUES = 'ordered_local_importance_values'
    PER_CLASS_NAMES = 'per_class_names'
    PER_CLASS_RANK = 'per_class_rank'
    PER_CLASS_VALUES = 'per_class_values'
    PER_CLASS_IMPORTANCE_NAMES = 'per_class_importance_names'
    PER_CLASS_IMPORTANCE_RANK = 'per_class_importance_rank'
    PER_CLASS_IMPORTANCE_VALUES = 'per_class_importance_values'
    PREFIX = 'prefix'
    PROPERTIES = 'properties'
    RANKED_GLOBAL_NAMES = 'ranked_global_names'
    RANKED_GLOBAL_VALUES = 'ranked_global_values'
    RANKED_PER_CLASS_NAMES = 'ranked_per_class_names'
    RANKED_PER_CLASS_VALUES = 'ranked_per_class_values'
    RICH_METADATA = 'rich_metadata'
    TYPE = 'type'
    VERSION = 'version'
    VERSION_TYPE = 'version_type'
    COMMENT = 'comment'
    SCORING_MODEL = 'scoring_model'


class ExplainType(object):
    """Constants for model and explainer type information, useful for visualization"""
    CLASSIFICATION = 'classification'
    DATA = 'data_type'
    EXPLAIN = 'explain_type'
    EXPLAINER = 'explainer'
    FUNCTION = 'function'
    HAN = 'han'
    LIME = 'lime'
    METHOD = 'method'
    MIMIC = 'mimic'
    MODEL = 'model_type'
    MODEL_CLASS = 'model_class'
    MODEL_TASK = 'model_task'
    REGRESSION = 'regression'
    SHAP = 'shap'
    SHAP_DEEP = 'shap_deep'
    SHAP_KERNEL = 'shap_kernel'
    SHAP_TREE = 'shap_tree'
    TABULAR = 'tabular'
    TEXT = 'text'
    PFI = 'pfi'


class IO(object):
    """File input and output related constants"""
    JSON = 'json'
    PICKLE = 'pickle'
    UTF8 = 'utf-8'


class ExplainParams(object):
    """Constants for explain model (init, explain_local and explain_global) parameters"""
    CLASSES = 'classes'
    CLASSIFICATION = 'classification'
    DATA_MAPPER = 'data_mapper'
    DATA_MAPPER_INTERNAL = '_data_mapper'
    EXPECTED_VALUES = 'expected_values'
    FEATURES = 'features'
    GLOBAL_IMPORTANCE_NAMES = 'global_importance_names'
    GLOBAL_IMPORTANCE_VALUES = 'global_importance_values'
    GLOBAL_IMPORTANCE_RANK = 'global_importance_rank'
    LOCAL_EXPLANATION = 'local_explanation'
    LOCAL_IMPORTANCE_VALUES = 'local_importance_values'
    METHOD = 'method'
    MODEL_TASK = 'model_task'
    MODEL_TYPE = 'model_type'
    ORDER = 'order'
    PER_CLASS_NAMES = 'per_class_names'
    PER_CLASS_RANK = 'per_class_rank'
    PER_CLASS_VALUES = 'per_class_values'
    SCORING_MODEL = 'scoring_model'
    EXPLAIN_SUBSET = 'explain_subset'
    SILENT = 'silent'
    NSAMPLES = 'nsamples'
    SAMPLING_POLICY = 'sampling_policy'
    TOP_K = 'top_k'
    NCLUSTERS = 'nclusters'
    EXPLANATION_ID = 'explanation_id'
    INCLUDE_LOCAL = 'include_local'
    SHAP_VALUES_OUTPUT = 'shap_values_output'
    PROBABILITIES = 'probabilities'


class Defaults(object):
    """Constants for default values to explain methods"""
    AUTO = 'auto'
    # hdbscan is an unsupervised learning library to find the optimal number of clusters in a dataset
    # See this github repo for more details: https://github.com/scikit-learn-contrib/hdbscan
    HDBSCAN = 'hdbscan'
    MAX_DIM = 50


class Attributes(object):
    """Constants for attributes"""
    EXPECTED_VALUE = 'expected_value'


class Dynamic(object):
    """Constants for dynamically generated classes"""
    LOCAL_EXPLANATION = 'DynamicLocalExplanation'
    GLOBAL_EXPLANATION = 'DynamicGlobalExplanation'


class Tensorflow(object):
    """Tensorflow and tensorboard related constants"""
    TFLOG = 'tflog'
    CPU0 = '/CPU:0'


class SKLearn(object):
    """Scikit-learn related constants"""
    PREDICTIONS = 'predictions'
    LABELS = 'labels'
    EXAMPLES = 'examples'
    BALL_TREE = 'ball_tree'


class Spacy(object):
    """Spacy related constants"""
    NER = 'ner'
    TAGGER = 'tagger'
    EN = 'en'


class LoggingNamespace(object):
    """Logging namespace related constants"""
    AZUREML = 'azureml'


class ModelTask(Enum):
    """The model task.  Can be classification, regression or unknown."""

    Classification = 'Classification'
    Regression = 'Regression'
    Unknown = 'Unknown'


class ShapValuesOutput(str, Enum):
    """The shap values output from the explainer.  Can be default, probability or teacher_probability.

    If teacher probability is specified, we use the probabilities from the teacher model.
    """

    DEFAULT = 'default'
    PROBABILITY = 'probability'
    TEACHER_PROBABILITY = 'teacher_probability'


class ExplainableModelType(str, Enum):
    """The explainable model type."""

    TREE_EXPLAINABLE_MODEL_TYPE = 'tree_explainable_model_type'
    LINEAR_EXPLAINABLE_MODEL_TYPE = 'linear_explainable_model_type'


class MimicSerializationConstants(object):
    """Internal class that defines fields used for MimicExplainer serialization."""

    MODEL = 'model'
    LOGGER = '_logger'
    INITIALIZATION_EXAMPLES = 'initialization_examples'
    IDENTITY = '_identity'
    FUNCTION = 'function'
    PREDICT_PROBA_FLAG = 'predict_proba_flag'

    nonify_properties = ['_logger', 'model', 'function', 'initialization_examples']
    save_properties = ['surrogate_model']
    enum_properties = ['_shap_values_output']


class LightGBMSerializationConstants(object):
    """Internal class that defines fields used for MimicExplainer serialization."""

    MULTICLASS = 'multiclass'
    LOGGER = '_logger'
    TREE_EXPLAINER = '_tree_explainer'
    IDENTITY = '_identity'
    MODEL_STR = 'model_str'

    nonify_properties = [LOGGER, TREE_EXPLAINER]
    save_properties = ['_lgbm']
    enum_properties = ['_shap_values_output']


class LightGBMParams(object):
    CATEGORICAL_FEATURE = 'categorical_feature'
