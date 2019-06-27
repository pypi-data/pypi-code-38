import logging
import os.path
import glob
import itertools
import re


def find(base, headers, inheritance='public', many=True,
         required=False):
    '''Scan header files for classes inheriting from a given base class,
    according to the specified inheritance pattern (defaults to 'public').
    Returns a sequence of class names.'''

    regex = '^\s*class\s+([a-zA-Z_]\w+)\s*:\s*' + inheritance + '\s*' + base
    logging.debug('regex: ' + regex)
    cregex = re.compile(regex, re.MULTILINE)

    classes = []
    for header in headers:
        logging.debug('scanning header: ' + header)
        with open(header) as hfile:
            text = hfile.read()
        found_classes = [match.group(1) for match in re.finditer(cregex, text)]
        if found_classes:
            logging.debug(str(len(found_classes)) + ' matches in this file')
        classes += [(c, os.path.realpath(header)) for c in found_classes]

    missing = RuntimeError('could not find any '
                           + base
                           + '-derived class in the specified files.')
    if required and not classes:
        raise missing
    if not many:
        try:
            the_class = classes[0]
        except IndexError:
            if not required:
                return None
            else:
                raise missing
        if len(classes) > 1:
            logging.warning('found several '
                            + base
                            + '-derived classes in the specified files. '
                            'Selecting '
                            + the_class[0] + '(from ' + the_class[1] + ').')
        return the_class
    else:
        return classes


def find_in_dirs(base, dirs, suffixes=[''], inheritance='public', many=True,
                 required=False):
    headers = itertools.chain.from_iterable(
        glob.iglob(os.path.join(directory, '*'+suffix))
        for suffix in suffixes for directory in dirs)
    return find(base, headers,
                inheritance=inheritance, many=many, required=required)


def find_header_for_class(name, dirs, suffixes=['']):
    regex = '^\s*class\s+' + name + '\s*[:{]'
    cregex = re.compile(regex, re.MULTILINE)

    headers = itertools.chain.from_iterable((
        glob.iglob(os.path.join(directory, '*'+suffix))
        for suffix in suffixes for directory in dirs
        ))
    for header in headers:
        with open(header) as hfile:
            text = hfile.read()
        if re.search(cregex, text):
            return header

    return None
