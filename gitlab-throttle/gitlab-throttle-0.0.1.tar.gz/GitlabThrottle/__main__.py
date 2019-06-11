import os
from .import throttle


throttle.abort_old_pipelines(dict(os.environ))
