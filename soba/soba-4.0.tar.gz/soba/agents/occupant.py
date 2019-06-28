import operator
from collections import OrderedDict
import datetime
from transitions import Machine
from transitions import State
from soba.agents.resources.behaviourMarkov import Markov
from mesa import Agent
import random
import math
import numpy as np

class Occupant(Agent):
	"""
	Base class to models occupants as Occupant objects.
	The occupants are agents with their activity defined by markov states.

		Attributes:
			color: Color with which the occupant will be represented in the visualization.
			positionByState: Position associated to each state for an occupant.
			timeActivity: Time that is required to complete an activity (state) in minutes.
			schedule: Activity periods (hours:minutes).
			states: States of the occupant.
			machine: State machine defined by the attribute 'states'.
			movements: List of movements that will be followed by the occupant.
			pos_to_go: Position to which the occupant wishes to move.
			markov_machine: Object of the Markov class that regulates markovian behavior.
		
		Methods:
			setTodaySchedule: Calculate and define the schedules of the occupants.
			start_activity: Defines the actions that are made when a state is started.
			finish_activity: Defines the actions that are made when a state is finished.
			changeSchedule: Force a possible change of state to reach a certain end of period.
			getPeriod: Get the temporary period in which the occupant is.
			step: Method invoked by the Model scheduler in each step. Step common to all occupants.

	"""

	def __init__(self, unique_id, model, json, speed = 0.71428):
		super().__init__(unique_id, model)
		"""
		Create a new Occupant object.
			Args: 
				unique_id: Unique identifier corresponding to the agent.
				models: Associated Model object
				json: Json of definition of parameters of behavior
				speed: Movement speed in m/s
			Return: Occupant object
		"""

		self.shape = 'circle' if json.get('shape') == None else json.get('shape')
		self.model.schedule.add(self)
		self.color = 'blue' if json.get('color') == None else json.get('color')
		self.variationSchedule = json.get('variation')
		self.jsonSchedule = json['schedule']
		self.schedule = json['schedule'].copy()
		self.setTodaySchedule()
		self.type = json['type']

		self.markovActivity = json['markovActivity']

		self.timeActivity = json['timeActivity']
		self.timeActivityVariation = json.get('timeActivityVariation')

		self.positionByStateAux = json['states']

		#State machine
		self.positionByState = {}
		self.states = []
		for k, v in json['states'].items():
			name = k
			on_enter = 'start_activity'
			on_exit = 'finish_activity'
			self.states.append(State(name=name, on_enter=[on_enter], on_exit=[on_exit]))
		self.machine = Machine(model=self, states=self.states, initial=list(json['states'].items())[0][0])

		self.triggers = {}
		n_state = 0
		for k, v in json['states'].items():
			name = k
			self.machine.add_transition('setState'+str(n_state), '*', name)
			self.triggers[name] = 'setState'+str(n_state)+'()'
			n_state = n_state + 1

		self.markov_machine = Markov(self)

		self.speed = speed
		self.markov = True
		self.time_activity = 0
		self.lastSchedule = 0.0
		self.N = 0
		self.pos = (0, 0)
		self.pos_to_go = (0, 0)
		self.movements = [self.pos]
		self.inbuilding = False

	def setTodaySchedule(self):
		"""
		Calculate and define the schedules of the occupants applying the information provided and normal Gaussian variations.
		"""
		for k, v in self.jsonSchedule.items():
			if not self.variationSchedule:
				self.schedule[k] = datetime.datetime(2017, 10, 1, int(v[0]+v[1]), int(v[3]+v[4]), 0, 0)
			else:
				variation = self.variationSchedule.get(k)
				variation = datetime.datetime(2017, 10, 1, int(variation[0]+variation[1]), int(variation[3]+variation[4]), 0, 0)
				reference = datetime.datetime(2017, 10, 1, 0, 0, 0, 0)
				variationSeconds = (variation - reference).total_seconds()
				mu = 0
				sigma = variationSeconds/3
				variationSecondsNormal = np.random.normal(mu, sigma)
				variationTime = datetime.timedelta(seconds=variationSecondsNormal)
				newSchedule = datetime.datetime(2017, 10, 1, int(v[0]+v[1]), int(v[3]+v[4]), 0, 0) + datetime.timedelta(seconds=variationSecondsNormal)
				self.schedule[k] = newSchedule

	def start_activity(self):
		""" 
		Defines the actions that are made when a state is started. 
		Default, this method calculates the value of the attributes 'time_activity' and 'movements'
		corresponding to the new state.
		"""
		self.markov = False
		self.N = 0
		self.pos_to_go = self.getPlaceToGo()
		if self.pos != self.pos_to_go:
			self.movements = self.getWay()
		else:
			self.movements = [self.pos]
		time_in_state = self.timeActivity[self.getPeriod()][list(self.positionByState.keys()).index(self.state)]
		if self.timeActivityVariation:
			time_in_state_variation = self.timeActivityVariation[self.getPeriod()][list(self.positionByState.keys()).index(self.state)]
			mu = 0
			sigma = time_in_state_variation/3
			if sigma:
				time_in_state = time_in_state + np.random.normal(mu, sigma, 1)
		self.time_activity = (time_in_state*60)/self.model.clock.timeByStep

	def finish_activity(self):
		""" Defines the actions that are made when a state is finished."""
		pass

	def changeSchedule(self):
		""" 
		Force a possible change of state to reach a certain end of period. 

			Return: 
				True if the period has been changed, False otherwise.
		"""

		beh = sorted(self.schedule.items(), key=operator.itemgetter(1))
		nextSchedule = False
		for i in beh:
			a, b = i
			if b < self.model.clock.clock:
				nextSchedule = a
		if nextSchedule != self.lastSchedule:
			self.lastSchedule = nextSchedule
			return True
		else:
			return False

	def getPeriod(self):
		"""
		Get the temporary period in which the occupant is.

			Return: 
				Current period as String
		"""

		t1 = datetime.datetime(2017, 10, 1, 0, 0, 0, 0)
		t2 = datetime.datetime(2017, 10, 1, 23, 59, 59, 59)
		t1k = ''
		t2k = ''
		schedule = self.schedule
		for k, v in schedule.items():
			if((self.model.clock.clock.hour == v.hour and self.model.clock.clock.minute >= v.minute) or (self.model.clock.clock.hour > v.hour)) and ((v.hour > t1.hour) or (v.hour == t1.hour and v.minute >= t1.minute)):
				t1 = v
				t1k = k
			if((v.hour > self.model.clock.clock.hour) or (v.hour == self.model.clock.clock.hour and v.minute > self.model.clock.clock.minute)) and ((t2.hour > v.hour) or (t2.hour == v.hour and t2.minute > v.minute)):
				t2 = v
				t2k = k
		period = t1k + '-' + t2k
		return period

	def step(self):
		"""Method invoked by the Model scheduler in each step. Step common to all occupants."""
		pass