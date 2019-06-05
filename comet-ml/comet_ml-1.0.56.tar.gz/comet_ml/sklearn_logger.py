# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************
import copy
import logging

from comet_ml._logging import check_module

LOGGER = logging.getLogger(__name__)


def pre_process_params(params):
    try:
        if "random_state" in params:
            our_params = copy.copy(params)
            if our_params["random_state"].__class__.__name__ == "RandomState":
                del our_params["random_state"]
                return our_params

    except Exception as e:
        LOGGER.info("failed to remove RandomState from sklearn object with error %s", e)

    return params


def fit_logger(experiment, original, ret_val, *args, **kwargs):
    try:
        params = ret_val.get_params()
        processed_params = pre_process_params(params)
        experiment.log_parameters(processed_params)
    except Exception:
        LOGGER.error("Failed to extract parameters from estimator", exc_info=True)


def pipeline_fit_logger(experiment, original, ret_val, *args, **kwargs):
    try:
        params = ret_val.get_params()
        if params is not None and "steps" in params:
            for step in params["steps"]:
                step_name, step_mdl = step
                params = step_mdl.get_params()
                processed_params = pre_process_params(params)
                experiment.log_parameters(processed_params, prefix=step_name)
    except Exception:
        LOGGER.error("Failed to extract parameters from Pipeline", exc_info=True)


FIT_MODULES = [
    ("sklearn.linear_model.theil_sen", "TheilSenRegressor.fit"),
    ("sklearn.svm.classes", "SVR.fit"),
    ("sklearn.linear_model.stochastic_gradient", "SGDRegressor.fit"),
    ("sklearn.linear_model.ridge", "RidgeCV.fit"),
    ("sklearn.linear_model.ridge", "Ridge.fit"),
    ("sklearn.ensemble.forest", "RandomForestRegressor.fit"),
    ("sklearn.neighbors.regression", "RadiusNeighborsRegressor.fit"),
    ("sklearn.linear_model.ransac", "RANSACRegressor.fit"),
    ("sklearn.linear_model.passive_aggressive", "PassiveAggressiveRegressor.fit"),
    ("sklearn.cross_decomposition.pls_", "PLSRegression.fit"),
    ("sklearn.cross_decomposition.pls_", "PLSCanonical.fit"),
    ("sklearn.linear_model.omp", "OrthogonalMatchingPursuitCV.fit"),
    ("sklearn.linear_model.omp", "OrthogonalMatchingPursuit.fit"),
    ("sklearn.svm.classes", "NuSVR.fit"),
    ("sklearn.linear_model.coordinate_descent", "MultiTaskLassoCV.fit"),
    ("sklearn.linear_model.coordinate_descent", "MultiTaskLasso.fit"),
    ("sklearn.linear_model.coordinate_descent", "MultiTaskElasticNetCV.fit"),
    ("sklearn.linear_model.coordinate_descent", "MultiTaskElasticNet.fit"),
    ("sklearn.neural_network.multilayer_perceptron", "MLPRegressor.fit"),
    ("sklearn.svm.classes", "LinearSVR.fit"),
    ("sklearn.linear_model.base", "LinearRegression.fit"),
    ("sklearn.linear_model.least_angle", "LassoLarsIC.fit"),
    ("sklearn.linear_model.least_angle", "LassoLarsCV.fit"),
    ("sklearn.linear_model.least_angle", "LassoLars.fit"),
    ("sklearn.linear_model.coordinate_descent", "LassoCV.fit"),
    ("sklearn.linear_model.coordinate_descent", "Lasso.fit"),
    ("sklearn.linear_model.least_angle", "LarsCV.fit"),
    ("sklearn.linear_model.least_angle", "Lars.fit"),
    ("sklearn.kernel_ridge", "KernelRidge.fit"),
    ("sklearn.neighbors.regression", "KNeighborsRegressor.fit"),
    ("sklearn.linear_model.huber", "HuberRegressor.fit"),
    ("sklearn.ensemble.gradient_boosting", "GradientBoostingRegressor.fit"),
    ("sklearn.gaussian_process.gpr", "GaussianProcessRegressor.fit"),
    ("sklearn.gaussian_process.gaussian_process", "GaussianProcess.fit"),
    ("sklearn.ensemble.forest", "ExtraTreesRegressor.fit"),
    ("sklearn.tree.tree", "ExtraTreeRegressor.fit"),
    ("sklearn.linear_model.coordinate_descent", "ElasticNetCV.fit"),
    ("sklearn.linear_model.coordinate_descent", "ElasticNet.fit"),
    ("sklearn.tree.tree", "DecisionTreeRegressor.fit"),
    ("sklearn.cross_decomposition.cca_", "CCA.fit"),
    ("sklearn.linear_model.bayes", "BayesianRidge.fit"),
    ("sklearn.ensemble.bagging", "BaggingRegressor.fit"),
    ("sklearn.ensemble.weight_boosting", "AdaBoostRegressor.fit"),
    ("sklearn.linear_model.bayes", "ARDRegression.fit"),
    ("sklearn.svm.classes", "SVC.fit"),
    ("sklearn.linear_model.ridge", "RidgeClassifierCV.fit"),
    ("sklearn.linear_model.ridge", "RidgeClassifier.fit"),
    ("sklearn.ensemble.forest", "RandomForestClassifier.fit"),
    ("sklearn.neighbors.classification", "RadiusNeighborsClassifier.fit"),
    ("sklearn.discriminant_analysis", "QuadraticDiscriminantAnalysis.fit"),
    ("sklearn.linear_model.perceptron", "Perceptron.fit"),
    ("sklearn.linear_model.passive_aggressive", "PassiveAggressiveClassifier.fit"),
    ("sklearn.svm.classes", "NuSVC.fit"),
    ("sklearn.neighbors.nearest_centroid", "NearestCentroid.fit"),
    ("sklearn.naive_bayes", "MultinomialNB.fit"),
    ("sklearn.neural_network.multilayer_perceptron", "MLPClassifier.fit"),
    ("sklearn.linear_model.logistic", "LogisticRegressionCV.fit"),
    ("sklearn.linear_model.logistic", "LogisticRegression.fit"),
    ("sklearn.svm.classes", "LinearSVC.fit"),
    ("sklearn.discriminant_analysis", "LinearDiscriminantAnalysis.fit"),
    ("sklearn.semi_supervised.label_propagation", "LabelSpreading.fit"),
    ("sklearn.semi_supervised.label_propagation", "LabelPropagation.fit"),
    ("sklearn.neighbors.classification", "KNeighborsClassifier.fit"),
    ("sklearn.ensemble.gradient_boosting", "GradientBoostingClassifier.fit"),
    ("sklearn.gaussian_process.gpc", "GaussianProcessClassifier.fit"),
    ("sklearn.naive_bayes", "GaussianNB.fit"),
    ("sklearn.ensemble.forest", "ExtraTreesClassifier.fit"),
    ("sklearn.tree.tree", "ExtraTreeClassifier.fit"),
    ("sklearn.tree.tree", "DecisionTreeClassifier.fit"),
    ("sklearn.calibration", "CalibratedClassifierCV.fit"),
    ("sklearn.naive_bayes", "BernoulliNB.fit"),
    ("sklearn.ensemble.bagging", "BaggingClassifier.fit"),
    ("sklearn.ensemble.weight_boosting", "AdaBoostClassifier.fit"),
    ("sklearn.linear_model.stochastic_gradient", "SGDClassifier.fit"),
]

PIPELINE_FIT_MODULES = [("sklearn.pipeline", "Pipeline.fit")]


def patch(module_finder):
    check_module("sklearn")

    # Register the pipeline fit methods
    for module, object_name in PIPELINE_FIT_MODULES:
        module_finder.register_before(module, object_name, pipeline_fit_logger)
        module_finder.register_after(module, object_name, pipeline_fit_logger)

    # Register the fit methods
    for module, object_name in FIT_MODULES:
        module_finder.register_before(module, object_name, fit_logger)
        module_finder.register_after(module, object_name, fit_logger)


# https://blog.sqreen.io/dynamic-instrumentation-agent-for-python/

check_module("sklearn")
