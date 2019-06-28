import random

"""
In the file behaviourMarkov.py the Markovian behavior based on states is implemented.
"""
class Markov(object):
	"""
	Base class to models the activity of the agents by means of Markovian behavior.
		
		Attributes:
			agent: Agent that is controlled by this models.

		Methods:
			runStep: Execute a Markovian state change by evaluating the initial state and the probabilities associated with each possible state.
			getNextState: Evaluate a random change based on the probabilities corresponding to each state.

	"""

	def __init__(self, agent_aux):
		"""
		Create a new Markov object.
			Args: 
				agent_aux: Agent that is controlled by this Markov object.
			Return: Markov object.
		"""
		self.agent = agent_aux

	def runStep(self, markov_matrix):
		""" 
		Execute a Markovian state change by evaluating the initial state and the probabilities associated with each possible state.
			Args:
				markov_matrix: Markov matrix corresponding to a certain moment. 
		"""
		currentState = self.agent.state
		numberCurrentState = False
		self.n = 0
		for state in self.agent.machine.states:
			if state == currentState:
				break
			self.n = self.n + 1 
		numberCurrentState = self.n
		numberNextState = self.getNextState(markov_matrix, numberCurrentState)
		if (numberNextState != 0) and (numberNextState == False):
			return
		listKeyStates = list(self.agent.machine.states.keys())
		nextState = self.agent.machine.states[listKeyStates[numberNextState]]
		for n in self.agent.triggers.keys():
			if n == nextState.name:
				trigger = self.agent.triggers[n]
				cast = 'self.agent.'+ trigger
				eval(cast)

	def getNextState(self, markov_matrix, NumberCurrentState):
		""" 
		Evaluate a random change based on the probabilities corresponding to each state.
			Args:
				markov_matrix: Markov matrix corresponding to a certain moment.
				NumberCurrentState: Unique id as number of the current state.
		"""
		vector = markov_matrix[NumberCurrentState]
		randomNumber = random.randrange(0, 101)
		self.n = -1
		value_aux = 0
		for pos in vector: 
			self.n = self.n + 1
			value_aux = value_aux + pos
			if value_aux > randomNumber:
				return self.n
		return False