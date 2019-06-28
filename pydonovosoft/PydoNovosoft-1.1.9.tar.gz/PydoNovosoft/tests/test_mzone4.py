from unittest import TestCase
import PydoNovosoft


class TestMzone4(TestCase):

    def test_get_places(self):
        m = PydoNovosoft.scope.MZone4("", "")
        places = m.get_places(filter="401", ps=2).text
        self.assertTrue(places is not None)

    def test_mzone_delete_place(self):
        m = PydoNovosoft.scope.MZone4("", "")
        resp = m.delete_place("f55b545c-3322-4f3b-bb34-5731ad46ca89").status_code
        self.assertTrue(resp is 200)

    def test_mzone_poll(self):
        m = PydoNovosoft.scope.MZone4("", "")
        vehicles = ["", ""]
        resp = m.get_poll_vehicles(vehicles).status_code
        self.assertTrue(resp is 200)
