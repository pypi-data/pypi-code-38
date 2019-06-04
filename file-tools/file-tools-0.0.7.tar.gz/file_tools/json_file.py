import json
from file_tools.utils.functions import get_file

#: Import JSON

def import_json(file, relative=False):
	with open(get_file(file, relative), 'r') as f:
		try:
			return json.load(f)
		except:
			return {}

#: Export JSON

def export_json(data, file, indent=2, relative=False):
	with open(get_file(file, relative), 'w') as f:
		json.dump(data, f, indent=indent)

#::: END PROGRAM :::
