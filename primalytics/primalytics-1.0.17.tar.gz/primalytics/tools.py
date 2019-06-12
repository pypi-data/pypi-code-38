import pandas
import numpy
import matplotlib.pyplot as plt
import seaborn as sns
import json

float_types = (float, numpy.float, numpy.float16, numpy.float32, numpy.float64)
int_types = (int, numpy.int, numpy.int16, numpy.int32, numpy.int64)


def get_json_dumpable(data: dict, depth=0, max_depth=10) -> dict:
	prc_data = {}
	for k, v in data.items():
		if isinstance(v, (pandas.datetime,)):
			v = str(v)
		elif isinstance(v, (numpy.float, numpy.float16, numpy.float32, numpy.float64)):
			v = float(v)
		elif isinstance(v, (numpy.int, numpy.int8, numpy.int16, numpy.int32, numpy.int64)):
			v = int(v)
		elif isinstance(v, dict):
			if depth == max_depth:
				raise Exception('Maximum depth {} reached'.format(max_depth))
			else:
				v = get_json_dumpable(data=v.copy(), depth=depth+1, max_depth=max_depth)

		if isinstance(k, (pandas.datetime,)):
			k = str(k)
		elif isinstance(k, (numpy.float, numpy.float16, numpy.float32, numpy.float64)):
			k = float(k)
		elif isinstance(k, (numpy.int, numpy.int8, numpy.int16, numpy.int32, numpy.int64)):
			k = int(k)

		prc_data.update({k: v})

	return prc_data


def jprint(j, indent=2):
	print(json.dumps(get_json_dumpable(j), indent=indent))


def describe(df: pandas.DataFrame, columns=None, excluded_columns=None, n_max_levels=100, n_bins=100):
	"""
	:param df: pandas.DataFrame to plot
	:param columns: columns to plot. None plots all the columns in df
	:param excluded_columns: columns to exclude
	:param n_max_levels: maximum number of levels to plot. Variables with more than n_max_levels will not be plot
	:param n_bins: nunber of bins for float/int variables
	"""
	original_figsize = plt.rcParams['figure.figsize']
	plt.rcParams['figure.figsize'] = (18, original_figsize[1])

	if columns is None:
		columns = df.columns
	if excluded_columns is not None:
		columns = [x for x in columns if x not in excluded_columns]

	for col in columns:
		dtype = df[col].dtype
		uniques = df[col].unique()
		n_uniques = len(uniques)
		print('{:_<125} '.format('[variable: {}] [dtype: {}] [n_uniques: {}] '.format(col, dtype, n_uniques)))

		if dtype in float_types:
			df[col].hist(bins=100)
			plt.tick_params('x', rotation=45)
		elif dtype in int_types:
			if n_uniques <= n_max_levels:
				sns.countplot(df[col])
				plt.tick_params('x', rotation=45)
			else:
				df[col].hist(bins=100)
				plt.tick_params('x', rotation=45)
		elif dtype == 'O' and n_uniques < n_max_levels:
			sns.countplot(df[col])
			plt.tick_params('x', rotation=45)

		plt.show()

	plt.rcParams['figure.figsize'] = original_figsize


# auxiliary functions
def inv_logit(x):
	return numpy.exp(x) / (1 + numpy.exp(x))


def linear(x):
	return x


def reciprocal(x):
	return 1.0 / x


def logit(x):
	return numpy.log(x / (1 - x))
