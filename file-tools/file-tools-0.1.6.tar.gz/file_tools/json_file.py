import json
from file_tools.utils.functions import get_file

#: Import JSON

def import_json(file, path=''):
	with open(get_file(file, path=path), 'r') as f:
		try:
			return json.load(f)
		except:
			return {}

#: Export JSON

def export_json(data, file, path='', indent=2):
	with open(get_file(file, path=path), 'w') as f:
		json.dump(data, f, indent=indent)

#::: END PROGRAM :::
