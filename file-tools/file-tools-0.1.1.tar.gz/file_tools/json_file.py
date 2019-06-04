import json
from file_tools.utils.functions import get_file

#: Import JSON

def import_json(file, relative=False):
	file = get_file(file) if not relative else get_file(f'{get_caller_path()}/{file}', relative)
	with open(file, 'r') as f:
		try:
			return json.load(f)
		except:
			return {}

#: Export JSON

def export_json(data, file, indent=2, relative=False):
	file = get_file(file) if not relative else get_file(f'{get_caller_path()}/{file}', relative)
	with open(file, 'w') as f:
		json.dump(data, f, indent=indent)

#::: END PROGRAM :::
