import pandas as pd

from forecastlib.libs.ModelSerializer import ModelSerializer

class ForecastWrapper(object):
	def __init__(self, inlier_model, outlier_model, classification_model):
		self.inlier_model = inlier_model
		self.outlier_model = outlier_model
		self.classification_model = classification_model

	def predict(self, x):
		x_with_outliers = self.add_outliers(x.copy())

		outliers = x_with_outliers[x_with_outliers.HIGHLY_SELLABLE == 1]

		if not outliers.empty:
			outliers["PREDICTED"] = self.outlier_model.predict(outliers)

		inliers = x_with_outliers[x_with_outliers.HIGHLY_SELLABLE == 0]

		if not inliers.empty:
			inliers["PREDICTED"] = self.inlier_model.predict(inliers)

		frames = [outliers, inliers]
		concatenated = pd.concat(frames)
		concatenated = concatenated.sort_index(axis=0)

		return concatenated["PREDICTED"]

	def add_outliers(self, x):
		outliers = self.classification_model.predict(x)
		x["HIGHLY_SELLABLE"] = outliers
		return x
