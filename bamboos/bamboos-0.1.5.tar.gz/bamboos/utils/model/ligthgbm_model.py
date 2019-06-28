import lightgbm as lgb
import numpy as np

from bamboos.utils.model.base_model import Model


class LGBModel(Model):
    def __init__(self, name: str, pred_type: str, threshold: float = 0.5, **kwargs) -> None:
        super().__init__(name, None, pred_type, threshold)
        self.kwargs = kwargs
        if self.pred_type == "multiclass":
            assert "num_class" in self.kwargs.keys()
            self.num_class = self.kwargs["num_class"]

    def fit(self, X_train, y_train):
        lgb_train = lgb.Dataset(X_train, y_train, free_raw_data=False)
        if self.pred_type == "binary":
            params = {"task": "train", "objective": "binary", "verbosity": -1}

        elif self.pred_type == "multiclass":
            params = {"task": "train", "objective": "multiclass", "verbosity": -1}

        elif self.pred_type == "regression":
            params = {"task": "train", "objective": "regression", "verbosity": -1}
        else:
            raise ValueError("pred_type should be one of the following: ['binary', 'multiclass', 'regression']")

        for key, value in self.kwargs.items():
            if key != "num_boost_round":
                params[key] = value

        if "num_boost_round" in self.kwargs.keys():
            self.model = lgb.train(params, lgb_train, self.kwargs.get("num_boost_round"))
        else:
            self.model = lgb.train(params, lgb_train)

    def predict(self, X_test):
        if self.pred_type == "binary":
            prob = self.model.predict(X_test)
            pred = np.where(prob >= self.threshold, 1, 0)
        elif self.pred_type == "multiclass":
            pred = np.argmax(self.model.predict(X_test), axis=1)
        elif self.pred_type == "regression":
            pred = self.model.predict(X_test)
        return pred

    def predict_proba(self, X_test):
        if self.pred_type in ["binary", "multiclass"]:
            result = self.model.predict(X_test)
        else:
            raise ValueError("pred_type should be on of the following: ['binary', 'multiclass']")
        return result
