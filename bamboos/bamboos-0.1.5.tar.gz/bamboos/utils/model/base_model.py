from typing import Any

import numpy as np
from sklearn.preprocessing import OneHotEncoder


class Model:
    def __init__(self, name: str, model: Any, pred_type: str, threshold: float) -> None:
        self.name = name
        self.model = model
        self.num_class = None
        self.pred_type = pred_type
        self.threshold = threshold

    def fit(self, X_train, y_train):
        raise NotImplementedError()

    def predict(self, X_test):
        raise NotImplementedError()

    def evaluate(self, X_val, y_val, metric, **kwargs):
        y_pred = self.predict(X_val)
        metric_value = metric(y_val, y_pred, **kwargs)
        return metric_value

    def predict_proba(self, X_test):
        raise NotImplementedError()

    def evaluate_proba(self, X_val, y_val, metric, **kwargs):
        y_score = self.predict_proba(X_val)
        if y_score is None:
            return np.nan

        if self.pred_type == "binary":
            result = metric(y_val, y_score, **kwargs)
        else:
            assert self.pred_type == "multiclass"
            if isinstance(y_val, np.ndarray):
                y_val_ohe = OneHotEncoder(categories=[range(self.num_class)], sparse=False).fit_transform(
                    y_val.reshape(-1, 1)
                )
            else:
                y_val_ohe = OneHotEncoder(categories=[range(self.num_class)], sparse=False).fit_transform(
                    y_val.values.reshape(-1, 1)
                )
            result = metric(y_val_ohe, y_score, **kwargs)
        return result
