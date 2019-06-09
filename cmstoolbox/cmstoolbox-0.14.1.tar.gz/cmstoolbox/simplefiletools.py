"""
Contains methods for manipulating txt files and sourcing bash scripts.

:author: Daniel Abercrombie <dabercro@mit.edu>
"""

import os
import subprocess
import logging

def load_env(configs):
    """Sources bash files and loads the resulting environment into os.environ

    :param configs: is a list of file names that should be sourced.
                    A string for a single configuration file is also accepted.
    :type configs: str or list
    """
    if isinstance(configs, str):
        load_env([configs])
    elif isinstance(configs, list):
        for config in configs:
            if os.path.exists(config):
                config_contents = subprocess.Popen(['bash', '-c', 'source ' + config + '; env'],
                                                   stdout=subprocess.PIPE)
                for line in config_contents.stdout:
                    if isinstance(line, bytes):
                        (key, _, value) = line.decode('utf-8').partition('=')
                    elif isinstance(line, str):
                        (key, _, value) = line.partition('=')
                    else:
                        logging.warning('Not sure how to handle subprocess output. Contact Dan.')
                        break
                    os.environ[str(key)] = str(value).strip('\n')

                config_contents.communicate()
            else:
                logging.warning('%s does not exist.', config)
    else:
        logging.critical('You passed an invalid argument type as config')
        exit()


def append_to_file(file_name, lines):
    """Appends lines to a file.
    This function may be useful for the exceedingly lazy.

    :param str file_name: is the file to append to
    :param lines: is the list of lines or a single line to append to the file
    :type lines: str or list
    """

    if not isinstance(lines, list):
        append_to_file(file_name, [lines])

    else:
        with open(file_name, 'a') as the_file:
            for line in lines:
                the_file.write(line + '\n')
