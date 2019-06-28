from .parsers import init_full
from .utils import Interfaces, factors
from .zmqs.area import Area


def create_director(name: str, interfaces: Interfaces, limit: int=6):
	def aggregate(result, areas, keys):
		for key in keys:
			result += areas[key]
		return result

	def fill(result, size):
		for x in range(1, size+1):
			result[x] = set()
		return result

	area = Area(name, interfaces)
	area.subscribe()
	area.context.update({'areas': set(), 'mapping': fill({}, 32), 'ready': set(), 'factors': set(), 'target': set()})

	empty = {}

	@area.pulse
	def routine():
		area.publish(empty, slot=str(max(area.context['factors'])))

	process = area.process
	comply = area.comply

	def replace_process(source, message, slot=None):
		if source in area.context['areas']:
			if slot == 'status':
				area.context['ready'].add(source)
		process(source, message, slot)

		if area.context['target'].issubset(area.context['ready']):
			area.proceed()
			area.context['ready'] -= area.context['target']
			area.context['factors'] = factors(area.time, limit)
			area.context['target'] = aggregate(area.context['target'], area.context['mapping'], area.context['factors'])

	def replace_comply(trigger, parameters={}):
		if trigger == 'add':
			try:
				target = parameters['name']
				slot = int(parameters['slot'])
				area.add(target, slots=['status'])
				init_full(area, target, ['status'])
				area.context['areas'].add(target)
				area.context['mapping'][slot].add(target)
			except: pass
		comply(trigger, parameters)

	area.process = replace_process
	area.comply = replace_comply
	return area


def create_clock(name: str, interfaces: Interfaces, limit: int=6):
	area = Area(name, interfaces)
	area.subscribe()
	empty = {}

	@area.pulse
	def routine():
		area.publish(empty, slot=str(max(factors(area.time, limit))).zfill(2))

	area.routine = area.proceed
	return area
