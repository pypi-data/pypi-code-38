from typing import Any

from sklearn.ensemble import (
    AdaBoostClassifier,
    AdaBoostRegressor,
    BaggingClassifier,
    BaggingRegressor,
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, LogisticRegression, Ridge, RidgeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.svm import LinearSVC, LinearSVR, SVC, SVR
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from bamboos.utils.model.ligthgbm_model import LGBModel
from bamboos.utils.model.sklearn_model import SkLearnModel
from bamboos.utils.model.xgboost_model import XGBoostModel

estimator_dict = {
    "LinearRegression": LinearRegression,
    "Ridge": Ridge,
    "Lasso": Lasso,
    "ElasticNet": ElasticNet,
    "SVR": SVR,
    "LinearSVR": LinearSVR,
    "KNeighborsRegressor": KNeighborsRegressor,
    "DecisionTreeRegressor": DecisionTreeRegressor,
    "AdaBoostRegressor": AdaBoostRegressor,
    "BaggingRegressor": BaggingRegressor,
    "ExtraTreesRegressor": ExtraTreesRegressor,
    "GradientBoostingRegressor": GradientBoostingRegressor,
    "RandomForestRegressor": RandomForestRegressor,
    "MLPRegressor": MLPRegressor,
    "LogisticRegression": LogisticRegression,
    "RidgeClassifier": RidgeClassifier,
    "SVC": SVC,
    "LinearSVC": LinearSVC,
    "GaussianNB": GaussianNB,
    "KNeighborsClassifier": KNeighborsClassifier,
    "DecisionTreeClassifier": DecisionTreeClassifier,
    "AdaBoostClassifier": AdaBoostClassifier,
    "BaggingClassifier": BaggingClassifier,
    "ExtraTreesClassifier": ExtraTreesClassifier,
    "GradientBoostingClassifier": GradientBoostingClassifier,
    "RandomForestClassifier": RandomForestClassifier,
    "MLPClassifier": MLPClassifier,
}


def get_estimator(model_name: str):
    if model_name in estimator_dict.keys():
        return estimator_dict[model_name]
    raise ValueError("model_name is not inside catalyst model dictionary")


def createModel(model_name: str, model_type: str, num_class: int = None, **kwargs):
    if model_type == "multiclass":
        if num_class is None:
            raise AssertionError("For multiclass model, num_class must be provided")
    model: Any
    if "XGBoost" in model_name:
        if num_class:
            model = XGBoostModel(model_name, model_type, num_class=num_class, **kwargs)
        else:
            model = XGBoostModel(model_name, model_type, **kwargs)
    elif "LightGBM" in model_name:
        if num_class:
            model = LGBModel(model_name, model_type, num_class=num_class, **kwargs)
        else:
            model = LGBModel(model_name, model_type, **kwargs)
    else:
        estimator = get_estimator(model_name)
        if num_class:
            model = SkLearnModel(model_name, estimator(**kwargs), model_type, num_class=num_class)
        else:
            model = SkLearnModel(model_name, estimator(**kwargs), model_type)
    return model


def regression_model_dict() -> dict:
    """
    Wrapper function containing dictionary of all sklearn, xgboost, and light gbm models for regression dataset.

    Returns:
        Dictionary containing all sklearn, xgboost, and light gbm models for regression dataset
    """
    return {
        "LinearRegression": createModel("LinearRegression", "regression"),
        "Ridge": createModel("Ridge", "regression"),
        "Lasso": createModel("Lasso", "regression"),
        "ElasticNet": createModel("ElasticNet", "regression"),
        "KNeighborsRegressor": createModel("KNeighborsRegressor", "regression"),
        "DecisionTreeRegressor": createModel("DecisionTreeRegressor", "regression"),
        "AdaBoostRegressor": createModel("AdaBoostRegressor", "regression"),
        "BaggingRegressor": createModel("BaggingRegressor", "regression"),
        "ExtraTreesRegressor": createModel("ExtraTreesRegressor", "regression", n_estimators=100),
        "GradientBoostingRegressor": createModel("GradientBoostingRegressor", "regression"),
        "RandomForestRegressor": createModel("RandomForestRegressor", "regression", n_estimators=100),
        "XGBoost": createModel("XGBoostRegressor", "regression", num_boost_round=100),
        "LightGBM": createModel("LightGBMRegressor", "regression", num_boost_round=100),
    }


def binary_model_dict() -> dict:
    """
    Wrapper function containing dictionary of all sklearn, xgboost, and light gbm models for binary dataset.

    Returns:
        Dictionary containing all sklearn, xgboost, and light gbm models for binary dataset
    """
    return {
        "LogisticRegression": createModel("LogisticRegression", "binary", solver="lbfgs", max_iter=1000),
        "RidgeClassifier": createModel("RidgeClassifier", "binary"),
        "GaussianNB": createModel("GaussianNB", "binary"),
        "KNeighborsClassifier": createModel("KNeighborsClassifier", "binary"),
        "DecisionTreeClassifier": createModel("DecisionTreeClassifier", "binary"),
        "AdaBoostClassifier": createModel("AdaBoostClassifier", "binary"),
        "BaggingClassifier": createModel("BaggingClassifier", "binary"),
        "ExtraTreesClassifier": createModel("ExtraTreesClassifier", "binary", n_estimators=100),
        "GradientBoostingClassifier": createModel("GradientBoostingClassifier", "binary"),
        "RandomForestClassifier": createModel("RandomForestClassifier", "binary", n_estimators=100),
        "XGBoost": createModel("XGBoostBinary", "binary", num_boost_round=100),
        "LightGBM": createModel("LightGBMBinary", "binary", num_boost_round=100),
    }


def multiclass_model_dict(num_class: int) -> dict:
    """
    Wrapper function containing dictionary of all sklearn, xgboost, and light gbm models for multiclass dataset.

    Args:
        num_class (int): Number of class in the multiclass dataset

    Returns:
        Dictionary containing all sklearn, xgboost, and light gbm models for multiclass dataset
    """
    return {
        "LogisticRegression": createModel(
            "LogisticRegression",
            "multiclass",
            num_class=num_class,
            multi_class="multinomial",
            solver="lbfgs",
            max_iter=1000,
        ),
        "RidgeClassifier": createModel("RidgeClassifier", "multiclass", num_class=num_class),
        "GaussianNB": createModel("GaussianNB", "multiclass", num_class=num_class),
        "KNeighborsClassifier": createModel("KNeighborsClassifier", "multiclass", num_class=num_class),
        "DecisionTreeClassifier": createModel("DecisionTreeClassifier", "multiclass", num_class=num_class),
        "ExtraTreesClassifier": createModel(
            "ExtraTreesClassifier", "multiclass", num_class=num_class, n_estimators=100
        ),
        "RandomForestClassifier": createModel(
            "RandomForestClassifier", "multiclass", num_class=num_class, n_estimators=100
        ),
        "XGBoost": createModel("XGBoostBinary", "multiclass", num_class=num_class, num_boost_round=100),
        "LightGBM": createModel("LightGBMBinary", "multiclass", num_class=num_class, num_boost_round=100),
    }
