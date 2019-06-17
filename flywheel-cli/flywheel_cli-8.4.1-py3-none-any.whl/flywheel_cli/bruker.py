import logging

import fs
from .util import set_nested_attr

log = logging.getLogger(__name__)

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
                key, sep, value = line[2:].partition('=')
                key = key.lstrip('$') # Paravision uses private parameters prefixed with '$'
                value = value.strip()

                # Check value
                if value:
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
        except ValueError as e:
            log.debug('Error processing bruker parameter line: {}'.format(e))
            # Any error should just reset state
            key = None
            value = ''

    if key:
        result[key] = value

    return result

def extract_bruker_metadata_fn(filename, keys):
    """Create a function that will open filename and extract bruker parameters.

    Arguments:
        filename (str): The name of the file to open (e.g. subject)
        keys (dict): The mapping of src_key to dst where dst is a key or a function
            that returns a key and a value, given an input value.

    Returns:
        function: The function that will extract bruker params as metadata
    """
    def extract_metadata(name, context, walker, path):
        file_path = walker.combine(path, filename)
        log.debug('Attempting to import params from: {}'.format(file_path))

        try:
            with walker.open(file_path, mode='r', encoding='utf-8') as f:
                params = parse_bruker_params(f)

            for src_key, dst_key in keys.items():
                if src_key in params:
                    value = params[src_key]
                    if callable(dst_key):
                        ret = dst_key(value, path=file_path, context=context)
                        if ret:
                            dst_key, value = ret
                        else:
                            dst_key = None

                    if dst_key:
                        set_nested_attr(context, dst_key, value)
        except FileNotFoundError:
            log.info('No param file located at: {}'.format(file_path))
        except IOError as e:
            log.error('Unable to process params file {}: {}'.format(file_path, e))

    return extract_metadata


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Read and print bruker parameters file')
    parser.add_argument('path', help='The path to the file to read')

    args = parser.parse_args()

    with open(args.path, 'r') as f:
        result = parse_bruker_params(f)

    for key, value in result.items():
        print('{} = {}'.format(key, value))
