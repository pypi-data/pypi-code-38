from ftw.builder import Builder
from ftw.builder import create
from ftw.copymovepatches.tests import FunctionalTestCase


class TestDexterityCopyFlags(FunctionalTestCase):

    def test_copy_flags_are_set_on_copy(self):
        self.grant('Manager')
        container_ori = create(Builder('dx container'))
        clipboard = self.portal.manage_copyObjects([container_ori.id])
        self.portal.manage_pasteObjects(clipboard)
        container_copy = self.portal.get('copy_of_' + container_ori.id)
        self.assertEquals(1, getattr(container_copy, '_v_is_cp', None))
