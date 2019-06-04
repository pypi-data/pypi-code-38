# coding: utf-8

"""
    ORCID Member

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: Latest
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six


class TranslatedTitleV30(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'value': 'str',
        'language_code': 'str'
    }

    attribute_map = {
        'value': 'value',
        'language_code': 'language-code'
    }

    def __init__(self, value=None, language_code=None):  # noqa: E501
        """TranslatedTitleV30 - a model defined in Swagger"""  # noqa: E501
        self._value = None
        self._language_code = None
        self.discriminator = None
        if value is not None:
            self.value = value
        self.language_code = language_code

    @property
    def value(self):
        """Gets the value of this TranslatedTitleV30.  # noqa: E501


        :return: The value of this TranslatedTitleV30.  # noqa: E501
        :rtype: str
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this TranslatedTitleV30.


        :param value: The value of this TranslatedTitleV30.  # noqa: E501
        :type: str
        """

        self._value = value

    @property
    def language_code(self):
        """Gets the language_code of this TranslatedTitleV30.  # noqa: E501


        :return: The language_code of this TranslatedTitleV30.  # noqa: E501
        :rtype: str
        """
        return self._language_code

    @language_code.setter
    def language_code(self, language_code):
        """Sets the language_code of this TranslatedTitleV30.


        :param language_code: The language_code of this TranslatedTitleV30.  # noqa: E501
        :type: str
        """
        if language_code is None:
            raise ValueError("Invalid value for `language_code`, must not be `None`")  # noqa: E501
        allowed_values = ["ab", "aa", "af", "ak", "sq", "am", "ar", "an", "hy", "as", "av", "ae", "ay", "az", "bm", "ba", "eu", "be", "bn", "bh", "bi", "bs", "br", "bg", "my", "ca", "ch", "ce", "zh_CN", "zh_TW", "cu", "cv", "kw", "co", "cr", "hr", "cs", "da", "dv", "nl", "dz", "en", "eo", "et", "ee", "fo", "fj", "fi", "fr", "fy", "ff", "gl", "lg", "ka", "de", "el", "kl", "gn", "gu", "ht", "ha", "iw", "hz", "hi", "ho", "hu", "is", "io", "ig", "in", "ia", "ie", "iu", "ik", "ga", "it", "ja", "jv", "kn", "kr", "ks", "kk", "km", "ki", "rw", "ky", "kv", "kg", "ko", "ku", "kj", "lo", "la", "lv", "li", "ln", "lt", "lu", "lb", "mk", "mg", "ms", "ml", "mt", "gv", "mi", "mr", "mh", "mo", "mn", "na", "nv", "ng", "ne", "nd", "se", "no", "nb", "nn", "ny", "oc", "oj", "or", "om", "os", "pi", "pa", "fa", "pl", "pt", "ps", "qu", "rm", "ro", "rn", "ru", "sm", "sg", "sa", "sc", "gd", "sr", "sn", "ii", "sd", "si", "sk", "sl", "so", "nr", "st", "es", "su", "sw", "ss", "sv", "tl", "ty", "tg", "ta", "tt", "te", "th", "bo", "ti", "to", "ts", "tn", "tr", "tk", "tw", "ug", "uk", "ur", "uz", "ve", "vi", "vo", "wa", "cy", "wo", "xh", "ji", "yo", "za", "zu"]  # noqa: E501
        if language_code not in allowed_values:
            raise ValueError(
                "Invalid value for `language_code` ({0}), must be one of {1}"  # noqa: E501
                .format(language_code, allowed_values)
            )

        self._language_code = language_code

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
        if issubclass(TranslatedTitleV30, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, TranslatedTitleV30):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
