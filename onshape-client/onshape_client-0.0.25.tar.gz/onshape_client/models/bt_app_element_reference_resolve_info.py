# coding: utf-8

"""
    Onshape REST API

    The Onshape REST API consumed by all clients.  # noqa: E501

    OpenAPI spec version: 1.97
    Contact: api-support@onshape.zendesk.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class BTAppElementReferenceResolveInfo(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'target_element_microversion_id': 'str',
        'resolved_element_microversion_id': 'str',
        'revision': 'str',
        'part_number': 'str',
        'change_id': 'str',
        'target_document_id': 'str',
        'target_element_id': 'str',
        'target_configuration': 'str',
        'sketch_ids': 'list[str]',
        'id_tag': 'str',
        'target_version_id': 'str',
        'is_sketch_only': 'bool',
        'id_tag_is_valid': 'bool',
        'reference_id': 'str',
        'target_document_microversion_id': 'str',
        'is_configurable': 'bool',
        'resolved_document_microversion_id': 'str',
        'is_flattened_part': 'bool',
        'track_new_versions': 'bool',
        'error_code': 'int',
        'error_value': 'str',
        'error_description': 'str'
    }

    attribute_map = {
        'target_element_microversion_id': 'targetElementMicroversionId',
        'resolved_element_microversion_id': 'resolvedElementMicroversionId',
        'revision': 'revision',
        'part_number': 'partNumber',
        'change_id': 'changeId',
        'target_document_id': 'targetDocumentId',
        'target_element_id': 'targetElementId',
        'target_configuration': 'targetConfiguration',
        'sketch_ids': 'sketchIds',
        'id_tag': 'idTag',
        'target_version_id': 'targetVersionId',
        'is_sketch_only': 'isSketchOnly',
        'id_tag_is_valid': 'idTagIsValid',
        'reference_id': 'referenceId',
        'target_document_microversion_id': 'targetDocumentMicroversionId',
        'is_configurable': 'isConfigurable',
        'resolved_document_microversion_id': 'resolvedDocumentMicroversionId',
        'is_flattened_part': 'isFlattenedPart',
        'track_new_versions': 'trackNewVersions',
        'error_code': 'errorCode',
        'error_value': 'errorValue',
        'error_description': 'errorDescription'
    }

    def __init__(self, target_element_microversion_id=None, resolved_element_microversion_id=None, revision=None, part_number=None, change_id=None, target_document_id=None, target_element_id=None, target_configuration=None, sketch_ids=None, id_tag=None, target_version_id=None, is_sketch_only=None, id_tag_is_valid=None, reference_id=None, target_document_microversion_id=None, is_configurable=None, resolved_document_microversion_id=None, is_flattened_part=None, track_new_versions=None, error_code=None, error_value=None, error_description=None):  # noqa: E501
        """BTAppElementReferenceResolveInfo - a model defined in OpenAPI"""  # noqa: E501

        self._target_element_microversion_id = None
        self._resolved_element_microversion_id = None
        self._revision = None
        self._part_number = None
        self._change_id = None
        self._target_document_id = None
        self._target_element_id = None
        self._target_configuration = None
        self._sketch_ids = None
        self._id_tag = None
        self._target_version_id = None
        self._is_sketch_only = None
        self._id_tag_is_valid = None
        self._reference_id = None
        self._target_document_microversion_id = None
        self._is_configurable = None
        self._resolved_document_microversion_id = None
        self._is_flattened_part = None
        self._track_new_versions = None
        self._error_code = None
        self._error_value = None
        self._error_description = None
        self.discriminator = None

        if target_element_microversion_id is not None:
            self.target_element_microversion_id = target_element_microversion_id
        if resolved_element_microversion_id is not None:
            self.resolved_element_microversion_id = resolved_element_microversion_id
        if revision is not None:
            self.revision = revision
        if part_number is not None:
            self.part_number = part_number
        if change_id is not None:
            self.change_id = change_id
        if target_document_id is not None:
            self.target_document_id = target_document_id
        if target_element_id is not None:
            self.target_element_id = target_element_id
        if target_configuration is not None:
            self.target_configuration = target_configuration
        if sketch_ids is not None:
            self.sketch_ids = sketch_ids
        if id_tag is not None:
            self.id_tag = id_tag
        if target_version_id is not None:
            self.target_version_id = target_version_id
        if is_sketch_only is not None:
            self.is_sketch_only = is_sketch_only
        if id_tag_is_valid is not None:
            self.id_tag_is_valid = id_tag_is_valid
        if reference_id is not None:
            self.reference_id = reference_id
        if target_document_microversion_id is not None:
            self.target_document_microversion_id = target_document_microversion_id
        if is_configurable is not None:
            self.is_configurable = is_configurable
        if resolved_document_microversion_id is not None:
            self.resolved_document_microversion_id = resolved_document_microversion_id
        if is_flattened_part is not None:
            self.is_flattened_part = is_flattened_part
        if track_new_versions is not None:
            self.track_new_versions = track_new_versions
        if error_code is not None:
            self.error_code = error_code
        if error_value is not None:
            self.error_value = error_value
        if error_description is not None:
            self.error_description = error_description

    @property
    def target_element_microversion_id(self):
        """Gets the target_element_microversion_id of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The target_element_microversion_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._target_element_microversion_id

    @target_element_microversion_id.setter
    def target_element_microversion_id(self, target_element_microversion_id):
        """Sets the target_element_microversion_id of this BTAppElementReferenceResolveInfo.


        :param target_element_microversion_id: The target_element_microversion_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._target_element_microversion_id = target_element_microversion_id

    @property
    def resolved_element_microversion_id(self):
        """Gets the resolved_element_microversion_id of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The resolved_element_microversion_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._resolved_element_microversion_id

    @resolved_element_microversion_id.setter
    def resolved_element_microversion_id(self, resolved_element_microversion_id):
        """Sets the resolved_element_microversion_id of this BTAppElementReferenceResolveInfo.


        :param resolved_element_microversion_id: The resolved_element_microversion_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._resolved_element_microversion_id = resolved_element_microversion_id

    @property
    def revision(self):
        """Gets the revision of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The revision of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._revision

    @revision.setter
    def revision(self, revision):
        """Sets the revision of this BTAppElementReferenceResolveInfo.


        :param revision: The revision of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._revision = revision

    @property
    def part_number(self):
        """Gets the part_number of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The part_number of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._part_number

    @part_number.setter
    def part_number(self, part_number):
        """Sets the part_number of this BTAppElementReferenceResolveInfo.


        :param part_number: The part_number of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._part_number = part_number

    @property
    def change_id(self):
        """Gets the change_id of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The change_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._change_id

    @change_id.setter
    def change_id(self, change_id):
        """Sets the change_id of this BTAppElementReferenceResolveInfo.


        :param change_id: The change_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._change_id = change_id

    @property
    def target_document_id(self):
        """Gets the target_document_id of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The target_document_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._target_document_id

    @target_document_id.setter
    def target_document_id(self, target_document_id):
        """Sets the target_document_id of this BTAppElementReferenceResolveInfo.


        :param target_document_id: The target_document_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._target_document_id = target_document_id

    @property
    def target_element_id(self):
        """Gets the target_element_id of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The target_element_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._target_element_id

    @target_element_id.setter
    def target_element_id(self, target_element_id):
        """Sets the target_element_id of this BTAppElementReferenceResolveInfo.


        :param target_element_id: The target_element_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._target_element_id = target_element_id

    @property
    def target_configuration(self):
        """Gets the target_configuration of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The target_configuration of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._target_configuration

    @target_configuration.setter
    def target_configuration(self, target_configuration):
        """Sets the target_configuration of this BTAppElementReferenceResolveInfo.


        :param target_configuration: The target_configuration of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._target_configuration = target_configuration

    @property
    def sketch_ids(self):
        """Gets the sketch_ids of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The sketch_ids of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: list[str]
        """
        return self._sketch_ids

    @sketch_ids.setter
    def sketch_ids(self, sketch_ids):
        """Sets the sketch_ids of this BTAppElementReferenceResolveInfo.


        :param sketch_ids: The sketch_ids of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: list[str]
        """

        self._sketch_ids = sketch_ids

    @property
    def id_tag(self):
        """Gets the id_tag of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The id_tag of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._id_tag

    @id_tag.setter
    def id_tag(self, id_tag):
        """Sets the id_tag of this BTAppElementReferenceResolveInfo.


        :param id_tag: The id_tag of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._id_tag = id_tag

    @property
    def target_version_id(self):
        """Gets the target_version_id of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The target_version_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._target_version_id

    @target_version_id.setter
    def target_version_id(self, target_version_id):
        """Sets the target_version_id of this BTAppElementReferenceResolveInfo.


        :param target_version_id: The target_version_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._target_version_id = target_version_id

    @property
    def is_sketch_only(self):
        """Gets the is_sketch_only of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The is_sketch_only of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: bool
        """
        return self._is_sketch_only

    @is_sketch_only.setter
    def is_sketch_only(self, is_sketch_only):
        """Sets the is_sketch_only of this BTAppElementReferenceResolveInfo.


        :param is_sketch_only: The is_sketch_only of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: bool
        """

        self._is_sketch_only = is_sketch_only

    @property
    def id_tag_is_valid(self):
        """Gets the id_tag_is_valid of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The id_tag_is_valid of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: bool
        """
        return self._id_tag_is_valid

    @id_tag_is_valid.setter
    def id_tag_is_valid(self, id_tag_is_valid):
        """Sets the id_tag_is_valid of this BTAppElementReferenceResolveInfo.


        :param id_tag_is_valid: The id_tag_is_valid of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: bool
        """

        self._id_tag_is_valid = id_tag_is_valid

    @property
    def reference_id(self):
        """Gets the reference_id of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The reference_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._reference_id

    @reference_id.setter
    def reference_id(self, reference_id):
        """Sets the reference_id of this BTAppElementReferenceResolveInfo.


        :param reference_id: The reference_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._reference_id = reference_id

    @property
    def target_document_microversion_id(self):
        """Gets the target_document_microversion_id of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The target_document_microversion_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._target_document_microversion_id

    @target_document_microversion_id.setter
    def target_document_microversion_id(self, target_document_microversion_id):
        """Sets the target_document_microversion_id of this BTAppElementReferenceResolveInfo.


        :param target_document_microversion_id: The target_document_microversion_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._target_document_microversion_id = target_document_microversion_id

    @property
    def is_configurable(self):
        """Gets the is_configurable of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The is_configurable of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: bool
        """
        return self._is_configurable

    @is_configurable.setter
    def is_configurable(self, is_configurable):
        """Sets the is_configurable of this BTAppElementReferenceResolveInfo.


        :param is_configurable: The is_configurable of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: bool
        """

        self._is_configurable = is_configurable

    @property
    def resolved_document_microversion_id(self):
        """Gets the resolved_document_microversion_id of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The resolved_document_microversion_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._resolved_document_microversion_id

    @resolved_document_microversion_id.setter
    def resolved_document_microversion_id(self, resolved_document_microversion_id):
        """Sets the resolved_document_microversion_id of this BTAppElementReferenceResolveInfo.


        :param resolved_document_microversion_id: The resolved_document_microversion_id of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._resolved_document_microversion_id = resolved_document_microversion_id

    @property
    def is_flattened_part(self):
        """Gets the is_flattened_part of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The is_flattened_part of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: bool
        """
        return self._is_flattened_part

    @is_flattened_part.setter
    def is_flattened_part(self, is_flattened_part):
        """Sets the is_flattened_part of this BTAppElementReferenceResolveInfo.


        :param is_flattened_part: The is_flattened_part of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: bool
        """

        self._is_flattened_part = is_flattened_part

    @property
    def track_new_versions(self):
        """Gets the track_new_versions of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The track_new_versions of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: bool
        """
        return self._track_new_versions

    @track_new_versions.setter
    def track_new_versions(self, track_new_versions):
        """Sets the track_new_versions of this BTAppElementReferenceResolveInfo.


        :param track_new_versions: The track_new_versions of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: bool
        """

        self._track_new_versions = track_new_versions

    @property
    def error_code(self):
        """Gets the error_code of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The error_code of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: int
        """
        return self._error_code

    @error_code.setter
    def error_code(self, error_code):
        """Sets the error_code of this BTAppElementReferenceResolveInfo.


        :param error_code: The error_code of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: int
        """

        self._error_code = error_code

    @property
    def error_value(self):
        """Gets the error_value of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The error_value of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._error_value

    @error_value.setter
    def error_value(self, error_value):
        """Sets the error_value of this BTAppElementReferenceResolveInfo.


        :param error_value: The error_value of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """
        allowed_values = ["OK", "TRANSACTION_CONFLICT", "NOT_FOUND", "INCONSISTENT_CHANGES"]  # noqa: E501
        if error_value not in allowed_values:
            raise ValueError(
                "Invalid value for `error_value` ({0}), must be one of {1}"  # noqa: E501
                .format(error_value, allowed_values)
            )

        self._error_value = error_value

    @property
    def error_description(self):
        """Gets the error_description of this BTAppElementReferenceResolveInfo.  # noqa: E501


        :return: The error_description of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :rtype: str
        """
        return self._error_description

    @error_description.setter
    def error_description(self, error_description):
        """Sets the error_description of this BTAppElementReferenceResolveInfo.


        :param error_description: The error_description of this BTAppElementReferenceResolveInfo.  # noqa: E501
        :type: str
        """

        self._error_description = error_description

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, BTAppElementReferenceResolveInfo):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
