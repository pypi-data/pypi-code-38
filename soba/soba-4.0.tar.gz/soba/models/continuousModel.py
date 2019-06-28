from collections import defaultdict
import random
import os
import os.path
import math
from soba.models.timeControl import Time
from soba.models.generalModel import GeneralModel
from soba.agents.continuousOccupant import ContinuousOccupant
from soba.agents.roomsOccupant import RoomsOccupant
import soba.agents.resources.aStar as aStar
from soba.space.continuousElements import GeneralItem
from soba.space.continuousElements import Door
from soba.space.continuousElements import Wall
from soba.space.continuousElements import Poi
import datetime as dt
import random
from mesa.space import Grid
import soba.visualization.ramen.performanceGenerator as ramen
from mesa import Model
from mesa.time import SimultaneousActivation
from soba.agents.occupant import Occupant
import soba.launchers.listener as api
import threading
from soba.agents.avatar import Avatar

class ContinuousModel(GeneralModel):
	"""

	Base Class to create simulation models on a simplified space based on rooms.
		Attributes:
			Those inherited from the Occupant class.
			rooms: List of Room objects.
			walls: List of Wall objects.
			pois: List of Pois objects.
			generalItems: List of GeneralItem objects.
			doors: List of Door objects.
		Methods:
			createOccupants: Create occupants of the ContinuousOccupant type.
			getScaledCoordinate: Gets the value of a coordinate or a cell size scaled.
			setMap: Define the map plane distribution.
			getAsciMap: Get the plane of the grid in an ASCII format, such as a matrix, to apply the fov algorithm.
			thereIsClosedDoor: Check if one door is closed or open.
			getDoorInPos: Get a Door object in a position given.
			getOccupantsPos: Get a Occupant objects in a position given.
			thereIsOccupant: Check if there is any Occupant object in a position given.
			getOccupantId: Get the occupant with the unique_id given.
			getPOIsId: Get the pois object with the id given.
			getPOIsPos: Get the position of a poi object.
			checkFreePOI: Check if one Point of interest is free (there is no occupant on this).
			xyInGrid: Check if one position is inside the grid.
			nearPos: Check if two positions are consecutive.

	"""
	global ramenAux
	global ramenRT
	ramenAux = False
	ramenRT = False
	def activeRamen(rt):
		global ramenAux
		global ramenRT
		ramenAux = True
		ramenRT = rt
		ContinuousOccupant.activeRamen()

	global server
	server = False
	def activeServer(portAux = 10000):
		global server
		global port
		server = True
		port = portAux

	def __init__(self, width, height, jsonMap, jsonsOccupants, seed = dt.datetime.now(), scale = 0.5, timeByStep = 60):
		super().__init__(width, height, seed, timeByStep)
		"""
		Create a new ContinuousModel object.
			Args:
				height: Height in number of grid cells.
				width: Width in number of grid cells.
				jsonMap: Json of description of the map plane.
				jsonsOccupants: Json of description of the occupancy.
				seed: Seed employ in random generations.
				scale: Define the scale of the cells in relation with the measures given in the jsonMap.
				timeByStep: Time in seconds associated with each step.
				asciMap: Plane of the grid in an ASCII format to apply the fov algorithm.
			Return: ContinuousModel object.
		"""
		self.walls = []
		self.lineWalls = []
		self.pois = []
		self.doors = []
		self.generalItems =  []
		self.exits = []
		if server:
			api.setModel(self)
			thread = threading.Thread(target=api.runServer, args=(port,))
			thread.start()
		self.occupantsInfo = {}
		self.ramenAux = ramenAux

		#Create the map
		self.setMap(jsonMap, scale)
		aStar.getObtacles(self)

	def createOccupants(self, jsonsOccupants):
		"""
		Create occupants of the ContinuousOccupant type.
				Args:
					jsonOccupants: Json of description of the occupants.
		"""
		for json in jsonsOccupants:
			for n in range(0, json['N']):
				a = ContinuousOccupant(n, self, json)
				self.occupants.append(a)
		self.updateOccupancyInfo()

	def createAvatar(self, idAvatar, pos, color = 'red', initial_state = 'walking'):
		"""
		Create one avatar
		"""
		unique_id = 100000 + int(idAvatar)
		a = Avatar(unique_id, self, pos, color, initial_state)
		self.occupants.append(a)
		return a

	def getScaledCoordinate(self, coordenate, scale):
		"""
		Gets the value of a coordinate or a cell size scaled to the size of the grid in relation to a given scale.
			Args:
				coordenate: Coordenate value to be scale
				scale: Value of the scale to be applied.
			Return: value of the coordinate.
		"""
		n = coordenate/scale
		up = True if(float(str(n-int(n))[1:]) > 0.1) else False
		n = int(n)
		if up == True:
			return (n+1)
		return n

	def setMap(self, jsonMap, scale):
		"""
		Define the map plane distribution.
			Args:
				jsonMap: Json of description of the map plane.
				scale: Value of the scale.
		"""
		walls = jsonMap["walls"]
		corners = jsonMap["corners"]
		items = jsonMap["items"]

		for k, v in walls.items():
			pos1 = corners[v["corner1"]]
			pos2 = corners[v["corner2"]]
			x1 = self.getScaledCoordinate(pos1["x"], scale)
			y1 = self.getScaledCoordinate(pos1["y"], scale)
			x2 = self.getScaledCoordinate(pos2["x"], scale)
			y2 = self.getScaledCoordinate(pos2["y"], scale)
			if x1 == x2:
				if y2 > y1:
					for yAux in range(y1+1, y2+1):
						block1 = [(x1, yAux), (x2+1, yAux)]
						block2 = [(x1, yAux), (x1+1, yAux-1), (x1+1, yAux+1)]
						block3 = [(x1+1, yAux), (x1, yAux-1), (x1, yAux+1)]
						w = Wall(block1, block2, block3)
						self.walls.append(w)
				else:
					for yAux in range(y2+1, y1+1):
						block1 = [(x1, yAux), (x2+1, yAux)]
						block2 = [(x1, yAux), (x1+1, yAux-1), (x1+1, yAux+1)]
						block3 = [(x1+1, yAux), (x1, yAux-1), (x1, yAux+1)]
						w = Wall(block1, block2, block3)
						self.walls.append(w)
			else:
				if x2 > x1:
					for xAux in range(x1+1, x2+1):
						block1 = [(xAux, y1), (xAux, y1+1)]
						block2 = [(xAux, y1), (xAux-1, y1+1), (xAux+1, y1+1)]
						block3 = [(xAux, y1+1), (xAux-1, y1), (xAux+1, y1)]
						w = Wall(block1, block2, block3)
						self.walls.append(w)
				else:
					for xAux in range(x2+1, x1+1):
						block1 = [(xAux, y1), (xAux, y1+1)]
						block2 = [(xAux, y1), (xAux-1, y1+1), (xAux+1, y1+1)]
						block3 = [(xAux, y1+1), (xAux-1, y1), (xAux+1, y1)]
						w = Wall(block1, block2, block3)
						self.walls.append(w)

		for k, v in items.items():
			x = self.getScaledCoordinate(v['pos']['x'], scale)
			y = self.getScaledCoordinate(v['pos']['y'], scale)
			centerX = (0.375 > float(str(v['pos']['x']-int(v['pos']['x']))[1:]) > 0.125) or (0.855 > float(str(v['pos']['x']-int(v['pos']['x']))[1:]) > 0.675)
			centerY = (0.375 > float(str(v['pos']['y']-int(v['pos']['y']))[1:]) > 0.125) or (0.855 > float(str(v['pos']['y']-int(v['pos']['y']))[1:]) > 0.675)
			dx = math.floor(self.getScaledCoordinate((v["dx"]), scale))
			dy = math.floor(self.getScaledCoordinate((v["dy"]), scale))
			dxAux2 = dxAux1 = int(dx/2)
			dyAux2 = dyAux1 = int(dy/2)
			if centerY and centerX:
				pass
			elif not centerY and centerX:
				dyAux1 = dyAux1-1
			elif centerY and not centerX:
				dxAux1 = dxAux1-1
			else:
				dxAux1 = dxAux1-1
				dyAux1 = dyAux1-1

			if v['itemType'] == 'door':
				if dx > 1 and dy > 1:
					for xAux in range(x - dxAux1, x + dxAux2+1):
						for yAux in range(y - dyAux1, y + dyAux2+1):
							i = Door(self, (xAux, yAux), (xAux+1, yAux+1), v["rot"])
							self.doors.append(i)
				elif dx > 1:
					for xAux in range(x - dxAux1, x + dxAux2+1):
						yAux = y
						i = Door(self, (xAux, yAux), (xAux, yAux+1), v["rot"])
						self.doors.append(i)
				elif dy > 1:
					for yAux in range(y - dyAux1, y + dyAux2+1):
						xAux = x
						i = Door(self, (xAux, yAux), (xAux+1, yAux), v["rot"])
						self.doors.append(i)
				elif dx == 1 and dy == 1:
					xAux = x
					yAux = y
					rot = v["rot"]
					if rot == 'y':
						i = Door(self, (xAux, yAux), (xAux+1, yAux), v["rot"])
					else:
						i = Door(self, (xAux, yAux), (xAux, yAux+1), v["rot"])
					self.doors.append(i)

			elif v['itemType'] == 'poi':
				i = False
				if dx > 1 and dy > 1:
					for xAux in range(x - dxAux1, x + dxAux2+1):
						for yAux in range(y - dyAux1, y + dyAux2+1):
							if 'share' in v:
								i = Poi(self, (xAux, yAux), v['id'], v['share'])
							else:
								i = Poi(self, (xAux, yAux), v['id'], color = v.get('Color'))
							self.pois.append(i)
							if v['itemName'] == 'exit':
								self.exits.append(i.pos)
				elif dx > 1:
					for xAux in range(x - dxAux1, x + dxAux2+1):
						yAux = y
						if 'share' in v:
							i = Poi(self, (xAux, yAux), v['id'], v['share'])
						else:
							i = Poi(self, (xAux, yAux), v['id'], color = v.get('Color'))
						self.pois.append(i)
						if v['itemName'] == 'exit':
							self.exits.append(i.pos)
				elif dy > 1:
					for yAux in range(y - dyAux1, y + dyAux2+1):
						xAux = x
						if 'share' in v:
							i = Poi(self, (xAux, yAux), v['id'], v['share'])
						else:
							i = Poi(self, (xAux, yAux), v['id'], color = v.get('Color'))
						self.pois.append(i)
						if v['itemName'] == 'exit':
							self.exits.append(i.pos)
				elif dx == 1 and dy == 1:
					xAux = x
					yAux = y
					if 'share' in v:
						i = Poi(self, (xAux, yAux), v['id'], v['share'])
					else:
						i = Poi(self, (xAux, yAux), v['id'], color = v.get('Color'))
					self.pois.append(i)
					if v['itemName'] == 'exit':
						self.exits.append(i.pos)
			else:
				if dx > 1 and dy > 1:
					for xAux in range(x - dxAux1, x + dxAux2+1):
						for yAux in range(y - dyAux1, y + dyAux2+1):
							i = GeneralItem(self, (xAux, yAux), color = v.get('Color'))
							self.generalItems.append(i)
				elif dy > 1:
					for yAux in range(y - dyAux1, y + dyAux2+1):
						xAux = x
						i = GeneralItem(self, (xAux, yAux), color = v.get('Color'))
						self.generalItems.append(i)
				elif dx > 1:
					for xAux in range(x - dxAux1, x + dxAux2+1):
						yAux = y
						i = GeneralItem(self, (xAux, yAux), color = v.get('Color'))
						self.generalItems.append(i)
				if dx == 1 and dy == 1:
					i = GeneralItem(self, (x, y), color = v.get('Color'))
					self.generalItems.append(i)

		self.getAsciMap()

	def getAsciMap(self):
		"""Get the plane of the grid in an ASCII format, such as a matrix, to apply the fov algorithm."""
		asciMapAux = []
		asciMap2 = []
		for i in range(self.height):
			asciMapAux.append([0] * self.width)
		for i in range(self.height):
			for j in range(self.width):
				asciMapAux[i][j] = '.'
		for wall in self.walls:
			x, y = wall.block1[0]
			asciMapAux[y][x] = '#'
		for door in self.doors:
			x, y = door.pos1
			x2, y2 = door.pos2
			asciMapAux[y][x] = '.'
			asciMapAux[y2][x2] = '.'
		string = ''
		for line in asciMapAux:
			for element in line:
				string = string + element
			asciMap2.append(string)
			string = ''
		self.asciMap = asciMap2

	def thereIsClosedDoor(self, pos):
		"""
		Check if one door is closed or open.
			Args:
				pos: Position of the door as (x, y).
			Return: State of the door as boolean.
		"""
		possibleDoor = self.grid.get_cell_list_contents([pos])
		for item in possibleDoor:
			if isinstance(item, Door):
				return Door.state

	def getDoorInPos(self, pos):
		"""
		Get a Door object in a position given.
			Args:
				pos: Position of the door as (x, y).
			Return: Door object or false.
		"""
		possibleDoor = self.grid.get_cell_list_contents([pos])
		for item in possibleDoor:
			if isinstance(item, Door):
				return item
		return False

	def getOccupantsPos(self, pos):
		"""
		Get a Occupant objects in a position given.
			Args:
				pos: Position as (x, y).
			Return: List of Cccupant objects.
		"""
		possibleOccupants = self.grid.get_cell_list_contents([pos])
		occupants = []
		for item in possibleOccupants:
			if isinstance(item, Occupant):
				occupants.append(item)
		return occupants

	def thereIsOccupant(self, pos):
		"""
		Check if there is any Occupant object in a position given.
			Args:
				pos: Position as (x, y).
			Return: True (yes), False (no).
		"""
		possible_occupant = self.grid.get_cell_list_contents([pos])
		if (len(possible_occupant) > 0):
			for occupant in possible_occupant:
				if isinstance(occupant,Occupant):
					return True
		return False

	def getOccupantId(self, Id):
		"""
		Get the occupant with the unique_id given.
			Args:
				Id: Unique_id given as number
			Return: Occupant object or False.
		"""
		for o in self.occupants:
			if o.unique_id == Id:
				return o
		return False

	def getPOIsId(self, poiId):
		"""
		Get the pois object with the id given.
			Args:
				poiId: poi id given as number
			Return: list of pois object or False.
		"""
		pois = []
		for i in self.pois:
			if i.id == poiId:
				pois.append(i)
		if pois:
			return pois
		return False

	def getPOIsPos(self, poiPos):
		"""
		Get the position of a poi object.
			Args:
				poiPos: position as (x, y)
			Return: poi object or False.
		"""
		pois = []
		conts = self.grid.get_cell_list_contents(poiPos)
		for c in conts:
			if isinstance(c, Poi):
				pois.append(c)
		if pois:
			return pois
		return False

	def checkFreePOI(self, p):
		"""
		Check if one Point of interest is free (there is no occupant on this).
			Args:
				p: Poi object.
			Return: True (yes), False (no).
		"""
		conts = self.grid.get_cell_list_contents(p.pos)
		for c in conts:
			if isinstance(c, Occupant):
				return False
		return True

	def xyInGrid(self, pos):
		"""
		Check if one position is inside the grid.
			Args:
				pos: Position as (x, y).
			Return: True (yes), False (no).
		"""
		x, y = pos
		if x >= 0 and not x >= self.width:
			if y >= 0 and not y >= self.height:
				return True
		return False

	def nearPos(self, pos1, pos2):
		"""
		Check if two positions are consecutive.
			Args:
				pos1: Position as (x, y).
				pos2: Position as (x, y).
			Return: True (yes), False (no).
		"""
		x, y = pos2
		posis = [(x, y), (x+1, y+1), (x-1, y-1), (x+1, y-1), (x-1, y+1), (x+1, y), (x-1, y), (x, y+1), (x, y-1)]
		if pos1 in posis:
			return True
		return False

	#API methods
	def list_occupants(self):
		unique_ids = []
		for k, v in self.occupantsInfo.items():
			unique_ids.append(v.get('unique_id'))
		data = {"occupants": unique_ids}
		return data

	def movements_occupants(self):
		data = {}
		for k, v in self.occupantsInfo.items():
			if v.get('movement'):
				data[k] = v.get('movement')
		return data

	def positions_occupants(self):
		data = {}
		for k, v in self.occupantsInfo.items():
			x, y = v.get('position')
			data[k] = {"x": x, "y": y}
		return data

	def states_occupants(self):
		data = {}
		for k, v in self.occupantsInfo.items():
			data[k] = v.get('state')
		return data

	def movement_occupant(self, occupant_id):
		movement = self.occupantsInfo.get(str(occupant_id)).get('movement')
		data = {"movement": movement}
		return data

	def position_occupant(self, occupant_id):
		x, y = self.occupantsInfo.get(str(occupant_id)).get('position')
		data = {"position" : {"x": x, "y": y}}
		return data

	def state_occupant(self, occupant_id):
		state = self.occupantsInfo.get(str(occupant_id)).get('state')
		data = {"state": state}
		return data

	def fov_occupant(self, occupant_id):
		fov = self.occupantsInfo.get(str(occupant_id)).get('fov')
		fov_json = []
		if fov == None:
			return {"fov": fov_json}
		for pos in fov:
			x, y = pos
			fov_json.append({"x": x, "y": y})
		data = {"fov": fov_json}
		return data

	def info_occupant(self, occupant_id):
		data_fov = self.fov_occupant(occupant_id)
		data_movement = self.movement_occupant(occupant_id)
		data_position = self.position_occupant(occupant_id)
		data_state = self.state_occupant(occupant_id)
		data_occupant = {"unique_id": occupant_id, "fov": data_fov["fov"], "movement": data_movement["movement"], "position": data_position["position"], "state": data_state["state"]}
		data = {"occupant": data_occupant}
		return data

	def create_avatar(self, idAvatar, pos, color = 'red', initial_state = 'walking'):
		a = self.createAvatar(idAvatar, pos, color, initial_state)
		self.occupants.append(a)
		return a

	def move_avatar(self, idAvatar, pos):
		a = self.getOccupantId(int(idAvatar))
		if not a:
			return a
		a.makeMovementAvatar(pos)
		return a

	#Report method aux
	def updateOccupancyInfo(self):
		for occupant in self.occupants:
			ocDict = {'unique_id': occupant.unique_id,
					  'movement': occupant.movement,
					  'state': occupant.state,
					  'position': occupant.pos,
					  'fov': occupant.fov}
			self.occupantsInfo[str(occupant.unique_id)] = ocDict

	def step(self):
		if self.finishSimulation and ramenAux and not ramenRT:
			ramen.generateJSON()
		for a in self.occupants:
			a.alreadyMovement = False
		super().step()
		self.updateOccupancyInfo()
		if ramenRT:
			ramen.generateRTJSON(self.NStep-1)