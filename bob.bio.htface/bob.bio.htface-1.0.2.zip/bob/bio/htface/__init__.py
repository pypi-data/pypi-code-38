from . import database
from . import algorithm
from . import extractor
from . import preprocessor
from . import architectures
from . import utils
from . import baselines
from . import configs
from . import loss

def get_config():
  """Returns a string containing the configuration information.
  """

  import bob.extension
  return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
