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


class BTExportTessellatedFacesBody(object):
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
        'id': 'str',
        'appearance': 'BTGraphicsAppearance',
        'faces': 'list[BTExportTessellatedFacesFace]',
        'body_type': 'str',
        'facet_points': 'list[BTVector3d]',
        'type_id': 'int',
        'connection_source': 'BTConnection',
        'export_type_name': 'str',
        'unknown_class': 'bool'
    }

    attribute_map = {
        'id': 'id',
        'appearance': 'appearance',
        'faces': 'faces',
        'body_type': 'bodyType',
        'facet_points': 'facetPoints',
        'type_id': 'typeId',
        'connection_source': 'connectionSource',
        'export_type_name': 'exportTypeName',
        'unknown_class': 'unknownClass'
    }

    def __init__(self, id=None, appearance=None, faces=None, body_type=None, facet_points=None, type_id=None, connection_source=None, export_type_name=None, unknown_class=None):  # noqa: E501
        """BTExportTessellatedFacesBody - a model defined in OpenAPI"""  # noqa: E501

        self._id = None
        self._appearance = None
        self._faces = None
        self._body_type = None
        self._facet_points = None
        self._type_id = None
        self._connection_source = None
        self._export_type_name = None
        self._unknown_class = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if appearance is not None:
            self.appearance = appearance
        if faces is not None:
            self.faces = faces
        if body_type is not None:
            self.body_type = body_type
        if facet_points is not None:
            self.facet_points = facet_points
        if type_id is not None:
            self.type_id = type_id
        if connection_source is not None:
            self.connection_source = connection_source
        if export_type_name is not None:
            self.export_type_name = export_type_name
        if unknown_class is not None:
            self.unknown_class = unknown_class

    @property
    def id(self):
        """Gets the id of this BTExportTessellatedFacesBody.  # noqa: E501


        :return: The id of this BTExportTessellatedFacesBody.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this BTExportTessellatedFacesBody.


        :param id: The id of this BTExportTessellatedFacesBody.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def appearance(self):
        """Gets the appearance of this BTExportTessellatedFacesBody.  # noqa: E501


        :return: The appearance of this BTExportTessellatedFacesBody.  # noqa: E501
        :rtype: BTGraphicsAppearance
        """
        return self._appearance

    @appearance.setter
    def appearance(self, appearance):
        """Sets the appearance of this BTExportTessellatedFacesBody.


        :param appearance: The appearance of this BTExportTessellatedFacesBody.  # noqa: E501
        :type: BTGraphicsAppearance
        """

        self._appearance = appearance

    @property
    def faces(self):
        """Gets the faces of this BTExportTessellatedFacesBody.  # noqa: E501


        :return: The faces of this BTExportTessellatedFacesBody.  # noqa: E501
        :rtype: list[BTExportTessellatedFacesFace]
        """
        return self._faces

    @faces.setter
    def faces(self, faces):
        """Sets the faces of this BTExportTessellatedFacesBody.


        :param faces: The faces of this BTExportTessellatedFacesBody.  # noqa: E501
        :type: list[BTExportTessellatedFacesFace]
        """

        self._faces = faces

    @property
    def body_type(self):
        """Gets the body_type of this BTExportTessellatedFacesBody.  # noqa: E501


        :return: The body_type of this BTExportTessellatedFacesBody.  # noqa: E501
        :rtype: str
        """
        return self._body_type

    @body_type.setter
    def body_type(self, body_type):
        """Sets the body_type of this BTExportTessellatedFacesBody.


        :param body_type: The body_type of this BTExportTessellatedFacesBody.  # noqa: E501
        :type: str
        """
        allowed_values = ["SOLID", "SURFACE", "UNKNOWN"]  # noqa: E501
        if body_type not in allowed_values:
            raise ValueError(
                "Invalid value for `body_type` ({0}), must be one of {1}"  # noqa: E501
                .format(body_type, allowed_values)
            )

        self._body_type = body_type

    @property
    def facet_points(self):
        """Gets the facet_points of this BTExportTessellatedFacesBody.  # noqa: E501


        :return: The facet_points of this BTExportTessellatedFacesBody.  # noqa: E501
        :rtype: list[BTVector3d]
        """
        return self._facet_points

    @facet_points.setter
    def facet_points(self, facet_points):
        """Sets the facet_points of this BTExportTessellatedFacesBody.


        :param facet_points: The facet_points of this BTExportTessellatedFacesBody.  # noqa: E501
        :type: list[BTVector3d]
        """

        self._facet_points = facet_points

    @property
    def type_id(self):
        """Gets the type_id of this BTExportTessellatedFacesBody.  # noqa: E501


        :return: The type_id of this BTExportTessellatedFacesBody.  # noqa: E501
        :rtype: int
        """
        return self._type_id

    @type_id.setter
    def type_id(self, type_id):
        """Sets the type_id of this BTExportTessellatedFacesBody.


        :param type_id: The type_id of this BTExportTessellatedFacesBody.  # noqa: E501
        :type: int
        """

        self._type_id = type_id

    @property
    def connection_source(self):
        """Gets the connection_source of this BTExportTessellatedFacesBody.  # noqa: E501


        :return: The connection_source of this BTExportTessellatedFacesBody.  # noqa: E501
        :rtype: BTConnection
        """
        return self._connection_source

    @connection_source.setter
    def connection_source(self, connection_source):
        """Sets the connection_source of this BTExportTessellatedFacesBody.


        :param connection_source: The connection_source of this BTExportTessellatedFacesBody.  # noqa: E501
        :type: BTConnection
        """

        self._connection_source = connection_source

    @property
    def export_type_name(self):
        """Gets the export_type_name of this BTExportTessellatedFacesBody.  # noqa: E501


        :return: The export_type_name of this BTExportTessellatedFacesBody.  # noqa: E501
        :rtype: str
        """
        return self._export_type_name

    @export_type_name.setter
    def export_type_name(self, export_type_name):
        """Sets the export_type_name of this BTExportTessellatedFacesBody.


        :param export_type_name: The export_type_name of this BTExportTessellatedFacesBody.  # noqa: E501
        :type: str
        """

        self._export_type_name = export_type_name

    @property
    def unknown_class(self):
        """Gets the unknown_class of this BTExportTessellatedFacesBody.  # noqa: E501


        :return: The unknown_class of this BTExportTessellatedFacesBody.  # noqa: E501
        :rtype: bool
        """
        return self._unknown_class

    @unknown_class.setter
    def unknown_class(self, unknown_class):
        """Sets the unknown_class of this BTExportTessellatedFacesBody.


        :param unknown_class: The unknown_class of this BTExportTessellatedFacesBody.  # noqa: E501
        :type: bool
        """

        self._unknown_class = unknown_class

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
        if not isinstance(other, BTExportTessellatedFacesBody):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
