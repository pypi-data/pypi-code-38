import warnings
from .contrib.django.settings import *  # NOQA

from .deprecation import RemovedInRestosaur08Warning

warnings.warn(
        '`%s` module is deprecated and will be removed in v0.8.'
        'Please replace your imports using '
        '``restosaur.contrib.django.settings`` module' % __name__,
        RemovedInRestosaur08Warning, stacklevel=2)
