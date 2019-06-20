"""Package skeleton

.. moduleauthor:: Wojciech Sobala <wojciech.sobala@pl.ibm.com>
"""

from os.path import join as path_join
import pkg_resources
import sys

try:
    wml_location = pkg_resources.get_distribution("watson-machine-learning-client").location
    sys.path.insert(1, path_join(wml_location, 'watson_machine_learning_client', 'libs'))
    sys.path.insert(2, path_join(wml_location, 'watson_machine_learning_client', 'tools'))
except pkg_resources.DistributionNotFound:
    pass
from .utils import version
from .client import WatsonMachineLearningAPIClient

from .utils import is_python_2
if is_python_2():
    from .log_util import get_logger
    logger = get_logger('wml_client_initialization')
    logger.warning("Python 2 is not officially supported.")
