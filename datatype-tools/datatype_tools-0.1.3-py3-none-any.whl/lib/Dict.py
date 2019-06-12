from forbiddenfruit import curse
from datatype_tools.utils.type_functions import (dict_sort_by_val,
	dict_sort_by_key, dict_nested_sort_by_val)

#: Dict Curses

curse(dict, 'sort_by_val', dict_sort_by_val)
curse(dict, 'sort_by_key', dict_sort_by_key)
curse(dict, 'nested_sort', dict_nested_sort_by_val)

#::: END PROGRAM :::
