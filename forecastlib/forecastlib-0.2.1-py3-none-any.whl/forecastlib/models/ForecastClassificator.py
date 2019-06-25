import pandas as pd

class ForecastClassificator(object):
    def __init__(self, high_sell_classification_model):
        self.high_sell_classification_model = high_sell_classification_model

    def classify(self, data: pd.DataFrame):
        data["SELL"] = self.high_sell_classification_model.predict(data)
        data["KNOWN"] = data["AVG_UPA"].apply(lambda x: 1 if float(x) > 0 else 0)

        data["CLASSIFICATION"] = data.apply(lambda row: ForecastClassificator.get_classification(row), axis=1)

        return data["CLASSIFICATION"]

    @staticmethod
    def get_classification(row):
        group = ""

        if row["SELL"] == 0:
            group += "low"
        else:
            group += "high"

        group += "_"

        if row["KNOWN"] > 0:
            group += "known"
        else:
            group += "unknown"

        return group
