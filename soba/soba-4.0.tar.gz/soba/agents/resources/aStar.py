import random
import time
import sys

"""
In the file aStar.py the AStar algorithm is implemented.

	Methods:
		getPathRooms: Calculate the optimal path in the models with the space defined by rooms.
		getPathContinuous: Calculate the optimal path in the models with the space continuous.
		getConectedCellsRooms: Gets a list of connected cells in a space defined by rooms.
		getConectedCellsContinuous: Gets a list of connected cells in a continuous space.
		canMovePos: Evaluate if a position is reachable in a continuous space.

"""

def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    '''
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    '''
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '=' * filled_length + '>' + '-' * (bar_length - filled_length - 1)

    sys.stdout.write('\r%s [%s] %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.flush()

global maxIteration
maxIteration = 10000

generalItemsPos = []
doorsPoss = []

class Cell(object):
	def __init__(self, pos):
		self.x, self.y = pos
		self.x = self.x if not 0 > self.x else 0
		self.y = self.y if not 0 > self.y else 0
		self.parent = None

def getPathRooms(model, start, finish):
	"""
	Calculate the optimal path in the models with the space defined by rooms.
		Args:
			model: Model which invokes the algorithm.
			start: Initial position.
			finish: Final position.
		Return: List of positions (x, y). 
	"""
	finish = Cell(finish)
	start = Cell(start)
	not_visited = [start]
	visited = []
	finishCell = None
	notFinished = True
	while notFinished:
		for cell_not_visited in not_visited:
			if cell_not_visited.x == finish.x and cell_not_visited.y == finish.y:
				finishCell = cell_not_visited
				notFinished = False
			else:
				cells = getConectedCellsRooms(model, cell_not_visited) #create adject cells with conection
				for cell in cells:
					cell_already_visited = isCellVisited(cell, visited)
					if not cell_already_visited:
						cell.parent = cell_not_visited
						not_visited = not_visited + [cell]
						visited = visited + [cell]
				not_visited.remove(cell_not_visited)
			break
	cellWay = [finishCell]
	cell = finishCell
	while not (cellWay[len(cellWay)-1] is start):
		cell = cell.parent;
		cellWay = cellWay + [cell]
	cellWay.pop()
	way = []
	for cell in cellWay:
		pos = (cell.x, cell.y)
		way = way + [pos]
	way.reverse()
	return way

def getPathContinuous(model, start, finish, other = []):
	"""
	Calculate the optimal path in the models with the space continuous.
		Args:
			model: Model which invokes the algorithm.
			start: Initial position.
			finish: Final position.
			other: List of auxiliary positions given to be considered impenetrable, that is, they will not be used by the AStar.
		Return: List of positions (x, y).
	"""
	if start == finish:
		return [start]
	finish = Cell(finish)
	start = Cell(start)
	not_visited = [start]
	visited = []
	finishCell = None
	notFinished = True
	it = 0
	while notFinished:
		it = it + 1
		print_progress(it, maxIteration, prefix='Progress:', suffix='Complete', bar_length=30)
		if it > maxIteration or (finish.x, finish.y) in other:
			print("Demasida iteración, devolvemos: ", (start.x, start.y))
			print("Queriamos ir a: ", (finish.x, finish.y))
			return [(start.x, start.y)]
		for cell_not_visited in not_visited:
			if cell_not_visited.x == finish.x and cell_not_visited.y == finish.y:
				finishCell = cell_not_visited
				notFinished = False
			else:
				cells = getConectedCellsContinuous(model, cell_not_visited, other) #create adject cells with conection
				for cell in cells:
					cell_already_visited = isCellVisited(cell, visited)
					if not cell_already_visited:
						cell.parent = cell_not_visited
						if not cell in not_visited:
							not_visited = not_visited + [cell]
						visited = visited + [cell]
				not_visited.remove(cell_not_visited)
			break      
	cellWay = [finishCell]
	cell = finishCell
	while not (cellWay[len(cellWay)-1] is start):
		cell = cell.parent;
		cellWay = cellWay + [cell]
	cellWay.pop()
	way = []
	for cell in cellWay:
		pos = (cell.x, cell.y)
		way = way + [pos]
	way.reverse()
	if len(way) == 1 and not canMovePos(model, start, way[0]):
		way = [(start.x, start.y)]
	return way

def getConectedCellsRooms(model, cell):
	"""
	Gets a list of connected cells in a space defined by rooms.
		Args:
			model: Model which invokes the algorithm.
			cell: cell object corresponding to the room.
		Return: List of positions (x, y).
	"""
	room = model.getRoom((cell.x, cell.y))
	rooms = room.roomsConected
	cells = []
	for room in rooms:
		cell = Cell(room.pos)
		cells = cells + [cell]
	return cells

def getConectedCellsContinuous(model, cell, others):
	"""
	Gets a list of connected cells in a continuous space.
		Args:
			model: Model which invokes the algorithm.
			cell: cell object corresponding to the position.
			other: List of auxiliary positions given to be considered impenetrable, that is, they will not be used by the AStar.
		Return: List of positions (x, y).
	"""
	cellPos = (cell.x, cell.y)
	cells = []
	possiblePosition1 = [(cell.x, cell.y + 1), (cell.x + 1, cell.y), (cell.x - 1, cell.y), (cell.x, cell.y - 1)]
	possiblePosition2 = [(cell.x + 1, cell.y + 1), (cell.x + 1, cell.y - 1), (cell.x - 1, cell.y - 1), (cell.x - 1, cell.y + 1)]
	possiblePosition = possiblePosition1 + possiblePosition2
	for posAux in possiblePosition:
		pos1 = (0, 0)
		pos2 = (0, 0)
		aux = True
		if canMovePos(model, cellPos, posAux, others):
			cellAdded = Cell(posAux)
			cells.append(cellAdded)
	return cells

def getObtacles(model):
	for i in model.generalItems:
		generalItemsPos.append(i.pos)
	for d in model.doors:
		doorsPosAux = []
		doorsPosAux.append(d.pos1)
		doorsPosAux.append(d.pos2)
		doorsPoss.append(doorsPosAux)

def canMovePos(model, cellPos, posAux, others = []):
	"""
	Evaluate if a position is reachable in a continuous space.
		Args:
			model: Model which invokes the algorithm.
			cellPos: a first one position given as (x, y).
			posAux: a second one position given as (x, y).
			others: List of auxiliary positions given to be considered impenetrable,
			that is, they will not be used by the AStar.
		Return: List of positions (x, y).
	"""
	move = True
	for wall in model.walls:
		if (cellPos in wall.block1 and posAux in wall.block1) or (cellPos in wall.block2 and posAux in wall.block2) or (cellPos in wall.block3 and posAux in wall.block3):
			move = False
	if not move:
		for doorsPos in doorsPoss:
			if ((cellPos in doorsPos) and (posAux in doorsPos)):
				move = True
	if move:
		if not (cellPos in generalItemsPos or posAux in generalItemsPos):
			if not (posAux in others) or not (cellPos in others):
				return True
	return False

def isCellVisited(cell, visited):
	for cells in visited:
		if cells.x == cell.x and cells.y == cell.y:
			return True
	return False