"""
Copyright 2019 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import itertools
import warnings
from typing import List, Optional

from cortex.camel import Document, CamelResource
from cortex.logger import getLogger
from cortex_common.types import ProfileAttributeType
from cortex_common.types import ProfileVersionSummary, HistoricProfile, Profile as ProfileType, \
    ProfileSchema as ProfileSchemaType, HistoricProfileAttribute

log = getLogger(__name__)

__all__ = [
    'Profile',
    'ProfileSchema'
]


class ProfileAttribute(Document):
    """
    Accessing an existent attribute within a Cortex Profile.
    """

    @staticmethod
    def get_attribute(profileId:str, attributeKey:str, profile_client) -> Optional['ProfileAttribute']:
        """
        Fetches a profile adhering to a specific schema ...
        """
        return ProfileAttribute({
            "attributeKey":attributeKey,
            "profileId": profileId,
        }, profile_client)

    def __init__(self, params:dict, profile_client):
        super().__init__(params, True)
        self._profile_client = profile_client

    def latest(self, schema_id:str) -> Optional[ProfileAttributeType]:
        """
        Returns the latest version of the profile against a specific schema ...
        :param schema_id:
        :return:
        """
        return self._profile_client.describeAttributeByKey(self.profileId, schema_id, self.attributeKey)

    def historic(self, schema_id:str) -> Optional[HistoricProfileAttribute]:
        """
        Gets the historic version of the profile
        :return:
        """
        return self._profile_client.describeHistoricAttributeByKey(self.profileId, schema_id, self.attributeKey)

    def __repr__(self):
        return "<Attribute: {}, ProfileId: {}>".format(self.attributeKey, self.profileId)


class Profile(Document):
    """
    Accessing an existent Cortex Profile.
    """

    @staticmethod
    def get_profile(profileId:str, profile_client) -> Optional['Profile']:
        """
        Fetches a profile adhering to a specific schema ...
        """
        return Profile({"profileId":profileId}, profile_client)

    def __init__(self, profile:ProfileType, profile_client):
        super().__init__(dict(profile), True)
        self._profile_client = profile_client

    def attribute(self, attributeKey:str) -> ProfileAttribute:
        """
        :param attributeKey:
        :return:
        """
        return ProfileAttribute.get_attribute(self.profileId, attributeKey, self._profile_client)

    def latest(self, schema_id:str) -> ProfileType:
        """
        Returns the latest version of the profile against a specific schema ...
        :param schema_id:
        :return:
        """
        return self._profile_client.describeProfile(self.profileId, schema_id)

    def historic(self, schema_id:str) -> HistoricProfile:
        """
        Gets the historic version of the profile
        :return:
        """
        return self._profile_client.describeHistoricProfile(self.profileId, schema_id)

    def delete(self, schema_id:str) -> bool:
        """
        Deletes the profile built against a specific schema.
        :return:
        """
        if schema_id is None:
            warnings.warn("SchemaId must be provided to delete profile against a specific schema.")
            return False
        return self._profile_client.deleteProfile(self.profileId, schema_id)

    def deleteAll(self) -> bool:
        """
        Deletes all instances of the profile against all schemas.
        :return:
        """
        return self._profile_client.deleteProfile(self.profileId)

    def allVersions(self) -> List[ProfileVersionSummary]:
        """
        Lists the different versions of the profile ...
        If a schema name is specified, only versions of the profile against that schema are returned
        :return:
        """
        return list(itertools.chain(*[
            self._profile_client.listVersions(self.profileId, schemaId)
            for schemaId in self._profile_client.schemasForProfile(self.profileId)
        ]))

    def versions(self, schema_name:str) -> List[ProfileVersionSummary]:
        """
        Lists the different versions of the profile against a specific schema.
        :return:
        """
        if schema_name is None:
            warnings.warn("schema_name must be provided. Returning no versions ... ")
            return []
        return self._profile_client.listVersions(self.profileId, schema_name)

    def exists(self, schemaId:Optional[str]=None) -> bool:
        if schemaId is None:
            return len(self.allVersions()) > 0
        else:
            return len(self.versions(schemaId)) > 0

    def __repr__(self):
        return "<Profile: {}>".format(self.profileId)


class ProfileSchema(CamelResource):
    """
    Accessing an existent Cortex ProfileSchema.
    """

    @staticmethod
    def get_schema(schema_name_or_id:str, profile_client) -> 'ProfileSchema':
        """
        Fetches the requested schema by id ...
        """
        return ProfileSchema(schema_name_or_id, profile_client)

    def __init__(self, schema_name_or_id:str, profile_client):
        self._schema_requested = schema_name_or_id
        self._profile_client = profile_client
        self._refresh_schema()
        super().__init__(self._schema.to_dict_with_internals() if self._exists else {}, True)

    def _refresh_schema(self):
        """
        Refreshes the internal state of the schema ...
        This is only really needed prior to deleting ...
        Or ... prior to getting the latest versions of an untagged schema
        :return:
        """
        self._schema = self._profile_client.describeSchema(self._schema_requested)
        self._exists = self._schema is not None

    def delete(self, all:bool=False) -> bool:
        """
        Deletes the schema ...
        :param all: This flag is needed because the default behavior of getting a schema without specifying a version
        resolves to the latest schema ... thus if someone wants to delete all versions of the schema, not just the
        latest, they must explicitly do so.
        :param consider_dne_successful: This determines how to treat the deletion of schemas that don't exist prior to the delete call ...
        :return:
        """
        # Its possible we make the client ... and then hold onto it for a while ... and a schema gets created post
        # client initialization ...
        self._refresh_schema()
        if(all):
            return self._profile_client.deleteSchema(self.name if self.name else self._schema_requested)
        else:
            return self._profile_client.deleteSchema(self.id if self.id else self._schema_requested)

    def latest(self) -> Optional[ProfileSchemaType]:
        """
        Returns the id of the latest version of the specified schema.
        :return:
        """
        self._refresh_schema()
        return self._schema

    def exists(self) -> bool:
        """
        Returns whether or not the schema requested actually exists ...
        :return:
        """
        self._refresh_schema()
        return self._exists

    def __repr__(self):
        return repr(self._schema) if self._exists else repr(None)
