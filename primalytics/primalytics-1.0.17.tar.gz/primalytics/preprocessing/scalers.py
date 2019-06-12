import numpy
import pandas


class Scaler:
	def __init__(self, scaler_class, fit_variables):
		self.__scaler_class = scaler_class
		self.__fit_variables = fit_variables
		self.__scalers = {}
		self.__fitted = False

	def reset(self):
		self.__scalers = {}
		self.__fitted = False

	def fit(self, df: pandas.DataFrame):
		self.reset()

		for variable in self.__fit_variables:
			scaler = self.__scaler_class()
			scaler.fit(df[[variable]])
			self.__scalers.update({variable: scaler})

		self.__fitted = True

	def transform(self, data, transform_variables: list = None, array_indices: list = None):
		if transform_variables is None:
			transform_variables = self.__fit_variables
		if self.__fitted:
			# transformed = None
			if isinstance(data, dict):
				transformed = data.copy()
				for variable in transform_variables:
					transformed.update({variable: self.__scalers[variable].transform([[data[variable]]])[0, 0]})

			elif isinstance(data, pandas.DataFrame):
				original_variables = list(data.columns)
				other_variables = list(data.columns.difference(transform_variables))
				transformed = pandas.DataFrame(index=data.index)
				for variable in transform_variables:
					transformed = transformed.join(pandas.DataFrame(self.__scalers[variable].transform(data[[variable]]), index=data.index, columns=[variable]))
				transformed = data[other_variables].join(transformed)[original_variables]

			elif isinstance(data, pandas.Series):
				original_variables = list(data.index)
				other_variables = list(data.index.difference(transform_variables))
				transformed = pandas.Series(name=data.name)
				for variable in transform_variables:
					transformed = transformed.append(pandas.Series(self.__scalers[variable].transform([[data[variable]]])[0], index=[variable]))
				transformed = data[other_variables].append(transformed)[original_variables]

			elif isinstance(data, numpy.ndarray):
				if len(data.shape) != 2:
					raise Exception('2D array expected. Got {}D array instead'.format(len(data.shape)))
				if len(array_indices) == len(transform_variables):
					transformed = numpy.array([]).reshape(data.shape[0], 0)
					for i, index in enumerate(range(data.shape[1])):
						if index in array_indices:
							variable = transform_variables[i]
							transformed = numpy.concatenate([transformed, self.__scalers[variable].transform(data[:, [index]])], axis=1)
						else:
							transformed = numpy.concatenate([transformed, data[:, [i]]], axis=1)
				else:
					raise Exception('Wrong number of array_indices! Expected {}, got {}'.format(len(transform_variables), len(array_indices)))

			else:
				raise Exception('Type {} is invalid for scaling transformation'.format(type(data)))

		else:
			raise Exception('Scaler not fitted')

		return transformed

	def fit_transform(self, df: pandas.DataFrame):
		self.fit(df)
		return self.transform(df)


class MultiDimStandardScaler:
	def __init__(self):
		self._mean = None
		self._var = None
		self._std = None
		self.__fitted = None

	def fit(self, df):
		if isinstance(df, pandas.DataFrame):
			data = df.values
		else:
			data = df.copy()

		self._mean = numpy.mean(data, axis=0)
		self._var = numpy.var(data, axis=0)
		self._std = numpy.sqrt(self._var)
		self.__fitted = True

	def transform(self, df):
		if self.__fitted:
			sample_len = len(df)
			scaled = df - numpy.array([self._mean for _ in range(sample_len)])
			scaled = scaled / numpy.array([self._std for _ in range(sample_len)])
		else:
			raise Exception('Scaler not fitted.')

		return scaled

	def fit_transform(self, df):
		self.fit(df)
		return self.transform(df)
