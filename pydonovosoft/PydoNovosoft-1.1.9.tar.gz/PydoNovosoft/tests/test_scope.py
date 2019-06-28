from unittest import TestCase
import PydoNovosoft


class TestScope(TestCase):

    def test_CanProto(self):
        pro = PydoNovosoft.scope.MProfiler("", "", "")
        pro.get_messages()
        self.assertTrue(True)


