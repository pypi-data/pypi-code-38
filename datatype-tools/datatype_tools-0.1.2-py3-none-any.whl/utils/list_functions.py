from datatype_tools.utils.string_functions import format_date
from datatype_tools.utils.dict_functions import get_nested_keys, get_nested_tuple

#: Dict to Tuple

def to_tuple(d):
	"""
	Expects dict with single key, returns tuple.
	>>> to_tuple({'a': 1})
	('a', 1)
	"""
	return next(iter(d.items()))

#: Sort List

def list_sort(obj, mod=1, asc=True, sort_type='string', date_input='mdy'):
	"""
	Expects list of dicts, mod 0 or 1 for keys or values, asc for ascending or descending, sort_type in ['string', 'int', 'float', 'date'],
	and date_input for date input format.
	>>> list_sort([{ 'b': 'c'}, {'a': 'd' }], mod=1, asc=True, sort_type='string')
	[{'b': 'c'}, {'a': 'd'}]
	"""
	if sort_type == 'string':
		return sorted(obj, key=lambda x: to_tuple(x)[mod], reverse=not asc)
	elif sort_type == 'int':
		return sorted(obj, key=lambda x: int(to_tuple(x)[mod]), reverse=not asc)
	elif sort_type == 'float':
		return sorted(obj, key=lambda x: float(to_tuple(x)[mod]), reverse=not asc)
	elif sort_type == 'date':
		return sorted(obj, key=lambda x: int(format_date(to_tuple(x)[mod],
					date_input=date_input, date_format='yyyymmdd')), reverse=not asc)

#: Sort List by Key

def list_key_sort(obj, key, asc=True, sort_type='string', date_input='mdy'):
	"""
	Expects list of dicts, key, mod 0 or 1 for keys or values, asc for ascending or descending, sort_type in ['string', 'int', 'float', 'date'],
	and date_input for date input format.
	>>> list_key_sort([{ 'a': 2, 'b': 1 }, {'a': 1, 'b': 2 }], key='b', asc=False, sort_type='int')
	[{'a': 1, 'b': 2}, {'a': 2, 'b': 1}]
	"""
	if sort_type == 'string':
		return sorted(obj, key=lambda x: x[key], reverse=not asc)
	elif sort_type == 'int':
		return sorted(obj, key=lambda x: int(x[key]), reverse=not asc)
	elif sort_type == 'float':
		return sorted(obj, key=lambda x: float(x[key]), reverse=not asc)
	elif sort_type == 'date':
		return sorted(obj, key=lambda x: int(format_date(x[key],
					date_input=date_input, date_format='yyyymmdd')), reverse=not asc)

#: Nested Sort for List

def list_nested_sort(obj, nested_args, mod=1, asc=True):
	"""
	Expects list of dicts, nested_args for sort arguments.
	nested_args expects a list of dict, i.e. [{ 'keys': ['b', 'c'], 'sort_type': 'date', 'date_input': 'mdy'}]
	keys indicates the nested keys respectively to sort by, sort_type in ['string', 'int', 'float', 'date'],
	and date_input for date input format.
	Multiple dicts can be added to sort by multiple nested keys respectively.
	Also expects mod 0 or 1 for keys or values, asc for ascending or descending.
	>>> list_nested_sort([{'a': {'b': 2}}, {'a': {'b': 1}}], nested_args=[{ 'keys': ['b'], 'sort_type': 'int'}])
	[{'a': {'b': 1}}, {'a': {'b': 2}}]
	"""
	return sorted(obj, key=lambda x: get_nested_tuple(
				elem=to_tuple(x), arr=nested_args, mod=mod), reverse=not asc)

#::: END PROGRAM :::
