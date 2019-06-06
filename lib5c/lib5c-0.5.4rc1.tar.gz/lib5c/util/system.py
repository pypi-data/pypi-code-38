"""
Module containing utility functions to assist in system-specific compatibility.
"""

import os


def shell_quote(string):
    """
    Quote a string with the correct quotes (double quotes on Windows and single
    quotes otherwise) to prevent the shell from eating the quotes.

    Useful for when assembling command line strings with arguments that must be
    quoted.

    Parameters
    ----------
    string : str
        The string to quote.

    Returns
    -------
    str
        The appropriately-quoted version of the input string.
    """
    if os.name == 'nt':
        return '"%s"' % string
    else:
        return "'%s'" % string


def splitall(path):
    """
    Recursively splits a path into a list of all its parts.

    https://www.safaribooksonline.com/library/view/python-cookbook/0596001673/
    ch04s16.html

    Parameters
    ----------
    path : str
        A path to split.

    Returns
    -------
    List[str]
        The parts of the path.
    """
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def check_outdir(outfile):
    """
    Makes sure the directories needed to write an output file exist.

    Parameters
    ----------
    outfile : str
        Path to a hypothetical output file to be written to the disk.
    """
    if type(outfile) == dict:
        for r, f in outfile.iteritems():
            check_outdir(f)
    else:
        head, tail = os.path.split(outfile)
        if head and not os.path.exists(head):
            try:
                print('creating directory %s' % head)
                os.makedirs(head)
            except OSError, e:
                if e.errno != os.errno.EEXIST:
                    raise
