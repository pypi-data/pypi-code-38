from forbiddenfruit import curse
from datatype_tools.utils.type_functions import (list_sort_by_val,
	list_sort_by_key, list_sort_by_key_val,
	list_nested_sort_by_val)

#: List Curses

curse(list, 'sort_by_val', list_sort_by_val)
curse(list, 'sort_by_key', list_sort_by_key)
curse(list, 'sort_by_key_val', list_sort_by_key_val)
curse(list, 'nested_sort', list_nested_sort_by_val)

#::: END PROGRAM :::
