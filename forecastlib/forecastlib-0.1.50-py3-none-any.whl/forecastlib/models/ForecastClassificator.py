import pandas as pd
import numpy as np

class ForecastClassificator(object):
    def __init__(self, high_sell_classification_model):
        self.high_sell_classification_model = high_sell_classification_model

    def classify(self, data: pd.DataFrame):
        data["HIGH_SELL"] = self.high_sell_classification_model.predict(data)
        data["KNOWN"] = data["AVG_UPA"].apply(lambda x: 1 if float(x) > 0 else 0)


        data["CLASSIFICATION"] = data.apply(lambda row: ForecastClassificator.get_classification(row), axis=1)

        return data["CLASSIFICATION"]

    @staticmethod
    def get_classification(row):
        is_high_sell = row["HIGH_SELL"] > 0
        is_known = row["KNOWN"] > 0

        if is_high_sell and is_known:
            return "high_known"
        if not is_high_sell and is_known:
            return "low_known"
        if is_high_sell and not is_known:
            return "high_unknown"
        if not is_high_sell and not is_known:
            return "low_unknown"

        return "unknown"
