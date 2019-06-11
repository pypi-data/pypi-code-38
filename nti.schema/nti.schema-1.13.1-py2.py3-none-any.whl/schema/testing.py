# -*- coding: utf-8 -*-
"""
Test support for schemas and interfaces, mostly in the form of
Hamcrest matchers.

The following functions can still be imported from here, but have been
moved to :mod:`nti.testing.matchers`:

- :func:`~nti.testing.matchers.provides`
- :func:`~nti.testing.matchers.implements`
- :func:`~nti.testing.matchers.verifiably_provides`
- :func:`~nti.testing.matchers.validly_provides`
- :func:`~nti.testing.matchers.validated_by`
- :func:`~nti.testing.matchers.not_validated_by`
"""

from __future__ import division
from __future__ import print_function

from zope.deprecation import moved
moved('nti.testing.matchers')
