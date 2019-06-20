# -*- coding: utf-8 -*-
from persistent.dict import PersistentDict
from plone.app.viewletmanager.exportimport.storage import exportViewletSettingsStorage  # noqa: E501
from plone.app.viewletmanager.exportimport.storage import importViewletSettingsStorage  # noqa: E501
from plone.app.viewletmanager.exportimport.storage import ViewletSettingsStorageNodeAdapter  # noqa: E501
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from plone.app.viewletmanager.storage import ViewletSettingsStorage
from plone.app.viewletmanager.testing import PLONE_APP_VIEWLETMANAGER_INTEGRATION_TESTING  # noqa: E501
from Products.CMFPlone.exportimport.tests.base import BodyAdapterTestCase
from Products.GenericSetup.tests.common import BaseRegistryTests
from Products.GenericSetup.tests.common import DummyExportContext
from Products.GenericSetup.tests.common import DummyImportContext
from xml.parsers.expat import ExpatError
from zope.component import getUtility

import unittest


COMMON_SETUP_ORDER = {
    'basic': {'top': ('one', )},
    'fancy': {'top': ('two', 'three', 'one')},
    }

COMMON_SETUP_HIDDEN = {
    'light': {'top': ('two', )},
    }

_VIEWLETS_XML = b"""\
<?xml version="1.0" encoding="utf-8"?>
<object>
 <order manager="top" skinname="basic">
  <viewlet name="one"/>
 </order>
 <order manager="top" skinname="fancy">
  <viewlet name="two"/>
  <viewlet name="three"/>
  <viewlet name="one"/>
 </order>
 <hidden manager="top" skinname="light">
  <viewlet name="two"/>
 </hidden>
</object>
"""

_EMPTY_EXPORT = """\
<?xml version="1.0"?>
<object />
"""

_CHILD_PURGE_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order manager="top" skinname="fancy" purge="True" />
 <hidden manager="top" skinname="light" purge="True" />
</object>
"""


_FRAGMENT1_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order manager="top" skinname="fancy">
  <viewlet name="three" insert-before="two"/>
 </order>
</object>
"""

_FRAGMENT2_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order manager="top" skinname="*">
  <viewlet name="four" insert-after="three"/>
 </order>
</object>
"""

_FRAGMENT3_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order manager="top" skinname="*">
  <viewlet name="three" insert-before="*"/>
  <viewlet name="four" insert-after="*"/>
 </order>
</object>
"""

_FRAGMENT4_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order manager="top" skinname="*">
  <viewlet name="three" remove="1"/>
 </order>
</object>
"""

_FRAGMENT5_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order manager='top' skinname="existing" based-on="fancy">
 </order>
 <order manager='top' skinname="new" based-on="fancy">
  <viewlet name="three" insert-before="two"/>
 </order>
 <order manager='top' skinname="wrongbase" based-on="invalid_base_id">
  <viewlet name="two"/>
 </order>
</object>"""

_FRAGMENT6_IMPORT = """\
<?xml version="1.0"?>
<object>
 <order manager="top" skinname="added" make_default="True">
  <viewlet name="one"/>
  <viewlet name="two"/>
  <viewlet name="three"/>
 </order>
 <hidden manager="top" skinname="added" make_default="True">
  <viewlet name="two"/>
 </hidden>
</object>
"""

_FRAGMENT7_IMPORT = """\
<?xml version="1.0"?>
<object>
  <hidden manager="top" skinname="*" >
    <viewlet name="two"/>
  </hidden>
</object>
"""


class ViewletSettingsStorageXMLAdapterTests(BodyAdapterTestCase):

    layer = PLONE_APP_VIEWLETMANAGER_INTEGRATION_TESTING

    def setUp(self):
        self.site = self.layer['portal']
        sm = self.site.getSiteManager()
        sm.registerUtility(ViewletSettingsStorage(), IViewletSettingsStorage)

        self._obj = getUtility(IViewletSettingsStorage)
        self._BODY = _VIEWLETS_XML

    def tearDown(self):
        sm = self.site.getSiteManager()
        sm.unregisterUtility(self._obj, IViewletSettingsStorage)

    def _getTargetClass(self):
        return ViewletSettingsStorageNodeAdapter

    def _populate(self, obj):
        obj.setOrder('top', 'fancy', ('two', 'three', 'one'))
        obj.setOrder('top', 'basic', ('one', ))
        obj.setHidden('top', 'light', ('two', ))

    def _verifyImport(self, obj):
        fancydict = {'top': ('two', 'three', 'one')}
        hiddendict = {'top': ('two', )}
        self.assertEqual(type(obj._order), PersistentDict)
        self.failUnless('fancy' in obj._order.keys())
        self.assertEqual(type(obj._order['fancy']), PersistentDict)
        self.assertEqual(dict(obj._order['fancy']), fancydict)
        self.assertEqual(type(obj._hidden), PersistentDict)
        self.failUnless('light' in obj._hidden.keys())
        self.assertEqual(type(obj._hidden['light']), PersistentDict)
        self.assertEqual(dict(obj._hidden['light']), hiddendict)


class _ViewletSettingsStorageSetup(BaseRegistryTests):

    layer = PLONE_APP_VIEWLETMANAGER_INTEGRATION_TESTING

    def setUp(self):
        BaseRegistryTests.setUp(self)
        self.app = self.layer['app']
        self.site = self.layer['portal']
        sm = self.site.getSiteManager()
        sm.registerUtility(ViewletSettingsStorage(), IViewletSettingsStorage)
        self.storage = getUtility(IViewletSettingsStorage)

    def afterSetUp(self):
        # avoid setting up an unrestricted user
        # which causes test isolation issues
        pass

    def tearDown(self):
        sm = self.site.getSiteManager()
        sm.unregisterUtility(self.storage, IViewletSettingsStorage)

    def _populateSite(self, order={}, hidden={}):
        for skinname in sorted(order):
            for manager in order[skinname].keys():
                self.storage.setOrder(manager, skinname,
                                      order[skinname][manager])

        for skinname in sorted(hidden):
            for manager in hidden[skinname].keys():
                self.storage.setHidden(manager, skinname,
                                       hidden[skinname][manager])


class ExportViewletSettingsStorageTests(_ViewletSettingsStorageSetup):

    def test_empty(self):
        context = DummyExportContext(self.site)
        exportViewletSettingsStorage(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'viewlets.xml')
        self._compareDOM(text, _EMPTY_EXPORT)
        self.assertEqual(content_type, 'text/xml')

    def test_normal(self):

        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN
        self._populateSite(order=_ORDER, hidden=_HIDDEN)

        context = DummyExportContext(self.site)
        exportViewletSettingsStorage(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'viewlets.xml')
        self._compareDOM(text, _VIEWLETS_XML)
        self.assertEqual(content_type, 'text/xml')


class ImportViewletSettingsStorageTests(_ViewletSettingsStorageSetup):

    _VIEWLETS_XML = _VIEWLETS_XML
    _EMPTY_EXPORT = _EMPTY_EXPORT
    _CHILD_PURGE_IMPORT = _CHILD_PURGE_IMPORT
    _FRAGMENT1_IMPORT = _FRAGMENT1_IMPORT
    _FRAGMENT2_IMPORT = _FRAGMENT2_IMPORT
    _FRAGMENT3_IMPORT = _FRAGMENT3_IMPORT
    _FRAGMENT4_IMPORT = _FRAGMENT4_IMPORT
    _FRAGMENT5_IMPORT = _FRAGMENT5_IMPORT
    _FRAGMENT6_IMPORT = _FRAGMENT6_IMPORT
    _FRAGMENT7_IMPORT = _FRAGMENT7_IMPORT

    def test_empty_default_purge(self):
        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN
        self._populateSite(order=_ORDER, hidden=_HIDDEN)

        site = self.site
        utility = self.storage
        self.assertEqual(len(utility.getOrder('top', 'fancy')), 3)
        self.assertEqual(len(utility.getOrder('top', 'basic')), 1)
        self.assertEqual(len(utility.getHidden('top', 'light')), 1)
        # Falls back to 'basic'
        self.assertEqual(len(utility.getOrder('top', 'undefined')), 1)

        context = DummyImportContext(site)
        context._files['viewlets.xml'] = self._EMPTY_EXPORT
        importViewletSettingsStorage(context)

        self.assertEqual(len(utility.getOrder('top', 'fancy')), 0)
        self.assertEqual(len(utility.getOrder('top', 'basic')), 0)
        self.assertEqual(len(utility.getHidden('top', 'light')), 0)
        # Falls back to 'basic'
        self.assertEqual(len(utility.getOrder('top', 'undefined')), 0)

    def test_empty_explicit_purge(self):
        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN
        self._populateSite(order=_ORDER, hidden=_HIDDEN)

        site = self.site
        utility = self.storage

        self.assertEqual(len(utility.getOrder('top', 'fancy')), 3)
        self.assertEqual(len(utility.getOrder('top', 'basic')), 1)
        self.assertEqual(len(utility.getHidden('top', 'light')), 1)
        # Falls back to 'basic'
        self.assertEqual(len(utility.getOrder('top', 'undefined')), 1)

        context = DummyImportContext(site, True)
        context._files['viewlets.xml'] = self._EMPTY_EXPORT
        importViewletSettingsStorage(context)

        self.assertEqual(len(utility.getOrder('top', 'fancy')), 0)
        self.assertEqual(len(utility.getOrder('top', 'basic')), 0)
        self.assertEqual(len(utility.getHidden('top', 'light')), 0)
        # Falls back to 'basic'
        self.assertEqual(len(utility.getOrder('top', 'undefined')), 0)

    def test_empty_skip_purge(self):
        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN
        self._populateSite(order=_ORDER, hidden=_HIDDEN)

        site = self.site
        utility = self.storage

        self.assertEqual(len(utility.getOrder('top', 'fancy')), 3)
        self.assertEqual(len(utility.getOrder('top', 'basic')), 1)
        self.assertEqual(len(utility.getHidden('top', 'light')), 1)
        # Falls back to 'basic'
        self.assertEqual(len(utility.getOrder('top', 'undefined')), 1)

        context = DummyImportContext(site, False)
        context._files['viewlets.xml'] = self._EMPTY_EXPORT
        importViewletSettingsStorage(context)

        self.assertEqual(len(utility.getOrder('top', 'fancy')), 3)
        self.assertEqual(len(utility.getOrder('top', 'basic')), 1)
        self.assertEqual(len(utility.getHidden('top', 'light')), 1)
        # Falls back to 'basic'
        self.assertEqual(len(utility.getOrder('top', 'undefined')), 1)

    def test_specific_child_purge(self):
        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN
        self._populateSite(order=_ORDER, hidden=_HIDDEN)

        site = self.site
        utility = self.storage

        self.assertEqual(len(utility.getOrder('top', 'fancy')), 3)
        self.assertEqual(len(utility.getOrder('top', 'basic')), 1)
        self.assertEqual(len(utility.getHidden('top', 'light')), 1)
        # Falls back to 'basic'
        self.assertEqual(len(utility.getOrder('top', 'undefined')), 1)

        context = DummyImportContext(site, False)
        context._files['viewlets.xml'] = self._CHILD_PURGE_IMPORT
        importViewletSettingsStorage(context)

        self.assertEqual(len(utility.getOrder('top', 'basic')), 1)
        self.assertEqual(len(utility.getHidden('top', 'light')), 0)
        # All of the following fall back to basic because there either
        # there are not anymore viewlet for the skinname or the skinname
        # is not found
        self.assertEqual(utility._order['fancy']['top'], ())
        self.assertEqual(len(utility.getOrder('top', 'fancy')), 1)
        self.assertNotIn('undefined', utility._order)
        self.assertEqual(len(utility.getOrder('top', 'undefined')), 1)

    def test_normal(self):
        site = self.site
        utility = self.storage
        self.assertEqual(len(utility._order.keys()), 0)
        self.assertEqual(len(utility._hidden.keys()), 0)

        context = DummyImportContext(site, False)
        context._files['viewlets.xml'] = self._VIEWLETS_XML
        importViewletSettingsStorage(context)

        self.assertEqual(utility.getOrder('top', 'basic'), ('one', ))
        # Falls back to 'basic'
        self.assertEqual(utility.getOrder('top', 'undefined (fallback)'),
                         ('one', ))
        self.assertEqual(utility.getOrder('top', 'fancy'),
                         ('two', 'three', 'one'))
        self.assertEqual(utility.getHidden('top', 'light'), ('two', ))

    def test_fragment_skip_purge(self):
        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN
        self._populateSite(order=_ORDER, hidden=_HIDDEN)

        site = self.site
        utility = self.storage
        self.assertEqual(len(utility._order.keys()), 2)
        self.assertEqual(len(utility._hidden.keys()), 1)

        self.assertEqual(utility.getOrder('top', 'fancy'),
                         ('two', 'three', 'one'))
        # Falls back to 'basic'
        self.assertEqual(utility.getOrder('top', 'undefined (fallback)'),
                         ('one', ))
        self.assertEqual(utility.getOrder('top', 'basic'), ('one', ))
        self.assertEqual(utility.getHidden('top', 'light'), ('two', ))

        context = DummyImportContext(site, False)
        context._files['viewlets.xml'] = self._FRAGMENT1_IMPORT
        importViewletSettingsStorage(context)

        self.assertEqual(utility.getOrder('top', 'basic'), ('one', ))
        self.assertEqual(utility.getOrder('top', 'fancy'),
                         ('three', 'two', 'one'))
        self.assertEqual(utility.getHidden('top', 'light'), ('two', ))

        context._files['viewlets.xml'] = self._FRAGMENT2_IMPORT
        importViewletSettingsStorage(context)

        # as the fragment FRAGMENT2_IMPORT sets the order for all skins
        # not only 'light', 'fancy' and 'basic' keys show up, also all other
        # skins registered on portal_skins. Hence adding them to the order
        skins = len(self.site.portal_skins.getSkinPaths())
        self.assertEqual(len(utility._order.keys()), 3 + skins)

        self.assertEqual(len(utility._hidden.keys()), 1)

        self.assertEqual(utility.getOrder('top', 'fancy'),
                         ('three', 'four', 'two', 'one'))
        self.assertEqual(utility.getOrder('top', 'basic'), ('one', 'four'))
        self.assertEqual(utility.getOrder('top', 'light'), ('four', ))
        self.assertEqual(utility.getHidden('top', 'light'), ('two', ))

        context._files['viewlets.xml'] = self._FRAGMENT1_IMPORT
        importViewletSettingsStorage(context)

        self.assertEqual(utility.getOrder('top', 'fancy'),
                         ('four', 'three', 'two', 'one'))

    def test_fragment3_skip_purge(self):
        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN
        self._populateSite(order=_ORDER, hidden=_HIDDEN)

        site = self.site
        utility = self.storage
        self.assertEqual(len(utility._order.keys()), 2)
        self.assertEqual(len(utility._hidden.keys()), 1)

        self.assertEqual(utility.getOrder('top', 'fancy'),
                         ('two', 'three', 'one'))
        # Falls back to 'basic'
        self.assertEqual(utility.getOrder('top', 'undefined (fallback)'),
                         ('one',))
        self.assertEqual(utility.getOrder('top', 'basic'), ('one', ))
        self.assertEqual(utility.getHidden('top', 'light'), ('two', ))

        context = DummyImportContext(site, False)
        context._files['viewlets.xml'] = self._FRAGMENT3_IMPORT
        importViewletSettingsStorage(context)
        self.assertEqual(utility.getOrder('top', 'basic'),
                         ('three', 'one', 'four'))
        self.assertEqual(utility.getOrder('top', 'fancy'),
                         ('three', 'two', 'one', 'four'))
        self.assertEqual(utility.getOrder('top', 'light'),
                         ('three', 'four'))
        self.assertEqual(utility.getHidden('top', 'light'), ('two', ))

    def test_fragment4_remove(self):
        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN
        self._populateSite(order=_ORDER, hidden=_HIDDEN)

        site = self.site
        utility = self.storage
        self.assertEqual(len(utility._order.keys()), 2)
        self.assertEqual(len(utility._hidden.keys()), 1)

        self.assertEqual(utility.getOrder('top', 'fancy'),
                         ('two', 'three', 'one'))
        # Falls back to 'basic'
        self.assertEqual(utility.getOrder('top', 'undefined (fallback)'),
                         ('one', ))
        self.assertEqual(utility.getOrder('top', 'basic'), ('one', ))
        self.assertEqual(utility.getHidden('top', 'light'), ('two', ))

        context = DummyImportContext(site, False)
        context._files['viewlets.xml'] = self._FRAGMENT4_IMPORT
        importViewletSettingsStorage(context)

        self.assertEqual(utility.getOrder('top', 'basic'), ('one', ))
        self.assertEqual(utility.getOrder('top', 'fancy'), ('two', 'one'))
        self.assertEqual(utility.getHidden('top', 'light'), ('two', ))

    def test_fragment5_based_on(self):
        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN
        self._populateSite(order=_ORDER, hidden=_HIDDEN)

        site = self.site
        utility = self.storage
        self.assertEqual(len(utility._order.keys()), 2)
        self.assertEqual(len(utility._hidden.keys()), 1)

        self.assertEqual(utility.getOrder('top', 'fancy'),
                         ('two', 'three', 'one'))
        # Falls back to 'basic'
        self.assertEqual(utility.getOrder('top', 'undefined (fallback)'),
                         ('one',))
        self.assertEqual(utility.getOrder('top', 'basic'), ('one', ))
        self.assertEqual(utility.getHidden('top', 'light'), ('two', ))

        context = DummyImportContext(site, False)
        context._files['viewlets.xml'] = self._FRAGMENT5_IMPORT
        importViewletSettingsStorage(context)

        self.assertEqual(len(utility._order.keys()), 5)

        self.assertEqual(utility.getOrder('top', 'fancy'),
                         ('two', 'three', 'one'))
        self.assertEqual(utility.getOrder('top', 'existing'),
                         ('two', 'three', 'one'))
        self.assertEqual(utility.getOrder('top', 'new'),
                         ('three', 'two', 'one'))
        self.assertEqual(utility.getOrder('top', 'wrongbase'), ('two', ))
        # Falls back to 'basic'
        self.assertEqual(utility.getOrder('top', 'undefined (fallback)'),
                         ('one',))
        self.assertEqual(utility.getOrder('top', 'basic'), ('one', ))
        self.assertEqual(utility.getHidden('top', 'light'), ('two', ))

    def test_fragment6_make_default(self):
        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN
        self._populateSite(order=_ORDER, hidden=_HIDDEN)

        site = self.site
        utility = self.storage
        self.assertEqual(len(utility._order.keys()), 2)
        self.assertEqual(len(utility._hidden.keys()), 1)

        self.assertEqual(utility.getOrder('top', 'fancy'),
                         ('two', 'three', 'one'))
        # Falls back to 'basic'
        self.assertEqual(utility.getOrder('top', 'undefined (fallback)'),
                         ('one', ))
        self.assertEqual(utility.getOrder('top', 'basic'), ('one', ))
        self.assertEqual(utility.getHidden('top', 'light'), ('two', ))

        context = DummyImportContext(site, False)
        context._files['viewlets.xml'] = self._FRAGMENT6_IMPORT
        importViewletSettingsStorage(context)

        self.assertEqual(utility.getOrder('top', 'undefined'),
                         ('one', 'two', 'three'))
        self.assertEqual(utility.getHidden('top', 'undefined'), ('two', ))

    def test_fragment7_make_default(self):
        _ORDER = COMMON_SETUP_ORDER
        _HIDDEN = COMMON_SETUP_HIDDEN

        self._populateSite(order=_ORDER, hidden=_HIDDEN)

        site = self.site
        utility = self.storage
        self.assertEqual(len(utility._order.keys()), 2)
        self.assertEqual(len(utility._hidden.keys()), 1)

        self.assertEqual(utility.getOrder('top', 'fancy'),
                         ('two', 'three', 'one'))
        # Falls back to 'basic'
        self.assertEqual(utility.getOrder('top', 'undefined (fallback)'),
                         ('one', ))
        self.assertEqual(utility.getOrder('top', 'basic'), ('one', ))
        self.assertEqual(utility.getHidden('top', 'light'), ('two', ))

        context = DummyImportContext(site, False)
        context._files['viewlets.xml'] = self._FRAGMENT7_IMPORT
        importViewletSettingsStorage(context)
        self.assertEqual(utility.getHidden('top', 'fancy'), ('two', ))
        self.assertEqual(utility.getHidden('top', 'basic'), ('two', ))

    def test_syntax_error_reporting(self):
        site = self.site
        context = DummyImportContext(site, False)
        context._files['viewlets.xml'] = """<?xml version="1.0"?>\n<"""
        self.assertRaises(ExpatError, importViewletSettingsStorage, context)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ViewletSettingsStorageXMLAdapterTests))
    suite.addTest(unittest.makeSuite(ExportViewletSettingsStorageTests))
    suite.addTest(unittest.makeSuite(ImportViewletSettingsStorageTests))
    return suite
