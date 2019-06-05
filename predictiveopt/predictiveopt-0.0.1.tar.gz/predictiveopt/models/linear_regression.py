from sklearn.linear_model import LinearRegression
import pandas as pd


class LinearRegressionModel:

    def __init__(self, x_train, y_train, x_test):
        self.x_train = x_train
        self.y_train = y_train
        self.x_test = x_test

    def run(self):
        model = LinearRegression()
        model.fit(self.x_train, self.y_train)

        predictions = pd.Series(model.predict(self.x_test))

        return predictions
