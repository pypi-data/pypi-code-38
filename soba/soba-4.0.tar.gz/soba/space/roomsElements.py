"""
In the file continuousItems.py three classes are defined to implement the elements 
	of the physical space in a simplified model based on a room distribution:

	-Room: Class that implements the rooms through which the Agent/Ocupant objects are located, 
	move and where activities are carried out.
	-Door: Class that implements bulding plane doors.
	-Wall: Class that implements building walls.
"""

class Room():
	"""
	Class that implements the rooms through which the Agent/Ocupant objects are located, move and where activities are carried out.
		Attributes:
			name: Unique name of the room.
			roomsConected: List of accessible rooms from this room.
			dx: Size in the ordinate x (meters).
			dy: Size in the ordinate y (meters).
			pos: Position of the room (x, y).
			agentsInRoom: List of agent objects in the room
			walls: List of Wall objects of the room.
			doors: List of Doors objects of the room.
	"""
	def __init__(self, name, conectedTo, dx, dy, pos = (0,0)):
		"""
		Create a new Room object.
			Args: 
				name: Unique name of the room.
				conectedTo: List of names of connected rooms from this room.
				dx: Size in the ordinate x (meters).
				dy: Size in the ordinate y (meters).
				pos: Position of the room (x, y).
			Return: Room object
		"""        
		self.name = name
		self.conectedTo = conectedTo
		self.dx = dx
		self.dy = dy
		self.pos = pos
		self.roomsConected = []
		self.agentsInRoom = []
		self.walls = []
		self.entrance = None
		self.doors = []

class Door():
	"""
	Class that implements bulding plane doors.
		Attributes:
			state: Door status, open (True) or closed (False).
			room1: First room to croos the door.
			room2: Second room to croos the door.
		Methods:
			open: Change the status of the door to open.
			close: Change the status of the door to close.
	"""
	def __init__(self, room1 = False, room2= False, state=False):
		"""
		Create a new Door object.
			Args: 
				room1: First room to croos the door.
				room2: Second room to croos the door.
				state: Door status, open (True) or closed (False).
			Return: Door object
		"""
		self.state = state
		self.room1 = room1
		self.room2 = room2

	def open(self):
		""" Change the status of the door to open (True) """
		self.state = True

	def close(self):
		""" Change the status of the door to closed (False) """
		self.state = False

class Wall():
	"""
	Class that implements building walls.
		Attributes:
			room1: First room to croos the door.
			room2: Second room to croos the door.
	"""
	def __init__(self, room1 = False, room2 = False):
		"""
		Create a new Wall object.
			Args:
				room1: Room on side one of the wall.
				room2: Room on side two of the wall.
			Return: Wall object
		"""
		self.room1 = room1
		self.room2 = room2