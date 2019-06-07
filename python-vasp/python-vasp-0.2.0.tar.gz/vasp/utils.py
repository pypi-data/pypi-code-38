import re


def clean_lines(lines):
    """
    Clean a list of lines containing text, it will:

    - Erase newlines
    - Substitute double (or more) spaces by one spaces
    - Remove Whitespaces at the end and beginning of line
    - Remove Whitespaces at the end and beginning of line
    - Remove empty lines

    It will do the above mentioned in that order
    """
    # kill newlines
    lines = map(lambda x: x.replace("\n", ''), lines)

    # double spaces out
    lines = map(lambda x: re.sub(r'  *', ' ', x), lines)

    # Whitespaces at the begginning and end
    lines = map(lambda x: re.sub(r'^ *', '', x), lines)
    lines = map(lambda x: re.sub(r' *$', '', x), lines)

    # takeout empty lines
    lines = list(filter(lambda x: x, lines))

    return lines
