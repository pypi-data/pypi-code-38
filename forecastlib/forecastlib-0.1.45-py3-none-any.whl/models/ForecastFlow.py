import pandas as pd


class ForecastFlow(object):
    def __init__(self, classificator, model_map):
        self.classificator = classificator
        self.model_map = model_map

    def predict(self, x):
        classified = self.classify(x.copy())

        frames = []
        for k, v in self.model_map.items():
            group = classified[classified["CLASSIFICATION"] == k]
            if not group.empty:
                group.loc["PREDICTED"] = v.predict(group)
                frames.append(group["PREDICTED"])

        concatenated = pd.concat(frames)
        concatenated = concatenated.sort_index(axis=0)

        return concatenated

    def classify(self, x: pd.DataFrame):
        classification = self.classificator.classify(x)
        x["CLASSIFICATION"] = classification
        return x
