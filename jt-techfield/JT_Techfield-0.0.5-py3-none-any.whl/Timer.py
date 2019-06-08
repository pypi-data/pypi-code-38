import time

class Timer():
	def __init__(self):
		self.tictoc = time.time()
	def tic(self):
		self.tictoc = time.time()
	def toc(self):
		return (time.time() - self.tictoc)
	
