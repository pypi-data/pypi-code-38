import sys
import typing
from . import types
from . import app
from . import ops
from . import path
from . import props
from . import context
from . import utils

context: 'types.Context' = None

data: 'types.BlendData' = None
'''Access to Blenders internal data '''
