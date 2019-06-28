# coding: utf-8

# -----------------------------------------------------------------------------------
# <copyright company="Aspose">
#   Copyright (c) 2018 Aspose.Slides for Cloud
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

import pprint
import re  # noqa: F401

import six

from asposeslidescloud.models.resource_base import ResourceBase

class Document(ResourceBase):


    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'self_uri': 'ResourceUri',
        'alternate_links': 'list[ResourceUri]',
        'document_properties': 'ResourceUriElement',
        'slides': 'ResourceUriElement',
        'images': 'ResourceUriElement',
        'layout_slides': 'ResourceUriElement',
        'master_slides': 'ResourceUriElement'
    }

    attribute_map = {
        'self_uri': 'SelfUri',
        'alternate_links': 'AlternateLinks',
        'document_properties': 'DocumentProperties',
        'slides': 'Slides',
        'images': 'Images',
        'layout_slides': 'LayoutSlides',
        'master_slides': 'MasterSlides'
    }

    def __init__(self, self_uri=None, alternate_links=None, document_properties=None, slides=None, images=None, layout_slides=None, master_slides=None):  # noqa: E501
        """Document - a model defined in Swagger"""  # noqa: E501
        super(Document, self).__init__(self_uri, alternate_links)

        self._document_properties = None
        self._slides = None
        self._images = None
        self._layout_slides = None
        self._master_slides = None

        if document_properties is not None:
            self.document_properties = document_properties
        if slides is not None:
            self.slides = slides
        if images is not None:
            self.images = images
        if layout_slides is not None:
            self.layout_slides = layout_slides
        if master_slides is not None:
            self.master_slides = master_slides

    @property
    def document_properties(self):
        """Gets the document_properties of this Document.  # noqa: E501

        Link to Document properties.  # noqa: E501

        :return: The document_properties of this Document.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._document_properties

    @document_properties.setter
    def document_properties(self, document_properties):
        """Sets the document_properties of this Document.

        Link to Document properties.  # noqa: E501

        :param document_properties: The document_properties of this Document.  # noqa: E501
        :type: ResourceUriElement
        """
        self._document_properties = document_properties

    @property
    def slides(self):
        """Gets the slides of this Document.  # noqa: E501

        Link to slides collection.  # noqa: E501

        :return: The slides of this Document.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._slides

    @slides.setter
    def slides(self, slides):
        """Sets the slides of this Document.

        Link to slides collection.  # noqa: E501

        :param slides: The slides of this Document.  # noqa: E501
        :type: ResourceUriElement
        """
        self._slides = slides

    @property
    def images(self):
        """Gets the images of this Document.  # noqa: E501

        Link to images collection.  # noqa: E501

        :return: The images of this Document.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._images

    @images.setter
    def images(self, images):
        """Sets the images of this Document.

        Link to images collection.  # noqa: E501

        :param images: The images of this Document.  # noqa: E501
        :type: ResourceUriElement
        """
        self._images = images

    @property
    def layout_slides(self):
        """Gets the layout_slides of this Document.  # noqa: E501

        Link to layout slides collection.  # noqa: E501

        :return: The layout_slides of this Document.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._layout_slides

    @layout_slides.setter
    def layout_slides(self, layout_slides):
        """Sets the layout_slides of this Document.

        Link to layout slides collection.  # noqa: E501

        :param layout_slides: The layout_slides of this Document.  # noqa: E501
        :type: ResourceUriElement
        """
        self._layout_slides = layout_slides

    @property
    def master_slides(self):
        """Gets the master_slides of this Document.  # noqa: E501

        Link to master slides collection.  # noqa: E501

        :return: The master_slides of this Document.  # noqa: E501
        :rtype: ResourceUriElement
        """
        return self._master_slides

    @master_slides.setter
    def master_slides(self, master_slides):
        """Sets the master_slides of this Document.

        Link to master slides collection.  # noqa: E501

        :param master_slides: The master_slides of this Document.  # noqa: E501
        :type: ResourceUriElement
        """
        self._master_slides = master_slides

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
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
        if not isinstance(other, Document):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
