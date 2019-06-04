from datatype_tools.utils.string_functions import format_date

#: Get Nested Keys

def get_nested_keys(obj, key_list):
	"""
	Expects dict object and list of keys in respective order, returns tuple
	>>> get_nested_keys({ 'a': { 'b': { 'c': 1 } }, 'd': 2 }, ['a', 'b', 'c'])
	('c', 1)
	"""
	if len(key_list) == 1:
		return (key_list[0], obj[key_list[0]],)

	elif len(key_list) > 1:
		return get_nested_keys(obj[key_list[0]], key_list[1:])

#: Get Nested Tuple

def get_nested_tuple(elem, arr, mod=1):
	"""
	Expects tuple, lits of nested key arguments, and mod 0 or 1 for keys or values, returns tuple.
	>>> get_nested_tuple(( 'a', { 'b': { 'c': 'd' } }), [{ 'keys': ['b', 'c'], 'sort_type': 'string'}], mod=1)
	('d',)
	>>> get_nested_tuple(( 'a', { 'b': { 'c': 'd' } }), [{ 'keys': ['b', 'c'], 'sort_type': 'string'}], mod=0)
	('c',)
	>>> get_nested_tuple(( 'a', { 'b': { 'c': 1 } }), [{ 'keys': ['b', 'c'], 'sort_type': 'int'}], mod=1)
	(1,)
	>>> get_nested_tuple(( 'a', { 'b': { 1: 'c' } }), [{ 'keys': ['b', 1], 'sort_type': 'int'}], mod=0)
	(1,)
	>>> get_nested_tuple(( 'a', { 'b': { 'c': 1.05 } }), [{ 'keys': ['b', 'c'], 'sort_type': 'float'}], mod=1)
	(1.05,)
	>>> get_nested_tuple(( 'a', { 'b': { 1.05: 'c' } }), [{ 'keys': ['b', 1.05], 'sort_type': 'float'}], mod=0)
	(1.05,)
	>>> get_nested_tuple(( 'a', { 'b': { 'c': '05/11/95' } }), [{ 'keys': ['b', 'c'], 'sort_type': 'date', 'date_input': 'mdy'}], mod=1)
	(19950511,)
	>>> get_nested_tuple(( 'a', { 'b': { '05/11/95': 'd' } }), [{ 'keys': ['b', '05/11/95'], 'sort_type': 'date', 'date_input': 'mdy'}], mod=0)
	(19950511,)
	"""
	nested_tuple = ()
	for i in range(0, len(arr)):
		if arr[i]['sort_type'] == 'string':
			nested_tuple += (get_nested_keys(elem[1], arr[i]['keys'])[mod],)
		elif arr[i]['sort_type'] == 'int':
			nested_tuple += (int(get_nested_keys(elem[1], arr[i]['keys'])[mod]),)
		elif arr[i]['sort_type'] == 'float':
			nested_tuple += (float(get_nested_keys(elem[1], arr[i]['keys'])[mod]),)
		elif arr[i]['sort_type'] == 'date':
			nested_tuple += (int(format_date(get_nested_keys(elem[1], arr[i]['keys'])[mod],
									date_input=arr[i]['date_input'], date_format='yyyymmdd')),)
	return nested_tuple

#: Sort Dict

def dict_sort(obj, mod=1, asc=True, sort_type='string', date_input='mdy'):
	"""
	Expects dict object, mod 0 or 1 for keys or values, asc for ascending or descending, sort_type in ['string', 'int', 'float', 'date'],
	and date_input for date input format.
	>>> dict_sort({ 'b': 'c', 'a': 'd' }, mod=1, asc=True, sort_type='string')
	{'b': 'c', 'a': 'd'}
	>>> dict_sort({ 'b': 'c', 'a': 'd' }, mod=1, asc=False, sort_type='string')
	{'a': 'd', 'b': 'c'}
	>>> dict_sort({ 'b': 'c', 'a': 'd' }, mod=0, asc=True, sort_type='string')
	{'a': 'd', 'b': 'c'}
	>>> dict_sort({ 'b': 'c', 'a': 'd' }, mod=0, asc=False, sort_type='string')
	{'b': 'c', 'a': 'd'}
	>>> dict_sort({ 2: 3, 1: 4 }, mod=1, asc=True, sort_type='int')
	{2: 3, 1: 4}
	>>> dict_sort({ 2: 3, 1: 4 }, mod=1, asc=False, sort_type='int')
	{1: 4, 2: 3}
	>>> dict_sort({ 2: 3, 1: 4 }, mod=0, asc=True, sort_type='int')
	{1: 4, 2: 3}
	>>> dict_sort({ 2: 3, 1: 4 }, mod=0, asc=False, sort_type='int')
	{2: 3, 1: 4}
	>>> dict_sort({ 2.02: 3.03, 1.01: 4.04 }, mod=1, asc=True, sort_type='float')
	{2.02: 3.03, 1.01: 4.04}
	>>> dict_sort({ 2.02: 3.03, 1.01: 4.04 }, mod=1, asc=False, sort_type='float')
	{1.01: 4.04, 2.02: 3.03}
	>>> dict_sort({ 2.02: 3.03, 1.01: 4.04 }, mod=0, asc=True, sort_type='float')
	{1.01: 4.04, 2.02: 3.03}
	>>> dict_sort({ 2.02: 3.03, 1.01: 4.04 }, mod=0, asc=False, sort_type='float')
	{2.02: 3.03, 1.01: 4.04}
	>>> dict_sort({ 'b': '12/12/1940', 'a': '01/01/2019' }, mod=1, asc=True, sort_type='date', date_input='mdy')
	{'b': '12/12/1940', 'a': '01/01/2019'}
	>>> dict_sort({ 'b': '12/12/1940', 'a': '01/01/2019' }, mod=1, asc=False, sort_type='date', date_input='mdy')
	{'a': '01/01/2019', 'b': '12/12/1940'}
	>>> dict_sort({ '12/12/1940': 'b', '01/01/2019': 'a' }, mod=0, asc=True, sort_type='date', date_input='mdy')
	{'12/12/1940': 'b', '01/01/2019': 'a'}
	>>> dict_sort({ '12/12/1940': 'b', '01/01/2019': 'a' }, mod=0, asc=False, sort_type='date', date_input='mdy')
	{'01/01/2019': 'a', '12/12/1940': 'b'}
	"""
	if sort_type == 'string':
		return {k: v for k, v in sorted(obj.items(), key=lambda x: x[mod], reverse=not asc)}
	elif sort_type == 'int':
		return {k: v for k, v in sorted(obj.items(), key=lambda x: int(x[mod]), reverse=not asc)}
	elif sort_type == 'float':
		return {k: v for k, v in sorted(obj.items(), key=lambda x: float(x[mod]), reverse=not asc)}
	elif sort_type == 'date':
		return {k: v for k, v in sorted(obj.items(),
					key=lambda x: int(format_date(x[mod],
					date_input=date_input, date_format='yyyymmdd')),
					reverse=not asc)}

#: Sort Nested Dict

def dict_sort_nested(obj, nested_args, mod=1, asc=True):
	"""
	Expects dict object, nested_args for sort arguments.
	nested_args expects a list of dict, i.e. [{ 'keys': ['b', 'c'], 'sort_type': 'date', 'date_input': 'mdy'}]
	keys indicates the nested keys respectively to sort by, sort_type in ['string', 'int', 'float', 'date'],
	and date_input for date input format.
	Multiple dicts can be added to sort by multiple nested keys respectively.
	Also expects mod 0 or 1 for keys or values, asc for ascending or descending.
	>>> dict_sort_nested({ 'a': { 'b': { 'c': 2 }, 'd': 1 }, 'b': { 'b': { 'c': 1 }, 'd': 3  }, 'c': { 'b': { 'c': 1 }, 'd': 2 } }, nested_args=[{'keys': ['b', 'c'], 'sort_type': 'int'}, {'keys': ['d'], 'sort_type': 'int'}], asc=True)
	{'c': {'b': {'c': 1}, 'd': 2}, 'b': {'b': {'c': 1}, 'd': 3}, 'a': {'b': {'c': 2}, 'd': 1}}
	"""
	return {k: v for k, v in sorted(obj.items(), key=lambda x: get_nested_tuple(
				elem=x, arr=nested_args, mod=mod), reverse=not asc)}

#::: END PROGRAM :::
