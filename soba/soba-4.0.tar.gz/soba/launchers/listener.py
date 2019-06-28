from tornado import httpserver
from tornado.ioloop import IOLoop
import tornado.web
import json



"""
	In this file, the API is defined to obtain information about the simulation and control of avatars.
	Specifically, the API provide the next requests:

		/api/v1/movements_occupants
			Returns the movement of all occupants as a list of positions [x, y].

		/api/v1/positions_occupants
			Returns the position of all occupants as a list of positions [x, y].

		/api/v1/state_occupants
			Returns the state of all occupants as a String.

		/api/v1/movement_occupant/id
			Returns the movement of one occupant given as orientation and speed.

		/api/v1/position_occupant/id
			Returns the position of one occupant as position [x, y].

		/api/v1/getstatesoccupant/id
			Returns the state of one occupant as a String.

		/api/v1/fov_occupant/id
			Returns the FOV (field of view) of one occupant as a list of positiions [x, y].

		/api/v1/info_occupant/id
			Returns the state, movement, position and FOV of one occupant.

		/api/v1/create_avatar/id&x,y
			Creates an avatar with an id in an (x, y) position in the grid.

		/api/v1/move_avatar/id&x,y
			Moves an avatar to the position (x, y) in the grid.
			
		Where:
			id is a number with the unique_id of an occupant.
			x and y are the two numbers with the grid coordinates.

"""

# Simulation model
global model
model = None

# External handlers to expand the API. 
global externalHandlers
externalHandlers = []

def setModel(modelAux):
	global model
	if not model:
		model = modelAux

class presentation(tornado.web.RequestHandler):
	def get(self):
		global model
		response = ' Welcome to SOBA API! \n Simulation in step: {}'.format(model.NStep)
		self.write(response)

class list_occupants(tornado.web.RequestHandler):
	def get(self):
		global model
		data = model.list_occupants()
		response = json.dumps(data)
		self.write(response)

class movements_occupants(tornado.web.RequestHandler):
	def get(self):
		global model
		data = model.movements_occupants()
		response = json.dumps(data)
		self.write(response)

class positions_occupants(tornado.web.RequestHandler):
	def get(self):
		global model
		data = model.positions_occupants()
		response = json.dumps(data)
		self.write(response)

class states_occupants(tornado.web.RequestHandler):
	def get(self):
		global model
		data = model.states_occupants()
		response = json.dumps(data)
		self.write(response)

class movement_occupant(tornado.web.RequestHandler):
	def get(self, occupant_id):
		global model
		data = model.movement_occupant(occupant_id)
		response = json.dumps(data)
		self.write(response)

class position_occupant(tornado.web.RequestHandler):
	def get(self, occupant_id):
		global model
		data = model.position_occupant(occupant_id)
		response = json.dumps(data)
		self.write(response)

	def post(self, avatar_id):
		global model
		data = tornado.escape.json_decode(self.request.body)
		x = data["x"]
		y = data["y"]
		pos = (int(x), int(y))
		a = model.move_avatar(avatar_id, pos)
		x, y = a.pos
		data = {'avatar': {'id': a.unique_id, 'position': {'x': x, 'y': y}}}
		response = json.dumps(data)
		self.write(response)

class state_occupant(tornado.web.RequestHandler):
	def get(self, occupant_id):
		global model
		data = model.state_occupant(occupant_id)
		response = json.dumps(data)
		self.write(response)

class fov_occupant(tornado.web.RequestHandler):
	def get(self, occupant_id):
		global model
		data = model.fov_occupant(occupant_id)
		response = json.dumps(data)
		self.write(response)

class info_occupant(tornado.web.RequestHandler):
	def get(self, occupant_id):
		global model
		data = model.info_occupant(occupant_id)
		response = json.dumps(data)
		self.write(response)

	def put(self, avatar_id):
		global model
		data = tornado.escape.json_decode(self.request.body)
		x = data["x"]
		y = data["y"]
		pos = (int(x), int(y))
		a = model.create_avatar(avatar_id, pos)
		x, y = a.pos
		data = {'avatar': {'id': a.unique_id, 'position': {'x': x, 'y': y}}}
		response = json.dumps(data)
		self.write(response)
		#self.write('Avatar with id: {}, created in pos: {} \n'.format(a.unique_id, a.pos))

#Defining application
class Application(tornado.web.Application):
    global externalHandlers
    def __init__(self):
        internalHandlers = [
            (r"/?", presentation),
            (r"/api/v1/occupants?", list_occupants),
            (r"/api/v1/occupants/movements?", movements_occupants),
            (r"/api/v1/occupants/positions?", positions_occupants),
            (r"/api/v1/occupants/states?", states_occupants),
            (r"/api/v1/occupants/([0-9]+)?", info_occupant),
            (r"/api/v1/occupants/([0-9]+)/movement?", movement_occupant),
            (r"/api/v1/occupants/([0-9]+)/position?", position_occupant),
            (r"/api/v1/occupants/([0-9]+)/state?", state_occupant),
            (r"/api/v1/occupants/([0-9]+)/fov?", fov_occupant)
        ]
        for t1 in internalHandlers:
            for t2 in externalHandlers:
                if t1[0]==t2[0]:
                    internalHandlers.remove((t1[0], t1[1]))
        handlers = internalHandlers + externalHandlers
        tornado.web.Application.__init__(self, handlers)

#Run server method
def runServer(port=10000):
	global app
	print('server launched in port: {}.\n'.format(port))
	app = Application()
	app.listen(port, address='127.0.1.1')
	tornado.autoreload.start()
	IOLoop.current().start()