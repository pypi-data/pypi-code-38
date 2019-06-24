import pandas as pd

class ForecastClassificatorSingle(object):
    def classify(self, data: pd.DataFrame):
        data["CLASSIFICATION"] = data.apply(lambda row: ForecastClassificatorSingle.get_classification(row), axis=1)

        return data["CLASSIFICATION"]

    @staticmethod
    def get_classification(row):
        group = "single"

        group += "_"

        if row["WITH_HISTORY"] > 0:
            group += "known"
        else:
            group += "unknown"

        return group
