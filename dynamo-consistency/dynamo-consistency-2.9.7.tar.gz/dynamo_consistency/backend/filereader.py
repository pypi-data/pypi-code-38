"""
Holds general functions used for reading file dumps
"""

import os

from .. import datatypes
from .. import config

def file_reader(filename, translator):
    """
    :param str filename: Name of a file to read file information from
    :param func translator: A function that takes a line of a file as an arument
                            and transforms the line into input for
                            :py:func:`dynamo_consistencydatatypes.DirectoryInfo.add_file_list`.
    :returns: A directory tree created from reading the input file
    :rtype: dynamo_consistency.datatypes.DirectoryInfo
    """

    tree = datatypes.DirectoryInfo(
        name=config.config_dict()['RootPath']
        )

    config_dict = config.config_dict()
    dirlist = ['%s' % os.path.join(config_dict['RootPath'], directory)
               for directory in config_dict['DirectoryList']]

    def line_yielder():
        """
        Yields the translated lines of the input file
        for :py:func:`dynamo_consistency.datatypes.DirectoryInfo.add_file_list`
        """
        with open(filename, 'r') as inputfile:
            for line in inputfile:
                for directory in dirlist:
                    if line.startswith(directory):
                        yield translator(line)
                        break

    tree.add_file_list(line_yielder())

    return tree
