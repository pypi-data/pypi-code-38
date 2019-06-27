# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Various constants used throughout AutoML."""
import sys


# TODO deprecate this class since Miro has its own source of truth
class SupportedAlgorithms:
    """Names for all algorithms supported by AutoML."""

    LogisticRegression = 'LogisticRegression'
    SGDClassifier = 'SGDClassifierWrapper'
    MultinomialNB = 'NBWrapper'
    BernoulliNB = 'NBWrapper'
    SupportVectorMachine = 'SVCWrapper'
    LinearSupportVectorMachine = 'LinearSVMWrapper'
    KNearestNeighborsClassifier = 'KNeighborsClassifier'
    DecisionTree = 'DecisionTreeClassifier'
    RandomForest = 'RandomForestClassifier'
    ExtraTrees = 'ExtraTreesClassifier'
    LightGBMClassifier = 'LightGBMClassifier'
    TensorFlowDNNClassifier = 'TensorFlowDNN'
    XGBoostClassifier = 'XGBoostClassifier'
    TensorFlowLinearClassifier = 'TensorFlowLinearClassifier'

    ElasticNet = 'ElasticNet'
    GradientBoostingRegressor = 'GradientBoostingRegressor'
    DecisionTreeRegressor = 'DecisionTreeRegressor'
    KNearestNeighborsRegressor = 'KNeighborsRegressor'
    LassoLars = 'LassoLars'
    SGDRegressor = 'SGDRegressor'
    RandomForestRegressor = 'RandomForestRegressor'
    ExtraTreesRegressor = 'ExtraTreesRegressor'
    LightGBMRegressor = 'LightGBMRegressor'
    XGBoostRegressor = 'XGBoostRegressor'
    TensorFlowLinearRegressor = 'TensorFlowLinearRegressor'
    TensorFlowDNNRegressor = 'TensorFlowDNN'

    # To be deprecated soon
    _KNN = 'kNN'
    _SVM = 'SVM'
    _KNNRegressor = 'kNN regressor'

    ALL = {
        LogisticRegression,
        SGDClassifier,
        MultinomialNB,
        BernoulliNB,
        SupportVectorMachine,
        LinearSupportVectorMachine,
        KNearestNeighborsClassifier,
        DecisionTree,
        RandomForest,
        ExtraTrees,
        LightGBMClassifier,
        TensorFlowDNNClassifier,
        XGBoostClassifier,
        TensorFlowLinearClassifier,
        ElasticNet,
        GradientBoostingRegressor,
        DecisionTreeRegressor,
        KNearestNeighborsRegressor,
        LassoLars,
        SGDRegressor,
        RandomForestRegressor,
        LightGBMRegressor,
        ExtraTreesRegressor,
        XGBoostRegressor,
        TensorFlowLinearRegressor,
        TensorFlowDNNRegressor,
        _KNN,
        _SVM,
        _KNNRegressor}


MODEL_EXPLANATION_TAG = "model_explanation"
MODEL_PATH = "outputs/model.pkl"
MODEL_PATH_TRAIN = "outputs/internal_cross_validated_models.pkl"
MODEL_PATH_ONNX = "outputs/model.onnx"
MODEL_RESOURCE_PATH_ONNX = "outputs/model_onnx.json"
DEPENDENCIES_PATH = "outputs/env_dependencies.json"
MAX_ITERATIONS = 1000
MAX_SAMPLES_BLACKLIST = 5000
MAX_SAMPLES_BLACKLIST_ALGOS = [SupportedAlgorithms.KNearestNeighborsClassifier,
                               SupportedAlgorithms.KNearestNeighborsRegressor,
                               SupportedAlgorithms.SupportVectorMachine,
                               SupportedAlgorithms._KNN,
                               SupportedAlgorithms._KNNRegressor,
                               SupportedAlgorithms._SVM]
EARLY_STOPPING_NUM_LANDMARKS = 20

"""Names of algorithms that do not support sample weights."""
Sample_Weights_Unsupported = {
    SupportedAlgorithms.ElasticNet,
    SupportedAlgorithms.KNearestNeighborsClassifier,
    SupportedAlgorithms.KNearestNeighborsRegressor,
    SupportedAlgorithms.LassoLars,
    SupportedAlgorithms._KNN,
}


"""Algorithm names that we must force to run in single threaded mode."""
SINGLE_THREADED_ALGORITHMS = [
    'KNeighbors'
]


class CustomerFacingSupportedModelNames:
    """Customer Facing Names for all algorithms supported by AutoML."""

    class ClassificationModelNames:
        """Classification model names."""

        LogisticRegression = 'LogisticRegression'
        SGDClassifier = 'SGD'
        MultinomialNB = 'MultinomialNaiveBayes'
        BernoulliNB = 'BernoulliNaiveBayes'
        SupportVectorMachine = 'SVM'
        LinearSupportVectorMachine = 'LinearSVM'
        KNearestNeighborsClassifier = 'KNN'
        DecisionTree = 'DecisionTree'
        RandomForest = 'RandomForest'
        ExtraTrees = 'ExtremeRandomTrees'
        LightGBMClassifier = 'LightGBM'
        GradientBoosting = 'GradientBoosting'
        TensorFlowDNNClassifier = 'TensorFlowDNN'
        TensorFlowLinearClassifier = 'TensorFlowLinearClassifier'
        XGBoostClassifier = 'XGBoostClassifier'

    class RegressionModelNames:
        """Regression Model Names."""

        ElasticNet = 'ElasticNet'
        GradientBoostingRegressor = 'GradientBoosting'
        DecisionTreeRegressor = 'DecisionTree'
        KNearestNeighborsRegressor = 'KNN'
        LassoLars = 'LassoLars'
        SGDRegressor = 'SGD'
        RandomForestRegressor = 'RandomForest'
        ExtraTreesRegressor = 'ExtremeRandomTrees'
        LightGBMRegressor = 'LightGBM'
        TensorFlowLinearRegressor = 'TensorFlowLinearRegressor'
        TensorFlowDNNRegressor = 'TensorFlowDNN'
        XGBoostRegressor = 'XGBoostRegressor'


class EnsembleConstants(object):
    """List of constants used for Ensemble iterations."""

    VOTING_ENSEMBLE_PIPELINE_ID = "__AutoML_Ensemble__"
    STACK_ENSEMBLE_PIPELINE_ID = "__AutoML_Stack_Ensemble__"
    ENSEMBLE_PIPELINE_IDS = [VOTING_ENSEMBLE_PIPELINE_ID, STACK_ENSEMBLE_PIPELINE_ID]
    # by default, we'll use 20% of the training data (when doing TrainValidation split) for training the meta learner
    DEFAULT_TRAIN_PERCENTAGE_FOR_STACK_META_LEARNER = 0.2

    class StackMetaLearnerAlgorithmNames(object):
        """List of algorithms supported for training dthe Stack Ensemble meta learner."""

        LogisticRegression = CustomerFacingSupportedModelNames.ClassificationModelNames.LogisticRegression
        LogisticRegressionCV = "LogisticRegressionCV"
        LightGBMClassifier = CustomerFacingSupportedModelNames.ClassificationModelNames.LightGBMClassifier
        ElasticNet = CustomerFacingSupportedModelNames.RegressionModelNames.ElasticNet
        ElasticNetCV = "ElasticNetCV"
        LightGBMRegressor = CustomerFacingSupportedModelNames.RegressionModelNames.LightGBMRegressor
        LinearRegression = "LinearRegression"
        ALL = [
            LogisticRegression,
            LogisticRegressionCV,
            LightGBMClassifier,
            ElasticNet,
            ElasticNetCV,
            LightGBMRegressor,
            LinearRegression]


class ModelClassNames:
    """Class names for models."""

    class ClassificationModelClassNames:
        """Classification model names."""

        LogisticRegression = 'LogisticRegression'
        SGDClassifier = 'SGDClassifierWrapper'
        MultinomialNB = 'NBWrapper'
        BernoulliNB = 'NBWrapper'  # BernoulliNB use NBWrapper as classname
        SupportVectorMachine = 'SVCWrapper'
        LinearSupportVectorMachine = 'LinearSVMWrapper'
        KNearestNeighborsClassifier = 'KNeighborsClassifier'
        DecisionTree = 'DecisionTreeClassifier'
        RandomForest = 'RandomForestClassifier'
        ExtraTrees = 'ExtraTreesClassifier'
        LightGBMClassifier = 'LightGBMClassifier'
        GradientBoosting = 'GradientBoostingClassifier'
        TensorFlowDNNClassifier = 'TFDNNClassifierWrapper'
        TensorFlowLinearClassifier = 'TFLinearClassifierWrapper'
        XGBoostClassifier = 'XGBoostClassifier'

    class RegressionModelClassNames:
        """Regression Model Names."""

        ElasticNet = 'ElasticNet'
        GradientBoostingRegressor = 'GradientBoostingRegressor'
        DecisionTreeRegressor = 'DecisionTreeRegressor'
        KNearestNeighborsRegressor = 'KNeighborsRegressor'
        LassoLars = 'LassoLars'
        SGDRegressor = 'SGDRegressor'
        RandomForestRegressor = 'RandomForestRegressor'
        ExtraTreesRegressor = 'ExtraTreesRegressor'
        LightGBMRegressor = 'LightGBMRegressor'
        TensorFlowLinearRegressor = 'TFLinearRegressorWrapper'
        TensorFlowDNNRegressor = 'TFDNNRegressorWrapper'
        XGBoostRegressor = 'XGBoostRegressor'


class LegacyModelNames:
    """Names for all legacy model names supported by AutoML."""

    class ClassificationLegacyModelNames:
        """Names for all classification legacy model names."""

        LogisticRegression = 'logistic regression'
        SGDClassifier = 'SGD classifier'
        MultinomialNB = 'MultinomialNB'
        BernoulliNB = 'BernoulliNB'
        SupportVectorMachine = 'SVM'
        LinearSupportVectorMachine = 'LinearSVM'
        KNearestNeighborsClassifier = 'kNN'
        DecisionTree = 'DT'
        RandomForest = 'RF'
        ExtraTrees = 'extra trees'
        LightGBMClassifier = 'lgbm_classifier'
        GradientBoosting = 'gradient boosting'
        TensorFlowDNNClassifier = 'TF DNNClassifier'
        TensorFlowLinearClassifier = 'TF LinearClassifier'
        XGBoostClassifier = 'xgboost classifier'

    class RegressionLegacyModelNames:
        """Names for all regression legacy model names."""

        ElasticNet = 'Elastic net'
        GradientBoostingRegressor = 'Gradient boosting regressor'
        DecisionTreeRegressor = 'DT regressor'
        KNearestNeighborsRegressor = 'kNN regressor'
        LassoLars = 'Lasso lars'
        SGDRegressor = 'SGD regressor'
        RandomForestRegressor = 'RF regressor'
        ExtraTreesRegressor = 'extra trees regressor'
        LightGBMRegressor = 'lightGBM regressor'
        TensorFlowLinearRegressor = 'TF LinearRegressor'
        TensorFlowDNNRegressor = 'TF DNNRegressor'
        XGBoostRegressor = 'xgboost regressor'


class ModelName:
    """Model names with customer, legacy and class names."""

    def __init__(self, customer_model_name, legacy_model_name, model_class_name):
        """Init ModelName."""
        self.customer_model_name = customer_model_name
        self.legacy_model_name = legacy_model_name
        self.model_class_name = model_class_name


class SupportedModelNames:
    """A list of supported models with all customer name, legacy model name and model class name."""

    SupportedClassificationModelList = [
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            LogisticRegression,
            LegacyModelNames.ClassificationLegacyModelNames.LogisticRegression,
            ModelClassNames.ClassificationModelClassNames.LogisticRegression),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            SGDClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.SGDClassifier,
            ModelClassNames.ClassificationModelClassNames.SGDClassifier),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            MultinomialNB,
            LegacyModelNames.ClassificationLegacyModelNames.MultinomialNB,
            ModelClassNames.ClassificationModelClassNames.MultinomialNB),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            BernoulliNB,
            LegacyModelNames.ClassificationLegacyModelNames.BernoulliNB,
            ModelClassNames.ClassificationModelClassNames.BernoulliNB),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            SupportVectorMachine,
            LegacyModelNames.ClassificationLegacyModelNames.
            SupportVectorMachine,
            ModelClassNames.ClassificationModelClassNames.SupportVectorMachine),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            LinearSupportVectorMachine,
            LegacyModelNames.ClassificationLegacyModelNames.
            LinearSupportVectorMachine,
            ModelClassNames.ClassificationModelClassNames.
            LinearSupportVectorMachine),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            KNearestNeighborsClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.
            KNearestNeighborsClassifier,
            ModelClassNames.ClassificationModelClassNames.
            KNearestNeighborsClassifier),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            DecisionTree,
            LegacyModelNames.ClassificationLegacyModelNames.DecisionTree,
            ModelClassNames.ClassificationModelClassNames.DecisionTree),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            RandomForest,
            LegacyModelNames.ClassificationLegacyModelNames.RandomForest,
            ModelClassNames.ClassificationModelClassNames.RandomForest),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            ExtraTrees,
            LegacyModelNames.ClassificationLegacyModelNames.ExtraTrees,
            ModelClassNames.ClassificationModelClassNames.ExtraTrees),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            LightGBMClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.LightGBMClassifier,
            ModelClassNames.ClassificationModelClassNames.LightGBMClassifier),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            XGBoostClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.XGBoostClassifier,
            ModelClassNames.ClassificationModelClassNames.XGBoostClassifier),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            GradientBoosting,
            LegacyModelNames.ClassificationLegacyModelNames.GradientBoosting,
            ModelClassNames.ClassificationModelClassNames.GradientBoosting),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            TensorFlowDNNClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.
            TensorFlowDNNClassifier,
            ModelClassNames.ClassificationModelClassNames.
            TensorFlowDNNClassifier),
        ModelName(
            CustomerFacingSupportedModelNames.ClassificationModelNames.
            TensorFlowLinearClassifier,
            LegacyModelNames.ClassificationLegacyModelNames.
            TensorFlowLinearClassifier,
            ModelClassNames.ClassificationModelClassNames.
            TensorFlowLinearClassifier)]

    SupportedRegressionModelList = [
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.ElasticNet,
            LegacyModelNames.RegressionLegacyModelNames.ElasticNet,
            ModelClassNames.RegressionModelClassNames.ElasticNet),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            GradientBoostingRegressor,
            LegacyModelNames.RegressionLegacyModelNames.
            GradientBoostingRegressor,
            ModelClassNames.RegressionModelClassNames.
            GradientBoostingRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            DecisionTreeRegressor,
            LegacyModelNames.RegressionLegacyModelNames.DecisionTreeRegressor,
            ModelClassNames.RegressionModelClassNames.DecisionTreeRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            KNearestNeighborsRegressor,
            LegacyModelNames.RegressionLegacyModelNames.
            KNearestNeighborsRegressor,
            ModelClassNames.RegressionModelClassNames.
            KNearestNeighborsRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.LassoLars,
            LegacyModelNames.RegressionLegacyModelNames.LassoLars,
            ModelClassNames.RegressionModelClassNames.LassoLars),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            SGDRegressor,
            LegacyModelNames.RegressionLegacyModelNames.SGDRegressor,
            ModelClassNames.RegressionModelClassNames.SGDRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            RandomForestRegressor,
            LegacyModelNames.RegressionLegacyModelNames.RandomForestRegressor,
            ModelClassNames.RegressionModelClassNames.RandomForestRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            ExtraTreesRegressor,
            LegacyModelNames.RegressionLegacyModelNames.ExtraTreesRegressor,
            ModelClassNames.RegressionModelClassNames.ExtraTreesRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            LightGBMRegressor,
            LegacyModelNames.RegressionLegacyModelNames.LightGBMRegressor,
            ModelClassNames.RegressionModelClassNames.LightGBMRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            XGBoostRegressor,
            LegacyModelNames.RegressionLegacyModelNames.XGBoostRegressor,
            ModelClassNames.RegressionModelClassNames.XGBoostRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            TensorFlowLinearRegressor,
            LegacyModelNames.RegressionLegacyModelNames.
            TensorFlowLinearRegressor,
            ModelClassNames.RegressionModelClassNames.
            TensorFlowLinearRegressor),
        ModelName(
            CustomerFacingSupportedModelNames.RegressionModelNames.
            TensorFlowDNNRegressor,
            LegacyModelNames.RegressionLegacyModelNames.TensorFlowDNNRegressor,
            ModelClassNames.RegressionModelClassNames.TensorFlowDNNRegressor)]


class ModelNameMappings:
    """Model name mappings."""

    CustomerFacingModelToLegacyModelMapClassification = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedClassificationModelList],
        [model.legacy_model_name for model in SupportedModelNames.
            SupportedClassificationModelList]))

    CustomerFacingModelToLegacyModelMapRegression = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedRegressionModelList],
        [model.legacy_model_name for model in SupportedModelNames.
            SupportedRegressionModelList]))

    CustomerFacingModelToClassNameModelMapClassification = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedClassificationModelList],
        [model.model_class_name for model in SupportedModelNames.
            SupportedClassificationModelList]))

    CustomerFacingModelToClassNameModelMapRegression = dict(zip(
        [model.customer_model_name for model in SupportedModelNames.
            SupportedRegressionModelList],
        [model.model_class_name for model in SupportedModelNames.
            SupportedRegressionModelList]))

    ClassNameToCustomerFacingModelMapClassification = dict(zip(
        [model.model_class_name for model in SupportedModelNames.
            SupportedClassificationModelList],
        [model.customer_model_name for model in SupportedModelNames.
            SupportedClassificationModelList]))

    ClassNameToCustomerFacingModelMapRegression = dict(zip(
        [model.model_class_name for model in SupportedModelNames.
            SupportedRegressionModelList],
        [model.customer_model_name for model in SupportedModelNames.
            SupportedRegressionModelList]))


class Defaults:
    """Default values for pipelines."""

    DEFAULT_PIPELINE_SCORE = float('NaN')  # Jasmine and 016N
    INVALID_PIPELINE_VALIDATION_SCORES = {}
    INVALID_PIPELINE_FITTED = ''
    INVALID_PIPELINE_OBJECT = None


class RunState:
    """Names for the states a run can be in."""

    START_RUN = 'running'
    FAIL_RUN = 'failed'
    CANCEL_RUN = 'canceled'
    COMPLETE_RUN = 'completed'


class API:
    """Names for the AzureML API operations that can be performed."""

    CreateExperiment = 'Create Experiment'
    CreateParentRun = 'Create Parent Run'
    GetNextPipeline = 'Get Pipeline'
    SetParentRunStatus = 'Set Parent Run Status'
    StartRemoteRun = 'Start Remote Run'
    StartRemoteSnapshotRun = 'Start Remote Snapshot Run'
    CancelChildRun = 'Cancel Child Run'
    StartChildRun = 'Start Child Run'
    SetRunProperties = 'Set Run Properties'
    LogMetrics = 'Log Metrics'
    InstantiateRun = 'Get Run'


class AcquisitionFunction:
    """Names for all acquisition functions used to select the next pipeline.

    The default is EI (expected improvement).
    """

    EI = "EI"
    PI = "PI"
    UCB = "UCB"
    THOMPSON = "thompson"
    EXPECTED = "expected"

    FULL_SET = {EI, PI, UCB, THOMPSON, EXPECTED}


class Status:
    """Names for the possible child run states."""

    NotStarted = 'Not Started'
    Started = 'Started'
    InProgress = 'In Progress'
    Completed = 'Completed'
    Terminated = 'Terminated'

    FULL_SET = {NotStarted, Started, InProgress, Completed, Terminated}

    @classmethod
    def pretty(cls, metric):
        """
        Verbose printing of AutoMLRun statuses.

        :param metric: The metric to print.
        :type metric: azureml.train.automl.constants.Status
        :return: Pretty print of the metric.
        :rtype: str
        """
        return {
            cls.Started: "Started",
            cls.InProgress: "In Progress running one of the child iterations.",
            cls.Completed: "Completed",
            cls.Terminated: "Terminated before finishing execution",
        }[metric]


class PipelineParameterConstraintCheckStatus:
    """Values for whether pipeline is a valid pipeline."""

    VALID = 0
    REMOVE = 1
    REJECTPIPELINE = 2


class OptimizerObjectives:
    """Names for the objectives an algorithm can have relative to a metric.

    Some metrics should be maximized and some should be minimized.
    """

    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"
    NA = 'NA'

    FULL_SET = {MAXIMIZE, MINIMIZE, NA}


class Optimizer:
    """Names for the categories of pipeline prediction algorithms used.

    - random provides a baseline by selecting a pipeline randomly
    - lvm uses latent variable models to predict probable next pipelines
    given performance on previous pipelines.
    """

    Random = "random"
    LVM = "lvm"

    FULL_SET = {Random, LVM}


class Tasks:
    """Names for the types of machine learning tasks supported by AutoML."""

    CLASSIFICATION = 'classification'
    REGRESSION = 'regression'

    ALL = [CLASSIFICATION, REGRESSION]


class ClientErrors:
    """Names for the client errors that can occur when violating user-specified cost contraints."""

    EXCEEDED_TIME_CPU = "CPU time exceeded the specified limit. Please consider increasing the CPU time limit."
    EXCEEDED_TIME = "Wall clock time exceeded the specified limit. Please consider increasing the time limit."
    EXCEEDED_MEMORY = "Memory usage exceeded the specified limit or was killed by the OS due to low memory " \
                      "conditions. Please consider increasing available memory."
    SUBPROCESS_ERROR = "The subprocess was killed due to an error."
    GENERIC_ERROR = "An unknown error occurred."

    ALL_ERRORS = {
        EXCEEDED_TIME_CPU, EXCEEDED_TIME, EXCEEDED_MEMORY,
        SUBPROCESS_ERROR, GENERIC_ERROR
    }


class ServerStatus:
    """Values that the server status can take."""

    OK = 'ok'
    INCREASE_TIME_THRESHOLD = 'threshold'


class TimeConstraintEnforcement:
    """Enumeration of time contraint enforcement modes."""

    TIME_CONSTRAINT_NONE = 0
    TIME_CONSTRAINT_PER_ITERATION = 1
    TIME_CONSTRAINT_TOTAL = 2
    TIME_CONSTRAINT_TOTAL_AND_ITERATION = 3


class PipelineCost:
    """Names for the different cost model modes.

    - COST_NONE returns all predicted pipelines
    - COST_FILTER returns only pipelines that were predicted by cost models
        to meet the user-specified cost conditions
    """

    COST_NONE = 0
    COST_FILTER = 1
    COST_SCALE_ACQUISITION = 2
    COST_SCALE_AND_FILTER = 3
    COST_SCALE_THEN_FILTER = 4
    COST_ALTERNATE = 5
    COST_SCALE_AND_FILTER_ANNEAL = 6
    # Used to restrict the number of piplines we predict cost for if we want to save time
    # currently set to the same values as the pruned index so no optimization is made
    MAX_COST_PREDICTS = 20000


class PipelineMaskProfiles:
    """Mask profiles for pipelines."""

    MASK_NONE = 'none'
    MASK_PARTIAL_FIT = 'partial_fit'
    MASK_LGBM_ONLY = 'lgbm'
    MASK_MANY_FEATURES = 'many_features'
    MASK_NO_SVM_KNN = 'no_svm_knn'
    MASK_SPARSE = 'sparse'
    MASK_PRUNE = 'prune'
    MASK_TIME_PRUNE = 'time_prune'
    MASK_RANGE = 'range_mask'
    MASK_INDEX = 'pruned_index_name'

    ALL_MASKS = [
        MASK_NONE,
        MASK_PARTIAL_FIT, MASK_MANY_FEATURES,
        MASK_SPARSE,
        MASK_RANGE]


class SubsamplingTreatment:
    """Subsampling Treatment in GP."""

    LOG = 'log'
    LINEAR = 'linear'


class SubsamplingSchedule:
    """Subsampling Stragies."""

    HYPERBAND = 'hyperband'
    HYPERBAND_CLIP = 'hyperband_clip'
    FULL_PCT = 100.0


class EnsembleMethod:
    """Ensemble methods."""

    ENSEMBLE_AVERAGE = 'average'
    ENSEMBLE_STACK = 'stack_lr'
    # take the best model from each class, This is what H20 does
    ENSEMBLE_BEST_MODEL = 'best_model'
    # stack, but with a lgbm not a logistic regression
    ENSEMBLE_STACK_LGBM = 'stack_lgbm'
    # take the best model from each cluster of the model's latent space
    ENSEMBLE_LATENT_SPACE = 'latent_space'
    # take the best model from each of the datasets classes
    ENSEMBLE_BEST_CLASS = 'best_class'


class TrainingResultsType:
    """Potential results from runners class."""

    # Metrics
    TRAIN_METRICS = 'train'
    VALIDATION_METRICS = 'validation'
    TEST_METRICS = 'test'
    TRAIN_FROM_FULL_METRICS = 'train from full'
    TEST_FROM_FULL_METRICS = 'test from full'
    CV_METRICS = 'CV'
    CV_MEAN_METRICS = 'CV mean'

    # Other useful things
    TRAIN_TIME = 'train time'
    FIT_TIME = 'fit_time'
    PREDICT_TIME = 'predict_time'
    BLOB_TIME = 'blob_time'
    ALL_TIME = {TRAIN_TIME, FIT_TIME, PREDICT_TIME}
    TRAIN_PERCENT = 'train_percent'
    MODELS = 'models'

    # Status:
    TRAIN_VALIDATE_STATUS = 'train validate status'
    TRAIN_FULL_STATUS = 'train full status'
    CV_STATUS = 'CV status'


class Metric:
    """Names for all metrics supported by classification and regression."""

    # Classification
    AUCMacro = 'AUC_macro'
    AUCMicro = 'AUC_micro'
    AUCWeighted = 'AUC_weighted'
    Accuracy = 'accuracy'
    WeightedAccuracy = 'weighted_accuracy'
    BalancedAccuracy = 'balanced_accuracy'
    NormMacroRecall = 'norm_macro_recall'
    LogLoss = 'log_loss'
    F1Micro = 'f1_score_micro'
    F1Macro = 'f1_score_macro'
    F1Weighted = 'f1_score_weighted'
    PrecisionMicro = 'precision_score_micro'
    PrecisionMacro = 'precision_score_macro'
    PrecisionWeighted = 'precision_score_weighted'
    RecallMicro = 'recall_score_micro'
    RecallMacro = 'recall_score_macro'
    RecallWeighted = 'recall_score_weighted'
    AvgPrecisionMicro = 'average_precision_score_micro'
    AvgPrecisionMacro = 'average_precision_score_macro'
    AvgPrecisionWeighted = 'average_precision_score_weighted'
    AccuracyTable = 'accuracy_table'
    ConfusionMatrix = 'confusion_matrix'

    # Regression
    ExplainedVariance = 'explained_variance'
    R2Score = 'r2_score'
    Spearman = 'spearman_correlation'
    MAPE = 'mean_absolute_percentage_error'
    MeanAbsError = 'mean_absolute_error'
    MedianAbsError = 'median_absolute_error'
    RMSE = 'root_mean_squared_error'
    RMSLE = 'root_mean_squared_log_error'
    NormMeanAbsError = 'normalized_mean_absolute_error'
    NormMedianAbsError = 'normalized_median_absolute_error'
    NormRMSE = 'normalized_root_mean_squared_error'
    NormRMSLE = 'normalized_root_mean_squared_log_error'
    Residuals = 'residuals'
    PredictedTrue = 'predicted_true'

    # Forecast
    ForecastMAPE = 'forecast_mean_average_precision_error'
    ForecastResiduals = 'forecast_residuals'

    SCALAR_CLASSIFICATION_SET = {
        AUCMacro, AUCMicro, AUCWeighted, Accuracy,
        WeightedAccuracy, NormMacroRecall, BalancedAccuracy,
        LogLoss, F1Micro, F1Macro, F1Weighted, PrecisionMicro,
        PrecisionMacro, PrecisionWeighted, RecallMicro, RecallMacro,
        RecallWeighted, AvgPrecisionMicro, AvgPrecisionMacro,
        AvgPrecisionWeighted
    }

    NONSCALAR_CLASSIFICATION_SET = {
        AccuracyTable, ConfusionMatrix
    }

    CLASSIFICATION_SET = (SCALAR_CLASSIFICATION_SET |
                          NONSCALAR_CLASSIFICATION_SET)

    SCALAR_REGRESSION_SET = {
        ExplainedVariance, R2Score, Spearman, MAPE, MeanAbsError,
        MedianAbsError, RMSE, RMSLE, NormMeanAbsError,
        NormMedianAbsError, NormRMSE, NormRMSLE
    }

    NONSCALAR_REGRESSION_SET = {
        Residuals, PredictedTrue
    }

    REGRESSION_SET = (SCALAR_REGRESSION_SET |
                      NONSCALAR_REGRESSION_SET)

    NONSCALAR_FORECAST_SET = {
        ForecastMAPE, ForecastResiduals
    }

    FORECAST_SET = (NONSCALAR_FORECAST_SET)

    CLASSIFICATION_PRIMARY_SET = {
        Accuracy, AUCWeighted, NormMacroRecall, AvgPrecisionWeighted,
        PrecisionWeighted
    }

    CLASSIFICATION_BALANCED_SET = {
        # this is for metrics where we would recommend using class_weights
        BalancedAccuracy, AUCMacro, NormMacroRecall, AvgPrecisionMacro,
        PrecisionMacro, F1Macro, RecallMacro
    }

    REGRESSION_PRIMARY_SET = {
        Spearman, NormRMSE, R2Score, NormMeanAbsError
    }

    SAMPLE_WEIGHTS_UNSUPPORTED_SET = {
        WeightedAccuracy, Spearman, MedianAbsError, NormMedianAbsError
    }

    FULL_SET = CLASSIFICATION_SET | REGRESSION_SET | FORECAST_SET
    NONSCALAR_FULL_SET = (NONSCALAR_CLASSIFICATION_SET |
                          NONSCALAR_REGRESSION_SET |
                          NONSCALAR_FORECAST_SET)
    SCALAR_FULL_SET = (SCALAR_CLASSIFICATION_SET |
                       SCALAR_REGRESSION_SET)
    SCALAR_FULL_SET_TIME = (SCALAR_FULL_SET | TrainingResultsType.ALL_TIME)

    # TODO: These types will be removed when the artifact-backed
    # metrics are defined with protobuf
    # Do not use these constants except in artifact-backed metrics
    SCHEMA_TYPE_ACCURACY_TABLE = 'accuracy_table'
    SCHEMA_TYPE_CONFUSION_MATRIX = 'confusion_matrix'
    SCHEMA_TYPE_RESIDUALS = 'residuals'
    SCHEMA_TYPE_PREDICTIONS = 'predictions'
    SCHEMA_TYPE_MAPE = 'mape_table'

    @classmethod
    def pretty(cls, metric):
        """Verbose names for metrics."""
        return {
            cls.AUCMacro: "Macro Area Under The Curve",
            cls.AUCMicro: "Micro Area Under The Curve",
            cls.AUCWeighted: "Weighted Area Under The Curve",
            cls.Accuracy: "Accuracy",
            cls.WeightedAccuracy: "Weighted Accuracy",
            cls.NormMacroRecall: "Normed Macro Recall",
            cls.BalancedAccuracy: "Balanced Accuracy",
            cls.LogLoss: "Log Loss",
            cls.F1Macro: "Macro F1 Score",
            cls.F1Micro: "Micro F1 Score",
            cls.F1Weighted: "Weighted F1 Score",
            cls.PrecisionMacro: "Macro Precision",
            cls.PrecisionMicro: "Micro Precision",
            cls.PrecisionWeighted: "Weighted Precision",
            cls.RecallMacro: "Macro Recall",
            cls.RecallMicro: "Micro Recall",
            cls.RecallWeighted: "Weighted Recall",
            cls.AvgPrecisionMacro: "Macro Average Precision",
            cls.AvgPrecisionMicro: "Micro Average Precision",
            cls.AvgPrecisionWeighted: "Weighted Average Precision",
            cls.ExplainedVariance: "Explained Variance",
            cls.R2Score: "R2 Score",
            cls.Spearman: "Spearman Correlation",
            cls.MeanAbsError: "Mean Absolute Error",
            cls.MedianAbsError: "Median Absolute Error",
            cls.RMSE: "Root Mean Squared Error",
            cls.RMSLE: "Root Mean Squared Log Error",
            cls.NormMeanAbsError: "Normalized Mean Absolute Error",
            cls.NormMedianAbsError: "Normalized Median Absolute Error",
            cls.NormRMSE: "Normalized Root Mean Squared Error",
            cls.NormRMSLE: "Normalized Root Mean Squared Log Error"
        }[metric]

    CLIPS_POS = {
        # TODO: If we are no longer transforming by default reconsider these
        # it is probably not necessary for them to be over 1
        LogLoss: 1,
        NormMeanAbsError: 1,
        NormMedianAbsError: 1,
        NormRMSE: 1,
        NormRMSLE: 1,
        # current timeout value but there is a long time
        TrainingResultsType.TRAIN_TIME: 10 * 60 * 2
    }

    CLIPS_NEG = {
        # TODO: If we are no longer transforming by default reconsider these
        # it is probably not necessary for them to be over 1
        # spearman is naturally limitted to this range but necessary for transform_y to work
        # otherwise spearmen is getting clipped to 0 by default
        Spearman: -1,
        ExplainedVariance: -1,
        R2Score: -1
    }


class MetricObjective:
    """Mappings from metrics to their objective.

    Objectives are maximization or minimization (regression and
    classification).
    """

    Classification = {
        Metric.AUCMicro: OptimizerObjectives.MAXIMIZE,
        Metric.AUCMacro: OptimizerObjectives.MAXIMIZE,
        Metric.AUCWeighted: OptimizerObjectives.MAXIMIZE,
        Metric.Accuracy: OptimizerObjectives.MAXIMIZE,
        Metric.WeightedAccuracy: OptimizerObjectives.MAXIMIZE,
        Metric.NormMacroRecall: OptimizerObjectives.MAXIMIZE,
        Metric.BalancedAccuracy: OptimizerObjectives.MAXIMIZE,
        Metric.LogLoss: OptimizerObjectives.MINIMIZE,
        Metric.F1Micro: OptimizerObjectives.MAXIMIZE,
        Metric.F1Macro: OptimizerObjectives.MAXIMIZE,
        Metric.F1Weighted: OptimizerObjectives.MAXIMIZE,
        Metric.PrecisionMacro: OptimizerObjectives.MAXIMIZE,
        Metric.PrecisionMicro: OptimizerObjectives.MAXIMIZE,
        Metric.PrecisionWeighted: OptimizerObjectives.MAXIMIZE,
        Metric.RecallMacro: OptimizerObjectives.MAXIMIZE,
        Metric.RecallMicro: OptimizerObjectives.MAXIMIZE,
        Metric.RecallWeighted: OptimizerObjectives.MAXIMIZE,
        Metric.AvgPrecisionMacro: OptimizerObjectives.MAXIMIZE,
        Metric.AvgPrecisionMicro: OptimizerObjectives.MAXIMIZE,
        Metric.AvgPrecisionWeighted: OptimizerObjectives.MAXIMIZE,
        Metric.AccuracyTable: OptimizerObjectives.NA,
        Metric.ConfusionMatrix: OptimizerObjectives.NA,
        TrainingResultsType.TRAIN_TIME: OptimizerObjectives.MINIMIZE
    }

    Regression = {
        Metric.ExplainedVariance: OptimizerObjectives.MAXIMIZE,
        Metric.R2Score: OptimizerObjectives.MAXIMIZE,
        Metric.Spearman: OptimizerObjectives.MAXIMIZE,
        Metric.MeanAbsError: OptimizerObjectives.MINIMIZE,
        Metric.NormMeanAbsError: OptimizerObjectives.MINIMIZE,
        Metric.MedianAbsError: OptimizerObjectives.MINIMIZE,
        Metric.NormMedianAbsError: OptimizerObjectives.MINIMIZE,
        Metric.RMSE: OptimizerObjectives.MINIMIZE,
        Metric.NormRMSE: OptimizerObjectives.MINIMIZE,
        Metric.RMSLE: OptimizerObjectives.MINIMIZE,
        Metric.NormRMSLE: OptimizerObjectives.MINIMIZE,
        Metric.MAPE: OptimizerObjectives.MINIMIZE,
        Metric.Residuals: OptimizerObjectives.NA,
        Metric.PredictedTrue: OptimizerObjectives.NA,
        TrainingResultsType.TRAIN_TIME: OptimizerObjectives.MINIMIZE
    }

    Forecast = {
        Metric.ForecastResiduals: OptimizerObjectives.NA,
        Metric.ForecastMAPE: OptimizerObjectives.NA
    }


class ModelParameters:
    """
    The parameter names specific to certain models.

    For example, to indicate which features in the dataset are categorical
    a LightGBM model accepts the 'categorical_feature' parameter while
    a CatBoost model accepts the 'cat_features' parameter.
    """

    CATEGORICAL_FEATURES = {
        ModelClassNames.ClassificationModelClassNames.LightGBMClassifier: 'categorical_feature',
        ModelClassNames.RegressionModelClassNames.LightGBMRegressor: 'categorical_feature'
        # TODO: Use these when the CatBoost model wrapper is added
        # ModelClassNames.ClassificationModelClassNames.CatBoostClassifier: 'cat_features',
        # ModelClassNames.RegressionModelClassNames.CatBoostRegressor: 'cat_features'
    }


class TrainingType:
    """Names for validation methods.

    Different experiment types will use different validation methods.
    """

    # Yields TRAIN_FROM_FULL_METRICS and TEST_FROM_FULL_METRICS
    TrainFull = 'train_full'
    # Yields VALIDATION_METRICS
    TrainAndValidation = 'train_valid'
    # Yields TRAIN_METRICS, VALIDATION_METRICS, and TEST_METRICS
    TrainValidateTest = 'train_valid_test'
    # Yields CV_METRICS and CV_MEAN_METRICS
    CrossValidation = 'CV'
    MeanCrossValidation = 'MeanCrossValidation'
    FULL_SET = {
        TrainFull,
        TrainAndValidation,
        TrainValidateTest,
        CrossValidation,
        MeanCrossValidation}

    @classmethod
    def pretty(cls, metric):
        """Verbose names for training types."""
        return {
            cls.TrainFull: "Full",
            cls.TrainAndValidation: "Train and Validation",
            cls.CrossValidation: "Cross Validation",
            cls.MeanCrossValidation: "Mean of the Cross Validation",
        }[metric]


class NumericalDtype:
    """Names for supported numerical datatypes.

    Names correspond to the output of pandas.api.types.infer_dtype().
    """

    Integer = 'integer'
    Floating = 'floating'
    MixedIntegerFloat = 'mixed-integer-float'
    MixedInteger = 'mixed-integer'

    FULL_SET = {Integer, Floating, MixedIntegerFloat, MixedInteger}


class DatetimeDtype:
    """Names for supported datetime datatypes.

    Names correspond to the output of pandas.api.types.infer_dtype().
    """

    Date = 'date'
    Datetime = 'datetime'
    Datetime64 = 'datetime64'

    FULL_SET = {Date, Datetime, Datetime64}


class TextOrCategoricalDtype:
    """Names for supported categorical datatypes."""

    String = 'string'

    FULL_SET = {String}


class TimeSeries:
    """Parameters used for timeseries."""

    TIME_COLUMN_NAME = 'time_column_name'
    GRAIN_COLUMN_NAMES = 'grain_column_names'
    DROP_COLUMN_NAMES = 'drop_column_names'
    GROUP_COLUMN = 'group'
    TARGET_LAGS = 'target_lags'
    TARGET_ROLLING_WINDOW_SIZE = 'target_rolling_window_size'
    MAX_HORIZON = 'max_horizon'
    COUNTRY_OR_REGION = 'country_or_region'
    SEASONALITY = 'seasonality'
    USE_STL = 'use_stl'
    STL_OPTION_SEASON_TREND = 'season_trend'
    STL_OPTION_SEASON = 'season'


class TimeSeriesInternal:
    """Non user-facing TimeSeries constants."""

    DUMMY_GROUP_COLUMN = '_automl_dummy_group_col'
    DUMMY_ORDER_COLUMN = '_automl_original_order_col'
    DUMMY_GRAIN_COLUMN = '_automl_dummy_grain_col'
    DUMMY_TARGET_COLUMN = '_automl_target_col'
    MAX_HORIZON_FEATURIZER = 'max_horizon_featurizer'
    LAG_LEAD_OPERATOR = 'lag_lead_operator'
    ROLLING_WINDOW_OPERATOR = 'rolling_window_operator'
    ORIGIN_TIME_COLNAME = 'origin_time_column_name'
    MAKE_NUMERIC_NA_DUMMIES = 'make_numeric_na_dummies'
    IMPUTE_NA_NUMERIC_COLUMNS = 'impute_na_numeric_columns'
    MAKE_TIME_INDEX_FEATURES = 'make_time_index_featuers'
    DROP_IRRELEVANT_COLUMNS = 'drop_irrelevant_columns'
    MAKE_GRAIN_FEATURES = 'make_grain_features'
    MAKE_CATEGORICALS_NUMERIC = 'make_categoricals_numeric'
    MAKE_CATEGORICALS_ONEHOT = 'make_categoricals_onehot'
    MAKE_SEASONALITY_AND_TREND = 'make_seasonality_and_trend'
    IMPUTE_NA_FORWARD = 'fillna_imputer_ffill'
    IMPUTE_NA_BACKWARD = 'fillna_imputer_bfill'
    IMPUTE_NA_FINAL = 'fillna_imputer_final'

    LAGS_TO_CONSTRUCT = 'lags'  # The internal lags dictionary
    WINDOW_SIZE = 'window_size'  # The internal window_size variable
    WINDOW_OPTS = 'window_options'  # The internal window options (Currently is not used).
    # The rolling window transform dictionary, currently not publicly available.
    TRANSFORM_DICT = 'transform_dictionary'
    TRANSFORM_OPTS = 'transform_options'  # The options for rolling window transform.
    DROP_NA = 'dropna'  # dropna parameter of LagLeadOperator and RollingWindow. Currently set to DROP_NA_DEFAULT.
    # overwrite_columns parameter of LagLeadOperator and RollingWindow. Currently set to OVERWRITE_COLUMNS_DEFAULT.
    OVERWRITE_COLUMNS = 'overwrite_columns'
    ORIGIN_TIME_COLUMN_NAME = 'origin_time_colname'
    ORIGIN_TIME_COLNAME_DEFAULT = 'origin'
    HORIZON_NAME = 'horizon_origin'
    MAX_HORIZON_DEFAULT = 1
    WINDOW_SIZE_DEFDAULT = 5
    TARGET_LAGS_DEFAULT = 1
    TRANSFORM_DICT_DEFAULT = {'min': DUMMY_TARGET_COLUMN,
                              'max': DUMMY_TARGET_COLUMN,
                              'mean': DUMMY_TARGET_COLUMN}
    DROP_NA_DEFAULT = True
    OVERWRITE_COLUMNS_DEFAULT = True
    # The amount of memory occupied by perspective data frame
    # at which we decide to switch off lag leads and rolling windows.
    MEMORY_FRACTION_FOR_DF = 0.7
    # The column name reserved for holiday feature
    HOLIDAY_COLUMN_NAME = '_Holiday'
    PAID_TIMEOFF_COLUMN_NAME = '_IsPaidTimeOff'

    SEASONALITY_VALUE_NONSEASONAL = 1
    SEASONALITY_VALUE_DETECT = -1
    SEASONALITY_VALUE_DEFAULT = SEASONALITY_VALUE_DETECT
    USE_STL_DEFAULT = None
    STL_VALID_OPTIONS = {TimeSeries.STL_OPTION_SEASON_TREND,
                         TimeSeries.STL_OPTION_SEASON}
    STL_SEASON_SUFFIX = '_season'
    STL_TREND_SUFFIX = '_trend'
    RESERVED_COLUMN_NAMES = {DUMMY_GROUP_COLUMN,
                             DUMMY_ORDER_COLUMN,
                             DUMMY_GRAIN_COLUMN,
                             DUMMY_TARGET_COLUMN}
    FORCE_TIME_INDEX_FEATURES_NAME = 'force_time_index_features'
    FORCE_TIME_INDEX_FEATURES_DEFAULT = None


class Subtasks:
    """The names of the subtasks."""

    FORECASTING = 'forecasting'

    ALL = [FORECASTING]


class Transformers:
    """Names of transformers used for data processing."""

    X_TRANSFORMER = 'datatransformer'
    Y_TRANSFORMER = 'y_transformer'
    LAG_TRANSFORMER = 'laggingtransformer'
    TIMESERIES_TRANSFORMER = 'timeseriestransformer'
    ALL = [X_TRANSFORMER, Y_TRANSFORMER, LAG_TRANSFORMER, TIMESERIES_TRANSFORMER]


class TelemetryConstants:
    """The names of telemetry constants."""

    PRE_PROCESS_NAME = 'PreProcess'
    TRAINING_NAME = 'Training'
    FIT_ITERATION_NAME = 'FitIteration'
    OUTPUT_NAME = 'Output'
    GET_PIPELINE_NAME = 'GetPipeline'
    RUN_PIPELINE_NAME = 'RunPipeline'
    TIME_FIT_NAME = 'TimeFit'
    RUN_TRAIN_VALID_NAME = 'TrainValid'
    RUN_TRAIN_FULL_NAME = 'TrainFull'
    RUN_CV_NAME = 'RunCV'
    RUN_CV_MEAN_NAME = 'RunCVMean'
    RUN_NAME = 'Run'
    COMPUTE_METRICS_NAME = 'ComputeMetrics'
    PREDICT_NAME = 'Predict'
    RUN_ENSEMBLING_NAME = 'RunEnsembling'
    DOWNLOAD_ENSEMBLING_MODELS = 'DownloadEnsemblingModels'
    TIME_FIT_ENSEMBLE_NAME = 'TimeFitEnsemble'
    METRIC_AND_SAVE_MODEL_NAME = 'MetricsAndSaveModel'
    ONNX_CONVERSION = 'ONNXConversion'
    COMPONENT_NAME = 'automl'
    SUCCESS = 'Success'
    FAILURE = 'Failure'


def get_metric_from_type(t):
    """Get valid metrics for a given training type."""
    return {
        TrainingType.TrainFull: TrainingResultsType.TEST_FROM_FULL_METRICS,
        TrainingType.TrainAndValidation: (
            TrainingResultsType.VALIDATION_METRICS),
        TrainingType.TrainValidateTest: (
            TrainingResultsType.VALIDATION_METRICS),
        TrainingType.CrossValidation: TrainingResultsType.CV_MEAN_METRICS
    }[t]


def get_status_from_type(t):
    """Get valid training statuses for a given training type."""
    return {
        TrainingType.TrainFull: TrainingResultsType.TRAIN_FULL_STATUS,
        TrainingType.TrainAndValidation: (
            TrainingResultsType.TRAIN_VALIDATE_STATUS),
        TrainingType.TrainValidateTest: (
            TrainingResultsType.TRAIN_VALIDATE_STATUS),
        TrainingType.CrossValidation: TrainingResultsType.CV_STATUS
    }[t]


class ValidationLimitRule:
    """Class using hold the validation rules."""

    def __init__(
        self,
        lower_bound: int,
        upper_bound: int,
        number_of_cv: int
    ):
        """Init the rule based on the inputs."""
        self.LOWER_BOUND = lower_bound
        self.UPPER_BOUND = upper_bound
        self.NUMBER_OF_CV = number_of_cv


class RuleBasedValidation:
    """Constants for the Rule based validation setting."""

    # If number of input rows is less than CV_Validation_Limit, using CV, else train_valid_split
    CV_VALIDATION_LIMIT = 10000
    # Default CV number
    DEFAULT_N_CROSS_VALIDATIONS = 1  # is basically using train-validation split
    # Default train validate ratio
    DEFAULT_TRAIN_VALIDATE_TEST_SIZE = 0.1
    # Default train validate seed
    DEFAULT_TRAIN_VALIDATE_RANDOM_STATE = 42

    VALIDATION_LIMITS_NO_SPARSE = [
        ValidationLimitRule(0, 1000, 10),
        ValidationLimitRule(1000, 20000, 3),
        ValidationLimitRule(20000, sys.maxsize, 1)
    ]

    SPARSE_N_CROSS_VALIDATIONS = 1  # sparse is basically using train-validation split


# Hashing seed value for murmurhash
hashing_seed_value = 314489979


# Default app_name in custom dimensions of the logs.
DEFAULT_LOGGING_APP_NAME = "AutoML"
LOW_MEMORY_THRESHOLD = 0.5


class FeatureSweeping:
    """Constants for the Feature Sweeping."""

    LOGGER_KEY = 'logger'
