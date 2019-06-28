from soba.visualization.drawModelBack import BackEndVisualization
from mesa.visualization.ModularVisualization import ModularServer
import os
import soba
import tornado

"""
In the file visual.py is implemented the execution with visual representation:
	Methods: 
		run: Execute the simulation with visual representation.

"""

def run(model, parameters, visual, back = False):
	"""
	Execute the simulation with visual representation.
		Args:
			parameters: Parameters associated with the simulation model and others such as grid size.
			model: Model that is simulated.
			visual: JS files with the visualization elements that are included in the JavaScript browser visualization template.
			back: Python file working as backend visualization.
	"""

	backEndVisualization = BackEndVisualization(int(parameters['width']), int(parameters['height']), 500, 500, visual)

	path = os.path.abspath(soba.__file__)
	path = path.rsplit('/', 1)[0]

	local_handler = (r'/local/(.*)', tornado.web.StaticFileHandler,
                     {"path": path})
	external_handler = (r'/external/(.*)', tornado.web.StaticFileHandler,
                     {"path": ""})

	ModularServer.handlers = ModularServer.handlers[:-1]
	ModularServer.handlers = ModularServer.handlers + [local_handler] + [external_handler]
	if back != False:
		server = ModularServer(model, [backEndVisualization, back], name="Simulation", model_params=parameters)
	else:
		server = ModularServer(model, [backEndVisualization], name="Simulation", model_params=parameters)

	server.port = 7777
	server.launch()