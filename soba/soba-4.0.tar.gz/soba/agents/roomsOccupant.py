import random
import soba.agents.resources.aStar as aStar
from soba.agents.occupant import Occupant

class RoomsOccupant(Occupant):
	"""
	This class enables to create occupants that are modelled with a simplified models based on a discrete space associated with rooms.
	The occupants are agents with their activity defined by markov states.

	Attributes:
		Those inherited from the Occupant class.
	
	Methods:
		getPosState: Auxiliary method to distribute the occupants between the rooms shared by more than one occupant object.
		getWay: Invocation of the AStar resource to calculate the optimal path.
		occupantMovePos: Calculation of the control attributes that regulate the cost (steps) of the movement between rooms according to their size.
		getPlaceToGo: Obtaining the position associated with the current state.
		step: Method invoked by the Model scheduler in each step.
	"""

	def __init__(self, unique_id, model, json, speed = 0.7):
		super().__init__(unique_id, model, json, speed)
		"""
		Create a new RoomsOccupant object.
			Args: 
				unique_id: Unique identifier corresponding to the Occupant.
				models: Associated Model object, by default RoomsModel.
				json: Json of definition of parameters of behavior
				speed: Movement speed in m/s
			Return: RoomsOccupant object
		"""

		self.model.schedule.add(self)
		#State machine
		for k, v in json['states'].items():
			pos = self.getPosState(k, v)
			self.positionByState[k] = pos

		possible_rooms = []
		roomsNames = self.positionByState[self.state]
		for room in self.model.rooms:
			if isinstance(roomsNames, dict):
				for roomName, v in roomsNames.items():
					if room.name.split(r".")[0] == roomName:
						possible_rooms.append(room)
			else:
				if room.name.split(r".")[0] == self.positionByState[self.state]:
						possible_rooms.append(room)
		if len(possible_rooms) > 1:
			roomaux = random.choice(possible_rooms)
		else:
			roomaux = possible_rooms[0]

		self.model.grid.place_agent(self, roomaux.pos)
		self.model.pushAgentRoom(self, roomaux.pos)

		#control
		self.onMyWay1 = False
		self.onMyWay2 = False
		self.costMovementToNewRoom = 0
		self.costMovementInNewRoom = 0
		self.room1 = False
		self.room2 = False

	def getPosState(self, name, posAux):
		'''
		Auxiliary method to distribute the occupants between the rooms shared by more than one occupant object.
			Args:
				name: State name.
				posAux: Name of the room associated with this state, string, 
				or dictionary of room names with number of occupants. {'RoomName1': numberofOccupantsAssigned1,
				'RoomName2': numberofOccupantsAssigned2... }
			Return: Position associated with this occupant
		'''
		if isinstance(posAux, dict):
			for k, v in posAux.items():
				if v > 0:
					self.positionByStateAux[name][k]= v - 1
					return k
		return posAux

	#Movement
	def getWay(self, pos = None, pos_to_go = None):
		'''
		Invocation of the AStar resource to calculate the optimal path.
			Args:
				pos: Initial position, by default the current position of the occupant.
				pos_to_go: Final position, by default the value of the 'pos_to_go' attribute of the occupant.
			Return: List of positions (x, y).
		'''
		posSend = pos
		pos_to_goSend = pos_to_go
		if pos == None:
			posSend = self.pos
		if pos_to_go == None:
			pos_to_goSend = self.pos_to_go
		return aStar.getPathRooms(self.model, posSend, pos_to_goSend)

	def occupantMovePos(self, new_position):
		'''
		Calculation of the control attributes that regulate the cost (steps) of the movement between rooms according to their size.
				Args:
					new_position: Room object to which it moves.
		'''
		ux, uy = self.pos
		nx, ny = new_position
		for room in self.model.rooms:
			rx, ry = room.pos
			if room.pos == self.pos:
			#Cost as steps
				if (rx == nx):
					self.costMovemenToNewRoom = room.dy/2 * (1/self.speed) * (1/self.model.clock.timeByStep)# m * seg/m * step/seg
				if (ry == ny):
					self.costMovemenToNewRoom = room.dx/2 * (1/self.speed) * (1/self.model.clock.timeByStep)
			if room.pos == new_position:
				if (rx == ux):
					self.costMovementInNewRoom = room.dy/2 * (1/self.speed) * (1/self.model.clock.timeByStep)
				if (ry == uy):
					self.costMovementInNewRoom = room.dx/2 * (1/self.speed) * (1/self.model.clock.timeByStep)

	def getPlaceToGo(self):
		'''
		Obtaining the position associated with the current state. It is invoked when you enter a new state.
			Return: Position as coordinate (x, y).
		'''
		pos_to_go = self.pos
		roomsNames = self.positionByState[self.state]
		possible_rooms = []
		for room in self.model.rooms:
			if isinstance(roomsNames, dict):
				for roomName, v in roomsNames.items():
					if room.name.split(r".")[0] == roomName:
						possible_rooms.append(room.pos)
			else:
				if room.name.split(r".")[0] == self.positionByState[self.state]:
						possible_rooms.append(room.pos)
		if len(possible_rooms) > 1:
			pos_to_go = random.choice(possible_rooms)
		else:
			pos_to_go = possible_rooms[0]
		return pos_to_go

	def startActivity(self):
		super.startActivity()

	def step(self):
		"""
		Method invoked by the Model scheduler in each step. Evaluate if appropriate and, if so, perform: 
		A change of state, a movement or advance in the cost of a movement, or an advance in the performance of an activity.
		"""
		if self.markov == True or self.changeSchedule():
			self.markov_machine.runStep(self.markovActivity[self.getPeriod()])
		elif self.onMyWay1 == True:
			if self.costMovemenToNewRoom > 0:
				self.costMovemenToNewRoom = self.costMovemenToNewRoom - 1
			else:
				room1 = self.model.getRoom(self.pos)
				room2 = self.model.getRoom(self.movements[self.N])
				self.room1 = room1
				self.room2 = room2
				if room1.name.split(r".")[0] != room2.name.split(r".")[0]:
					self.model.openDoor(self, room1, room2)
				self.model.popAgentRoom(self, self.pos)
				self.model.grid.move_agent(self, self.movements[self.N])
				self.model.pushAgentRoom(self, self.pos)
				self.N = self.N + 1
				self.onMyWay1 = False
				self.onMyWay2 = True
		elif self.onMyWay2 == True:
			if self.costMovementInNewRoom > 0:
				self.costMovementInNewRoom = self.costMovementInNewRoom - 1
			else:
				room1 = self.room1
				room2 = self.room2
				if room1.name.split(r".")[0] != room2.name.split(r".")[0]:
					self.model.closeDoor(self, room1, room2)
				self.onMyWay2 = False
				self.step()
		elif self.pos != self.pos_to_go:
			self.occupantMovePos(self.movements[self.N])
			self.onMyWay1 = True
			self.step()
		else:
			self.N = 0
			if self.time_activity > 0:
				self.time_activity = self.time_activity - 1
			else:
				self.markov = True