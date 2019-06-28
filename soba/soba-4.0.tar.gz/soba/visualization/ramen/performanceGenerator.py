import json
import time
import subprocess
import math

steps = [[] for _ in range(100000)]

def post(file):
	nameFile = file
	subprocess.call('curl -d @'+nameFile+' -X POST http://localhost:8001/api', shell = True)
	print('POST petition made!')

def addAgentMovement(agent, step, direction, speed, rect, sentiment = 'happiness'):
	speed = (agent.speed/agent.model.clock.timeByStep)*0.1
	steps[step].append({'agent': agent.unique_id, 'direction': direction, 'speed': speed, 'sentiment': sentiment})

def stopAgent(agent, step):
	steps[step].append({ 'agent': agent.unique_id, 'stop': True})

def createAgent(agent, step, pos, rotation, sentiment = 'happiness'):
	x, y = pos
	steps[step].append({ 'agent': agent.unique_id, 'position': {'x': (x+1)*100*0.5, 'y': ((10-(y-1)*0.5+0.25)*100)}, 'sentiment': sentiment})

def removeAgent(agent, step):
	steps[step].append({ 'agent': agent.unique_id, 'outBuilding': True})

# Called methods
def reportCreation(agent, rotation):
    createAgent(agent, agent.model.NStep, agent.pos, rotation, sentiment = 'happiness')

def reportExit(agent):
    removeAgent(agent, agent.model.NStep)

def reportMovement(agent, direction, rect):
    addAgentMovement(agent, agent.model.NStep, direction, agent.speed, rect)

def reportStop(agent):
    stopAgent(agent, agent.model.NStep)

def generateJSON():
	data = {'type':2, 'steps': steps}
	print('JSON Generated!')
	with open('outRamen.json', 'w') as outfile:
		json.dump(data, outfile)
		outfile.close()

def generateRTJSON(step):
	data = steps[step]
	print('JSON RT Generated!')
	with open('outRTRamen.json', 'w') as outfile:
		json.dump(data, outfile)
		outfile.close()
	post('outRTRamen.json')