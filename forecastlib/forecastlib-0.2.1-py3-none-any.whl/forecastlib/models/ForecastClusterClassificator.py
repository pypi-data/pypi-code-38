import pandas as pd

class ForecastClusterClassificator(object):
    CLASSIFICATION_NO_OFFER = "no_offer"
    CLASSIFICATION_PROMO = "promo"


    def classify(self, data: pd.DataFrame):
        data["CLASSIFICATION"] = data.apply(lambda row: ForecastClusterClassificator.get_classification(row), axis=1)

        return data["CLASSIFICATION"]

    @staticmethod
    def get_classification(row):
        if ForecastClusterClassificator.is_no_offer(row):
            return ForecastClusterClassificator.CLASSIFICATION_NO_OFFER

        if ForecastClusterClassificator.is_promo:
            return ForecastClusterClassificator.CLASSIFICATION_PROMO

        return group

    @staticmethod
    def is_no_offer(row):
        return row["OFFER_CODE"] == "NO"

    @staticmethod
    def is_promo(row):
        return row["OFFER_CODE"] == "NO"