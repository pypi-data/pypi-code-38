#from adapt_first import *
#from adapt_1_2 import *
#from adapt_1_4 import *
#from adapt_1_5 import *
#from adapt_1_6 import *


def get_config():
  """Returns a string containing the configuration information.
  """

  import bob.extension
  return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
