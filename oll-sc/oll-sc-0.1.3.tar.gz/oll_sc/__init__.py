import logging
import os
import platform
from functools import wraps
from pathlib import Path

from PyKCS11 import PyKCS11Lib

from .exceptions import PlatformNotSupported

logger = logging.getLogger(__name__)

# prebuild opensc libraries
OPENSC_LIBS_PATHS = {
    'Darwin-64bit': 'opensc/opensc-pkcs11-Darwin-64bit.so',
    'Windows-64bit': 'opensc/opensc-pkcs11-Windows-64bit.dll',
    'Windows-32bit': 'opensc/opensc-pkcs11-Windows-32bit.dll',
    'Linux-64bit': 'opensc/opensc-pkcs11-Linux-64bit.so'  # NOTE: Built on Ubuntu 16.04!
}

# https://github.com/easybuilders/easybuild/wiki/OS_flavor_name_version
# One of ['Windows', 'Darwin', 'Linux']
_SYSTEM = platform.system()
# One of ['32bit' , '64bit'] - depends on python executable
_ARCHITECTURE = platform.architecture()[0]

PLATFORM = '{}-{}'.format(_SYSTEM, _ARCHITECTURE)

logger.info('Platform: %s', PLATFORM)

# opensc-pkcs11 lib absolute path
OPENSC_LIB_PATH = Path(__file__).parent / OPENSC_LIBS_PATHS.get(PLATFORM, '')


def init_pkcs11(api_func):
  """Decorator to reinitialize PyKCS11 lib. Needed for long running processes.
  """
  @wraps(api_func)
  def decorator(*args, **kwargs):
    """If pkcs11 is NOT passed in kwargs, instantiate it and add it to
    kwargs.
                  NOTE: pkcs11 MUST be passed as kwarg!
    """
    pkcs11 = kwargs.pop('pkcs11', None)
    if pkcs11 is None:
      if not OPENSC_LIB_PATH.is_file():
        raise PlatformNotSupported(
            'opensc-pkcs11 library for platform {} is not included'
            .format(PLATFORM))

      pkcs11 = PyKCS11Lib()
      pkcs11.load(str(OPENSC_LIB_PATH.resolve()))
      logger.debug('PyKCS11Lib successfully loaded OpenSC library.')
    kwargs['pkcs11'] = pkcs11

    return api_func(*args, **kwargs)
  return decorator
