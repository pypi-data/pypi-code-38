#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import text_type
from zope.interface import Interface
from zope.interface import classImplements
from zope.testing import cleanup

from nti.testing.layers import ConfiguringLayerMixin
from nti.testing.layers import ZopeComponentLayer

__docformat__ = "restructuredtext en"

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904,inherit-non-class

class SchemaLayer(ZopeComponentLayer,
                  ConfiguringLayerMixin):

    set_up_packages = ('nti.schema',)

    @classmethod
    def setUp(cls):
        cls.setUpPackages()

    @classmethod
    def tearDown(cls):
        cls.tearDownPackages()
        cleanup.cleanUp()

    @classmethod
    def testSetUp(cls):
        pass

    testTearDown = testSetUp


class IUnicode(Interface):
    "Unicode strings"


classImplements(text_type, IUnicode)
