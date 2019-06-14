"""Provides functions for scanning bruker parameters files"""
import logging
log = logging.getLogger(__name__)


def set_nested_attr(obj, key, value):
    """Set a nested attribute in dictionary, creating sub dictionaries as necessary.

    Arguments:
        obj (dict): The top-level dictionary
        key (str): The dot-separated key
        value: The value to set
    """
    parts = key.split('.')
    for part in parts[:-1]:
        obj.setdefault(part, {})
        obj = obj[part]
    obj[parts[-1]] = value


# pylint: disable=too-many-branches
def parse_bruker_params(fileobj):
    """Parse the pv5/6 parameters file, extracting keys

    References:
        - ParaVision D12_FileFormats.pdf
        - JCAMP DX format: http://www.jcamp-dx.org/protocols/dxnmr01.pdf

    Arguments:
        fileobj (file): The file-like object that supports readlines, opened in utf-8
    """
    result = {}

    # Variable names are ##/##$
    # And are either =value, =< value >, or =() with value(s) following the next lines
    # $$ appear to be comments

    key = None
    value = ''

    for line in fileobj.readlines():
        if line.startswith('$$'):
            continue

        try:
            if line.startswith('##'):
                if key:
                    result[key] = value

                # Parse parameter name
                key, _, value = line[2:].partition('=')
                key = key.lstrip('$')  # Paravision uses private parameters prefixed with '$'
                value = value.strip()

                # Check value
                if not value:
                    continue

                # Case 1: value is wrapped in brackets: < foo >
                if value[0] == '<' and value[-1] == '>':
                    result[key] = value[1:-1].strip()
                    key = None
                    value = ''
                elif value[0] == '(':
                    # Case 2: value is a structure
                    if ',' in value:
                        continue
                    # Case 3: value is size/dimensions, in which case we ignore it
                    value = ''
                    continue
                else:
                    # Case 4: value is directly assigned
                    result[key] = value.strip()
                    key = None
                    value = ''
            elif key:
                line = line.strip()
                if line[0] == '<' and line[-1] == '>':
                    line = line[1:-1]

                if value:
                    value = value + ' '

                value = value + line
        except ValueError as ex:
            log.debug('Error processing bruker parameter line: %s', ex)
            # Any error should just reset state
            key = None
            value = ''

    if key:
        result[key] = value

    return result
