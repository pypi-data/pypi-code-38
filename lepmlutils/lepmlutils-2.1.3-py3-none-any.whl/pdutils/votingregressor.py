from sklearn.base import BaseEstimator, TransformerMixin, RegressorMixin, clone
import numpy as np

# VotingRegressor is the usual sklearn estimator, but its
# predictions are the weighted average of several models
class VotingRegressor(BaseEstimator, RegressorMixin, TransformerMixin):
    def __init__(self, models, weights):
        self.models = models
        self.weights = weights
        
    # we define clones of the original models to fit the data in
    def fit(self, X, y):
        self.models = [clone(x) for x in self.models]
        
        # Train cloned base models
        for model in self.models:
            model.fit(X, y)

        return self
    
    #Now we do the predictions for cloned models and average them
    def predict(self, X):
        predictions = np.column_stack([
            model.predict(X) for model in self.models
        ]) * self.weights
        return np.sum(predictions, axis=1)   