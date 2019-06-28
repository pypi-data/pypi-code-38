import datetime
from mesa import Agent

class Time(Agent):
	"""
	Class that inherits of the Agent class to manage the time in sexagesimal units.

		Attributes:
			clock: Clock for time monitoring during simulation.
			timeByStep: Time in seconds associated with each step.
			startDay: Time of the beginning of a day in the simulation.
			endDay: Time of the end of a day in the simulation.
		Methods:
			step: Advance of the clock in a step.
			increaseTime: Increase the value of the clock a given time.
			decreaseTime: Decrease the value of the clock a given time.
	"""

	def __init__(self, model, timeByStep = 60, day = 1, hour = 7, minute = 50, seg = 0, microsecond = 0):
		super().__init__(100000, model)
		"""
		Create a new Time object.
			Args: 
				models: Associated Model object.
				timeByStep: Time in seconds associated with each step.
				day, hour, minute, seg, microsecond: Initial time value of the clock.
			Return: Time object.
		"""
		self.timeByStep = timeByStep
		today = datetime.date.today()
		self.startDay = datetime.datetime(today.year, today.month, day, hour, minute, seg, microsecond)
		self.endDay = datetime.datetime(today.year, today.month, 1, 20, 0, 0, 0)
		self.clock = self.startDay

	def increaseTime(self, seconds=0, days=0, hours=0, minutes=0, microseconds=0):
		"""
		Increase the value of the clock a given time.
			Args:
				seconds, days, hours, minutes, microseconds: Time value to be increase.
			Return: The new Clock object.
		"""
		clockOld = self.clock
		dayOld = clockOld.day
		clockNew = clockOld + datetime.timedelta(days=days, minutes=minutes, seconds=seconds, microseconds=microseconds)
		if clockNew.hour >= self.endDay.hour and clockNew.minute > self.endDay.minute:
			clockNew = datetime.datetime(2107, 1, dayOld+1, self.startDay.hour, self.startDay.minute, 0, 0)
			+ (clockNew - self.endDay)
		return clockNew

	def decreaseTime(self, days=0, hours=0, minutes=0, seconds=0, microseconds=0):
		"""
		Decrease the value of the clock a given time.
			Args:
				seconds, days, hours, minutes, microseconds: Time value to be decrease.
			Return: The new Clock object.
		"""
		clockOld = self.clock
		clockNew = clockOld - datetime.timedelta(days=days, minutes=minutes, seconds=seconds, microseconds=microseconds)
		return clockNew

	def step(self):
		"""Advance of the clock in a step."""
		self.clock = self.increaseTime(self.timeByStep)
		print(self.clock.strftime("%d:%H:%M:%S"))