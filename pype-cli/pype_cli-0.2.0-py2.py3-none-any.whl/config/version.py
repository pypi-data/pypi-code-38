# -*- coding: utf-8 -*-
"""Print current pype version."""

import pkg_resources

from pype.core import get_pype_basepath

base_path = get_pype_basepath()
version = pkg_resources.get_distribution('pype-cli').version
print('{} @ {}'.format(version, base_path))
