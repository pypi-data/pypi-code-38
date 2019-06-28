import sys
import soba.launchers.visual as visual
from mesa.batchrunner import BatchRunner as batchRunner
from soba.models.continuousModel import ContinuousModel
"""
In the file run.py is implemented the method
	Methods: 
		-run: This method is implemented to start the execution of the simulation.

"""

def process(aux):
	if aux == True:
		print('SOBA is running')
	else:
		print('\n Wrong params :(\n')
		print('   Options:')
		print('       -> First argument:')
		print('\n\t-v,\t\tVisual option on browser\n\t-b,\t\tBackground option\n')
		print('       -> Second argument:')
		print('\n\t-rb,\t\tRamen visualization after simulation\n\t-rt,\t\tRamen visualization real time\n\t-s,\t\tServer execution\n')
		print(' ')

def run(model, *args, visualJS = '', back = False, iterations = 1):
	"""
	Execution of the simulation according to the parameters given in the console.
		Args:
			model: Model that is simulated.
			args: Parameters associated with the simulation model and others such as grid size.
			visualJS: JS files with the visualization elements that are included in the JavaScript browser visualization template.
			back: Python file working as backend visualization.
			iterations: Number of simulations that will be executed in batch mode.
	"""
	if len(sys.argv) > 2:
		if sys.argv[2] == '-rb':
			process(True)
			ContinuousModel.activeRamen(rt = False)
		elif sys.argv[2] == '-rt':
			process(True)
			ContinuousModel.activeRamen(rt = True)
		elif sys.argv[2] == '-s':
			if len(sys.argv) > 3:
				ContinuousModel.activeServer(sys.argv[3])
			else:
				ContinuousModel.activeServer()
			process(True)
		else:
			pass
	if len(sys.argv) > 1:
		if sys.argv[1] == '-v':
			process(True)
			visual.run(model, visual = visualJS, back = back, parameters = args[0])
		elif sys.argv[1] == '-b':
			parameters = args[0]
			process(True)
			batch = batchRunner(model, fixed_parameters = parameters, variable_parameters = args[1], iterations = iterations, max_steps=10000000)
			batch.run_all()
		else:
			process(False)
	else:
		process(False)