import json
import unittest

from cortex import Cortex
from cortex_client.profilesclient import ProfilesClient
from cortex_common.types import EntityEvent, ProfileAttributeType
from cortex_common.types import ProfileValueTypeSummary
from cortex_common.types.attributes import load_profile_attribute_from_dict
from cortex_common.utils import dicts_to_classes, dict_to_attr_class
from mocket import mocketize
from mocket.mockhttp import Entry

from .fixtures import john_doe_token, build_mock_url, mock_api_endpoint, register_entry_from_path, register_entry


class TestAgent(unittest.TestCase):

    def setUp(self):

        # Initiallize Clients ...
        self.cortex = Cortex.client(api_endpoint=mock_api_endpoint(), token=john_doe_token())
        self.builder = self.cortex.builder()
        self.profiles_client = ProfilesClient(mock_api_endpoint(), "3", john_doe_token())

        self.profile_id = "P1"
        self.schema_name = "cortex/TestSchema"
        self.schema_version = 3
        self.schema_id = "{}:{}".format(self.schema_name, self.schema_version)

        self.valid_string_event = EntityEvent(
            event="profile.name",
            entityId=self.profile_id,
            entityType="cortex/profile-of-end-user",
            properties={
                "value": "Jack"
            }
        )
        # Registering List Schemas ...
        register_entry_from_path(
            Entry.GET,
            build_mock_url(ProfilesClient.URIs["schemas"], version=3),
            "./test/data/apis/profiles/schemas/list_schemas.json"
        )

        # Registering Get For Valid Schemas ... ...
        with open("./test/data/apis/profiles/schemas/list_schemas.json") as fh:
            schemas = json.load(fh).get("schemas", [])
            for s in schemas:
                schemaId = "{}:{}".format(s.get("name"), s.get("_version"))
                register_entry(
                    Entry.GET,
                    build_mock_url(ProfilesClient.URIs["schema"].format(schemaId=schemaId), version=3),
                    s
                )

        # Registering Get for Latest Profile ..
        register_entry_from_path(
            Entry.GET,
            build_mock_url(ProfilesClient._build_get_profile_uri(self.profile_id, self.schema_id, historic=False),
                           version=3),
            "./test/data/apis/profiles/get_latest_profile.json"
        )

        # Registering Get for Historic Profile ..
        register_entry_from_path(
            Entry.GET,
            build_mock_url(ProfilesClient._build_get_profile_uri(self.profile_id, self.schema_id, historic=True),
                           version=3),
            "./test/data/apis/profiles/get_historic_profile.json"
        )

    @mocketize
    def test_get_schema_with_client(self):
        """
        Tests getting schemas from a mocked endpoint ...
        :return:
        """
        schemas = self.profiles_client.listSchemas()
        self.assertEqual(len(schemas), 1)
        self.assertEqual(schemas[0].name, self.schema_name)

    @mocketize
    def test_get_schema_with_builder_pattern(self):
        schema = self.cortex.profile_schema(self.schema_id)
        self.assertIsNotNone(schema)
        self.assertEqual(schema.name, self.schema_name)
        self.assertEqual(schema.version, self.schema_version)

    @mocketize
    def test_get_latest_profile_with_client(self):
        """
        Tests getting schemas from a mocked endpoint ...
        :return:
        """
        profile = self.profiles_client.describeProfile(self.profile_id, self.schema_id)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.profileId, self.profile_id)

    @mocketize
    def test_get_latest_profile_with_builder_pattern(self):
        profile = self.cortex.profile(self.profile_id).latest(self.schema_id)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.profileId, self.profile_id)

    @mocketize
    def test_get_historic_profile_with_client(self):
        """
        Tests getting schemas from a mocked endpoint ...
        :return:
        """
        profile = self.profiles_client.describeHistoricProfile(self.profile_id, self.schema_id)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.profileId, self.profile_id)

    @mocketize
    def test_get_historic_profile_with_builder_pattern(self):
        profile = self.cortex.profile(self.profile_id).historic(self.schema_id)
        self.assertIsNotNone(profile)
        self.assertEqual(profile.profileId, self.profile_id)

    def test_parsing_attributes(self):
        attrs = [
            {
                "attributeKey": "account.properties",
                "id": "68cd1c62-8a71-4203-a1a3-a1fed40a3171",
                "profileId": self.profile_id,
                "profileSchema": "cortex/TestSchema:2",
                "classification": "declared",
                "attributeValue": {
                    "context": "cortex/attribute-value-entity",
                    "version": "0.0.1",
                    "value": {
                        "event": "age",
                        "entityId": "abc",
                        "entityType": "cortex/blah",
                        "properties": {
                            "p1": "some-string",
                            "p2": 123
                        }
                    }
                },
                "createdAt": "2019-03-22T22:06:17.058Z",
                "version": "0.0.1",
                "seq": 21,
                "context": "cortex/attributes-declared"
            }
        ]
        self.assertEqual(
            dicts_to_classes(attrs, ProfileAttributeType, dict_constructor=load_profile_attribute_from_dict)[0].attributeKey,
            attrs[0].get("attributeKey")
        )

    def test_parsing_events(self):
        event = self.valid_string_event
        self.assertEqual(self.valid_string_event.event, dict_to_attr_class(event, EntityEvent).event)

    def test_parsing_types(self):
        str_type = ProfileValueTypeSummary(**{
            "outerType": "str",
            "innerTypes": []
        })
        map_type = ProfileValueTypeSummary(**{
            "outerType": "map",
            "innerTypes": [
                {
                    "outerType": "str",
                    "innerTypes": []
                },
                {
                    "outerType": "int",
                    "innerTypes": []
                }
            ]
        })
        nested_map_type = ProfileValueTypeSummary(**{
            "outerType": "map",
            "innerTypes": [
                {
                    "outerType": "str",
                    "innerTypes": []
                },
                {
                    "outerType": "list",
                    "innerTypes": [
                        {
                            "outerType": "int",
                            "innerTypes": []
                        }
                    ]
                }
            ]
        })

        self.assertEqual(str_type.outerType, "str")

        self.assertEqual(map_type.outerType, "map")
        self.assertEqual(map_type.innerTypes[0].outerType, "str")
        self.assertEqual(map_type.innerTypes[1].outerType, "int")

        self.assertEqual(nested_map_type.outerType, "map")
        self.assertEqual(nested_map_type.innerTypes[0].outerType, "str")
        self.assertEqual(nested_map_type.innerTypes[1].outerType, "list")
        self.assertEqual(nested_map_type.innerTypes[1].innerTypes[0].outerType, "int")
