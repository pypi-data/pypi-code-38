import pandas as pd
from sklearn.preprocessing import MinMaxScaler, PolynomialFeatures
from sklearn.base import BaseEstimator, TransformerMixin
from .utilities import plot_history
import sklearn.pipeline

def set_debug(steps, flag=True, level=0):
	""" recursively set debugging (verbose) status of pipeline items
	"""
	for (name, step) in steps:
		if isinstance(step, (iPipeline, sklearn.pipeline.Pipeline)):
			# set_debug(step.steps, flag, level=level+1)
			# indent is disabled
			set_debug(step.steps, flag, level=0)
		else:
			if flag:
				if not hasattr(step, '_backup_fit'):
					step._backup_fit = step.fit
				else:
					step.fit = step._backup_fit	
				step._DEBUG_ = True
				step._DESC_ = '\t'*level + name
				def decorate_fit(func):
					def wrapper(self, *args, **kwargs):
						_name = self.__class__.__name__
						print("\t"*level, _name, "is fitting..", end=' ')
						f = func(*args, **kwargs)
						print("Ok")
						return f
					return wrapper
				functype = type(step.fit)
				step.fit = functype(decorate_fit(step.fit), step)

				if hasattr(step, 'transform'):
					if not hasattr(step, '_backup_transform'):
						step._backup_transform = step.transform
					else:
						step.transform = step._backup_transform	
					def decorate_transform(func, level):
						def wrapper(self, *args, **kwargs):
							_name = self.__class__.__name__
							print("\t"*level, _name, end=" => ")
							r = func(*args, **kwargs)
							print(r.shape)
							return r
						return wrapper
					functype = type(step.transform)
					step.transform = functype(decorate_transform(step.transform, level), step)
			else:
				if hasattr(step, '_backup_fit'):
					step.fit = step._backup_fit	
				if hasattr(step, 'transform') and hasattr(step, '_backup_transform'):
					step.transform = step._backup_transform
				
class iPipeline(sklearn.pipeline.Pipeline):
	_DEBUG_ = False
	_DESC_ = 'iPipeline'
	def __init__(self, steps, memory=None):
		super().__init__(steps, memory)
	def set_verbose(self, value):
		set_debug([('iPipeline', self)], value)

def make_pipeline(*steps, **kwargs):
	"""Construct a customized Pipeline from the given estimators.
	"""
	memory = kwargs.pop('memory', None)
	if kwargs:
		raise TypeError('Unknown keyword arguments: "{}"'
						.format(list(kwargs.keys())[0]))
	return iPipeline(sklearn.pipeline._name_estimators(steps), memory=memory)

class NoFitTransformer(BaseEstimator, TransformerMixin):
	'''A base class for transformers that does not require fit()'''
	def __init__(self):
		pass        
	def fit(self, X, y=None):
		return self

class BaseTransformer(BaseEstimator, TransformerMixin):
	'''A base class for dataframe transformation. It implements a 
	column list parameter for you so you don't have to repeat yourself.'''
	_DEBUG_ = False
	_DESC_ = 'BaseTransformer'
	def __init__(self, cols=None):
		self.cols = cols
	def get_cols(self, X, cols):
		columns = X.columns.tolist()
		sel = []
		if isinstance(cols, str):
			if cols == '__all__':
				sel = columns
			else:
				sel = [cols]
		else:
			sel = cols
		# check avaiability:
		r = []
		for li in sel:
			if li not in columns:
				print("Warning: column '{}' not found in dataset.".format(li))
			else:
				r.append(li)
		return r
	def fit(self, X, y=None):
		r = self._fit(X, y)
		# if self._DEBUG_:
		# 	print("{} is fitting..".format(self._DESC_))
		# 	self._debug_fit()
		return r
	def _fit(self, X, y):
		return self
	def transform(self, X):
		r = self._transform(X)
		# if self._DEBUG_:
		# 	print("{} : output data shape {}".format(self._DESC_, r.shape))
		# 	self._debug_transform()
		return r
	def _debug_fit(self):
		pass
	def _debug_transform(self):
		pass
	def _transform(self, X):
		return X
	def summary(self, X):
		msg = 'summary message'
		print(msg)


class Select(BaseTransformer):
	"""Select columns by name"""
	def _transform(self, X):
		return X.loc[:, self.cols]

class Drop(BaseTransformer):
	def _transform(self, X):
		return X.drop(self.get_cols(X,self.cols), axis=1)
		
class Dropna(BaseTransformer):
	"""Drop observations if the value of any of the columns are missing"""
	def _transform(self, X):
		return X.dropna(axis=0, how='any', subset=self.cols)

class Impute(BaseTransformer):
	"""Inpute columns with the given imputer"""
	def __init__(self, cols=None, value=0):
		self.cols = cols 
		self.value = value
	def _transform(self, X):
		cols = self.cols
		if not cols:
			cols = X.columns.tolist()
		X.loc[:,cols] = X[cols].fillna(self.value)
		return X

class Rescale(BaseTransformer):
	def __init__(self, cols=None, feature_range=(0,1)):
		self.cols = cols
		self.scaler = MinMaxScaler(feature_range=feature_range)
	def _fit(self, X, y=None):
		if not self.cols:
			self.cols = X.columns.tolist()
		self.scaler.fit(X[self.cols])
		return self
	def _transform(self, X):
		X.loc[:, self.cols] = self.scaler.transform(X[self.cols])
		return X

class Normalize():
	def __init__(self, cols):
		self.cols = cols
	def _fit(self, X, y=None):
		self.mean_std = X[self.cols].describe().loc[['mean', 'std']].to_dict()
		return self
	def _transform(self, X):
		for var, stats in self.mean_std.items():
			X[var] = (X[var] - stats['mean']) / stats['std']
		return X

class Interact(BaseTransformer):
	def __init__(self, cols, degree, drop_cols=True, interaction_only=False, normalize=True):
		self.cols = cols
		self.degree = degree
		self.drop_cols = drop_cols
		self.interaction_only = interaction_only
	def _transform(self, X):
		polyer = PolynomialFeatures(self.degree, interaction_only=self.interaction_only, include_bias=False)
		polys = polyer.fit_transform(X[self.cols])
		poly_names = polyer.get_feature_names(self.cols)
		polydf = pd.DataFrame(polys, columns=poly_names)
		if self.drop_cols:
			X = X.drop(self.cols, axis=1)
		X = pd.concat([X.reset_index(drop=True), polydf], axis=1)
		return X

class EncodeDummy(BaseTransformer):
	def __init__(self, cols):
		self.cols = cols
	def _fit(self, X, y=None):
		self.value_dict = dict()
		for li in self.cols:
			self.value_dict[li] = X[li].unique()
		return self
	def _transform(self, X):
		r_df = []
		for li in self.cols:
			for value in X[li].unique():
				if value not in self.value_dict[li]:
					# TODO: show the % of undocumented values?
					print("Warning: feature '{}' has undocumented value '{}'".format(li, value))
			categorical = pd.Categorical(X.loc[:,li], categories=self.value_dict[li])
			tdf = pd.get_dummies(categorical, prefix=li, dummy_na=True, drop_first=True)
			r_df.append(tdf)
			X.drop(li, axis=1, inplace=True)
		X = pd.concat([X.reset_index(drop=True), *r_df], axis=1)
		return X

class Model(TransformerMixin):
	def __init__(self, model, output='class'):
		self.model = model
		self.output = output

	def fit(self, *args, **kwargs):
		self.model.fit(*args, **kwargs)
		return self

	def transform(self, X, **transform_params):
		if self.output == 'class':
			return self.model.predict(X)
		elif self.output == 'proba':
			return self.model.predict_proba(X)
		else:
			raise ValueError(
				"Unrecognized output format : {}. Choose 'class' or 'proba'.".format(self.output))

class Describe(BaseTransformer):
	def _transform(self, X):
		return X

class Tokenize(BaseTransformer):
	def __init__(self, tokenizer, maxlen):
		self.tokenizer = tokenizer
		self.maxlen=maxlen
	def _fit(self, X, y=None):
		self.tokenizer.fit_on_texts(X)
		return self
	def _transform(self, X):
		from keras.preprocessing import sequence
		seq = self.tokenizer.texts_to_sequences(X)
		seqmat = sequence.pad_sequences(seq, maxlen=self.maxlen)
		return seqmat

class Autoencoder(BaseTransformer):
	def __init__(self, units, optimizer='RMSprop', loss='mean_squared_error',
				noise_param=0.2,
				batch_size=512,
				epochs=400,
				verbose=0):
		self.units = units
		self.optimizer = optimizer
		self.loss = loss
		self.noise_param = noise_param
		self.batch_size = batch_size
		self.epochs = epochs
		self.verbose = verbose
	def _fit(self, X, y=None):
		from .engines import get_AE, add_noise_masking
		m = X.shape[1]
		self.autoencoder, self.encoder, self.decoder = get_AE([m] + self.units)
		self.autoencoder.compile(optimizer=self.optimizer, loss=self.loss)

		Xnoised = add_noise_masking(self.noise_param, X)
		self.history = self.autoencoder.fit(Xnoised,X, 
				batch_size=self.batch_size, 
				epochs=self.epochs,
				verbose=self.verbose)
		return self
	def _debug_fit(self):
		return plot_history(self.history)
	def _transform(self, X):
		return self.encoder.predict(X)

class NN(BaseTransformer):
	def __init__(self, units, optimizer='RMSprop', loss='mean_squared_error',
				batch_size=512,
				epochs=400,
				metrics=None,
				verbose=0):
		self.units = units
		self.optimizer = optimizer
		self.loss = loss
		self.batch_size = batch_size
		self.epochs = epochs
		self.metrics = metrics
		self.verbose = verbose
	def _fit(self, X, y=None):
		from .engines import get_NN
		m = X.shape[1]
		self.nn = get_NN([m] + self.units)
		self.nn.compile(optimizer=self.optimizer, loss=self.loss, metrics=self.metrics)
		self.history = self.nn.fit(X, y, 
				batch_size=self.batch_size, 
				epochs=self.epochs,
				verbose=self.verbose)
		return self
	def _debug_fit(self):
		return plot_history(self.history)
	def _transform(self, X):
		return self.nn.predict(X)
	def score(self, X, y):
		from sklearn.metrics import accuracy_score
		return accuracy_score(y, self.nn.predict_classes(X))
	def predict(self, X):
		return self.nn.predict_classes(X)

class XGB(BaseTransformer):
	def __init__(self, output='class', n_estimators=100, learning_rate=0.1, n_jobs=4, max_depth=2, optimizer='count:poisson'):
		import xgboost as xgb
		self.output = output
		self.model = xgb.XGBClassifier(n_estimators=n_estimators,
								learning_rate=learning_rate,
								n_jobs=n_jobs,
								max_depth=max_depth,
								optimizer=optimizer
								)
	def _fit(self, X, y):
		self.model.fit(X,y)
		return self
	def _transform(self, X):
		if self.output=='class':
			r = self.model.predict(X)
		elif self.output=='proba':
			r = self.model.predict_proba(X)
		else:
			raise ValueError("Unrecognized output format : {}. Choose 'class' or 'proba'.".format(self.predict))
		return r
