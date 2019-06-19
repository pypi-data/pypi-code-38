import time
from scipy import interpolate
import numpy as np
from termcolor import cprint,colored

def get_terminal_width():
	try:
		from shutil import get_terminal_size
		return get_terminal_size().columns
	except ImportError:
		import subprocess
		return int(subprocess.check_output(["tput", "cols"]))

class dsb:
	def __init__(self,initial_value,final_value,**kwargs):
		"""
		~~~~~~~~~~~~~~
		**kwargs
		~~~~~~~~~~~~~~

		title should be a str that will be displayed before the statusbar. title
		should be no longer than 25 characters.

		"""

		self.terminal_width = get_terminal_width()
		used_space = len(
			'XXXX.X' + '% Complete, ' + 'XXXXX.X '
			+ ' sec, (est. ' + "XXXXX.X" + ' sec left)')
		self.statusbar_width = self.terminal_width - 2 - used_space

		self.title = kwargs.get("title",'a Loop')
		assert type(self.title) == str, "title should be a string"

		self.initial_value = initial_value
		assert (type(self.initial_value) == int
				and self.initial_value>=0), \
			"initial_value must be a positvie int or 0."

		self.final_value = final_value
		assert (type(self.final_value) == int
				and self.final_value>0), \
			"final_value must be a positvie int."

		self.time_left = '--'
		self.time_array = []
		self.start_time = time.time()

	def update(self,i,**kwargs):
		"""
		i is the current iteration (must be an int) and must be in [0,N).

		~~~~~~~~~~~~~~

		NOTE: you should place a print('\n') after the loop to ensure you
		begin printing on the next line.

		"""
		assert hasattr(self,"title"), "dsb() was not properly initialized. Does not have title."
		self.title = kwargs.get("title",self.title)
		assert type(self.title) == str, "title should be a string"

		assert type(i)==int, "i must be an int"
		assert self.initial_value<=i<self.final_value, \
			("i must be greater than or equal to "
			+ str(self.initial_value)
			+ " but less than "
			+ str(self.final_value)
			)

		if not hasattr(self,"bar_indices"):
			self.bar_indices = sorted(
				list(
					set(
						[int(el) for el in np.linspace(	self.initial_value,
														self.final_value,
														self.statusbar_width+1)]
						)
					)
				)
			self.percentage_indices = sorted(
				list(
					set(
						[int(el) for el in np.linspace(	self.initial_value,
														self.final_value,
														1001)]
						)
					)
				)
		else:
			if i == self.bar_indices[0]:
				self.reset()
				self.bar_indices = sorted(
					list(
						set(
							[int(el) for el in np.linspace(	self.initial_value,
															self.final_value,
															self.statusbar_width+1)]
							)
						)
					)
				self.percentage_indices = sorted(
					list(
						set(
							[int(el) for el in np.linspace(	self.initial_value,
															self.final_value,
															1001)]
							)
						)
					)

		if i == self.initial_value:
			print(colored(
				(">>> Running "
				+ self.title
				+ " <<<"
				),'blue',attrs=['bold']))
			self.statusbar_string = colored((
				'['
				+ '\u25a0'
					*int(
						(i-self.initial_value+1)
						/((self.final_value-self.initial_value)/self.statusbar_width)
						) \
				+ '\u25a1'
					*(
						self.statusbar_width
						-int(
							(i-self.initial_value+1)
							/((self.final_value-self.initial_value)/self.statusbar_width)
							)
					)
				+ '] '
				), 'white',attrs=['bold'])
		elif i == self.bar_indices[1]:
			self.statusbar_string = colored((
				'['
				+ '\u25a0'
					*int(
						(i-self.initial_value+1)
						/((self.final_value-self.initial_value)/self.statusbar_width)
						) \
				+ '\u25a1'
					*(
						self.statusbar_width
						-int(
							(i-self.initial_value+1)
							/((self.final_value-self.initial_value)/self.statusbar_width)
							)
					)
				+ '] '
				), 'white',attrs=['bold'])
			self.time_array.append(abs(time.time()-self.start_time))
			self.time_left = '{0:1.1f}'.format(self.time_array[-1]*((self.final_value-self.initial_value)/(i-self.initial_value+1)))
		elif i+1 in self.bar_indices[2:]:
			self.statusbar_string = colored((
				'['
				+ '\u25a0'
					*int(
						(i-self.initial_value+1)
						/((self.final_value-self.initial_value)/self.statusbar_width)
						) \
				+ '\u25a1'
					*(
						self.statusbar_width
						-int(
							(i-self.initial_value+1)
							/((self.final_value-self.initial_value)/self.statusbar_width)
							)
					)
				+ '] '
				), 'white',attrs=['bold'])
			self.time_array.append(abs(time.time()-self.start_time))
			run_time_func = interpolate.interp1d(
				np.arange(len(self.time_array)),
				self.time_array,
				fill_value='extrapolate'
				)
			end_time_estimate = run_time_func(len(self.bar_indices)-3)
			self.time_left = '{0:1.1f}'.format(
				float(abs(end_time_estimate - (time.time()-self.start_time)))
				)

		if i+1 in self.percentage_indices:
			if i+1 == self.percentage_indices[-1]:
				self.statusbar = (
					self.statusbar_string
					+ colored(
						('{0:1.1f}'.format((i-self.initial_value+1)/(self.final_value-self.initial_value)*100)
						+ '% complete, '
						),'blue')
					+ colored(
						('(Total Run Time: '
						+ '{0:1.1f}'.format(time.time() - self.start_time)
						+ ' sec)'
						),'green')
					+ '\n'
					)
				print(" "*(self.terminal_width-1), end='\r')
				print(self.statusbar + '\n', end='\r')
			else:
				if not hasattr(self,"statusbar"):
					previous_length = self.terminal_width-1
				else:
					previous_length = len(self.statusbar)
				self.statusbar = (
					self.statusbar_string
					+ colored((
						'{0:1.1f}'.format((i-self.initial_value+1)/(self.final_value-self.initial_value)*100)
						+ '% complete, '
						),'blue')
					+ colored((
						'{0:1.1f}'.format(time.time() - self.start_time)
						+ ' sec,'
						),'red')
					+ colored((
						' (est. '
						+ self.time_left
						+ ' sec left)'
						),'white')
					)
				if previous_length > len(self.statusbar):
					print(" "*(self.terminal_width-1), end='\r')
				print(self.statusbar, end='\r')
	def reset(self,**kwargs):
		"""
		Resets the statusbar for easy sequential loops. Default settings are best used for consecutive loops of the same size, with the same starting value and the same title. Title, starting value, and number of loops can be changed via **kwargs.

		~~~~~~~~~~~~~~
		**kwargs
		~~~~~~~~~~~~~~

		title should be a str that will be displayed before the statusbar. title
		should be no longer than 25 characters. Default will be the previous title.

		initial_value must be an int greater than or equal to zero. Default is the previous initial_value.

		final_value must be a positive int. Default is the previous final_value.
		"""

		self.__delattr__('bar_indices')

		assert hasattr(self,"title"), "dsb() has no attr 'title'. dsb() must be initialized before it can be reset."
		self.title = kwargs.get("title",self.title)
		assert type(self.title) == str, "title should be a string"

		assert hasattr(self,"initial_value"), "dsb() has no attr 'initial_value'. dsb() must be initialized before it can be reset."
		self.initial_value = kwargs.get("initial_value",self.initial_value)
		assert (type(self.initial_value) == int
				and self.initial_value>=0), \
			"initial_value must be a positvie int or 0."

		assert hasattr(self,"final_value"), "dsb() has no attr 'final_value'. dsb() must be initialized before it can be reset."
		self.final_value = kwargs.get('final_value',self.final_value)
		assert (type(self.final_value) == int
				and self.final_value>0), \
			"final_value must be a positvie int."

		self.time_left = '--'
		self.time_array = []
		self.start_time = time.time()
