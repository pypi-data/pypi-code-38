"""

lambda_utils (python3)

    Common functionality for use with AWS Lambda Service

Author:
    Blake Huber
    Copyright Blake Huber, All Rights Reserved.

License:

    MIT License.
    Additional terms may be found in the complete license agreement:
    https://opensource.org/licenses/MIT

    Project README:
    https://github.com/fstab50/pyaws/blob/master/README.md
"""

import os
import re
import inspect
from pyaws import logger


def read_env_variable(arg, default=None, patterns=None):
    """
    Summary.

        Parse environment variables, validate characters, convert
        type(s). default should be used to avoid conversion of an
        variable and retain string type

    Usage:
        >>> from lambda_utils import read_env_variable
        >>> os.environ['DBUGMODE'] = 'True'
        >>> myvar = read_env_variable('DBUGMODE')
        >>> type(myvar)
        True

        >>> from lambda_utils import read_env_variable
        >>> os.environ['MYVAR'] = '1345'
        >>> myvar = read_env_variable('MYVAR', 'default')
        >>> type(myvar)
        str

    Args:
        :arg (str):  Environment variable name (external name)
        :default (str): Default if no variable found in the environment under
            name in arg parameter
        :patterns (None):  Unused; not user callable. Used preservation of the
            patterns tuple between calls during runtime

    Returns:
        environment variable value, TYPE str

    """
    if patterns is None:
        patterns = (
            (re.compile('^[-+]?[0-9]+$'), int),
            (re.compile('\d+\.\d+'), float),
            (re.compile(r'^(true|false)$', flags=re.IGNORECASE), lambda x: x.lower() == 'true'),
            (re.compile('[a-z/]+', flags=re.IGNORECASE), str),
            (re.compile('[a-z/]+\.[a-z/]+', flags=re.IGNORECASE), str),
        )

    if arg in os.environ:
        var = os.environ[arg]
        if var is None:
            ex = KeyError('environment variable %s not set' % arg)
            logger.exception(ex)
            raise ex
        else:
            if default:
                return str(var)     # force default type (str)
            else:
                for pattern, func in patterns:
                    if pattern.match(var):
                        return func(var)
            # type not identified
            logger.warning(
                '%s: failed to identify environment variable [%s] type. May contain \
                special characters' % (inspect.stack()[0][3], arg)
                 )
            return str(var)
    else:
        ex = KeyError('environment variable %s not set' % arg)
        logger.exception(ex)
        raise ex
