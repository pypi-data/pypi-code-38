import re


FLOAT_REGEX = re.compile(r"""
(
    [-+]?       # optional plus or minus sign
    [0-9]*
    \.?         # floating point separator
    [0-9]+
)""", re.VERBOSE)


POSITIVE_FLOAT_REGEX = re.compile(r"([0-9]*\.?[0-9]+)", re.VERBOSE)


POSITIVE_FLOAT_LIST_REGEX = re.compile(r"""
(-0\.0)?                        # First float can be -0.0
(
    ({POSITIVE_FLOAT}+)         # positive float
    \s                          # separated by a space
)*
({POSITIVE_FLOAT}+)             # final positive float with no trailing space.
""".format(POSITIVE_FLOAT=POSITIVE_FLOAT_REGEX.pattern), re.VERBOSE)


TIMESERIE_ENTRY_REGEX = re.compile(r"""
(\d+)
(,)
([-+]?[0-9]*\.?[0-9]+)      # digit,float; for example: 5,-3.09
""", re.VERBOSE)


TIMESERIES_REGEX = re.compile(r"""
(
    {timeserie_entry}       # digit,float; for example: 60,-0.5
    \n                      # separated by newlines
)*
(
    {timeserie_entry}       # last entry does not have a newline.
){{1}}
""".format(timeserie_entry=TIMESERIE_ENTRY_REGEX.pattern), re.VERBOSE)
