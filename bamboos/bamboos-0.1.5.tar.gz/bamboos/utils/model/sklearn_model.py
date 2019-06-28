import warnings

from sklearn.base import BaseEstimator

from bamboos.utils.model.base_model import Model


class SkLearnModel(Model):
    def __init__(self, name: str, model: BaseEstimator, pred_type: str, threshold: float = 0.5, **kwargs) -> None:
        super().__init__(name, model, pred_type, threshold)
        self.kwargs = kwargs
        if self.pred_type == "multiclass":
            assert "num_class" in self.kwargs.keys()
            self.num_class = self.kwargs["num_class"]

    def fit(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X_test):
        if self.pred_type == "binary":
            result = self.model.predict(X_test)

        elif self.pred_type == "multiclass":
            result = self.model.predict(X_test)

        else:
            assert self.pred_type == "regression"
            result = self.model.predict(X_test)
        return result

    def predict_proba(self, X_test):
        if self.pred_type == "binary":
            if not hasattr(self.model, "predict_proba"):
                warnings.warn("Model {} does not have attribute predict_proba. Returning None".format(self.name))
                result = None
            else:
                result = self.model.predict_proba(X_test)[:, 1]
        elif self.pred_type == "multiclass":
            if not hasattr(self.model, "predict_proba"):
                warnings.warn("Model {} does not have attribute predict_proba. Returning None".format(self.name))
                result = None
            else:
                result = self.model.predict_proba(X_test)
        else:
            raise ValueError("pred_type should be on of the following: ['binary', 'multiclass']")
        return result
