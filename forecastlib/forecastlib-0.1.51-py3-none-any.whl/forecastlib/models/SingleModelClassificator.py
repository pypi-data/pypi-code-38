import pandas as pd


class SingleModelClassificator(object):
    def __init__(self, classification_model):
        self.classification_model = classification_model

    def classify(self, data: pd.DataFrame):
        return self.classification_model.predict(data)
