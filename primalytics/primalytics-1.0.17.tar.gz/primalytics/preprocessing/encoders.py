import numpy
import pandas
import sklearn
from sklearn.feature_extraction import FeatureHasher


class Encoder:
	def __init__(self, fit_variables: list, verbose: bool = False):
		self._fit_variables = fit_variables
		self._new_variables = {}
		self._verbose = verbose

		self._fitted = False

		self._is_df = False
		self._is_series = False
		self._is_dict = False
		self._is_array = False

	def reset(self):
		self._fitted = False
		self._new_variables = {}
		self._is_df = False
		self._is_series = False
		self._is_dict = False
		self._is_array = False

	def base_transform(self, data, array_indices, get_transformed):
		if not self._fitted:
			raise FitError('Encoder not fitted')

		self._is_df = isinstance(data, pandas.DataFrame)
		self._is_series = isinstance(data, pandas.Series)
		self._is_dict = isinstance(data, dict)
		self._is_array = isinstance(data, numpy.ndarray)

		if self._is_df:
			skip_data = data[data.columns.difference(self._fit_variables)]
			original_columns = list(data.columns)
			transformed_data = pandas.DataFrame(index=data.index)
		elif self._is_series:
			skip_data = data[data.index.difference(self._fit_variables)]
			original_columns = list(data.index)
			transformed_data = pandas.Series(name=data.name)
		elif self._is_dict:
			skip_data = None
			original_columns = list(data.keys())
			transformed_data = data.copy()
		elif self._is_array:
			skip_data = None
			original_columns = None
			transformed_data = numpy.array([])
			if array_indices is None:
				raise MissingIndicesError('Missing indices for array transformation')
		else:
			raise TypeError('Type not valid for transformation')

		final_columns = []
		if self._is_series or self._is_df or self._is_dict:
			for variable in original_columns:
				if variable in self._fit_variables:
					if self._verbose:
						print('Transforming', variable)

					transformed_col_or_val, new_columns = get_transformed(col_or_val=data[variable], variable=variable)
					final_columns += new_columns

					if self._is_series:
						transformed_data = transformed_data.append(transformed_col_or_val)
					elif self._is_df:
						transformed_data = transformed_data.join(transformed_col_or_val)
					elif self._is_dict:
						transformed_data.pop(variable)
						transformed_data.update(transformed_col_or_val)
				else:
					final_columns.append(variable)

		elif self._is_array:
			index = -1
			for i in range(len(data)):
				if i in array_indices:
					if self._verbose:
						print('Transforming', i)

					index += 1
					variable = self._fit_variables[index]
					transformed_col_or_val, new_columns = get_transformed(col_or_val=data[i], variable=variable)
					transformed_data = numpy.append(transformed_data, transformed_col_or_val)
				else:
					transformed_data = numpy.append(transformed_data, data[i])

		if self._is_series:
			result = skip_data.append(transformed_data)[final_columns]
		elif self._is_df:
			result = skip_data.join(transformed_data)[final_columns]
		elif self._is_dict:
			result = transformed_data
		else:
			result = transformed_data

		return result

	def fit(self, df: pandas.DataFrame, return_new_variables: bool = False):
		pass


class HashEncoder(Encoder):
	def __init__(self, fit_variables: list, n_min_features: int = 2, n_attempt_max: int = 3, n_attempt_tot_max: int = 30, verbose: bool = False):
		super().__init__(fit_variables, verbose)

		self._hashing_dict = {}
		self._n_min_features = n_min_features
		self._n_attempt_max = n_attempt_max
		self._n_attempt_tot_max = n_attempt_tot_max

	def fit(self, df: pandas.DataFrame, return_new_variables: bool = False):
		self.reset()
		self._hashing_dict = {}

		for variable in self._fit_variables:
			if self._verbose:
				print('Fitting', variable)
			self.__get_hashing(df, variable)

		self._fitted = True
		if return_new_variables:
			return self._new_variables

	def transform(self, data, array_indices=None):
		return super().base_transform(data=data, array_indices=array_indices, get_transformed=self.__get_transformed)

	def fit_transform(self, df, return_hashing_cols: bool = False, array_indices=None):
		self.fit(df=df, return_new_variables=return_hashing_cols)
		return self.transform(data=df, array_indices=array_indices)

	def __get_transformed(self, col_or_val, variable: str):
		new_columns = self._new_variables[variable]

		if self._is_series:
			transformed_col_or_val = pandas.Series(self._hashing_dict[variable][col_or_val], index=new_columns)
		elif self._is_df:
			transformed_col_or_val = pandas.DataFrame(list(col_or_val.apply(lambda x: self._hashing_dict[variable][x])), index=col_or_val.index, columns=new_columns)
		elif self._is_dict:
			try:
				hashing_values = self._hashing_dict[variable][col_or_val]
			except KeyError:
				raise HashingError('Value \'{}\' not found in hashing dict for variable \'{}\'.'.format(col_or_val, variable))

			transformed_col_or_val = {new_columns[i]: float(v) for i, v in enumerate(hashing_values)}
		else:
			transformed_col_or_val = numpy.array(self._hashing_dict[variable][col_or_val])

		return transformed_col_or_val, new_columns

	def __get_hashing(self, df: pandas.DataFrame, variable: str):
		n_features = self._n_min_features
		n_attempt = 0
		n_attempt_tot = 0
		lost = -1
		non_trivial = False
		uniques = df.loc[:, variable].unique()
		hashed_matrix = [[]]

		while (lost != 0 or not non_trivial) and n_attempt_tot < self._n_attempt_tot_max:
			non_trivial = False
			feature_hasher = FeatureHasher(input_type='string', n_features=n_features)
			keys_list = list(map(lambda x: str(x) + str(numpy.random.rand())[2:8], uniques))

			hashed_matrix = feature_hasher.fit_transform(keys_list).toarray().astype(int)
			hashed_code = set(map(lambda x: ''.join(x.astype(str)), hashed_matrix))

			lost = len(hashed_code) - len(uniques)

			n_attempt += 1
			n_attempt_tot += 1

			if n_attempt == self._n_attempt_max:
				n_attempt = 0
				n_features += 1

			if min(numpy.var(hashed_matrix, axis=0)) > 0:
				non_trivial = True

		if lost != 0 or not non_trivial:
			raise HashingError('Hashing failed on variable: {}. Lost: {}. Trivial: {}.'.format(variable, lost, not non_trivial))

		else:
			tmp_hashing_dict = dict(zip(uniques, map(list, hashed_matrix)))
			self._hashing_dict.update({variable: tmp_hashing_dict})
			self._new_variables.update({variable: ['{}_H{:03}'.format(variable, i) for i in range(hashed_matrix.shape[1])]})


class CircularEncoder(Encoder):
	def __init__(self, fit_variables: list, verbose: bool):
		super().__init__(fit_variables=fit_variables, verbose=verbose)
		self._variables = fit_variables
		self._parameters = {}

	def fit(self, df: pandas.DataFrame, ranges: dict = None):
		self.reset()
		self._parameters = {}

		for variable in self._variables:
			if ranges is None:
				min_value = df[variable].min()
				max_value = df[variable].max()
			else:
				if variable in ranges.keys():
					min_value = ranges[0]
					max_value = ranges[1]
				else:
					raise Exception('Error! dict \'ranges\' dosn\'t contain variable {}'.format(variable))

			self._parameters.update({variable: {'min': min_value, 'den': max_value - min_value + 1}})
			self._new_variables.update({variable: ['{}_{}'.format(variable, s) for s in ['C', 'S']]})

		self._fitted = True

	def transform(self, data, array_indices=None):
		return super().base_transform(data=data, array_indices=array_indices, get_transformed=self.__get_transformed)

	def fit_transform(self, df, ranges: dict = None, array_indices=None):
		self.fit(df=df, ranges=ranges)
		return self.transform(data=df, array_indices=array_indices)

	def __get_transformed(self, col_or_val, variable: str):
		new_columns = self._new_variables[variable]
		if self._is_series:
			transformed_col_or_val = pandas.Series(self.__get_mapped(col_or_val, variable), index=new_columns)
		elif self._is_df:
			transformed_col_or_val = pandas.DataFrame(list(col_or_val.apply(lambda x: self.__get_mapped(x, variable))), index=col_or_val.index, columns=new_columns)
		elif self._is_dict:
			transformed_col_or_val = {new_columns[i]: float(v) for i, v in enumerate(self.__get_mapped(col_or_val, variable))}
		else:
			transformed_col_or_val = numpy.array(self.__get_mapped(col_or_val, variable))

		return transformed_col_or_val, new_columns

	def __get_mapped(self, x, variable):
		theta = 2 * numpy.pi * (x - self._parameters[variable]['min']) / (self._parameters[variable]['den'])
		return [numpy.cos(theta), numpy.sin(theta)]


class OneHotEncoder(Encoder):
	def __init__(self, fit_variables, verbose: bool = False, **kwargs):
		"""
		:param fit_variables: names of the variables to use
		:param verbose: print log while processing
		:param kwargs: kwargs to pass to sklearn.preprocessing.OneHotEncoder
		"""
		super().__init__(fit_variables=fit_variables, verbose=verbose)
		self._variables = fit_variables

		ohe_args = {'categories': 'auto', 'sparse': False}
		ohe_args.update(kwargs)

		self.__one_hot_encoders = {variable: sklearn.preprocessing.OneHotEncoder(**ohe_args) for variable in self._variables}

	def fit(self, df: pandas.DataFrame, return_new_variables: bool = False):
		self.reset()
		for variable, encoder in self.__one_hot_encoders.items():
			encoder.fit(df[[variable]])

		self._new_variables = {variable: ['{}_OHE{:03}'.format(variable, i) for i, _ in enumerate(df[variable].unique())] for variable in self._variables}

		self._fitted = True
		if return_new_variables:
			return self._new_variables

	def transform(self, data, array_indices=None):
		return super().base_transform(data=data, array_indices=array_indices, get_transformed=self.__get_transformed)

	def fit_transform(self, df, array_indices=None):
		self.fit(df=df)
		return self.transform(data=df, array_indices=array_indices)

	def __get_transformed(self, col_or_val, variable: str):
		new_columns = self._new_variables[variable]

		if self._is_series:
			transformed_col_or_val = pandas.Series(self.__one_hot_encoders[variable].transform([[col_or_val]])[0], index=new_columns)
		elif self._is_df:
			transformed_col_or_val = pandas.DataFrame(self.__one_hot_encoders[variable].transform(col_or_val.values.reshape(-1, 1)), index=col_or_val.index, columns=new_columns)
		elif self._is_dict:
			transformed_col_or_val = {new_columns[i]: float(v) for i, v in enumerate(self.__one_hot_encoders[variable].transform([[col_or_val]])[0])}
		else:
			transformed_col_or_val = self.__one_hot_encoders[variable].transform([[col_or_val]])[0]

		return transformed_col_or_val, new_columns


class KBinsDiscretizer(Encoder):
	def __init__(self, fit_variables, verbose: bool = False, **kwargs):
		"""
		:param fit_variables: names of the variables to use
		:param verbose: print log while processing
		:param kwargs: kwargs to pass to sklearn.preprocessing.OneHotEncoder
		"""
		super().__init__(fit_variables=fit_variables, verbose=verbose)
		self._variables = fit_variables

		self._k_bins_discretizers = {variable: sklearn.preprocessing.KBinsDiscretizer(**kwargs) for variable in self._variables}

	def fit(self, df: pandas.DataFrame, return_new_variables: bool = False):
		self.reset()

		for variable, encoder in self._k_bins_discretizers.items():
			encoder.fit(df[[variable]])
			self._new_variables.update({variable: ['{}_KBD{:03}'.format(variable, i) for i in range(encoder.n_bins_[0])]})

		self._fitted = True
		if return_new_variables:
			return self._new_variables

	def transform(self, data, array_indices=None):
		return super().base_transform(data=data, array_indices=array_indices, get_transformed=self.__get_transformed)

	def fit_transform(self, df, array_indices=None):
		self.fit(df=df)
		return self.transform(data=df, array_indices=array_indices)

	def __get_transformed(self, col_or_val, variable: str):
		new_columns = self._new_variables[variable]
		print(new_columns)
		if self._is_series:
			transformed_col_or_val = pandas.Series(self._k_bins_discretizers[variable].transform([[col_or_val]])[0], index=new_columns)
		elif self._is_df:
			transformed_col_or_val = pandas.DataFrame(self._k_bins_discretizers[variable].transform(col_or_val.values.reshape(-1, 1)), index=col_or_val.index, columns=new_columns)
		elif self._is_dict:
			transformed_col_or_val = {new_columns[i]: float(v) for i, v in enumerate(self._k_bins_discretizers[variable].transform([[col_or_val]])[0])}
		else:
			transformed_col_or_val = self._k_bins_discretizers[variable].transform([[col_or_val]])[0]

		return transformed_col_or_val, new_columns

#
# class KBinsPowers(KBinsDiscretizer):
# 	def __init__(self, variables, verbose: bool = False, **kwargs):
# 		"""
# 		:param variables:
# 		:param verbose:
# 		:param kwargs:
# 		{
# 			'power' : <int>
# 			'variables': [ <variables list> ]
# 		}
# 		{
# 			'power' : <int>
# 			'variables': None
# 		}
# 		{
# 			'powers' :{
# 				variable : (None, [powers])
# 			}
# 		}
# 		{
# 			'powers' :{
# 				variable : ([ <bin indeces> ], [powers])
# 			}
# 		}
# 		"""
# 		super().__init__(variables=variables, verbose=verbose, **kwargs)
#
# 	def fit(self, df: pandas.DataFrame, **kwargs):
# 		super().fit(df, **kwargs)
# 		self._fitted = False
#
# 		power = kwargs.get('power')
# 		if power is not None:
# 			variables = kwargs.get('variables')
# 			if variables is None:
# 				variables = self._variables
#
# 			for variable in variables:
# 				dx = self.__get_dx(s=df[variable], variable=variable)
#
# 		elif 'powers' in kwargs.keys():
# 			for variable, powers in kwargs['powers'].items():
# 				encoder = self._k_bins_discretizers[variable]
#
# 	# encoder.fit(df[[variable]])
# 	# self.__new_columns.update({variable: ['{}_KBD{:03}'.format(variable, i) for i in range(encoder.n_bins_[0])]})
# 	def __get_dx(self, s: pandas.Series, variable: str):
# 		x0 = self._k_bins_discretizers[variable].bin_edges_
# 		dx = self._k_bins_discretizers[variable].transform(s)
# 		return dx


class LabelEncoder(Encoder):
	def __init__(self, fit_variables, verbose=False):
		super().__init__(fit_variables=fit_variables, verbose=verbose)
		self.__label_encoders = {variable: sklearn.preprocessing.LabelEncoder() for variable in self._fit_variables}

	def fit(self, df: pandas.DataFrame, return_new_variables: bool = False):
		self.reset()

		for variable, encoder in self.__label_encoders.items():
			encoder.fit(df[[variable]])

		self._fitted = True
		if return_new_variables:
			return self._new_variables

	def transform(self, data, array_indices=None):
		return super().base_transform(data=data, array_indices=array_indices, get_transformed=self.__get_transformed)

	def fit_transform(self, df, array_indices=None):
		self.fit(df=df)
		return self.transform(data=df, array_indices=array_indices)

	def __get_transformed(self, col_or_val, variable: str):
		if self._is_series:
			transformed_col_or_val = pandas.Series(self.__label_encoders[variable].transform([col_or_val])[0], index=[variable])
		elif self._is_df:
			transformed_col_or_val = pandas.DataFrame(self.__label_encoders[variable].transform(col_or_val.values).reshape(-1, 1), index=col_or_val.index, columns=[variable])
		elif self._is_dict:
			transformed_col_or_val = {variable: self.__label_encoders[variable].transform([col_or_val])[0]}
		else:
			transformed_col_or_val = self.__label_encoders[variable].transform([col_or_val])

		return transformed_col_or_val, variable


class SequentialEncoder:
	def __init__(self, transformers: list):
		"""
		:param transformers: list of tuples with shape: ('encoder_name', encoder_class, <encoder_init_parameters>)
		"""
		self.__encoders = {name: encoder(**kwargs) for name, encoder, kwargs in transformers}

	def fit(self, df: pandas.DataFrame, fit_parameters: dict = None):
		"""
		:param df: pandas.DataFrame to fit
		:param fit_parameters: parameters to pass to fit functions of each encoder: {'encoder_name_1' : {'variable_1': value_1, 'variable_2': value_2} ... }
		"""
		if fit_parameters is not None:
			fit_parameters.update({name: {} for name in self.__encoders.keys() if name not in fit_parameters.keys()})
		else:
			fit_parameters = {name: {} for name in self.__encoders.keys()}
		for name, encoder in self.__encoders.items():
			encoder.fit(df, **fit_parameters[name])

	def transform(self, data, array_indices: dict = None):
		"""
		:param data: data to tranform
		:param array_indices: dict containing indices to use in case data is a numpy.array: {'encoder_name_1: [i_1, i_2, ...], 'encoder_name_2: [...]}
		:return:
		"""
		if array_indices is not None:
			array_indices.update({name: {} for name in self.__encoders.keys() if name not in array_indices.keys()})
		else:
			array_indices = {name: {} for name in self.__encoders.keys()}

		transformed_data = data.copy()
		for name, encoder in self.__encoders.items():
			transformed_data = encoder.transform(data=transformed_data, array_indices=array_indices[name])

		return transformed_data

	def fit_transform(self, df, fit_parameters: dict = None, array_indices: dict = None):
		"""
		:param df: pandas.DataFrame to fit
		:param fit_parameters: parameters to pass to fit functions of each encoder: {'encoder_name_1' : {'variable_1': value_1, 'variable_2': value_2} ... }
		:param array_indices: dict containing indices to use in case data is a numpy.array: {'encoder_name_1: [i_1, i_2, ...], 'encoder_name_2: [...]}
		:return:
		"""
		self.fit(df=df, fit_parameters=fit_parameters)
		return self.transform(data=df, array_indices=array_indices)


# EXCEPTIONS --------------------------------------------------------------------------------------
class FitError(Exception):
	""":raises Error when class Hasher is not fitted"""


class HashingError(Exception):
	""":raises Error when hashing is invalid"""


class MissingIndicesError(Exception):
	""":raises Error when indices are missing"""
