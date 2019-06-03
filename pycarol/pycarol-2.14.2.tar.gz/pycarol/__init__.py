""" PyCarol - Connecting Carol to Python

"""

import os
import tempfile

__version__ = '2.14.2'

__BUCKET_NAME__= 'carol-internal'
__TEMP_STORAGE__ = os.path.join(tempfile.gettempdir(),'carolina/cache')

__CONNECTOR_PYCAROL__ = 'f9953f6645f449baaccd16ab462f9b64'


from .carol import Carol
from .staging import Staging
from .connectors import Connectors
from .query import Query
from .storage import Storage
from .carolina import Carolina
from .tasks import Tasks
from .data_models import DataModel
from .logger import CarolHandler