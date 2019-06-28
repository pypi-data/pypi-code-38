import numpy as np
import xgboost as xgb

from bamboos.utils.model.base_model import Model


class XGBoostModel(Model):
    def __init__(self, name: str, pred_type: str, threshold: float = 0.5, **kwargs) -> None:
        super().__init__(name, None, pred_type, threshold)
        self.kwargs = kwargs
        if self.pred_type == "multiclass":
            assert "num_class" in self.kwargs.keys()
            self.num_class = self.kwargs["num_class"]

    def fit(self, X_train, y_train):
        dtrain = xgb.DMatrix(X_train, label=y_train)
        if self.pred_type == "binary":
            params = {"objective": "binary:logistic", "silent": 1}

        elif self.pred_type == "multiclass":
            params = {"objective": "multi:softprob", "silent": 1}

        else:
            assert self.pred_type == "regression"
            params = {"objective": "reg:linear", "silent": 1}

        for key, value in self.kwargs.items():
            params[key] = value

        if "num_boost_round" in self.kwargs.keys():
            self.model = xgb.train(params, dtrain, self.kwargs.get("num_boost_round"), verbose_eval=False)
        else:
            self.model = xgb.train(params, dtrain, verbose_eval=False)

    def predict(self, X_test):
        dtest = xgb.DMatrix(X_test)
        if self.pred_type == "binary":
            prob = self.model.predict(dtest)
            pred = np.where(prob >= self.threshold, 1, 0)
        elif self.pred_type == "multiclass":
            if np.all(np.isnan(self.model.predict(dtest))):
                # Return array of NaN if model predicts all NaN
                pred = self.model.predict(dtest)[:, 0]
            else:
                pred = np.argmax(self.model.predict(dtest), axis=1)
        else:
            assert self.pred_type == "regression"
            pred = self.model.predict(dtest)
        return pred

    def predict_proba(self, X_test):
        dtest = xgb.DMatrix(X_test)
        if self.pred_type in ["binary", "multiclass"]:
            result = self.model.predict(dtest)
        else:
            raise ValueError("pred_type should be on of the following: ['binary', 'multiclass']")
        return result
