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


class BTWorkflowableTestObjectInfo(object):
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
        'info': 'dict(str, str)',
        'properties': 'list[BTWorkflowPropertyInfo]',
        'description': 'str',
        'workflow': 'BTWorkflowSnapshotInfo',
        'company_id': 'str',
        'is_obsoletion': 'bool',
        'document_id': 'str',
        'workflow_id': 'BTPublishedWorkflowId',
        'name_as_property': 'str',
        'description_as_property': 'str',
        'name': 'str',
        'id': 'str',
        'href': 'str',
        'view_ref': 'str'
    }

    attribute_map = {
        'info': 'info',
        'properties': 'properties',
        'description': 'description',
        'workflow': 'workflow',
        'company_id': 'companyId',
        'is_obsoletion': 'isObsoletion',
        'document_id': 'documentId',
        'workflow_id': 'workflowId',
        'name_as_property': 'nameAsProperty',
        'description_as_property': 'descriptionAsProperty',
        'name': 'name',
        'id': 'id',
        'href': 'href',
        'view_ref': 'viewRef'
    }

    def __init__(self, info=None, properties=None, description=None, workflow=None, company_id=None, is_obsoletion=None, document_id=None, workflow_id=None, name_as_property=None, description_as_property=None, name=None, id=None, href=None, view_ref=None):  # noqa: E501
        """BTWorkflowableTestObjectInfo - a model defined in OpenAPI"""  # noqa: E501

        self._info = None
        self._properties = None
        self._description = None
        self._workflow = None
        self._company_id = None
        self._is_obsoletion = None
        self._document_id = None
        self._workflow_id = None
        self._name_as_property = None
        self._description_as_property = None
        self._name = None
        self._id = None
        self._href = None
        self._view_ref = None
        self.discriminator = None

        if info is not None:
            self.info = info
        if properties is not None:
            self.properties = properties
        if description is not None:
            self.description = description
        if workflow is not None:
            self.workflow = workflow
        if company_id is not None:
            self.company_id = company_id
        if is_obsoletion is not None:
            self.is_obsoletion = is_obsoletion
        if document_id is not None:
            self.document_id = document_id
        if workflow_id is not None:
            self.workflow_id = workflow_id
        if name_as_property is not None:
            self.name_as_property = name_as_property
        if description_as_property is not None:
            self.description_as_property = description_as_property
        if name is not None:
            self.name = name
        if id is not None:
            self.id = id
        if href is not None:
            self.href = href
        if view_ref is not None:
            self.view_ref = view_ref

    @property
    def info(self):
        """Gets the info of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The info of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._info

    @info.setter
    def info(self, info):
        """Sets the info of this BTWorkflowableTestObjectInfo.


        :param info: The info of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: dict(str, str)
        """

        self._info = info

    @property
    def properties(self):
        """Gets the properties of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The properties of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: list[BTWorkflowPropertyInfo]
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Sets the properties of this BTWorkflowableTestObjectInfo.


        :param properties: The properties of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: list[BTWorkflowPropertyInfo]
        """

        self._properties = properties

    @property
    def description(self):
        """Gets the description of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The description of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this BTWorkflowableTestObjectInfo.


        :param description: The description of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def workflow(self):
        """Gets the workflow of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The workflow of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: BTWorkflowSnapshotInfo
        """
        return self._workflow

    @workflow.setter
    def workflow(self, workflow):
        """Sets the workflow of this BTWorkflowableTestObjectInfo.


        :param workflow: The workflow of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: BTWorkflowSnapshotInfo
        """

        self._workflow = workflow

    @property
    def company_id(self):
        """Gets the company_id of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The company_id of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: str
        """
        return self._company_id

    @company_id.setter
    def company_id(self, company_id):
        """Sets the company_id of this BTWorkflowableTestObjectInfo.


        :param company_id: The company_id of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: str
        """

        self._company_id = company_id

    @property
    def is_obsoletion(self):
        """Gets the is_obsoletion of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The is_obsoletion of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: bool
        """
        return self._is_obsoletion

    @is_obsoletion.setter
    def is_obsoletion(self, is_obsoletion):
        """Sets the is_obsoletion of this BTWorkflowableTestObjectInfo.


        :param is_obsoletion: The is_obsoletion of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: bool
        """

        self._is_obsoletion = is_obsoletion

    @property
    def document_id(self):
        """Gets the document_id of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The document_id of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: str
        """
        return self._document_id

    @document_id.setter
    def document_id(self, document_id):
        """Sets the document_id of this BTWorkflowableTestObjectInfo.


        :param document_id: The document_id of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: str
        """

        self._document_id = document_id

    @property
    def workflow_id(self):
        """Gets the workflow_id of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The workflow_id of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: BTPublishedWorkflowId
        """
        return self._workflow_id

    @workflow_id.setter
    def workflow_id(self, workflow_id):
        """Sets the workflow_id of this BTWorkflowableTestObjectInfo.


        :param workflow_id: The workflow_id of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: BTPublishedWorkflowId
        """

        self._workflow_id = workflow_id

    @property
    def name_as_property(self):
        """Gets the name_as_property of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The name_as_property of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: str
        """
        return self._name_as_property

    @name_as_property.setter
    def name_as_property(self, name_as_property):
        """Sets the name_as_property of this BTWorkflowableTestObjectInfo.


        :param name_as_property: The name_as_property of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: str
        """

        self._name_as_property = name_as_property

    @property
    def description_as_property(self):
        """Gets the description_as_property of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The description_as_property of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: str
        """
        return self._description_as_property

    @description_as_property.setter
    def description_as_property(self, description_as_property):
        """Sets the description_as_property of this BTWorkflowableTestObjectInfo.


        :param description_as_property: The description_as_property of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: str
        """

        self._description_as_property = description_as_property

    @property
    def name(self):
        """Gets the name of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The name of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this BTWorkflowableTestObjectInfo.


        :param name: The name of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def id(self):
        """Gets the id of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The id of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this BTWorkflowableTestObjectInfo.


        :param id: The id of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def href(self):
        """Gets the href of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The href of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this BTWorkflowableTestObjectInfo.


        :param href: The href of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: str
        """

        self._href = href

    @property
    def view_ref(self):
        """Gets the view_ref of this BTWorkflowableTestObjectInfo.  # noqa: E501


        :return: The view_ref of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :rtype: str
        """
        return self._view_ref

    @view_ref.setter
    def view_ref(self, view_ref):
        """Sets the view_ref of this BTWorkflowableTestObjectInfo.


        :param view_ref: The view_ref of this BTWorkflowableTestObjectInfo.  # noqa: E501
        :type: str
        """

        self._view_ref = view_ref

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
        if not isinstance(other, BTWorkflowableTestObjectInfo):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
