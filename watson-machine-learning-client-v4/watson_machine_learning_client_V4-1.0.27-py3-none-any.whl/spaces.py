################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from __future__ import print_function
import requests
from watson_machine_learning_client.utils import SPACES_DETAILS_TYPE, INSTANCE_DETAILS_TYPE, STR_TYPE, STR_TYPE_NAME, docstring_parameter, meta_props_str_conv, str_type_conv, get_file_from_cos
from watson_machine_learning_client.metanames import SpacesMetaNames
from watson_machine_learning_client.wml_resource import WMLResource


_DEFAULT_LIST_LENGTH = 50


class Spaces(WMLResource):
    """
    Store and manage your spaces.
    """
    ConfigurationMetaNames = SpacesMetaNames()
    """MetaNames for spaces creation."""

    def __init__(self, client):
        WMLResource.__init__(self, __name__, client)


        self._ICP = client.ICP

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def store(self, meta_props):
        """
                Create a space.

                **Parameters**

                .. important::
                   #. **meta_props**:  meta data of the space configuration. To see available meta names use:\n
                                    >>> client.spaces.ConfigurationMetaNames.get()

                      **type**: dict\n

                **Output**

                .. important::

                    **returns**: metadata of the stored space\n
                    **return type**: dict\n

                **Example**

                 >>> metadata = {
                 >>>  client.spaces.ConfigurationMetaNames.NAME: 'my_space',
                 >>>  client.spaces.ConfigurationMetaNames.DESCRIPTION: 'spaces',
                 >>> }
                 >>> spaces_details = client.spaces.store(training_definition_filepath, meta_props=metadata)
                 >>> spaces_href = client.spaces.get_href(spaces_details)
        """

        # quick support for COS credentials instead of local path
        # TODO add error handling and cleaning (remove the file)
        Spaces._validate_type(meta_props, u'meta_props', dict, True)
        space_meta = self.ConfigurationMetaNames._generate_resource_metadata(
            meta_props,
            with_validation=True,
            client=self._client

        )


        if not self._ICP:
            creation_response = requests.post(
                    self._wml_credentials['url'] + '/v4/spaces',
                    headers=self._client._get_headers(),
                    json=space_meta
            )
        else:
            creation_response = requests.post(
                self._wml_credentials['url'] + '/v4/spaces',
                headers=self._client._get_headers(),
                json=space_meta,
                verify=False
            )


        spaces_details = self._handle_response(201, u'creating new spaces', creation_response)

        return spaces_details

    @staticmethod
    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_href(spaces_details):
        """
            Get space_href from space details.

            **Parameters**

            .. important::
                #. **space_details**:  Metadata of the stored space\n
                   **type**: dict\n

            **Output**

            .. important::
                **returns**: space href\n
                **return type**: str

            **Example**

             >>> space_details = client.spaces.get_details(space_uid)
             >>> space_href = client.spaces.get_href(deployment)
        """

        Spaces._validate_type(spaces_details, u'spaces_details', object, True)
        Spaces._validate_type_of_details(spaces_details, SPACES_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(spaces_details, u'spaces_details',
                                                           [u'metadata', u'href'])

    @staticmethod
    def get_uid(spaces_details):
        """
            Get space_uid from space details.

            **Parameters**

            .. important::
                #. **space_details**:  Metadata of the stored space\n
                   **type**: dict\n

            **Output**

            .. important::
                **returns**: space UID\n
                **return type**: str

            **Example**

             >>> space_details = client.spaces.get_details(space_uid)
             >>> space_uid = client.spaces.get_uid(deployment)
        """

        Spaces._validate_type(spaces_details, u'spaces_details', object, True)
        Spaces._validate_type_of_details(spaces_details, SPACES_DETAILS_TYPE)

        return WMLResource._get_required_element_from_dict(spaces_details, u'spaces_details',
                                                           [u'metadata', u'guid'])

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def delete(self, space_uid):
        """
            Delete a stored space.

            **Parameters**

            .. important::
                #. **space_uid**:  space UID\n
                   **type**: str\n

            **Output**

            .. important::
                **returns**: status ("SUCCESS" or "FAILED")\n
                **return type**: str\n

            **Example**

             >>> client.spaces.delete(deployment_uid)
        """

        space_uid = str_type_conv(space_uid)
        Spaces._validate_type(space_uid, u'space_uid', STR_TYPE, True)

        space_endpoint = self._href_definitions.get_space_href(space_uid)
        if not self._ICP:
            response_delete = requests.delete(space_endpoint, headers=self._client._get_headers())
        else:
            response_delete = requests.delete(space_endpoint, headers=self._client._get_headers(), verify=False)

        return self._handle_response(204, u'space deletion', response_delete, False)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def get_details(self, space_uid=None, limit=None):
        """
           Get metadata of stored space(s). If space UID is not specified, it returns all the spaces metadata.

           **Parameters**

           .. important::
                #. **space_uid**: Space UID (optional)\n
                   **type**: str\n
                #. **limit**:  limit number of fetched records (optional)\n
                   **type**: int\n

           **Output**

           .. important::
                **returns**: metadata of stored space(s)\n
                **return type**: dict
                dict (if UID is not None) or {"resources": [dict]} (if UID is None)\n

           .. note::
                If UID is not specified, all spaces metadata is fetched\n

           **Example**

            >>> space_details = client.spaces.get_details(space_uid)
            >>> space_details = client.spaces.get_details()
        """

        space_uid = str_type_conv(space_uid)
        Spaces._validate_type(space_uid, u'space_uid', STR_TYPE, False)
        Spaces._validate_type(limit, u'limit', int, False)

        href = self._href_definitions.get_spaces_href()

        return self._get_artifact_details(href, space_uid, limit, 'spaces')

    def list(self, limit=None):
        """
           List stored spaces. If limit is set to None there will be only first 50 records shown.

           **Parameters**

           .. important::
                #. **limit**:  limit number of fetched records\n
                   **type**: int\n

           **Output**

           .. important::
                This method only prints the list of all spaces in a table format.\n
                **return type**: None\n

           **Example**

            >>> client.spaces.list()
        """

        space_resources = self.get_details(limit=limit)[u'resources']
        space_values = [(m[u'metadata'][u'guid'], m[u'entity'][u'name'], m[u'metadata'][u'created_at']) for m in space_resources]

        self._list(space_values, [u'GUID', u'NAME', u'CREATED'], limit, _DEFAULT_LIST_LENGTH)

    @docstring_parameter({'str_type': STR_TYPE_NAME})
    def update(self, space_uid, changes):
        """
                Updates existing space metadata.

                **Parameters**

                .. important::
                    #. **space_uid**:  UID of space which definition should be updated\n
                       **type**: str\n
                    #. **changes**:  elements which should be changed, where keys are ConfigurationMetaNames\n
                       **type**: dict\n

                **Output**

                .. important::
                    **returns**: metadata of updated space\n
                    **return type**: dict\n

                **Example**

                 >>> metadata = {
                 >>> client.spaces.ConfigurationMetaNames.NAME:"updated_space"
                 >>> }
                 >>> space_details = client.spaces.update(space_uid, changes=metadata)
        """

        space_uid = str_type_conv(space_uid)
        self._validate_type(space_uid, u'space_uid', STR_TYPE, True)
        self._validate_type(changes, u'changes', dict, True)
        meta_props_str_conv(changes)

        details = self.get_details(space_uid)

        patch_payload = self.ConfigurationMetaNames._generate_patch_payload(details['entity'], changes,
                                                                            with_validation=True)

        href = self._href_definitions.get_space_href(space_uid)
        if not self._ICP:
            response = requests.patch(href, json=patch_payload, headers=self._client._get_headers())
        else:
            response = requests.patch(href, json=patch_payload, headers=self._client._get_headers(), verify=False)
        updated_details = self._handle_response(200, u'spaces patch', response)

        return updated_details

