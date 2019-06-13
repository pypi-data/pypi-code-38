import json
import os

import numpy as np
# import the necessary packages
import pandas as pd

from forecastlib.evaluation.evaluation import CatalogProduct, EvaluatedProduct, EvaluatedCatalog
from forecastlib.models.ClassificationMLModel import ClassificationMLModel
from forecastlib.models.ForecastClassificator import ForecastClassificator
from forecastlib.models.ForecastFlow import ForecastFlow
from forecastlib.models.ForecastModel import ForecastModel

from forecastlib.training.Metrics import Metrics
from .MappingService import MappingService


class ForecastService(object):
    def __init__(
            self,
            model_loader,
            models,
            classification_model_name: str = "forecast_classification_forest",
            classification_model_version: int = None,
            map_model_name: str = "forecast_map",
            map_model_version: int = None,
            product_data_model_name: str = "product_data",
            product_data_model_version: int = None
    ):
        loaded_models = {}
        for name, model in models.items():
            m = model_loader.download(model.model_name, model.version)
            loaded_models[name] = ForecastModel.load(m)

        classification_path = model_loader.download(classification_model_name, classification_model_version)
        classification_model = ClassificationMLModel.load(classification_path)
        classificator = ForecastClassificator(classification_model)

        map_path = model_loader.download(map_model_name, map_model_version)
        map = self.load_map(map_path)
        product_data_path = model_loader.download(product_data_model_name, product_data_model_version)
        history = self.load_history(product_data_path)
        intents = self.load_intents(product_data_path)

        self.map_service = MappingService(map, history, intents)

        self.wrapper = ForecastFlow(classificator=classificator, model_map=loaded_models)

    def predict(self, original_data: np.array):
        df = self.map_service.from_json(original_data)

        # mapped = self.map_service.apply_mapping(df)
        mapped = self.map_service.apply(df)

        # Predict input
        predictions, classifications = self.wrapper.predict(mapped)

        df["PREDICTED"] = predictions
        df["CLASSIFICATION"] = classifications

        return df

    def load_map(self, path: str):
        with open(path + os.path.sep + "map.json") as json_file:
            return json.load(json_file)

    def load_history(self, path: str):
        history = pd.read_csv(path + os.path.sep + "history.csv", sep=",")
        history["OFFER_PERC_M"] = history["OFFER_PERC_M"].astype(object)
        return history

    def load_intents(self, path: str):
        intents = pd.read_csv(path + os.path.sep + "intents.csv", sep=",")
        return intents

    def evaluate(self, forecasted_data: pd.DataFrame):
        forecasted_data["NPU_RATIO"] = 1.573

        forecasted_data["COST"] = forecasted_data.apply(ForecastService.calculate_cost, axis=1)
        forecasted_data["CONS_COST"] = forecasted_data.apply(ForecastService.calculate_cons_cost, axis=1)
        forecasted_data["UNITS_FORECAST"] = forecasted_data["ACTIVE_CONSULTANTS"].astype(float) * forecasted_data[
            "PREDICTED"]

        forecasted_data["EVALUATED_PRODUCT"] = EvaluatedProduct(
            CatalogProduct(forecasted_data["PROD_ID"], forecasted_data["OFFER_PRICE"], forecasted_data["NPU_RATIO"],
                           forecasted_data["COST"], forecasted_data["CONS_COST"]),
            forecasted_data["OFFER_PERC"].astype(float) / 100.0,
            forecasted_data["UNITS_FORECAST"]
        )

        grouped = {}
        for y, x in forecasted_data.groupby("CAMPAIGN_CD"):
            grouped[y] = EvaluatedCatalog(x["EVALUATED_PRODUCT"], np.average(x["ACTIVE_CONSULTANTS"]))

        return grouped

    def validate(self, forecasted_data: pd.DataFrame):
        validation = {}
        validation["total_accuracy"] = Metrics.model_accuracy(forecasted_data["UPA_ACTUAL"],
                                                              forecasted_data["PREDICTED"])

        for k, v in forecasted_data.groupby("CLASSIFICATION"):
            validation[k] = {}
            group = forecasted_data[forecasted_data["CLASSIFICATION"] == k]
            validation[k]["accuracy"] = Metrics.model_accuracy(group["UPA_ACTUAL"], group["PREDICTED"])
            validation[k]["count"] = group.shape[0]
        return validation


    @staticmethod
    def calculate_cost(row):
        if float(row["OFFER_PERC"]) > 0:
            return float(row["OFFER_PRICE"]) * 100.0 * 0.2 / float(row["OFFER_PERC"])
        else:
            return float(row["OFFER_PRICE"])

    @staticmethod
    def calculate_cons_cost(row):
        if float(row["OFFER_PERC"]) > 0:
            return float(row["OFFER_PRICE"]) * 100.0 * 0.1 / float(row["OFFER_PERC"])
        else:
            return float(row["OFFER_PRICE"])
