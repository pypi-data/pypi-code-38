from forbiddenfruit import curse
from datatype_tools.utils.string_functions import (replace_multiple,
	format_date, find_nth, b64_encode, b64_decode, get_iso_date)

#: String Curses

curse(str, 'replace_multiple', replace_multiple)
curse(str, 'format_date', format_date)
curse(str, 'find_nth', find_nth)
curse(str, 'b64_enc', b64_encode)
curse(str, 'b64_dec', b64_decode)
curse(str, 'get_iso_date', get_iso_date)

#::: END PROGRAM :::
