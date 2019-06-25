import warnings

from .contrib.django.apps import *  # NOQA
from .deprecation import RemovedInRestosaur08Warning

warnings.warn(
        '`%s` module is deprecated and will be removed in v0.8.'
        'Please replace `restosaur` in INSTALLED_APPS using '
        '``restosaur.contrib.django`` name' % __name__,
        RemovedInRestosaur08Warning, stacklevel=2)
