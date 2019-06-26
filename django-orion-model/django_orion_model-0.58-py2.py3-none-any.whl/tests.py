from django.test import TestCase
from unittest.mock import Mock, patch


from waste_collection.models import KPI
from orion_manager.models import OrionEntity


class TestOrionEntity(TestCase):

    @patch.object(OrionEntity._orion, "get", Mock())
    def test_from_db(self):
        OrionEntity.objects.get(pk="")
        OrionEntity.from_db(None, ["id"], ["WE1212"])
        OrionEntity._orion.get.assert_called_with(element_id="WE1212")

    @patch.object(OrionEntity._orion, "patch", Mock())
    def test_save(self):
        orion_entity = OrionEntity()
        orion_entity.orion_id = "WE1212"
        orion_entity.type = "sensor"
        orion_entity.save()
        orion_entity._orion.patch.assert_not_called()
        orion_entity.data = {
            "id": "WE1212",
            "type": "Fake",
            "temperature": {
                "value": 23,
                "type": "Float"
            },
            "pressure": {
                "value": 720,
                "type": "Integer"
            }}
        orion_entity.updated = "temperature, pressure"

        orion_entity.save()
        orion_entity._orion.patch.assert_called_with(element_id="WE1212", **{
            "temperature": {
                "value": 23,
                "type": "Float"
            },
            "pressure": {
                "value": 720,
                "type": "Integer"
            }}
            )

    def test_global_property(self):

        orion_entity2 = KPI()
        orion_entity3 = KPI()
        orion_entity2.name = "Babar"
        self.assertNotEqual(orion_entity2.name, orion_entity3.name, "Global property error")

    def test_save_to_orion(self):
        self.fail()

    def test_update_from_orion(self):
        self.fail()

    def test_Now(self):
        self.fail()
