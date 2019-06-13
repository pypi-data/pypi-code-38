'''
Jacob Thompson

Feature Transforms
'''
import numpy as np

def StripedStack(array1, array2):
	if array1.shape != array2.shape:
		raise NameError('ARRAY SIZES DO NOT MATCH')
	out = np.array([])
	out.reshape(array1.shape[0], 0)
	for i in range(array1.shape[1]):
		out = np.hstack([out, array1[:, [i]], array2[:, [i]]])
	return out

class Transform():
	def Eval(self, feature):
		return self.Evaluate(feature)
	
	def Rev(self, feature):
		if 'Reverse' in dir(self):
			return self.Reverse(feature)
	
class Normalize(Transform):
	def __init__(self, data):
		self.name = 'Normalize'
		self.max = data.max()
		self.min = data.min()
		
	def Evaluate(self, feature):
		feature = (feature - self.min) / (self.max - self.min)
		return feature

	def Reverse(self, feature):
		feature * (self.max - self.min) + self.min
		return feature
		
class Square(Transform):
	def __init__(self, data):
		self.name = 'Square'
		self.suffix = '_squared'
		
	def Evaluate(self, feature):
		squared_feature = feature * feature
		return StripedStack(feature, feature_squared)
		
class Handle_Missing(Transform):
	def __init__(self, data, missing_str = 'NULL'):
		self.name = 'Handle Missing'
		self.suffix = '_missing'
		self.missing_str = missing_str
		
	def Evaluate(self, feature):
		feature_missing = feature == self.missing_str
		return StripedStack(feature, feature_missing)

class Category_Encode(Transform):
	def __init__(self, data):
		self.name = 'Category Encode'
		self.suffix = '_categorized'
		self.categories = list(set(data.flatten()))	
		
	def Evaluate(self, feature):
		feature_categorized = feature == categories
		return feature_categorized

class Binned_Encode(Transform):
	def __init__(self, data, bin_count = 50):
		bin_bounds = np.linspace(data.min(), data.max(), bin_count + 1)
		self.bin_bounds_lower = bin_bounds[:-1]
		self.bin_bounds_upper = bin_bounds[1:]
		self.bin_bounds_upper[-1] = np.inf
		
	def Evaluate(self, feature):
		feature_binned = (feature >= self.bin_bounds_lower) & (feature < self.bin_bounds_upper)
		return feature_binned
		

		
 
		
		
		
		
		