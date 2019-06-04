from datatype_tools.utils.dict_functions import dict_sort, dict_sort_nested
from datatype_tools.utils.list_functions import list_sort, list_key_sort, list_nested_sort

#::: DICT :::

#: Sort Dictionary by Value

def dict_sort_by_val(self, asc=True, sort_type='string', date_input='mdy'):
	return dict_sort(self, mod=1, asc=asc, sort_type=sort_type, date_input=date_input)

#: Sort Dictionary by Key

def dict_sort_by_key(self, asc=True, sort_type='string', date_input='mdy'):
	return dict_sort(self, mod=0, asc=asc, sort_type=sort_type, date_input=date_input)

#: Sort Nested Dictionary by Value(s)

def dict_nested_sort_by_val(self, nested_args, asc=True):
	return dict_sort_nested(self, nested_args=nested_args, mod=1, asc=asc)

#::: LIST :::

#: Sort List by Value

def list_sort_by_val(self, asc=True, sort_type='string', date_input='mdy'):
	return list_sort(self, mod=1, asc=asc, sort_type=sort_type, date_input=date_input)

#: Sort List by Keys

def list_sort_by_key(self, asc=True, sort_type='string', date_input='mdy'):
	return list_sort(self, mod=0, asc=asc, sort_type=sort_type, date_input=date_input)

#: Sort List by Key Value

def list_sort_by_key_val(self, key, asc=True, sort_type='string', date_input='mdy'):
	return list_key_sort(self, key=key, asc=asc, sort_type=sort_type, date_input=date_input)

#: Sort List of Nested Dictionaries by Value(s)

def list_nested_sort_by_val(self, nested_args, asc=True):
	return list_nested_sort(self, nested_args=nested_args, mod=1, asc=asc)

#::: END PROGRAM :::
