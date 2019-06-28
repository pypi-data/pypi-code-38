import argparse
import importlib
import os
from os import path
from pip._internal import main as pip_main


from . import repo
from .templates import create_clock
from .utils import read_interfaces


def main():
	parser = argparse.ArgumentParser(description='Run a Pabiana area.')
	parser.add_argument('names', help='specify module and area name in the form of module_name:area_name')
	parser.add_argument('-f', '--fast', action='store_true', help='prevent the use of Pip before running the area.')
	arguments = parser.parse_args()
	module_name, area_name = arguments.names.split(':')

	base_path = os.getcwd()
	module_path = path.join(base_path, module_name)
	interfaces_path = path.join(base_path, 'interfaces.json')
	requirements_path = path.join(base_path, module_name, 'requirements.txt')

	if not arguments.fast and path.isfile(requirements_path):
		pip_main(['install', '-U', '-r', requirements_path])

	run(module_name, area_name, base_path, module_path, interfaces_path)


def run(module_name, area_name, base_path, module_path, interfaces_path):
	repo['module-name'] = module_name
	repo['area-name'] = area_name
	repo['interfaces'] = read_interfaces(interfaces_path)
	repo['base-path'] = base_path
	repo['module-path'] = module_path

	try:
		mod = importlib.import_module(module_name)
	except ImportError:
		if module_name == 'def_clock' and area_name == 'clock':
			area = create_clock(name=area_name, interfaces=repo['interfaces'])
			area.run(timeout=500)
			return
		else:
			raise

	if hasattr(mod, 'premise'):
		mod.premise()

	if hasattr(mod, 'area'):
		if hasattr(mod, 'config'):
			params = {
				'clock_name': mod.config.get('clock-name'),
				'clock_slots': mod.config.get('clock-slots')
			}
			if 'subscriptions' in mod.config:
				params['subscriptions'] = mod.config['subscriptions']
			mod.area.subscribe(**params)
			if 'context-values' in mod.config:
				mod.area.context.update(mod.config['context-values'])
		mod.area.run()

	elif hasattr(mod, 'runner'):
		if hasattr(mod.runner, 'setup'):
			params = {}
			if hasattr(mod, 'config'):
				params.update(mod.config)
			mod.runner.setup(**params)
		mod.runner.run()


if __name__ == '__main__':
	main()