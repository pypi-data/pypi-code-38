"""
In the file continuousItems.py four classes are defined to implement the elements of
the physical space in a continuous model:

	-GeneralItem: Class that implements generic elements positioned on the map with the effect of being impenetrable.
	-Door: Class that implements bulding plane doors.
	-Wall: Class that implements building walls.
	-Poi: Class that implements points of interest where Occupancy objects perform certain actions.
"""

class GeneralItem():
	"""
	Class that implements generic elements positioned on the map with the effect of being impenetrable.
		Attributes:
			pos: Position where the object is located.
			color: Color with which the object will be represented in the visualization.
	"""
	def __init__(self, model, pos, color = None):
		"""
		Create a new Door object.
			Args: 
				model: Associated Model object
				pos: Position where the object is located.
				color: Color with which the object will be represented in the visualization.
			Return: GeneralItem object
		"""
		self.pos = pos
		model.grid.place_agent(self, pos)
		self.color = 'grey' if color == None else color

class Door():
	"""
	Class that implements bulding plane doors.
		Attributes:
			state: Door status, open (True) or closed (False).
			pos1: First position to access to the door.
			pos2: Second position to access to the door.
			rot: Door orientation in the grid ('x' or 'y').

		Methods:
			open: Change the status of the door to open.
			close: Change the status of the door to close.

	"""
	def __init__(self, model, pos1, pos2, rot, state = True):
		"""
		Create a new Door object.
			Args: 
				model: Associated Model object
				pos1: Position where the object is located.
				pos2: Position where the object is located.
				rot: Orientation of the door in the grid ('x' or 'y').
				state: Door status, open (True) or closed (False).
			Return: Door object
		"""
		self.state = state
		self.pos1 = pos1
		self.pos2 = pos2
		self.rot = rot

	def open(self):
		""" Change the status of the door to open (True) """
		self.state = True

	def close(self):
		"""Change the status of the door to close (False)"""
		self.state = False

class Wall():
	"""
	Class that implements building walls.
		Attributes:
			block1, block2, block3: lists of positions that contain positions between which an 
				occupant can move obeying with the impenetrability of the wall.
			color: Color with which the object will be represented in the visualization.
	"""
	def __init__(self, block1, block2, block3, color = None):
		"""
		Create a new Wall object.
			Args: 
				block1, block2, block3: lists of positions that contain positions between which an 
					occupant can move obeying with the impenetrability of the wall.
				color: Color with which the object will be represented in the visualization.
			Return: Wall object
		"""
		self.block1 = block1
		self.block2 = block2
		self.block3 = block3
		self.color = 'brown' if color == None else color

class Poi():
	"""
	Class that implements relevant elements in the simulations: points of interest where Occupancy objects perform certain actions by associating these points with certain states.
		Attributes:
			pos: Position where the object is located.
			ide: Unique identifier associated with the point of interest.
			share: Define if the poi can be shared by more than one occupant.
			color: Color with which the object will be represented in the visualization.
	"""
	def __init__(self, model, pos, ide, share = True, color = None):
		"""
		Create a new Door object.
			Args: 
				model: Associated Model object
				pos: Position where the object is located.
				ide: Unique identifier associated with the point of interest.
				share: Define if the poi can be shared by more than one occupant.
				color: Color with which the object will be represented in the visualization.
			Return: Door object
		"""
		self.pos = pos
		self.id = ide
		model.grid.place_agent(self, pos)
		self.used = False
		self.share = share
		self.color = 'green' if color == None else color