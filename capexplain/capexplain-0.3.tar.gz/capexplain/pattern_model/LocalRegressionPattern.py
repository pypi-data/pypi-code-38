import sys
import numpy as np
from sklearn import linear_model
import statsmodels.formula.api as smf
from capexplain.utils import *

class LocalRegressionPattern(object):
    """
        The local regression constraint derived with fixed attributes F, 
        variable attributes V, the assigned values f over fixed attributes F
        threshold \epsilon of deciding whether a tuple $t$ is an outlier 

        Attributes:
            F: fixed attributes
            f_value: the assigned values over F
            V: variable attributes
            epsilon: threshold of deciding outliers
            model: regression model from statsmodels library with the formula agg(B) ~ t[V] 
            regr: model fitted on \pi_{V}(Q_f(R))
            regr_skl: model fitted on \pi_{V}(Q_f(R)) using scikit-learn library
    """

    def __init__(self, F=[], f_value=[], V=[], agg_col='count', epsilon=0.1):
        self.fix_attr = F
        self.fix_attr_value = f_value
        self.var_attr = V
        self.agg_col = agg_col
        self.model = None
        self.regr = None
        self.regr_skl = None
        self.epsilon = epsilon

    def train(self, train_data, formula):
        self.model = smf.ols(formula=formula, data=train_data)
        self.regr = self.model.fit()

    def train_sklearn(self, train_X, train_y):
        self.regr_skl = linear_model.LinearRegression()
        self.regr_skl.fit(train_X, train_y)

    def predict(self, v_values):
        return self.regr.predict(v_values)

    def predict_sklearn(self, v_values):
        return self.regr_skl.predict(v_values)

    def same_fixed_attributes(self, t):
        return self.fix_attr_value == get_F_value(self.fix_attr, t)

    def print_fit_summary(self):
        if self.regr is not None:
            print(self.regr.summary())

    # API for passing fitted regression models
    def set_trained_result_sm(self, regr):
        self.regr = regr

    def set_trained_result_skl(self, regr):
        self.regr_skl = regr
    
