import warnings
from .contrib.django.forms import *  # NOQA

from .deprecation import RemovedInRestosaur08Warning

warnings.warn(
        '`%s` module is deprecated and will be removed in v0.8.'
        'Please replace your imports using '
        '``restosaur.contrib.django.forms`` module' % __name__,
        RemovedInRestosaur08Warning, stacklevel=2)
