import time
from scipy import interpolate
import numpy as np
from termcolor import cprint,colored

def print_input(input):
	print(input)

def double_input(input):
	return(2*input)

class dsb:
	def __init__(self):
		self.counter = 0
		self.time_array = []
		self.start_time = time.time()
		self.time_left = '--'
	def statusbar(self,i,N,**kwargs):
		"""
		i is the current iteration (must be an int) and N is the length of
		the range (must be an int). i must also be in [0,N).

		~~~~~~~~~~~~~~
		**kwargs
		~~~~~~~~~~~~~~

		title should be a str that will be displayed before the statusbar. title
		should be no longer than 25 characters.

		~~~~~~~~~~~~~~

		NOTE: you should place a print('\n') after the loop to ensure you
		begin printing on the next line.

		"""
		def get_terminal_width():
			try:
				from shutil import get_terminal_size
				return get_terminal_size().columns
			except ImportError:
				import subprocess
				return int(subprocess.check_output(["tput", "cols"]))

		terminal_width = get_terminal_width()
		used_space = len(
			'XXXX.X' + '% Complete, ' + 'XXXXX.X '
			+ ' sec, (est. ' + "XXXXX.X" + ' sec left)')
		statusbar_width = terminal_width - 2 - used_space

		title = kwargs.get("title",'Function')
		assert type(title) == str, "title should be a string"

		assert type(i)==int, "i must be an int"
		assert type(N)==int, "N must be an int"
		assert N>i, "N must be greater than i"
		assert N>0, "N must be a positive integer"
		assert i>=0, "i must not be negative (can be zero)"

		statusbar = colored(
			('['
			+ '\u25a0'*int((i+1)/(N/statusbar_width)) \
			+ '\u25a1'*(statusbar_width-int((i+1)/(N/statusbar_width)))
			+ '] '
			), 'white',attrs=['bold'])
		if hasattr(self,'bar_indices'):
			if i == self.bar_indices[0]:
				self.__delattr__('bar_indices')
				self.__init__()

		if self.counter == 0:
			self.bar_indices = list(
				set(
					[int(el) for el in np.linspace(i,N,statusbar_width+1)]
					)
				)
			print(colored(
				(">>> Running "
				+ title
				+ " <<<"
				),'blue',attrs=['bold']))
			self.counter += 1
		elif i==self.bar_indices[1] and self.counter == 1:
			self.time_array.append(time.time()-self.start_time)
			self.time_left = '{0:1.1f}'.format(self.time_array[-1]*(N/(i+1)))
			self.counter += 1
		elif i == self.bar_indices[self.counter]:
			self.time_array.append(time.time()-self.start_time)
			run_time_func = interpolate.interp1d(
				np.arange(len(self.time_array)),
				self.time_array,
				fill_value='extrapolate'
				)
			end_time_estimate = run_time_func(len(self.bar_indices)-3)
			self.time_left = '{0:1.1f}'.format(
				float(end_time_estimate - (time.time()-self.start_time))
				)
			self.counter += 1
		print(" "*(terminal_width-1),end='\r')
		print(
			(statusbar
			+ colored('{0:1.1f}'.format((i+1)/N*100) + '% complete, ','blue') + colored(
				('{0:1.1f}'.format(time.time() - self.start_time)
				+ ' sec,'
				),
				'red')
			+ colored(' (est. ' + self.time_left + ' sec left)','white')
			), \
			end='\r')
		if i == N-1:
			print(" "*terminal_width)
			print(
				statusbar
				+ colored(
					('{0:1.1f}'.format((i+1)/N*100)
					+ '% complete, '
					),
					'blue')
				+ colored(
					('(Total Run Time: '
					+ '{0:1.1f}'.format(time.time() - self.start_time)
					+ ' sec)'
					),
					'green')
				)
			print('\n')
	def reset_dsb(self):
		self.__delattr__('bar_indices')
		self.__init__()
