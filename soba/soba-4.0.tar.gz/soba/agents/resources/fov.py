FOV_RADIUS = 30000

"""In the file aStar.py the filed of vision algorithm is implemented."""

class Map(object):
	"""
	Class to calculate the field of vision (fov).

	Attributes:
		data: Map to which to apply the algorithm.
	
	Methods:
		do_fov: Calculate the field of view from a position (x, y).
	
	More information:
		http://www.roguebasin.com/index.php?title=Python_shadowcasting_implementation
	"""
	mult = [[1,  0,  0, -1, -1,  0,  0,  1], [0,  1, -1,  0,  0, -1,  1,  0], [0,  1,  1,  0,  0, -1, -1,  0], [1,  0,  0,  1, -1,  0,  0, -1]]
	
	def __init__(self, map):
		self.data = map
		self.width, self.height = len(map[0]), len(map)
		self.light = []
		for i in range(self.height):
			self.light.append([0] * self.width)
		self.flag = 0

	def square(self, x, y):
		return self.data[y][x]

	def blocked(self, x, y):
		return (x < 0 or y < 0 or x >= self.width or y >= self.height or self.data[y][x] == "#")

	def lit(self, x, y):
		return self.light[y][x] == self.flag

	def set_lit(self, x, y):
		if 0 <= x < self.width and 0 <= y < self.height:
			self.light[y][x] = self.flag

	def _cast_light(self, cx, cy, row, start, end, radius, xx, xy, yx, yy, id):
		if start < end:
			return
		radius_squared = radius*radius
		for j in range(row, radius+1):
			dx, dy = -j-1, -j
			blocked = False
			while dx <= 0:
				dx += 1
				X, Y = cx + dx * xx + dy * xy, cy + dx * yx + dy * yy
				l_slope, r_slope = (dx-0.5)/(dy+0.5), (dx+0.5)/(dy-0.5)
				if start < r_slope:
					continue
				elif end > l_slope:
					break
				else:
					if dx*dx + dy*dy < radius_squared:
						self.set_lit(X, Y)
					if blocked:
						if self.blocked(X, Y):
							new_start = r_slope
							continue
						else:
							blocked = False
							start = new_start
					else:
						if self.blocked(X, Y) and j < radius:
							blocked = True
							self._cast_light(cx, cy, j+1, start, l_slope,
											 radius, xx, xy, yx, yy, id+1)
							new_start = r_slope
			if blocked:
				break

	def do_fov(self, x, y):
		"""
		Calculate the field of view from a position (x, y).
			Args: 
				x, y: Observer's position

			Return: Array of sight positions.
		"""
		self.flag += 1
		for oct in range(8):
			self._cast_light(x, y, 1, 1.0, 0.0, 100,
							 self.mult[0][oct], self.mult[1][oct],
							 self.mult[2][oct], self.mult[3][oct], 0)
		return (self.light, self.flag)

def makeFOV(dungeon, pos):
	"""
		Create the invocation object of the fov algorithm and invoke it.
			Args:
				dungeon: Array 
				pos: Observer's position

			Return: Array of sight positions.
	"""
	map = Map(dungeon)
	x, y = pos
	return map.do_fov(x, y)