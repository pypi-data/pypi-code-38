import os
from time import time
import random
from mesa.space import MultiGrid
import soba.visualization.ramen.performanceGenerator as ramen
from mesa import Model
from mesa.time import RandomActivation
from soba.models.timeControl import Time
import signal

class GeneralModel(Model):
	"""
	Base Class to create simulation models.
	It creates and manages space and agents.

		Attributes:
			height: Height in number of grid cells.
			width: Width in number of grid cells.
			schedule: BaseScheduler object for agent activation.
			grid: Grid object to implement space.
			running: Parameter to control the models execution.
			NStep: Measure of the number of steps.
			occupants: List of Occupant objects created.
			agents: List of the all Agent objects created.
			asciMap: Representation of the map as ASCI used to get FOV information.
			seed: Seed employ in random generations.
			finishSimulation: Parameter to stop the software simulation.
		Methods:
			finishTheSimulation: Finish with the execution of the simulation software.
			run_model: Model execution.
			step: Execution of the scheduler steps.

	"""

	def __init__(self, width, height, seed = int(time()), timeByStep = 60):
		super().__init__()
		"""
		Create a new Model object.
			Args:
				height: Height in number of grid cells.
				width: Width in number of grid cells.
				schedule: BaseScheduler object for agent activation.
				grid: Grid object to implement space.
				running: Parameter to control the models execution.
				NStep: Measure of the number of steps.
				occupants: List of Occupant objects created.
				agents: List of the all Agent objects created.
				asciMap: Representation of the map as ASCI used to get FOV information.
				seed: Seed employ in random generations.
				finishSimulation: Parameter to stop the software simulation.
			Return: Model object
		"""

		self.width = width
		self.height = height
		self.schedule = RandomActivation(self)
		self.grid = MultiGrid(width, height, True)
		self.agents = []
		self.NStep = 0
		self.occupants = []
		self.clock = Time(self, timeByStep = timeByStep)
		self.asciMap = []
		self.finishSimulation = False

	def finishTheSimulation(self):
		"""Finish with the execution of the simulation software."""
		os.system("kill -9 %d"%(os.getpid()))
		os.killpg(os.getpgid(os.getpid()), signal.SIGTERM)

	def step(self):
		"""Main step of the simulation, execution of the scheduler steps."""
		if self.finishSimulation:
			self.finishTheSimulation()
		self.clock.step()
		self.schedule.step()
		self.NStep = self.NStep + 1