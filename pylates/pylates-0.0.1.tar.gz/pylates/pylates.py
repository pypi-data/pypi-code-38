from numpy import array, zeros, average
from scipy.interpolate import interp1d, UnivariateSpline
from numpy.random import uniform

class Pylates(object):

	def __init__(self):
		self._coefficients = []		# linear default
		self._boundaries = []
		self._dilfunction = None
		self._Y = None
		self.reset_to_default()

	def reset_to_default(self, use_spline=False):
		"""
			Resets the Dilation Function: the parameters are reverted to the normal semantics.
			Stated otherwise, the Dilator does not apply any dilation to the values.
		"""
		base = array([[0,0], [0.5, 0.5], [1,1]])
		self._coefficients = base.T[0]
		self._Y = base.T[1]
		if use_spline:
			self._dilfunction = UnivariateSpline(self._coefficients, self._Y)	
		else:
			self._dilfunction = interp1d(self._coefficients, self._Y, bounds_error=True, kind="linear")	

	def set_search_space(self, ss):
		self._boundaries = ss

	def specify_control_points(self, chi, use_spline=False):
		
		# step 0: extend coefficients with default points
		chi = [[0,0]]+chi
		chi = chi+[[1,1]]
		chi = array(chi)

		self._coefficients = chi.T[0]
		self._Y = chi.T[1]
		if use_spline:
			self._dilfunction = UnivariateSpline(self._coefficients, self._Y)	
		else:
			self._dilfunction = interp1d(self._coefficients, self._Y, bounds_error=True, kind="linear")	

	def plot_function(self):
		"""
			Service method for plotting the DF.
		"""
		X = self._coefficients
		Y = self._Y
		N = len(self._Y)
		fig, ax = subplots(1,2,figsize=(10,5))
		ax[0].scatter(self._coefficients, self._Y, color="green", label="Dilated function control points")
		ax[1].scatter(self._coefficients, self._boundaries[0][0]+self._Y*(self._boundaries[0][1]-self._boundaries[0][0]), color="green", label="Dilated function control points")
		for x,y in zip(self._coefficients, self._Y): ax[0].text(x,y,str(x))
		
		ax[0].plot(X, self._dilfunction(X), "-", color="lightgray", label="Dilated function")
		ax[1].plot(X, self._boundaries[0][0]+self._dilfunction(X)*(self._boundaries[0][1]-self._boundaries[0][0]), "-", color="lightgray", label="Dilated function")
		
		for (x,y) in zip (X,Y):
			ax[0].plot([x,x],[0,y], "--", color="yellow")
		ax[0].set_xlim(0,1)
		ax[0].set_ylim(0,1)
		ax[0].set_xlabel("Actual parameter value")
		ax[1].set_xlabel("Actual parameter value")
		ax[0].set_ylabel("Dilated parameter value (par 1)")
		ax[1].set_ylabel("Dilated parameter value (par 1) mapped in original space")
		ax[0].legend(loc="upper left")
		fig.tight_layout()
		sns.despine()
		show()

	def dilate_vector(self, V):
		"""	
			Once a Dilation Function is configured, this method can be used to 
			modify a vector of parameters (i.e., a candidate solution) according to
			the distortion defined by the Dilation Function itself.
		"""
		dil_temp = array([self._dilfunction(x) for x in V])
		N = len(dil_temp)
		res = zeros(N)
		for i in xrange(N):
			res[i] = self._boundaries[i][0]+dil_temp[i]*(self._boundaries[i][1]-self._boundaries[i][0])
		return res

	def set_real_fitness(self, fitness):
		"""
			This method binds an external fitness function to the Dilation Function object.
		"""
		self._real_fitness_fun = fitness

	def evaluator(self, X, **kwargs):
		"""
			This method evaluates the external fitness function on the dilated 
			vector of parameters.
		"""
		dilated_vector = self.dilate_vector(X)
		if kwargs:
			fitness_value = self._real_fitness_fun(dilated_vector, kwargs)
		else:
			fitness_value = self._real_fitness_fun(dilated_vector)
		return fitness_value

	def average_of_sampling(self, trials=100):
		ret = []
		for i in xrange(trials):
			rand = uniform(0,1,len(self._boundaries))
			candidate = self.dilate_vector(rand) 
			evaluation = self._real_fitness_fun(candidate) 
			ret.append(evaluation)
		return average(ret)