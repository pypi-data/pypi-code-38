from soba.models.timeControl import Time
from soba.agents.continuousOccupant import ContinuousOccupant
from soba.agents.roomsOccupant import RoomsOccupant
import soba.agents.resources.aStar as aStar
from soba.space.roomsElements import Room
from soba.space.roomsElements import Door as DoorRooms
from soba.space.roomsElements import Wall as WallRooms
import datetime as dt
import random
from mesa.space import Grid
import soba.visualization.ramen.performanceGenerator as ramen
from mesa import Model
from mesa.time import SimultaneousActivation
from soba.models.generalModel import GeneralModel
from time import time

class RoomsModel(GeneralModel):
	"""
	Base Class to create simulation models on a simplified space based on rooms.

		Attributes:
			Those inherited from the Occupant class.
			rooms: List of Room objects.
			Those inherited from the Occupant class.
			rooms: List of Room objects.
			walls: List of Wall objects.
			pois: List of Pois objects.
			generalItems: List of GeneralItem objects.
			doors: List of Door objects.
		Methods:
			createOccupants: Create occupants of the RoomsOccupant type.
			createRooms: Create the rooms in the grid space.
			setMap: Define the map plane distribution.
			createDoors: Create the doors in the grid space.
			createWalls: Create the walls in the grid space.
			thereIsClosedDoor: Check if one door is closed or open.
			thereIsOtherOccupantInRoom: Evaluate if there is another occupant apart of the past as a parameter in a room.
			thereIsSomeOccupantInRoom: Evaluate if there is any occupant in a room.
			thereIsOccupantInRoom: Evaluate if there is one specific occupant in a room.
			getRoom: Get one Room Object by position.
			pushAgentRoom: Add one agent to a room.
			popAgentRoom: Remove one agent from a room.
			openDoor: Change the status of the door to open.
			closeDoor: Change the status of the door to close.

	"""
	def __init__(self, width, height, jsonRooms, jsonsOccupants, seed = int(time()), timeByStep = 60):
		super().__init__(width, height, seed, timeByStep)
		"""
		Create a new RoomsModel object.
			Args:
				height: Height in number of grid cells.
				width: Width in number of grid cells.
				jsonRooms: Json of description of the map plane.
				jsonsOccupants: Json of description of the occupancy.
				seed: Seed employ in random generations.
				timeByStep: Time in seconds associated with each step.
			Return: RoomsModel object
		"""
		self.rooms = []
		self.createRooms(jsonRooms)
		self.setMap()
		self.createDoors()
		self.createWalls()

		self.createOccupants(jsonsOccupants)
	
	def createOccupants(self, jsonsOccupants):
		"""
		Create occupants of the RoomsOccupant type.
				Args:
					jsonOccupants: Json of description of the occupants.
		"""
		for json in jsonsOccupants:
			for n in range(0, json['N']):
				a = RoomsOccupant(n, self, json)
				self.occupants.append(a)

	def createRooms(self, jsonRooms):
		"""
		Create the rooms in the grid space.
			Args:
				jsonRooms: Json of description of the map plane.
		"""
		rooms = jsonRooms
		self.rooms = []
		for k,v in rooms.items():
			newRoom  = 0
			name = k
			conectedTo = v.get('conectedTo')
			entrance = v.get('entrance')
			measures = v['measures']
			dx = measures['dx']
			dy = measures['dy']
			newRoom = Room(name, conectedTo, dx, dy)
			newRoom.entrance = entrance
			self.rooms.append(newRoom)
		for room1 in self.rooms:
			if room1.conectedTo is not None:
				for otherRooms in list(room1.conectedTo.values()):
					for room2 in self.rooms:
						if room2.name == otherRooms:
							room1.roomsConected.append(room2)
							room2.roomsConected.append(room1)
		for room in self.rooms:
			room.roomsConected = list(set(room.roomsConected))
		sameRoom = {}
		for room in self.rooms:
			if sameRoom.get(room.name.split(r".")[0]) is None:
				sameRoom[room.name.split(r".")[0]] = 1
			else:
				sameRoom[room.name.split(r".")[0]] = sameRoom[room.name.split(r".")[0]] + 1

	def setMap(self):
		"""Define the map plane distribution."""
		rooms_noPos = self.rooms
		rooms_using = []
		rooms_used = []
		for room in self.rooms:
			if room.entrance is not None:
				room.pos = (int(1), 1)
				rooms_using.append(room)
				rooms_used.append(room)
				rooms_noPos.remove(room)
				break
		while len(rooms_noPos) > 0:
			for roomC in rooms_using:
				xc, yc = roomC.pos
				rooms_conected = roomC.conectedTo
				rooms_using.remove(roomC)
				if rooms_conected is not None:
					orientations = list(rooms_conected.keys())
					for orientation in orientations:
						if orientation == 'R':
							for room in rooms_noPos:
								if room.name == rooms_conected['R']:
									room.pos = (int(xc + 1), yc)
									rooms_noPos.remove(room)
									rooms_used.append(room)
									rooms_using.append(room)
						elif orientation == 'U':
							for room in rooms_noPos:
								if room.name == rooms_conected['U']:
									room.pos = (xc, int(yc + 1))
									rooms_noPos.remove(room)
									rooms_used.append(room)
									rooms_using.append(room)
						elif orientation == 'D':
							for room in rooms_noPos:
								if room.name == rooms_conected['D']:
									room.pos = (xc, int(yc - 1))
									rooms_noPos.remove(room)
									rooms_used.append(room)
									rooms_using.append(room)
						elif orientation == 'L':
							for room in rooms_noPos:
								if room.name == rooms_conected['L']:
									room.pos = (int(xc -1), yc)
									rooms_noPos.remove(room)
									rooms_used.append(room)
									rooms_using.append(room)
				else:
					pass
		self.rooms = rooms_used

	def createDoors(self):
		"""Create the doors in the grid space."""
		self.doors = []
		for roomC in self.rooms:
			roomsConected = roomC.roomsConected
			for room in roomsConected:
				door_created = False
				same_corridor = False
				if room.name != roomC.name:
					for door in self.doors:
						if (door.room1.name == roomC.name and door.room2.name == room.name) or (door.room2.name == roomC.name and door.room1.name == room.name):
							door_created = True
						if room.name.split(r".")[0] == roomC.name.split(r".")[0]:
							same_corridor = True
					if door_created == False and same_corridor == False:
						d = DoorRooms(roomC, room)
						self.doors.append(d)
						room.doors.append(d)
						roomC.doors.append(d)

	def createWalls(self):
		"""Create the walls in the grid space."""
		for room in self.rooms:
			walls = []
			xr, yr = room.pos
			roomA = self.getRoom((xr, yr+1))
			if roomA != False:
				if roomA.name.split(r".")[0] == room.name.split(r".")[0]:
					pass
				else:
					wall = WallRooms(room, roomA)
					walls.append(wall)
			else:
				wall = WallRooms(room)
				walls.append(wall)
			roomB = self.getRoom((xr, yr-1))
			if roomB != False:
				if roomB.name.split(r".")[0] == room.name.split(r".")[0]:
					pass
				else:
					wall = WallRooms(room, roomB)
					walls.append(wall)
			else:
				wall = WallRooms(room)
				walls.append(wall)
			roomC = self.getRoom((xr+1, yr))
			if roomC != False:
				if roomC.name.split(r".")[0] == room.name.split(r".")[0]:
					pass
				else:
					wall = WallRooms(room, roomC)
					walls.append(wall)
			else:
				wall = WallRooms(room)
				walls.append(wall)
			roomD = self.getRoom((xr-1, yr))
			if roomD != False:
				if roomD.name.split(r".")[0] == room.name.split(r".")[0]:
					pass
				else:
					wall = WallRooms(room, roomD)
					walls.append(wall)
			else:
				wall = WallRooms(room)
				walls.append(wall)

			room.walls = walls

	def thereIsClosedDoor(self, beforePos, nextPos):
		"""
		Check if one door is closed or open.
			Args:
				beforePos, nextPos: The two common positions of the door as (x, y).
			Return: True (closed) or False (opened).
		"""
		oldRoom = False
		newRoom = False
		for room in rooms:
			if room.pos == beforePos:
				oldRoom = room
			if room.pos == nextPos:
				newRoom = room
		for door in self.doors:
			if (door.room1.name == oldRoom.name and door.room2.name == newRoom.name) or (door.room2.name == oldRoom.name and door.room1.name == newRoom.name):
				if door.state == False:
					return True
		return False

	def thereIsOtherOccupantInRoom(self, room, agent):
		"""
		Evaluate if there is another occupant apart of the past as a parameter in a room.
			Args:
				room: Room object to be checked.
				agent: Occupant object to be ignored.
			Return: True (yes), False (no)
		"""
		for roomAux in self.rooms:
			possible_occupant = []
			if roomAux.name.split(r".")[0] == room.name.split(r".")[0]:
				possible_occupant = self.grid.get_cell_list_contents(roomAux.pos)
			for occupant in possible_occupant:
				if isinstance(occupant, Occupant) and occupant != agent:
					return True
		return False

	def thereIsSomeOccupantInRoom(self, room):
		"""
		Evaluate if there is any occupant in a room.
			Args:
				room: Room object to be checked.
			Return: True (yes), False (no)
		"""
		for roomAux in self.rooms:
			possible_occupant = []
			if roomAux.name.split(r".")[0] == room.name.split(r".")[0]:
				possible_occupant = self.grid.get_cell_list_contents(roomAux.pos)
			for occupant in possible_occupant:
				if isinstance(occupant, Occupant):
					return True
		return False

	def thereIsOccupantInRoom(self, room, agent):
		"""
		Evaluate if there is one specific occupant in a room.
			Args:
				room: Room object to be checked.
			Return: True (yes), False (no)
		"""
		for roomAux in self.rooms:
			possible_occupant = []
			if roomAux.name.split(r".")[0] == room.name.split(r".")[0]:
				possible_occupant = self.grid.get_cell_list_contents(roomAux.pos)
			for occupant in possible_occupant:
				if isinstance(occupant, Occupant) and occupant == agent:
					return True
		return False

	def getRoom(self, pos):
		""" 
		Get one Room Object by position.
			Args:
				pos: Position of the grid as (x,y).
			Return: Room Object or False
		"""
		for room in self.rooms:
			if room.pos == pos:
				return room
		return False

	def pushAgentRoom(self, agent, pos):
		"""
		Add one agent to a room.
			Args:
				agent: Agent Object
				pos: Position of the grid as (x,y)
		"""
		room = self.getRoom(pos)
		room.agentsInRoom.append(agent)

	def popAgentRoom(self, agent, pos):
		"""
		Remove one agent from a room.
			Args:
				agent: Agent Object
				pos: Position of the grid as (x,y)
		"""
		room = self.getRoom(pos)
		room.agentsInRoom.remove(agent)

	def openDoor(self, agent, room1, room2):
		"""
		Change the status of the door to open (True). 
			Args:
				agent: Agent object which want to open the door.
				room1, room2: The two common rooms of the door as Room object.
				"""
		for door in self.doors:
			if ((door.room1 == room1 and door.room2 == room2) or (door.room1 == room2 and door.room2 == room1)):
				door.state = False

	def closeDoor(self, agent, room1, room2):
		"""
		Change the status of the door to close (False).
			Args:
				agent: Agent object which want to close the door.
				room1, room2: The two common rooms of the door as Room object.
		"""
		numb = random.randint(0, 10)
		for door in self.doors:
			if ((door.room1 == room1 and door.room2 == room2) or (door.room1 == room2 and door.room2 == room1)):
				if  7 >= numb:
					door.state = False
				else:
					door.state = True

	def step(self):
		super().step()